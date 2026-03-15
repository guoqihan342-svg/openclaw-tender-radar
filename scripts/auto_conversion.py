#!/usr/bin/env python3
"""
全自动转化系统 - 表单收集 + 自动跟进
无需人工介入，自动完成从线索到付费的转化
"""

import sqlite3
import json
from datetime import datetime, timedelta
import os

DB_PATH = "/home/daministrator/.openclaw/workspace/openclaw-income-factory/data/tender_radar.db"

def init_conversion_tables():
    """初始化转化追踪表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 线索表（从网站表单提交）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        name TEXT,
        company TEXT,
        phone TEXT,
        source TEXT DEFAULT 'website',  -- website/seo/referral
        interest_plan TEXT DEFAULT 'standard',
        status TEXT DEFAULT 'new',  -- new/contacted/trial/converting/paid/lost
        created_date DATE DEFAULT CURRENT_DATE,
        contacted_date DATE,
        trial_start_date DATE,
        trial_end_date DATE,
        notes TEXT
    )
    ''')
    
    # 自动跟进记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS follow_ups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id INTEGER,
        step INTEGER,  -- 1=欢迎, 2=样刊, 3=价值证明, 4=转化, 5=提醒
        channel TEXT,  -- email/feishu
        content TEXT,
        sent_date DATE,
        opened BOOLEAN DEFAULT 0,
        replied BOOLEAN DEFAULT 0,
        converted BOOLEAN DEFAULT 0,
        FOREIGN KEY (lead_id) REFERENCES leads(id)
    )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ 转化追踪表初始化完成")

def add_lead_from_form(email, name=None, company=None, phone=None, interest_plan='standard'):
    """
    从网站表单添加线索
    实际使用时，这个函数会被网站表单调用
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 检查是否已存在
    cursor.execute("SELECT id, status FROM leads WHERE email = ?", (email,))
    existing = cursor.fetchone()
    
    if existing:
        print(f"⚠️ 线索已存在: {email}, 状态: {existing[1]}")
        conn.close()
        return existing[0]
    
    # 插入新线索
    cursor.execute('''
    INSERT INTO leads (email, name, company, phone, interest_plan, status, created_date)
    VALUES (?, ?, ?, ?, ?, 'new', CURRENT_DATE)
    ''', (email, name, company, phone, interest_plan))
    
    lead_id = cursor.lastrowid
    
    # 自动创建跟进计划
    create_follow_up_plan(lead_id, cursor)
    
    conn.commit()
    conn.close()
    
    print(f"✅ 新线索添加成功: {email}, ID: {lead_id}")
    
    # 触发自动欢迎（实际部署时）
    # auto_send_welcome(lead_id)
    
    return lead_id

def create_follow_up_plan(lead_id, cursor):
    """创建7天自动跟进计划"""
    
    today = datetime.now().date()
    
    follow_up_steps = [
        {
            'step': 1,
            'days': 0,  # 立即
            'channel': 'email',
            'content': '欢迎邮件+今日样刊'
        },
        {
            'step': 2,
            'days': 1,  # 第2天
            'channel': 'email',
            'content': '使用技巧+成功案例'
        },
        {
            'step': 3,
            'days': 3,  # 第4天
            'channel': 'email',
            'content': '价值证明+用户证言'
        },
        {
            'step': 4,
            'days': 6,  # 第7天（试用期结束）
            'channel': 'email',
            'content': '转化促成+付费优惠'
        },
        {
            'step': 5,
            'days': 8,  # 第9天（未付费提醒）
            'channel': 'email',
            'content': '最后提醒+延期优惠'
        }
    ]
    
    for step in follow_up_steps:
        send_date = today + timedelta(days=step['days'])
        cursor.execute('''
        INSERT INTO follow_ups (lead_id, step, channel, content, sent_date)
        VALUES (?, ?, ?, ?, ?)
        ''', (lead_id, step['step'], step['channel'], step['content'], send_date))

def generate_welcome_email(lead_id):
    """生成欢迎邮件内容"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT email, name, trial_end_date FROM leads WHERE id = ?", (lead_id,))
    lead = cursor.fetchone()
    conn.close()
    
    if not lead:
        return None
    
    email, name, trial_end = lead
    
    subject = "🎯 欢迎试用招标雷达！你的今日精选商机已生成"
    
    body = f"""
{name or '您好'}，

