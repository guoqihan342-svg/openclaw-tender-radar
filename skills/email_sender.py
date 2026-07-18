#!/usr/bin/env python3
"""
邮件发送模块 - 配置完成
"""

import smtplib
import sqlite3
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# 从配置文件读取
CONFIG_FILE = os.environ.get('EMAIL_CONFIG_FILE', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'email.conf'))

def load_config():
    """加载邮件配置"""
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    config[key] = value
    return config

# 加载配置
config = load_config()
SMTP_HOST = os.environ.get('SMTP_HOST') or config.get('SMTP_HOST', 'smtp.qq.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT') or config.get('SMTP_PORT', 465))
SMTP_USER = os.environ.get('SMTP_USER') or config.get('SMTP_USER', '')
SMTP_PASS = os.environ.get('SMTP_PASS') or config.get('SMTP_PASS', '')
FROM_EMAIL = os.environ.get('FROM_EMAIL') or config.get('FROM_EMAIL') or SMTP_USER

def send_email(to_email, subject, body, html_body=None):
    """发送邮件"""
    try:
        if not SMTP_USER or not SMTP_PASS or not FROM_EMAIL:
            raise ValueError('缺少 SMTP_USER、SMTP_PASS 或 FROM_EMAIL 配置')
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        
        # 添加纯文本内容
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # 添加HTML内容（如果有）
        if html_body:
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        
        # 连接SMTP服务器（QQ邮箱用SSL）
        server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
        server.login(SMTP_USER, SMTP_PASS)
        
        # 发送
        server.send_message(msg)
        server.quit()
        
        print(f"✅ 邮件已发送至: {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        return False

def send_welcome_email(to_email, name=""):
    """发送欢迎邮件"""
    subject = "🎯 欢迎订阅招标雷达！你的今日样刊"
    
    body = f"""Hi {name or '朋友'},

欢迎加入招标雷达！

🎁 你的7天免费试用已开启

📰 今日精选招标（3条免费预览）

1️⃣ 【智慧政务】深圳市政务云平台建设 | 预算280万 | 截止3.25
2️⃣ 【医疗信息化】长沙市某县人民医院系统升级 | 预算150万 | 截止3.28
3️⃣ 【教育数字化】杭州市某大学图书馆改造 | 预算80万 | 截止3.30

💡 完整版包含：
✅ 每日10条精选招标
✅ 包含预算、截止日、采购方联系方式
✅ AI智能筛选高价值项目
✅ 每周深度分析报告

👉 升级标准版（¥99/月）：
https://openclaw-tender-radar.vercel.app/payment/

有任何问题直接回复此邮件。

祝商祺！
招标雷达团队

---
退订请回复 TD
"""
    
    return send_email(to_email, subject, body)

def send_daily_report(to_email, report_content, is_paid=False):
    """发送日报"""
    subject = "📊 招标雷达日报 | " + __import__('datetime').datetime.now().strftime("%Y年%m月%d日")
    
    if is_paid:
        subject = "⭐【完整版】" + subject
    else:
        subject = "🎯【免费预览】" + subject
    
    return send_email(to_email, subject, report_content)

def test_email():
    """测试邮件发送"""
    print("🧪 测试邮件发送...")
    print(f"   SMTP服务器: {SMTP_HOST}")
    print(f"   发件人: {FROM_EMAIL}")
    
    # 测试发送给自己
    result = send_email(
        to_email=FROM_EMAIL,
        subject="招标雷达 - 邮件测试",
        body="这是一封测试邮件。如果收到，说明邮件配置成功！"
    )
    
    if result:
        print("✅ 邮件配置成功！")
    else:
        print("❌ 邮件配置失败，请检查授权码")
    
    return result

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_email()
    else:
        print("用法: python email_sender.py --test")
