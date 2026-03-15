#!/usr/bin/env python3
"""
招标雷达 - 月报生成脚本
生成每月业务数据报告

使用方法:
    python monthly_report.py [months_ago]
    python monthly_report.py          # 生成上月报告
    python monthly_report.py 0        # 生成本月报告
    python monthly_report.py 1        # 生成上月报告
    python monthly_report.py 2        # 生成2个月前的报告
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
import calendar

# 配置 - 使用绝对路径
BASE_DIR = Path("/home/daministrator/.openclaw/workspace/openclaw-income-factory")
DB_PATH = BASE_DIR / "data" / "tender_radar.db"
OUTPUT_DIR = BASE_DIR / "reports" / "monthly"


def get_db_connection():
    """获取数据库连接"""
    return sqlite3.connect(DB_PATH)


def get_month_range(months_ago=1):
    """获取指定月的开始和结束日期"""
    today = datetime.now()
    
    # 计算目标月份
    target_month = today.month - months_ago
    target_year = today.year
    
    while target_month <= 0:
        target_month += 12
        target_year -= 1
    
    # 月开始
    month_start = datetime(target_year, target_month, 1)
    # 月结束
    last_day = calendar.monthrange(target_year, target_month)[1]
    month_end = datetime(target_year, target_month, last_day)
    
    return month_start.strftime("%Y-%m-%d"), month_end.strftime("%Y-%m-%d"), target_year, target_month


def calculate_monthly_stats(conn, start_date, end_date):
    """计算月统计数据"""
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
    
    # 月收入 (MRR)
    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0) FROM payments 
        WHERE DATE(pay_date) BETWEEN ? AND ? AND status = 'completed'
    """, (start_date, end_date))
    mrr = cursor.fetchone()[0]
    
    # 新增招标
    cursor.execute("""
        SELECT COUNT(*) FROM tenders 
        WHERE DATE(created_date) BETWEEN ? AND ?
    """, (start_date, end_date))
    new_tenders = cursor.fetchone()[0]
    
    # 邮件统计
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
    
    # 按渠道统计
    cursor.execute("""
        SELECT channel, COUNT(*) FROM follow_ups 
        WHERE DATE(sent_date) BETWEEN ? AND ?
        GROUP BY channel
    """, (start_date, end_date))
    channel_stats = dict(cursor.fetchall())
    
    # 按plan统计付费
    cursor.execute("""
        SELECT plan, COUNT(*), SUM(amount) FROM payments 
        WHERE DATE(pay_date) BETWEEN ? AND ? AND status = 'completed'
        GROUP BY plan
    """, (start_date, end_date))
    plan_stats = cursor.fetchall()
    
    # 总用户统计
    cursor.execute("SELECT COUNT(*) FROM leads")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM leads WHERE trial_start_date IS NOT NULL")
    total_trials = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT subscriber_id) FROM payments WHERE status = 'completed'")
    total_paid = cursor.fetchone()[0]
    
    # 累计收入
    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status = 'completed'")
    total_revenue = cursor.fetchone()[0]
    
    # 招标总数
    cursor.execute("SELECT COUNT(*) FROM tenders")
    total_tenders = cursor.fetchone()[0]
    
    # 计算LTV (假设用户平均生命周期24个月)
    arpu = total_revenue / total_paid if total_paid > 0 else 0
    ltv = arpu * 24
    
    return {
        "new_users": new_users,
        "new_trials": new_trials,
        "new_paid": new_paid,
        "mrr": mrr,
        "new_tenders": new_tenders,
        "emails_sent": emails_sent,
        "emails_opened": emails_opened,
        "emails_replied": emails_replied,
        "channel_stats": channel_stats,
        "plan_stats": plan_stats,
        "total_users": total_users,
        "total_trials": total_trials,
        "total_paid": total_paid,
        "total_revenue": total_revenue,
        "total_tenders": total_tenders,
        "arpu": round(arpu, 2),
        "ltv": round(ltv, 2)
    }


def get_last_month_stats(conn):
    """获取上月数据用于对比"""
    last_start, last_end, _, _ = get_month_range(2)
    return calculate_monthly_stats(conn, last_start, last_end)


