#!/usr/bin/env python3
"""
招标雷达 - 看板数据生成脚本
生成 dashboard 需要的 data.json 文件

使用方法:
    python generate_dashboard_data.py
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

# 配置 - 使用绝对路径
BASE_DIR = Path("/home/daministrator/.openclaw/workspace/openclaw-income-factory")
DB_PATH = BASE_DIR / "data" / "tender_radar.db"
OUTPUT_PATH = BASE_DIR / "site" / "dashboard" / "data.json"


def get_db_connection():
    return sqlite3.connect(DB_PATH)


def get_today_stats(conn):
    """获取今日统计"""
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    cursor = conn.cursor()
    
    # DAU
    cursor.execute("""
        SELECT COUNT(DISTINCT lead_id) FROM follow_ups 
        WHERE DATE(sent_date) = ?
    """, (today,))
    dau = cursor.fetchone()[0] or 0
    
    cursor.execute("""
        SELECT COUNT(DISTINCT lead_id) FROM follow_ups 
        WHERE DATE(sent_date) = ?
    """, (yesterday,))
    yesterday_dau = cursor.fetchone()[0] or 0
    
    # 新增用户
    cursor.execute("SELECT COUNT(*) FROM leads WHERE DATE(created_date) = ?", (today,))
    new_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM leads WHERE DATE(created_date) = ?", (yesterday,))
    yesterday_new_users = cursor.fetchone()[0]
    
    # 收入
    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0) FROM payments 
        WHERE DATE(pay_date) = ? AND status = 'completed'
    """, (today,))
    revenue = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0) FROM payments 
        WHERE DATE(pay_date) = ? AND status = 'completed'
    """, (yesterday,))
    yesterday_revenue = cursor.fetchone()[0]
    
    # 新增招标
    cursor.execute("SELECT COUNT(*) FROM tenders WHERE DATE(created_date) = ?", (today,))
    new_tenders = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tenders WHERE DATE(created_date) = ?", (yesterday,))
    yesterday_new_tenders = cursor.fetchone()[0]
    
    # 邮件统计
    cursor.execute("""
        SELECT COUNT(*), 
               SUM(CASE WHEN opened = 1 THEN 1 ELSE 0 END),
               SUM(CASE WHEN replied = 1 THEN 1 ELSE 0 END)
        FROM follow_ups WHERE DATE(sent_date) = ?
    """, (today,))
    email_stats = cursor.fetchone()
    emails_sent = email_stats[0]
    emails_opened = email_stats[1] or 0
    emails_replied = email_stats[2] or 0
    
    cursor.execute("""
        SELECT COUNT(*), 
               SUM(CASE WHEN opened = 1 THEN 1 ELSE 0 END)
        FROM follow_ups WHERE DATE(sent_date) = ?
    """, (yesterday,))
    yes_email_stats = cursor.fetchone()
    yes_emails_sent = yes_email_stats[0]
    yes_emails_opened = yes_email_stats[1] or 0
    
    open_rate = (emails_opened / emails_sent * 100) if emails_sent > 0 else 0
    reply_rate = (emails_replied / emails_sent * 100) if emails_sent > 0 else 0
    
    yes_open_rate = (yes_emails_opened / yes_emails_sent * 100) if yes_emails_sent > 0 else 0
    
    return {
        "dau": dau,
        "new_users": new_users,
        "revenue": revenue,
        "new_tenders": new_tenders,
        "emails_sent": emails_sent,
        "emails_opened": emails_opened,
        "emails_replied": emails_replied,
        "open_rate": round(open_rate, 1),
        "reply_rate": round(reply_rate, 1)
    }, {
        "dau": yesterday_dau,
        "new_users": yesterday_new_users,
        "revenue": yesterday_revenue,
        "new_tenders": yesterday_new_tenders,
        "open_rate": round(yes_open_rate, 1)
    }


def get_conversion_data(conn):
    """获取转化数据"""
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM leads")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM leads WHERE trial_start_date IS NOT NULL")
    trial_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT subscriber_id) FROM payments WHERE status = 'completed'")
    paid_users = cursor.fetchone()[0]
    
    trial_rate = (trial_users / total_users * 100) if total_users > 0 else 0
    pay_rate = (paid_users / trial_users * 100) if trial_users > 0 else 0
    
    return {
        "total_users": total_users,
        "trial_users": trial_users,
        "paid_users": paid_users,
        "trial_rate": round(trial_rate, 1),
        "pay_rate": round(pay_rate, 1)
    }


def get_trend_7d(conn):
    """获取7天趋势数据"""
    cursor = conn.cursor()
    trend = []
    
    for i in range(6, -1, -1):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        
        # DAU
        cursor.execute("""
            SELECT COUNT(DISTINCT lead_id) FROM follow_ups 
            WHERE DATE(sent_date) = ?
        """, (date,))
        dau = cursor.fetchone()[0] or 0
        
        # 新增用户
        cursor.execute("SELECT COUNT(*) FROM leads WHERE DATE(created_date) = ?", (date,))
        new_users = cursor.fetchone()[0]
        
        # 收入
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) FROM payments 
            WHERE DATE(pay_date) = ? AND status = 'completed'
        """, (date,))
        revenue = cursor.fetchone()[0]
        
        # 新增招标
        cursor.execute("SELECT COUNT(*) FROM tenders WHERE DATE(created_date) = ?", (date,))
        new_tenders = cursor.fetchone()[0]
        
        # 邮件统计
        cursor.execute("""
            SELECT COUNT(*), 
                   SUM(CASE WHEN opened = 1 THEN 1 ELSE 0 END),
                   SUM(CASE WHEN replied = 1 THEN 1 ELSE 0 END)
            FROM follow_ups WHERE DATE(sent_date) = ?
        """, (date,))
        email_stats = cursor.fetchone()
        emails_sent = email_stats[0]
        emails_opened = email_stats[1] or 0
        emails_replied = email_stats[2] or 0
        
        open_rate = (emails_opened / emails_sent * 100) if emails_sent > 0 else 0
        reply_rate = (emails_replied / emails_sent * 100) if emails_sent > 0 else 0
        
        trend.append({
            "date": date,
            "dau": dau,
            "new_users": new_users,
            "revenue": revenue,
            "new_tenders": new_tenders,
            "emails_sent": emails_sent,
            "open_rate": round(open_rate, 1),
            "reply_rate": round(reply_rate, 1)
        })
    
    return trend


def generate_dashboard_data():
    """生成看板数据"""
    conn = get_db_connection()
    
    today_stats, yesterday_stats = get_today_stats(conn)
    conversion = get_conversion_data(conn)
    trend_7d = get_trend_7d(conn)
    
    conn.close()
    
    data = {
        "generated_at": datetime.now().isoformat(),
        "today": today_stats,
        "yesterday": yesterday_stats,
        "conversion": conversion,
        "trend_7d": trend_7d
    }
    
    return data


def main():
    print("📊 生成看板数据...")
    
    data = generate_dashboard_data()
    
    # 保存数据
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 数据已保存到: {OUTPUT_PATH}")
    print(f"\n📋 数据摘要:")
    print(f"   DAU: {data['today']['dau']}")
    print(f"   新增用户: {data['today']['new_users']}")
    print(f"   收入: ¥{data['today']['revenue']}")
    print(f"   7日趋势数据: {len(data['trend_7d'])} 条")


if __name__ == "__main__":
    main()
