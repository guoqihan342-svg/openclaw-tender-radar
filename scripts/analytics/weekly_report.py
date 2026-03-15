#!/usr/bin/env python3
"""
招标雷达 - 周报生成脚本
生成每周业务数据报告

使用方法:
    python weekly_report.py [weeks_ago]
    python weekly_report.py          # 生成上周报告
    python weekly_report.py 1        # 生成上周报告
    python weekly_report.py 2        # 生成2周前的报告
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

# 配置 - 使用绝对路径
BASE_DIR = Path("/home/daministrator/.openclaw/workspace/openclaw-income-factory")
DB_PATH = BASE_DIR / "data" / "tender_radar.db"
OUTPUT_DIR = BASE_DIR / "reports" / "weekly"


def get_db_connection():
    """获取数据库连接"""
    return sqlite3.connect(DB_PATH)


def get_week_range(weeks_ago=1):
    """获取指定周的开始和结束日期"""
    today = datetime.now()
    # 上周开始 (周一)
    week_start = today - timedelta(days=today.weekday() + 7 * weeks_ago)
    # 上周结束 (周日)
    week_end = week_start + timedelta(days=6)
    
    return week_start.strftime("%Y-%m-%d"), week_end.strftime("%Y-%m-%d")


def calculate_weekly_stats(conn, start_date, end_date):
    """计算周统计数据"""
    cursor = conn.cursor()
    
    # 新增用户
    cursor.execute("""
        SELECT COUNT(*) FROM leads 
        WHERE DATE(created_date) BETWEEN ? AND ?
    """, (start_date, end_date))
    new_users = cursor.fetchone()[0]
    
    # 新增试用用户
    cursor.execute("""
        SELECT COUNT(*) FROM leads 
        WHERE DATE(trial_start_date) BETWEEN ? AND ?
    """, (start_date, end_date))
    new_trials = cursor.fetchone()[0]
    
    # 新增付费用户
    cursor.execute("""
        SELECT COUNT(DISTINCT subscriber_id) FROM payments 
        WHERE DATE(pay_date) BETWEEN ? AND ? AND status = 'completed'
    """, (start_date, end_date))
    new_paid = cursor.fetchone()[0]
    
    # 收入
    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0) FROM payments 
        WHERE DATE(pay_date) BETWEEN ? AND ? AND status = 'completed'
    """, (start_date, end_date))
    revenue = cursor.fetchone()[0]
    
    # 新增招标
    cursor.execute("""
        SELECT COUNT(*) FROM tenders 
        WHERE DATE(created_date) BETWEEN ? AND ?
    """, (start_date, end_date))
    new_tenders = cursor.fetchone()[0]
    
    # 邮件发送统计
    cursor.execute("""
        SELECT COUNT(*), 
               SUM(CASE WHEN opened = 1 THEN 1 ELSE 0 END),
               SUM(CASE WHEN replied = 1 THEN 1 ELSE 0 END)
        FROM follow_ups 
        WHERE DATE(sent_date) BETWEEN ? AND ?
    """, (start_date, end_date))
    email_stats = cursor.fetchone()
    emails_sent = email_stats[0]
    emails_opened = email_stats[1] or 0
    emails_replied = email_stats[2] or 0
    
    # 总用户统计
    cursor.execute("SELECT COUNT(*) FROM leads")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM leads WHERE trial_start_date IS NOT NULL")
    total_trials = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT subscriber_id) FROM payments WHERE status = 'completed'")
    total_paid = cursor.fetchone()[0]
    
    # 总收入
    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status = 'completed'")
    total_revenue = cursor.fetchone()[0]
    
    # 招标总数
    cursor.execute("SELECT COUNT(*) FROM tenders")
    total_tenders = cursor.fetchone()[0]
    
    return {
        "new_users": new_users,
        "new_trials": new_trials,
        "new_paid": new_paid,
        "revenue": revenue,
        "new_tenders": new_tenders,
        "emails_sent": emails_sent,
        "emails_opened": emails_opened,
        "emails_replied": emails_replied,
        "total_users": total_users,
        "total_trials": total_trials,
        "total_paid": total_paid,
        "total_revenue": total_revenue,
        "total_tenders": total_tenders
    }


def calculate_retention(conn, start_date):
    """计算留存率"""
    cursor = conn.cursor()
    
    # 次日留存
    d1_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT COUNT(DISTINCT lead_id) FROM follow_ups 
        WHERE DATE(sent_date) = ?
    """, (d1_date,))
    d1_users = cursor.fetchone()[0]
    
    # 7日留存
    d7_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=7)).strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT COUNT(DISTINCT lead_id) FROM follow_ups 
        WHERE DATE(sent_date) = ?
    """, (d7_date,))
    d7_users = cursor.fetchone()[0]
    
    # 获取开始日新增用户
    cursor.execute("SELECT COUNT(*) FROM leads WHERE DATE(created_date) = ?", (start_date,))
    base_users = cursor.fetchone()[0]
    
    d1_rate = (d1_users / base_users * 100) if base_users > 0 else 0
    d7_rate = (d7_users / base_users * 100) if base_users > 0 else 0
    
    return {
        "d1_retention": round(d1_rate, 2),
        "d7_retention": round(d7_rate, 2),
        "base_users": base_users
    }


def get_last_week_stats(conn):
    """获取上周数据用于对比"""
    last_week_start = (datetime.now() - timedelta(days=datetime.now().weekday() + 14)).strftime("%Y-%m-%d")
    last_week_end = (datetime.now() - timedelta(days=datetime.now().weekday() + 8)).strftime("%Y-%m-%d")
    return calculate_weekly_stats(conn, last_week_start, last_week_end)


