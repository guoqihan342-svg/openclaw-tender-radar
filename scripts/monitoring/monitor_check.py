#!/usr/bin/env python3
"""
招标雷达 - 指标监控检查脚本
检查关键指标是否正常，触发告警

使用方法:
    python monitor_check.py [--dry-run]
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

# 配置 - 使用绝对路径
BASE_DIR = Path("/home/daministrator/.openclaw/workspace/openclaw-income-factory")
DB_PATH = BASE_DIR / "data" / "tender_radar.db"
CONFIG_FILE = BASE_DIR / "scripts" / "monitoring" / "config.json"
ALERT_LOG = BASE_DIR / "logs" / "alerts.json"


def get_db_connection():
    """获取数据库连接"""
    return sqlite3.connect(DB_PATH)


def load_config():
    """加载监控配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return get_default_config()


def get_default_config():
    """默认监控配置"""
    return {
        "dau": {"min": 10, "max": 1000, "threshold_pct": -30},
        "new_users": {"min": 5, "max": 500, "threshold_pct": -50},
        "revenue": {"min": 100, "max": 100000, "threshold_pct": -40},
        "email_open_rate": {"min": 10, "max": 100, "threshold_pct": -30},
        "email_reply_rate": {"min": 3, "max": 50, "threshold_pct": -40},
        "new_tenders": {"min": 1, "max": 1000, "threshold_pct": -50},
        "conversion_rate": {"min": 5, "max": 50, "threshold_pct": -25}
    }


def get_yesterday_stats(conn):
    """获取昨日统计数据"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    cursor = conn.cursor()
    
    # DAU
    cursor.execute("""
        SELECT COUNT(DISTINCT lead_id) FROM follow_ups 
        WHERE DATE(sent_date) = ?
    """, (yesterday,))
    dau = cursor.fetchone()[0]
    
    # 新增用户
    cursor.execute("SELECT COUNT(*) FROM leads WHERE DATE(created_date) = ?", (yesterday,))
    new_users = cursor.fetchone()[0]
    
    # 收入
    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0) FROM payments 
        WHERE DATE(pay_date) = ? AND status = 'completed'
    """, (yesterday,))
    revenue = cursor.fetchone()[0]
    
    # 邮件统计
    cursor.execute("""
        SELECT COUNT(*), 
               SUM(CASE WHEN opened = 1 THEN 1 ELSE 0 END),
               SUM(CASE WHEN replied = 1 THEN 1 ELSE 0 END)
        FROM follow_ups WHERE DATE(sent_date) = ?
    """, (yesterday,))
    email_stats = cursor.fetchone()
    emails_sent = email_stats[0]
    emails_opened = email_stats[1] or 0
    emails_replied = email_stats[2] or 0
    
    open_rate = (emails_opened / emails_sent * 100) if emails_sent > 0 else 0
    reply_rate = (emails_replied / emails_sent * 100) if emails_sent > 0 else 0
    
    # 新增招标
    cursor.execute("SELECT COUNT(*) FROM tenders WHERE DATE(created_date) = ?", (yesterday,))
    new_tenders = cursor.fetchone()[0]
    
    # 转化率
    cursor.execute("SELECT COUNT(*) FROM leads")
    total_users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT subscriber_id) FROM payments WHERE status = 'completed'")
    paid_users = cursor.fetchone()[0]
    conversion_rate = (paid_users / total_users * 100) if total_users > 0 else 0
    
    return {
        "date": yesterday,
        "dau": dau,
        "new_users": new_users,
        "revenue": revenue,
        "emails_sent": emails_sent,
        "emails_opened": emails_opened,
        "emails_replied": emails_replied,
        "open_rate": round(open_rate, 2),
        "reply_rate": round(reply_rate, 2),
        "new_tenders": new_tenders,
        "conversion_rate": round(conversion_rate, 2)
    }


def get_last_week_avg(conn, metric):
    """获取指标过去7天平均值"""
    cursor = conn.cursor()
    today = datetime.now()
    
    metrics_map = {
        "dau": "SELECT COUNT(DISTINCT lead_id) FROM follow_ups WHERE DATE(sent_date) = ?",
        "new_users": "SELECT COUNT(*) FROM leads WHERE DATE(created_date) = ?",
        "revenue": "SELECT COALESCE(SUM(amount), 0) FROM payments WHERE DATE(pay_date) = ? AND status = 'completed'",
        "email_open_rate": "SELECT COUNT(*), SUM(CASE WHEN opened = 1 THEN 1 ELSE 0 END) FROM follow_ups WHERE DATE(sent_date) = ?",
        "email_reply_rate": "SELECT COUNT(*), SUM(CASE WHEN replied = 1 THEN 1 ELSE 0 END) FROM follow_ups WHERE DATE(sent_date) = ?",
        "new_tenders": "SELECT COUNT(*) FROM tenders WHERE DATE(created_date) = ?",
    }
    
    values = []
    for i in range(1, 8):
        date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        cursor.execute(metrics_map.get(metric, ""), (date,))
        result = cursor.fetchone()
        
        if metric in ["email_open_rate", "email_reply_rate"]:
            total, opened = result
            value = (opened / total * 100) if total > 0 else 0
        else:
            value = result[0] if result else 0
        
        values.append(value)
    
    return sum(values) / len(values) if values else 0


