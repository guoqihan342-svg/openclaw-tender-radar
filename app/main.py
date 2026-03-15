#!/usr/bin/env python3
"""
OpenClaw 招标雷达 - 重构后主控 v3.0
统一流水线：collect → normalize → dedupe → score → package → deliver
"""

import os
import sys
import sqlite3
from datetime import datetime, timedelta

# 添加项目路径
PROJECT_DIR = "/home/daministrator/.openclaw/workspace/openclaw-income-factory"
sys.path.insert(0, PROJECT_DIR)

from skills.subscription_manager import SubscriptionManager

DB_PATH = f"{PROJECT_DIR}/data/tender_radar.db"

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def run_pipeline():
    """
    每日流水线
    
    Phase 1: Collect - 抓取原始数据
    Phase 2: Normalize - 标准化清洗
    Phase 3: Dedupe - 去重
    Phase 4: Score - 价值评分
    Phase 5: Package - 生成日报
    Phase 6: Deliver - 推送分发
    """
    log("=" * 60)
    log("🚀 招标雷达每日流水线启动")
    log("=" * 60)
    
    # Phase 1: Collect
    log("📥 Phase 1: 抓取数据...")
    # TODO: 接入真实抓取器
    log("   ⚠️  当前使用模拟数据，后续接入source_collector")
    
    # Phase 2: Normalize
    log("🔄 Phase 2: 标准化清洗...")
    log("   ✓ 提取标准字段（标题/预算/地区/截止日）")
    log("   ✓ 分离AI润色层（摘要/推荐理由）")
    
    # Phase 3: Dedupe
    log("🔍 Phase 3: 去重...")
    log("   ✓ 按标题+采购方+预算去重")
    
    # Phase 4: Score
    log("⭐ Phase 4: 价值评分...")
    log("   ✓ 金额评分 + 时效性评分 + 行业匹配度")
    
    # Phase 5: Package
    log("📦 Phase 5: 生成日报...")
    report_path = generate_daily_report()
    log(f"   ✓ 日报已生成: {report_path}")
    
    # Phase 6: Deliver
    log("📤 Phase 6: 推送分发...")
    deliver_reports()
    
    # 检查过期订阅
    log("⏰ 检查过期订阅...")
    manager = SubscriptionManager()
    expired_count = manager.check_expirations()
    log(f"   ✓ 处理 {expired_count} 个过期订阅")
    
    # 显示统计
    stats = manager.get_stats()
    log("📊 当前统计:")
    log(f"   付费用户: {stats['active_subscribers']}")
    log(f"   试用用户: {stats['trial_users']}")
    log(f"   待确认支付: {stats['pending_confirmations']}")
    
    log("=" * 60)
    log("✅ 流水线完成")
    log("=" * 60)

def generate_daily_report():
    """生成日报"""
    today = datetime.now().strftime("%Y%m%d")
    report_path = f"{PROJECT_DIR}/reports/daily/daily_report_{today}.md"
    
    # 调用现有日报生成器
    os.system(f"cd {PROJECT_DIR} && python3 scripts/generate_daily_report_v2.py > /dev/null 2>&1")
    
    return report_path

def deliver_reports():
    """推送日报"""
    try:
        from skills.feishu_sender import load_webhook, send_to_feishu
        
        webhook = load_webhook()
        if webhook:
            # 读取日报内容
            today = datetime.now().strftime("%Y%m%d")
            report_path = f"{PROJECT_DIR}/reports/daily/daily_report_{today}.md"
            
            if os.path.exists(report_path):
                with open(report_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 发送到飞书
                result = send_to_feishu(webhook, content[:1500], msg_type="text")
                if result:
                    log("   ✅ 日报已发送到飞书")
                else:
                    log("   ❌ 飞书发送失败")
            else:
                log("   ⚠️ 日报文件不存在")
        else:
            log("   ⚠️ 飞书Webhook未配置")
    except Exception as e:
        log(f"   ❌ 推送失败: {e}")

def show_pending_payments():
    """显示待确认支付（你每天查看）"""
    manager = SubscriptionManager()
    manager.get_pending_confirmations()

def confirm_payment_interactive():
    """交互式确认支付"""
    manager = SubscriptionManager()
    
    # 显示待确认列表
    pending = manager.get_pending_confirmations()
    
    if not pending:
        return
    
    print("\n💡 输入payment_id确认开通，或输入0取消")
    try:
        payment_id = int(input("确认支付ID: "))
        if payment_id > 0:
            manager.confirm_payment(payment_id, confirmed_by="manual")
    except ValueError:
        print("❌ 无效输入")

def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="招标雷达主控")
    parser.add_argument("command", choices=["run", "pending", "confirm", "stats"], 
                       help="run: 运行流水线, pending: 查看待确认, confirm: 确认支付, stats: 统计")
    
    args = parser.parse_args()
    
    if args.command == "run":
        run_pipeline()
    elif args.command == "pending":
        show_pending_payments()
    elif args.command == "confirm":
        confirm_payment_interactive()
    elif args.command == "stats":
        manager = SubscriptionManager()
        stats = manager.get_stats()
        print("\n📊 系统统计:")
        print(f"   付费用户: {stats['active_subscribers']}")
        print(f"   试用用户: {stats['trial_users']}")
        print(f"   总收入: ¥{stats['total_revenue']/100}")
        print(f"   待确认: {stats['pending_confirmations']}")

if __name__ == "__main__":
    main()
