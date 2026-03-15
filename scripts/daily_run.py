#!/usr/bin/env python3
"""
极简每日运行脚本 - 手动触发版
后续再改成自动
"""

import sqlite3
from datetime import datetime
import os

DB_PATH = "/home/daministrator/.openclaw/workspace/openclaw-income-factory/data/tender_radar.db"
REPORT_DIR = "/home/daministrator/.openclaw/workspace/openclaw-income-factory/reports/daily"

def daily_run():
    """每日运行流程"""
    
    print("🚀 开始每日招标雷达运行...")
    
    # Step 1: 抓取数据（目前用脚本生成）
    print("📥 Step 1: 抓取招标数据...")
    os.system(f"cd /home/daministrator/.openclaw/workspace/openclaw-income-factory && python3 scripts/generate_sample_report.py")
    
    # Step 2: 获取今日订阅用户
    print("👥 Step 2: 获取订阅用户...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM subscribers WHERE status='active'")
    count = cursor.fetchone()[0]
    print(f"   当前活跃订阅用户: {count} 人")
    
    # Step 3: 获取今日报告路径
    today = datetime.now().strftime("%Y%m%d")
    report_path = f"{REPORT_DIR}/daily_report_{today}.md"
    
    if os.path.exists(report_path):
        print(f"✅ Step 3: 今日报告已生成: {report_path}")
        
        # 读取并显示前20行
        with open(report_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:20]
            print("\n📄 报告预览:")
            print("".join(lines))
            print("...\n")
    else:
        print("❌ Step 3: 报告未生成")
    
    # Step 4: 记录日志
    print("📝 Step 4: 记录运行日志...")
    log_entry = f"[{datetime.now()}] 运行完成，用户:{count}, 报告:{report_path}\n"
    
    log_path = f"/home/daministrator/.openclaw/workspace/openclaw-income-factory/logs/daily_{today}.log"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(log_entry)
    
    print(f"✅ 日志已保存: {log_path}")
    
    # Step 5: 准备分发（手动）
    print("📤 Step 5: 准备分发...")
    print("   ⚠️ 当前为手动模式，请手动发送报告给用户")
    print(f"   报告路径: {report_path}")
    
    conn.close()
    
    print("\n🎉 每日运行完成！")
    print("\n下一步:")
    print("1. 检查报告质量")
    print("2. 手动发送给订阅用户")
    print("3. 收取今日新增订阅")

def add_subscriber(name, plan="free"):
    """添加订阅用户"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO subscribers (name, plan, status) VALUES (?, ?, 'active')",
        (name, plan)
    )
    
    conn.commit()
    subscriber_id = cursor.lastrowid
    conn.close()
    
    print(f"✅ 用户添加成功: {name}, ID: {subscriber_id}, 套餐: {plan}")
    return subscriber_id

def record_payment(subscriber_id, amount, plan):
    """记录支付"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO payments (subscriber_id, amount, plan, status) VALUES (?, ?, ?, 'completed')",
        (subscriber_id, amount, plan)
    )
    
    # 更新用户套餐
    cursor.execute(
        "UPDATE subscribers SET plan = ? WHERE id = ?",
        (plan, subscriber_id)
    )
    
    conn.commit()
    conn.close()
    
    print(f"✅ 支付记录成功: 用户{subscriber_id}, ¥{amount}, {plan}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "add_user":
            name = sys.argv[2] if len(sys.argv) > 2 else "测试用户"
            plan = sys.argv[3] if len(sys.argv) > 3 else "free"
            add_subscriber(name, plan)
        elif sys.argv[1] == "add_payment":
            subscriber_id = int(sys.argv[2])
            amount = int(sys.argv[3])
            plan = sys.argv[4]
            record_payment(subscriber_id, amount, plan)
        else:
            print("用法:")
            print("  python daily_run.py              # 运行日报生成")
            print("  python daily_run.py add_user 张三 standard  # 添加用户")
            print("  python daily_run.py add_payment 1 99 standard  # 记录支付")
    else:
        daily_run()
