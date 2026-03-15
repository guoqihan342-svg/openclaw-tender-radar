#!/usr/bin/env python3
"""
OpenClaw 招标雷达 - 全自动主控系统
每天自动运行，无需人工干预
"""

import os
import sys
import sqlite3
from datetime import datetime

PROJECT_DIR = "/home/daministrator/.openclaw/workspace/openclaw-income-factory"
DB_PATH = f"{PROJECT_DIR}/data/tender_radar.db"

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def run_command(cmd, description):
    """执行命令并记录"""
    log(f"🚀 {description}")
    result = os.system(cmd)
    if result == 0:
        log(f"✅ {description} 完成")
    else:
        log(f"❌ {description} 失败，返回码: {result}")
    return result == 0

def daily_auto_run():
    """
    每日全自动运行流程
    这个函数每天早上自动执行
    """
    log("=" * 60)
    log("🤖 OpenClaw 招标雷达 - 每日自动运行启动")
    log("=" * 60)
    
    os.chdir(PROJECT_DIR)
    
    # Step 1: 生成招标日报
    if not run_command(
        "python3 scripts/generate_sample_report.py",
        "生成招标日报"
    ):
        log("⚠️ 日报生成失败，跳过今日发送")
        return False
    
    # Step 2: 获取今日付费用户列表
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT s.id, s.email, s.plan, s.name 
    FROM subscribers s
    WHERE s.status = 'active' 
    AND (s.plan = 'standard' OR s.plan = 'premium')
    """)
    
    paid_users = cursor.fetchall()
    conn.close()
    
    log(f"📊 今日待发送用户: {len(paid_users)} 人")
    
    # Step 3: 自动发送给付费用户
    today = datetime.now().strftime("%Y%m%d")
    report_path = f"{PROJECT_DIR}/reports/daily/daily_report_{today}.md"
    
    if not os.path.exists(report_path):
        log(f"❌ 报告文件不存在: {report_path}")
        return False
    
    # 读取报告内容
    with open(report_path, 'r', encoding='utf-8') as f:
        report_content = f.read()
    
    # 自动发送（这里集成飞书/邮件发送）
    for user in paid_users:
        user_id, email, plan, name = user
        log(f"   📤 准备发送给: {name or email} ({plan})")
        
        # 实际部署时调用发送API
        # send_to_feishu(email, report_content)
        # send_email(email, report_content)
    
    log(f"✅ 日报发送准备完成（待发: {len(paid_users)} 人）")
    
    # Step 4: 执行自动转化跟进
    run_command(
        "python3 scripts/auto_conversion.py follow",
        "执行自动转化跟进"
    )
    
    # Step 5: 记录运行日志
    log_path = f"{PROJECT_DIR}/logs/auto_run_{today}.log"
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now()}] 自动运行完成，发送用户: {len(paid_users)}\n")
    
    log("=" * 60)
    log("🎉 每日自动运行完成")
    log("=" * 60)
    
    return True

def init_all():
    """初始化所有系统"""
    log("🚀 初始化 OpenClaw 招标雷达系统...")
    
    os.chdir(PROJECT_DIR)
    
    # 初始化数据库
    run_command("python3 scripts/init_db.py", "初始化数据库")
    
    # 初始化转化系统
    run_command("python3 scripts/auto_conversion.py init", "初始化转化系统")
    
    # 生成获客内容
    run_command("python3 scripts/generate_acquisition_content.py", "生成获客内容")
    
    log("✅ 系统初始化完成")

def show_stats():
    """显示系统统计"""
    log("📊 系统统计")
    
    os.chdir(PROJECT_DIR)
    
    # 转化统计
    run_command("python3 scripts/auto_conversion.py stats", "获取转化统计")
    
    # 数据库统计
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM subscribers WHERE status='active'")
    subscribers = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM payments WHERE status='completed'")
    payments = cursor.fetchone()[0]
    
    conn.close()
    
    log(f"   活跃订阅用户: {subscribers}")
    log(f"   已完成支付: {payments}")

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'init':
            init_all()
        elif command == 'daily':
            daily_auto_run()
        elif command == 'stats':
            show_stats()
        elif command == 'help':
            print("""
OpenClaw 招标雷达 - 全自动主控系统

用法:
  python auto_master.py init    # 初始化系统（首次运行）
  python auto_master.py daily   # 执行每日自动运行
  python auto_master.py stats   # 查看系统统计
  python auto_master.py help    # 显示帮助

系统架构:
  1. 每日自动抓取招标信息
  2. AI生成精选日报
  3. 自动发送给付费用户
  4. 自动跟进转化线索
  5. 全自动获客（SEO内容站）

你需要做的:
  - 审核系统运行状态
  - 确认收款（初期手动）
  - 重大决策
            """)
        else:
            print(f"未知命令: {command}")
            print("使用: python auto_master.py help")
    else:
        # 默认执行每日运行
        daily_auto_run()

if __name__ == "__main__":
    main()
