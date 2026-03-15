#!/usr/bin/env python3
"""
招标雷达 - 每日数据汇总脚本
生成每日业务数据报告

使用方法:
    python daily_report.py [date]
    python daily_report.py          # 生成昨天的报告
    python daily_report.py 2026-03-14  # 生成指定日期的报告
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# 配置 - 使用绝对路径
BASE_DIR = Path("/home/daministrator/.openclaw/workspace/openclaw-income-factory")
DB_PATH = BASE_DIR / "data" / "tender_radar.db"
OUTPUT_DIR = BASE_DIR / "reports" / "daily"
TEMPLATE_DIR = BASE_DIR / "templates"


def get_db_connection():
    """获取数据库连接"""
    return sqlite3.connect(DB_PATH)


def get_date_arg():
    """获取命令行日期参数"""
    import sys
    if len(sys.argv) > 1:
        return sys.argv[1]
    return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")


def calculate_dau(conn, date):
    """计算日活跃用户数"""
    cursor = conn.cursor()
    # 活跃用户: 有跟进记录的用户
    cursor.execute("""
        SELECT COUNT(DISTINCT lead_id) 
        FROM follow_ups 
        WHERE DATE(sent_date) = ?
    """, (date,))
    result = cursor.fetchone()[0]
    return result if result else 0


def calculate_new_users(conn, date):
    """计算新增用户数"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM leads 
        WHERE DATE(created_date) = ?
    """, (date,))
    return cursor.fetchone()[0]


def calculate_trial_users(conn, date):
    """计算新增试用用户数"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM leads 
        WHERE DATE(trial_start_date) = ?
    """, (date,))
    return cursor.fetchone()[0]


def calculate_paid_users(conn, date):
    """计算新增付费用户数"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(DISTINCT subscriber_id) FROM payments 
        WHERE DATE(pay_date) = ? AND status = 'completed'
    """, (date,))
    return cursor.fetchone()[0]


def calculate_revenue(conn, date):
    """计算当日收入"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0) FROM payments 
        WHERE DATE(pay_date) = ? AND status = 'completed'
    """, (date,))
    return cursor.fetchone()[0]


def calculate_new_tenders(conn, date):
    """计算新增招标数"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM tenders 
        WHERE DATE(created_date) = ?
    """, (date,))
    return cursor.fetchone()[0]


def calculate_total_tenders(conn):
    """计算招标总数"""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tenders")
    return cursor.fetchone()[0]


def calculate_emails_sent(conn, date):
    """计算邮件发送数"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM follow_ups 
        WHERE DATE(sent_date) = ?
    """, (date,))
    return cursor.fetchone()[0]


def calculate_emails_opened(conn, date):
    """计算邮件打开数"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM follow_ups 
        WHERE DATE(sent_date) = ? AND opened = 1
    """, (date,))
    return cursor.fetchone()[0]


def calculate_emails_replied(conn, date):
    """计算邮件回复数"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM follow_ups 
        WHERE DATE(sent_date) = ? AND replied = 1
    """, (date,))
    return cursor.fetchone()[0]


def calculate_conversion_rates(conn, date):
    """计算转化率"""
    cursor = conn.cursor()
    
    # 总注册用户
    cursor.execute("SELECT COUNT(*) FROM leads WHERE DATE(created_date) <= ?", (date,))
    total_users = cursor.fetchone()[0]
    
    # 试用用户
    cursor.execute("SELECT COUNT(*) FROM leads WHERE trial_start_date IS NOT NULL")
    trial_users = cursor.fetchone()[0]
    
    # 付费用户
    cursor.execute("SELECT COUNT(DISTINCT subscriber_id) FROM payments WHERE status = 'completed'")
    paid_users = cursor.fetchone()[0]
    
    trial_rate = (trial_users / total_users * 100) if total_users > 0 else 0
    pay_rate = (paid_users / trial_users * 100) if trial_users > 0 else 0
    
    return {
        "trial_rate": round(trial_rate, 2),
        "pay_rate": round(pay_rate, 2),
        "total_users": total_users,
        "trial_users": trial_users,
        "paid_users": paid_users
    }


def calculate_yesterday_dau(conn, yesterday):
    """计算昨日DAU用于对比"""
    return calculate_dau(conn, yesterday)


def generate_daily_report(date):
    """生成每日报告"""
    yesterday = (datetime.strptime(date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    
    conn = get_db_connection()
    
    # 核心指标
    dau = calculate_dau(conn, date)
    yesterday_dau = calculate_yesterday_dau(conn, yesterday)
    dau_change = ((dau - yesterday_dau) / yesterday_dau * 100) if yesterday_dau > 0 else 0
    
    new_users = calculate_new_users(conn, date)
    trial_users = calculate_trial_users(conn, date)
    paid_users = calculate_paid_users(conn, date)
    revenue = calculate_revenue(conn, date)
    
    new_tenders = calculate_new_tenders(conn, date)
    total_tenders = calculate_total_tenders(conn)
    
    emails_sent = calculate_emails_sent(conn, date)
    emails_opened = calculate_emails_opened(conn, date)
    emails_replied = calculate_emails_replied(conn, date)
    
    open_rate = (emails_opened / emails_sent * 100) if emails_sent > 0 else 0
    reply_rate = (emails_replied / emails_sent * 100) if emails_sent > 0 else 0
    
    conversion_rates = calculate_conversion_rates(conn, date)
    
    conn.close()
    
    # 汇总数据
    report = {
        "date": date,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "dau": dau,
            "dau_change": round(dau_change, 2),
            "new_users": new_users,
            "trial_users": trial_users,
            "paid_users": paid_users,
            "revenue": revenue,
            "new_tenders": new_tenders,
            "total_tenders": total_tenders
        },
        "email_metrics": {
            "sent": emails_sent,
            "opened": emails_opened,
            "replied": emails_replied,
            "open_rate": round(open_rate, 2),
            "reply_rate": round(reply_rate, 2)
        },
        "conversion": conversion_rates
    }
    
    return report


def save_report_json(report, output_dir):
    """保存JSON格式报告"""
    date = report["date"]
    output_path = output_dir / f"{date}.json"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return output_path


def generate_markdown_report(report):
    """生成Markdown格式报告"""
    date = report["date"]
    summary = report["summary"]
    email = report["email_metrics"]
    conv = report["conversion"]
    
    md = f"""# 📊 招标雷达 - 每日数据报告