def calculate_monthly_retention(conn, start_date):
    """计算月留存率"""
    cursor = conn.cursor()
    
    # 30日留存
    d30_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=30)).strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT COUNT(DISTINCT lead_id) FROM follow_ups 
        WHERE DATE(sent_date) = ?
    """, (d30_date,))
    d30_users = cursor.fetchone()[0]
    
    # 获取开始日新增用户
    cursor.execute("SELECT COUNT(*) FROM leads WHERE DATE(created_date) = ?", (start_date,))
    base_users = cursor.fetchone()[0]
    
    d30_rate = (d30_users / base_users * 100) if base_users > 0 else 0
    
    return {
        "d30_retention": round(d30_rate, 2),
        "base_users": base_users
    }


def generate_monthly_report(months_ago=1):
    """生成月报告"""
    start_date, end_date, year, month = get_month_range(months_ago)
    month_name = calendar.month_name[month]
    
    conn = get_db_connection()
    
    # 本月统计
    stats = calculate_monthly_stats(conn, start_date, end_date)
    
    # 留存率
    retention = calculate_monthly_retention(conn, start_date)
    
    # 上月对比
    last_month = get_last_month_stats(conn)
    
    conn.close()
    
    # 计算变化
    def calc_change(current, previous):
        if previous == 0:
            return 0
        return round((current - previous) / previous * 100, 2)
    
    report = {
        "month": f"{year}年{month_name}",
        "year": year,
        "month_num": month,
        "start_date": start_date,
        "end_date": end_date,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "new_users": stats["new_users"],
            "new_users_change": calc_change(stats["new_users"], last_month["new_users"]),
            "new_trials": stats["new_trials"],
            "new_paid": stats["new_paid"],
            "mrr": stats["mrr"],
            "mrr_change": calc_change(stats["mrr"], last_month["mrr"]),
            "new_tenders": stats["new_tenders"],
            "new_tenders_change": calc_change(stats["new_tenders"], last_month["new_tenders"])
        },
        "retention": retention,
        "email_metrics": {
            "sent": stats["emails_sent"],
            "opened": stats["emails_opened"],
            "replied": stats["emails_replied"],
            "open_rate": round(stats["emails_opened"] / stats["emails_sent"] * 100, 2) if stats["emails_sent"] > 0 else 0,
            "reply_rate": round(stats["emails_replied"] / stats["emails_sent"] * 100, 2) if stats["emails_sent"] > 0 else 0,
            "by_channel": stats["channel_stats"]
        },
        "subscription": {
            "by_plan": [{"plan": p[0], "count": p[1], "revenue": p[2]} for p in stats["plan_stats"]]
        },
        "financial": {
            "arpu": stats["arpu"],
            "ltv": stats["ltv"],
            "total_revenue": stats["total_revenue"],
            "total_paid": stats["total_paid"],
            "pay_conversion_rate": round(stats["new_paid"] / stats["new_trials"] * 100, 2) if stats["new_trials"] > 0 else 0
        },
        "cumulative": {
            "total_users": stats["total_users"],
            "total_trials": stats["total_trials"],
            "total_paid": stats["total_paid"],
            "total_revenue": stats["total_revenue"],
            "total_tenders": stats["total_tenders"]
        },
        "arr": stats["mrr"] * 12  # 年度经常性收入
    }
    
    return report


def save_report_json(report, output_dir):
    """保存JSON格式报告"""
    month_str = f"{report['year']}_{report['month_num']:02d}"
    output_path = output_dir / f"{month_str}.json"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return output_path


def generate_markdown_report(report):
    """生成Markdown格式报告"""
    summary = report["summary"]
    email = report["email_metrics"]
    retention = report["retention"]
    financial = report["financial"]
    cumulative = report["cumulative"]
    subscription = report["subscription"]
    
    def trend(change):
        if change > 0:
            return f"↑ {change}%"
        elif change < 0:
            return f"↓ {abs(change)}%"
        return "-"
    
    # 订阅计划明细
    plan_rows = ""
    for plan in subscription["by_plan"]:
        plan_rows += f"| {plan['plan']} | {plan['count']} | ¥{plan['revenue']} |\n"
    
    # 渠道明细
    channel_rows = ""
    for channel, count in email["by_channel"].items():
        channel_rows += f"| {channel} | {count} |\n"
    
    md = f"""# 📊 招标雷达 - 月度数据报告