欢迎试用 OpenClaw 招标雷达！

🎁 你的7天免费试用已开启
试用到期日：{trial_end or '7天后'}

📰 今日精选招标（3条免费预览）

1️⃣ 【智慧政务】XX市政务云平台建设 | 预算280万 | 深圳
2️⃣ 【医疗信息化】XX县人民医院系统升级 | 预算150万 | 长沙  
3️⃣ 【教育数字化】XX大学图书馆数字化改造 | 预算80万 | 北京

💡 试用期间你将收到：
✅ 每日3条精选招标（免费版）
✅ 1份周报深度分析
✅ 专属客服支持

🚀 升级标准版（¥99/月）解锁：
✅ 每日10条精选
✅ 按地区+行业筛选
✅ 每周深度报告

👉 升级链接：[点击升级]

有任何问题，直接回复此邮件。

祝商祺！
OpenClaw 招标雷达团队

---
退订请回复 TD
"""
    
    return {'subject': subject, 'body': body}

def auto_follow_up():
    """
    自动执行今日需要发送的跟进
    这个函数每天运行一次
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    today = datetime.now().date()
    
    # 查询今天需要发送的跟进
    cursor.execute('''
    SELECT f.id, f.lead_id, f.step, f.channel, l.email, l.name
    FROM follow_ups f
    JOIN leads l ON f.lead_id = l.id
    WHERE f.sent_date = ? AND f.sent_date IS NULL
    ''', (today,))
    
    pending = cursor.fetchall()
    
    print(f"📧 今日待发送跟进: {len(pending)} 条")
    
    for follow in pending:
        follow_id, lead_id, step, channel, email, name = follow
        
        # 根据步骤生成内容
        if step == 1:
            content = generate_welcome_email(lead_id)
        else:
            content = {'subject': f'跟进邮件步骤{step}', 'body': '内容待生成'}
        
        # 标记为已发送（实际部署时这里调用邮件发送）
        cursor.execute('''
        UPDATE follow_ups SET sent_date = CURRENT_DATE
        WHERE id = ?
        ''', (follow_id,))
        
        print(f"   ✅ 已生成跟进: {email} - 步骤{step}")
    
    conn.commit()
    conn.close()

def get_conversion_stats():
    """获取转化统计"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    stats = {}
    
    # 总线索数
    cursor.execute("SELECT COUNT(*) FROM leads")
    stats['total_leads'] = cursor.fetchone()[0]
    
    # 各状态分布
    cursor.execute("SELECT status, COUNT(*) FROM leads GROUP BY status")
    stats['status_distribution'] = dict(cursor.fetchall())
    
    # 今日新增
    cursor.execute("SELECT COUNT(*) FROM leads WHERE created_date = CURRENT_DATE")
    stats['today_new'] = cursor.fetchone()[0]
    
    # 转化率
    cursor.execute("SELECT COUNT(*) FROM leads WHERE status = 'paid'")
    paid = cursor.fetchone()[0]
    stats['conversion_rate'] = f"{(paid / stats['total_leads'] * 100):.1f}%" if stats['total_leads'] > 0 else "0%"
    
    conn.close()
    
    return stats

def main():
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'init':
            init_conversion_tables()
        elif sys.argv[1] == 'add' and len(sys.argv) >= 3:
            email = sys.argv[2]
            name = sys.argv[3] if len(sys.argv) > 3 else None
            add_lead_from_form(email, name)
        elif sys.argv[1] == 'follow':
            auto_follow_up()
        elif sys.argv[1] == 'stats':
            stats = get_conversion_stats()
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        else:
            print("用法:")
            print("  python auto_conversion.py init              # 初始化表")
            print("  python auto_conversion.py add 邮箱 [姓名]   # 添加线索")
            print("  python auto_conversion.py follow            # 执行自动跟进")
            print("  python auto_conversion.py stats             # 查看统计")
    else:
        print("自动转化系统")
        print("请指定命令: init / add / follow / stats")

if __name__ == "__main__":
    main()
