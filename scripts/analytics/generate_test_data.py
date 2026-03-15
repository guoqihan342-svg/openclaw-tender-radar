#!/usr/bin/env python3
"""
招标雷达 - 测试数据生成脚本
生成模拟数据用于测试

使用方法:
    python generate_test_data.py
"""

import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path

# 配置
BASE_DIR = Path("/home/daministrator/.openclaw/workspace/openclaw-income-factory")
DB_PATH = BASE_DIR / "data" / "tender_radar.db"


def get_db_connection():
    return sqlite3.connect(DB_PATH)


def generate_test_data():
    """生成测试数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("📊 生成测试数据...")
    
    # 1. 生成招标数据 (过去30天)
    regions = ["广东省", "浙江省", "江苏省", "北京市", "上海市", "深圳市", "杭州市", "广州市"]
    categories = ["信息化建设", "系统集成", "软件服务", "网络安全", "云服务"]
    sources = ["中国政府采购网", "公共资源交易中心", "企业招标网"]
    
    print("   生成招标数据...")
    tender_count = 0
    for i in range(30):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        # 每天生成3-8条招标
        for _ in range(random.randint(3, 8)):
            title = f"{random.choice(regions)}{random.choice(['某区', '某市', '某县'])}{random.choice(['政府', '医院', '学校', '企业'])}{random.choice(categories)}项目"
            budget = random.randint(100000, 3000000)
            region = random.choice(regions)
            deadline = (datetime.now() + timedelta(days=random.randint(7, 60))).strftime("%Y-%m-%d")
            purchaser = f"{region}{random.choice(['政务服务数据管理局', '人民医院', '教育局', '科技局'])}"
            source = random.choice(sources)
            
            cursor.execute("""
                INSERT INTO tenders (title, budget, region, deadline, category, purchaser, source, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, budget, region, deadline, None, purchaser, source, date))
            tender_count += 1
    
    # 2. 生成leads数据 (过去30天)
    print("   生成用户数据...")
    lead_count = 0
    lead_ids = []
    for i in range(30):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        # 每天生成2-5个新用户
        for _ in range(random.randint(2, 5)):
            name = f"用户{random.randint(1000, 9999)}"
            email = f"user{random.randint(1000, 9999)}@example.com"
            company = f"{random.choice(['科技', '咨询', '服务', '贸易'])}有限公司"
            
            cursor.execute("""
                INSERT INTO leads (email, name, company, source, status, created_date, interest_plan)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (email, name, company, "website", "active", date, random.choice(["standard", "pro", "enterprise"])))
            
            lead_id = cursor.lastrowid
            lead_ids.append(lead_id)
            lead_count += 1
            
            # 部分用户开始试用
            if random.random() < 0.6:
                trial_start = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=random.randint(1, 3))).strftime("%Y-%m-%d")
                trial_end = (datetime.strptime(trial_start, "%Y-%m-%d") + timedelta(days=14)).strftime("%Y-%m-%d")
                cursor.execute("""
                    UPDATE leads SET trial_start_date = ?, trial_end_date = ? WHERE id = ?
                """, (trial_start, trial_end, lead_id))
    
    # 3. 生成payments数据
    print("   生成支付数据...")
    paid_count = 0
    for lead_id in lead_ids[:int(len(lead_ids) * 0.3)]:  # 30%转化
        pay_date = (datetime.now() - timedelta(days=random.randint(0, 25))).strftime("%Y-%m-%d")
        amount = random.choice([99, 199, 299, 499, 999, 2999])
        plan = random.choice(["standard", "pro", "enterprise"])
        
        cursor.execute("""
            INSERT INTO payments (subscriber_id, amount, plan, pay_method, pay_date, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (lead_id, amount, plan, "wechat", pay_date, "completed"))
        paid_count += 1
    
    # 4. 生成follow_ups数据 (邮件发送记录)
    print("   生成邮件数据...")
    email_count = 0
    for lead_id in lead_ids:
        # 每个用户每天可能收到1-3封邮件
        for i in range(random.randint(5, 15)):
            sent_date = (datetime.now() - timedelta(days=random.randint(0, 25))).strftime("%Y-%m-%d")
            channel = random.choice(["email", "sms", "wechat"])
            opened = random.random() < 0.35  # 35%打开率
            replied = random.random() < 0.08  # 8%回复率
            
            cursor.execute("""
                INSERT INTO follow_ups (lead_id, channel, content, sent_date, opened, replied)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (lead_id, channel, f"招标信息 #{i+1}", sent_date, opened, replied))
            email_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ 测试数据生成完成!")
    print(f"   - 招标信息: {tender_count} 条")
    print(f"   - 用户: {lead_count} 人")
    print(f"   - 付费用户: {paid_count} 人")
    print(f"   - 邮件记录: {email_count} 条")


def main():
    generate_test_data()


if __name__ == "__main__":
    main()