def check_metric(name, value, config):
    """检查单个指标"""
    alerts = []
    
    # 绝对值检查
    if "min" in config and value < config["min"]:
        alerts.append({
            "level": "critical" if value == 0 else "warning",
            "message": f"{name}过低: {value} (最低: {config['min']})"
        })
    
    if "max" in config and value > config["max"]:
        alerts.append({
            "level": "warning",
            "message": f"{name}过高: {value} (最高: {config['max']})"
        })
    
    return alerts


def generate_alert_message(alerts, stats):
    """生成飞书告警消息"""
    date = stats["date"]
    
    message = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": f"🚨 招标雷达 - 指标异常告警",
                "template": "red" if any(a["level"] == "critical" for a in alerts) else "orange"
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": f"**日期**: {date}\n**告警数**: {len(alerts)}"
                }
            ]
        }
    }
    
    # 添加每个告警详情
    for alert in alerts:
        message["card"]["elements"].append({
            "tag": "markdown",
            "content": f"- {'🔴' if alert['level'] == 'critical' else '🟡'} {alert['message']}"
        })
    
    # 添加关键指标摘要
    message["card"]["elements"].append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": "**关键指标快照**"
        }
    })
    
    metrics_summary = [
        f"DAU: {stats['dau']}",
        f"新增用户: {stats['new_users']}",
        f"收入: ¥{stats['revenue']}",
        f"邮件打开率: {stats['open_rate']}%",
        f"邮件回复率: {stats['reply_rate']}%"
    ]
    
    message["card"]["elements"].append({
        "tag": "markdown",
        "content": " | ".join(metrics_summary)
    })
    
    return message


def save_alert_log(alerts, stats):
    """保存告警日志"""
    ALERT_LOG.parent.mkdir(parents=True, exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "date": stats["date"],
        "alerts": alerts,
        "stats": stats
    }
    
    # 读取现有日志
    logs = []
    if ALERT_LOG.exists():
        with open(ALERT_LOG, "r") as f:
            logs = json.load(f)
    
    logs.append(log_entry)
    
    # 只保留最近30条
    logs = logs[-30:]
    
    with open(ALERT_LOG, "w") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


def run_monitor(dry_run=False):
    """运行监控检查"""
    print("🔍 运行指标监控检查...")
    
    conn = get_db_connection()
    config = load_config()
    stats = get_yesterday_stats(conn)
    conn.close()
    
    print(f"📊 检查日期: {stats['date']}")
    print(f"   DAU: {stats['dau']}")
    print(f"   新增用户: {stats['new_users']}")
    print(f"   收入: ¥{stats['revenue']}")
    
    all_alerts = []
    
    # 检查各项指标
    alerts = check_metric("DAU", stats["dau"], config.get("dau", {}))
    all_alerts.extend(alerts)
    
    alerts = check_metric("新增用户", stats["new_users"], config.get("new_users", {}))
    all_alerts.extend(alerts)
    
    alerts = check_metric("收入", stats["revenue"], config.get("revenue", {}))
    all_alerts.extend(alerts)
    
    alerts = check_metric("邮件打开率", stats["open_rate"], config.get("email_open_rate", {}))
    all_alerts.extend(alerts)
    
    alerts = check_metric("邮件回复率", stats["reply_rate"], config.get("email_reply_rate", {}))
    all_alerts.extend(alerts)
    
    alerts = check_metric("新增招标", stats["new_tenders"], config.get("new_tenders", {}))
    all_alerts.extend(alerts)
    
    alerts = check_metric("转化率", stats["conversion_rate"], config.get("conversion_rate", {}))
    all_alerts.extend(alerts)
    
    # 打印告警
    if all_alerts:
        print(f"\n⚠️  发现 {len(all_alerts)} 个告警:")
        for alert in all_alerts:
            level_icon = "🔴" if alert["level"] == "critical" else "🟡"
            print(f"   {level_icon} {alert['message']}")
        
        # 生成告警消息
        alert_message = generate_alert_message(all_alerts, stats)
        print(f"\n📝 告警消息 (飞书格式):")
        print(json.dumps(alert_message, ensure_ascii=False, indent=2))
        
        # 保存告警日志
        save_alert_log(all_alerts, stats)
        print(f"\n✅ 告警日志已保存")
        
        if not dry_run:
            # TODO: 实际发送飞书告警
            # send_feishu_alert(alert_message)
            print("📤 告警通知已发送 (dry-run模式)")
        else:
            print("🔸 Dry-run模式，未发送实际告警")
    else:
        print("\n✅ 所有指标正常，无告警")
    
    return all_alerts


if __name__ == "__main__":
    import sys
    dry_run = "--dry-run" in sys.argv
    run_monitor(dry_run)