def generate_weekly_report(weeks_ago=1):
    """生成周报告"""
    start_date, end_date = get_week_range(weeks_ago)
    
    conn = get_db_connection()
    
    # 本周统计
    stats = calculate_weekly_stats(conn, start_date, end_date)
    
    # 留存率
    retention = calculate_retention(conn, start_date)
    
    # 上周对比
    last_week = get_last_week_stats(conn)
    
    conn.close()
    
    # 计算变化
    def calc_change(current, previous):
        if previous == 0:
            return 0
        return round((current - previous) / previous * 100, 2)
    
    report = {
        "week": f"{start_date} ~ {end_date}",
        "start_date": start_date,
        "end_date": end_date,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "new_users": stats["new_users"],
            "new_users_change": calc_change(stats["new_users"], last_week["new_users"]),
            "new_trials": stats["new_trials"],
            "new_paid": stats["new_paid"],
            "revenue": stats["revenue"],
            "revenue_change": calc_change(stats["revenue"], last_week["revenue"]),
            "new_tenders": stats["new_tenders"]
        },
        "retention": retention,
        "email_metrics": {
            "sent": stats["emails_sent"],
            "opened": stats["emails_opened"],
            "replied": stats["emails_replied"],
            "open_rate": round(stats["emails_opened"] / stats["emails_sent"] * 100, 2) if stats["emails_sent"] > 0 else 0,
            "reply_rate": round(stats["emails_replied"] / stats["emails_sent"] * 100, 2) if stats["emails_sent"] > 0 else 0
        },
        "cumulative": {
            "total_users": stats["total_users"],
            "total_trials": stats["total_trials"],
            "total_paid": stats["total_paid"],
            "total_revenue": stats["total_revenue"],
            "total_tenders": stats["total_tenders"]
        }
    }
    
    return report


def save_report_json(report, output_dir):
    """保存JSON格式报告"""
    week = report["week"].replace(" ~ ", "_")
    output_path = output_dir / f"{week}.json"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return output_path


def generate_markdown_report(report):
    """生成Markdown格式报告"""
    summary = report["summary"]
    email = report["email_metrics"]
    retention = report["retention"]
    cumulative = report["cumulative"]
    
    def trend(change):
        if change > 0:
            return f"↑ {change}%"
        elif change < 0:
            return f"↓ {abs(change)}%"
        return "-"
    
    md = f"""# 📊 招标雷达 - 周数据报告

**周期**: {report["week"]}  
**生成时间**: {report["generated_at"]}

---

## 📈 核心指标

| 指标 | 本周 | 环比变化 |
|-----|------|---------|
| 新增用户 | {summary["new_users"]} | {trend(summary['new_users_change'])} |
| 新增试用 | {summary["new_trials"]} | - |
| 新增付费 | {summary["new_paid"]} | - |
| 周收入 | ¥{summary["revenue"]} | {trend(summary['revenue_change'])} |
| 新增招标 | {summary["new_tenders"]} | - |

---

## 👥 用户留存

| 指标 | 数值 |
|-----|------|
| 次日留存率 | {retention["d1_retention"]}% |
| 7日留存率 | {retention["d7_retention"]}% |
| 基准用户数 | {retention["base_users"]} |

---

## 📬 邮件效果

| 指标 | 数值 | 比例 |
|-----|------|-----|
| 发送数量 | {email["sent"]} | |
| 打开数量 | {email["opened"]} | {email["open_rate"]}% |
| 回复数量 | {email["replied"]} | {email["reply_rate"]}% |

---

## 📉 累计数据

| 指标 | 总数 |
|-----|------|
| 注册用户 | {cumulative["total_users"]} |
| 试用用户 | {cumulative["total_trials"]} |
| 付费用户 | {cumulative["total_paid"]} |
| 累计收入 | ¥{cumulative["total_revenue"]} |
| 招标总数 | {cumulative["total_tenders"]} |

---

## 💰 收入明细

- **ARPU**: ¥{round(cumulative['total_revenue'] / cumulative['total_paid'], 2) if cumulative['total_paid'] > 0 else 0}
- **付费转化率**: {round(cumulative['total_paid'] / cumulative['total_trials'] * 100, 2) if cumulative['total_trials'] > 0 else 0}%

---

*报告自动生成于 招标雷达系统*
"""
    return md


def save_report_markdown(report, output_dir):
    """保存Markdown格式报告"""
    week = report["week"].replace(" ~ ", "_")
    output_path = output_dir / f"{week}.md"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    md_content = generate_markdown_report(report)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    return output_path


def main():
    import sys
    weeks_ago = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    
    start_date, end_date = get_week_range(weeks_ago)
    print(f"📊 生成 {start_date} ~ {end_date} 的周报告...")
    
    # 生成报告
    report = generate_weekly_report(weeks_ago)
    
    # 保存JSON
    json_path = save_report_json(report, OUTPUT_DIR)
    print(f"✅ JSON报告已保存: {json_path}")
    
    # 保存Markdown
    md_path = save_report_markdown(report, OUTPUT_DIR)
    print(f"✅ Markdown报告已保存: {md_path}")
    
    # 打印摘要
    print(f"\n📋 报告摘要:")
    print(f"   新增用户: {report['summary']['new_users']}")
    print(f"   周收入: ¥{report['summary']['revenue']}")
    print(f"   次日留存: {report['retention']['d1_retention']}%")


if __name__ == "__main__":
    main()