**月份**: {report["month"]}  
**周期**: {report["start_date"]} ~ {report["end_date"]}  
**生成时间**: {report["generated_at"]}

---

## 📈 核心指标

| 指标 | 本月 | 环比变化 |
|-----|------|---------|
| 新增用户 | {summary["new_users"]} | {trend(summary['new_users_change'])} |
| 新增试用 | {summary["new_trials"]} | - |
| 新增付费 | {summary["new_paid"]} | - |
| 月收入 (MRR) | ¥{summary["mrr"]} | {trend(summary['mrr_change'])} |
| 新增招标 | {summary["new_tenders"]} | {trend(summary['new_tenders_change'])} |

---

## 💰 收入分析

| 指标 | 数值 |
|-----|------|
| 月收入 (MRR) | ¥{summary["mrr"]} |
| 年度收入 (ARR) | ¥{report["arr"]} |
| 累计收入 | ¥{financial["total_revenue"]} |
| ARPU | ¥{financial["arpu"]} |
| LTV | ¥{financial["ltv"]} |
| 付费转化率 | {financial['pay_conversion_rate']}% |

### 订阅计划分布

| 计划 | 付费用户数 | 收入 |
|-----|-----------|------|
{plan_rows}

---

## 👥 用户留存

| 指标 | 数值 |
|-----|------|
| 30日留存率 | {retention["d30_retention"]}% |
| 基准用户数 | {retention["base_users"]} |

---

## 📬 邮件营销效果

| 指标 | 数值 | 比例 |
|-----|------|-----|
| 发送总数 | {email["sent"]} | |
| 打开数 | {email["opened"]} | {email["open_rate"]}% |
| 回复数 | {email["replied"]} | {email["reply_rate"]}% |

### 渠道分布

| 渠道 | 发送量 |
|-----|-------|
{channel_rows}

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

## 🎯 关键洞察

1. **用户增长**: 本月新增用户 {summary['new_users']} 人，{trend(summary['new_users_change'])}
2. **收入表现**: MRR ¥{summary['mrr']}，{trend(summary['mrr_change'])}
3. **获客成本**: LTV/ARPU = {round(financial['ltv'] / financial['arpu'], 1) if financial['arpu'] > 0 else 'N/A'}
4. **营销效果**: 邮件打开率 {email['open_rate']}%，回复率 {email['reply_rate']}%

---

*报告自动生成于 招标雷达系统*
"""
    return md


def save_report_markdown(report, output_dir):
    """保存Markdown格式报告"""
    month_str = f"{report['year']}_{report['month_num']:02d}"
    output_path = output_dir / f"{month_str}.md"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    md_content = generate_markdown_report(report)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    return output_path


def main():
    import sys
    months_ago = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    
    start_date, end_date, year, month = get_month_range(months_ago)
    month_name = calendar.month_name[month]
    print(f"📊 生成 {year}年{month_name} 的月报告...")
    
    # 生成报告
    report = generate_monthly_report(months_ago)
    
    # 保存JSON
    json_path = save_report_json(report, OUTPUT_DIR)
    print(f"✅ JSON报告已保存: {json_path}")
    
    # 保存Markdown
    md_path = save_report_markdown(report, OUTPUT_DIR)
    print(f"✅ Markdown报告已保存: {md_path}")
    
    # 打印摘要
    print(f"\n📋 报告摘要:")
    print(f"   新增用户: {report['summary']['new_users']}")
    print(f"   月收入: ¥{report['summary']['mrr']}")
    print(f"   ARR: ¥{report['arr']}")
    print(f"   LTV: ¥{report['financial']['ltv']}")


if __name__ == "__main__":
    main()