**日期**: {date}  
**生成时间**: {report["generated_at"]}

---

## 📈 核心指标

| 指标 | 数值 | 备注 |
|-----|------|-----|
| 日活跃用户 (DAU) | **{summary["dau"]}** | {'↑' if summary['dau_change'] > 0 else '↓'} {abs(summary['dau_change'])}% vs 昨日 |
| 新增用户 | {summary["new_users"]} | |
| 新增试用用户 | {summary["trial_users"]} | |
| 新增付费用户 | {summary["paid_users"]} | |
| 当日收入 | ¥{summary["revenue"]} | |

---

## 📬 邮件推送指标

| 指标 | 数值 | 比例 |
|-----|------|-----|
| 发送数量 | {email["sent"]} | |
| 打开数量 | {email["opened"]} | {email["open_rate"]}% |
| 回复数量 | {email["replied"]} | {email["reply_rate"]}% |

---

## 🎯 转化漏斗

| 阶段 | 数量 | 转化率 |
|-----|------|-------|
| 总注册用户 | {conv["total_users"]} | - |
| 试用用户 | {conv["trial_users"]} | {conv["trial_rate"]}% |
| 付费用户 | {conv["paid_users"]} | {conv["pay_rate"]}% |

---

## 📋 招标数据

| 指标 | 数值 |
|-----|------|
| 今日新增招标 | {summary["new_tenders"]} |
| 招标总数 | {summary["total_tenders"]} |

---

*报告自动生成于 招标雷达系统*
"""
    return md


def save_report_markdown(report, output_dir):
    """保存Markdown格式报告"""
    date = report["date"]
    output_path = output_dir / f"{date}.md"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    md_content = generate_markdown_report(report)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    return output_path


def main():
    date = get_date_arg()
    print(f"📊 生成 {date} 的每日报告...")
    
    # 生成报告
    report = generate_daily_report(date)
    
    # 保存JSON
    json_path = save_report_json(report, OUTPUT_DIR)
    print(f"✅ JSON报告已保存: {json_path}")
    
    # 保存Markdown
    md_path = save_report_markdown(report, OUTPUT_DIR)
    print(f"✅ Markdown报告已保存: {md_path}")
    
    # 打印摘要
    print(f"\n📋 报告摘要:")
    print(f"   DAU: {report['summary']['dau']}")
    print(f"   新增用户: {report['summary']['new_users']}")
    print(f"   收入: ¥{report['summary']['revenue']}")
    print(f"   邮件打开率: {report['email_metrics']['open_rate']}%")


if __name__ == "__main__":
    main()
