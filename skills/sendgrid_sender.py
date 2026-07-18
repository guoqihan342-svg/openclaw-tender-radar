#!/usr/bin/env python3
"""
SendGrid 邮件发送模块
使用SendGrid API发送邮件
"""

import os
import json
from datetime import datetime

# 尝试导入sendgrid
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    print("⚠️  SendGrid SDK未安装，尝试使用HTTP API")

import requests

# 配置
CONFIG_FILE = os.environ.get('SENDGRID_CONFIG_FILE', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'sendgrid.conf'))
FROM_EMAIL = os.environ.get('SENDGRID_FROM_EMAIL') or os.environ.get('FROM_EMAIL', '')

def load_api_key():
    """加载SendGrid API Key"""
    api_key = os.environ.get('SENDGRID_API_KEY')
    if api_key:
        return api_key
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            for line in f:
                if 'SENDGRID_API_KEY=' in line and not line.startswith('#'):
                    api_key = line.split('=', 1)[1].strip()
                    break
    return api_key

def send_email_http(api_key, to_email, subject, body):
    """使用HTTP API发送邮件"""
    url = "https://api.sendgrid.com/v3/mail/send"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "personalizations": [
            {
                "to": [{"email": to_email}]
            }
        ],
        "from": {"email": FROM_EMAIL, "name": "招标雷达"},
        "subject": subject,
        "content": [
            {
                "type": "text/plain",
                "value": body
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 202:
            print(f"✅ 邮件已发送至: {to_email}")
            return True
        else:
            print(f"❌ 发送失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def send_email_sdk(api_key, to_email, subject, body):
    """使用SDK发送邮件"""
    try:
        sg = SendGridAPIClient(api_key)
        
        message = Mail(
            from_email=Email(FROM_EMAIL, '招标雷达'),
            to_emails=To(to_email),
            subject=subject,
            plain_text_content=Content('text/plain', body)
        )
        
        response = sg.send(message)
        
        if response.status_code == 202:
            print(f"✅ 邮件已发送至: {to_email}")
            return True
        else:
            print(f"❌ 发送失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ SDK错误: {e}")
        return False

def send_email(to_email, subject, body):
    """发送邮件（自动选择方式）"""
    api_key = load_api_key()
    
    if not api_key:
        print("❌ 未配置SendGrid API Key")
        print(f"   请编辑: {CONFIG_FILE}")
        return False
    
    if not FROM_EMAIL:
        print('❌ 未配置 SENDGRID_FROM_EMAIL 或 FROM_EMAIL')
        return False

    if SENDGRID_AVAILABLE:
        return send_email_sdk(api_key, to_email, subject, body)
    else:
        return send_email_http(api_key, to_email, subject, body)

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

def test_sendgrid():
    """测试SendGrid"""
    api_key = load_api_key()
    test_email = os.environ.get('TEST_EMAIL') or FROM_EMAIL
    
    if not api_key:
        print("❌ 未配置SendGrid API Key")
        print(f"\n请编辑配置文件: {CONFIG_FILE}")
        print("添加: SENDGRID_API_KEY=你的API_Key")
        print("\n获取API Key步骤:")
        print("1. 登录SendGrid https://app.sendgrid.com")
        print("2. Settings → API Keys")
        print("3. Create API Key → Full Access")
        print("4. 复制Key（只显示一次）")
        return False
    if not FROM_EMAIL or not test_email:
        print("❌ 未配置 SENDGRID_FROM_EMAIL（或 FROM_EMAIL）和测试收件地址")
        return False
    
    print("🧪 测试SendGrid邮件发送...")
    print("   API Key: 已配置（内容不显示）")
    print(f"   发件人: {FROM_EMAIL}")
    print(f"   收件人: {test_email}")
    print()
    
    result = send_email(
        to_email=test_email,
        subject="招标雷达 - SendGrid测试",
        body="这是一封测试邮件。如果收到，说明SendGrid配置成功！\n\n发送时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    return result

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_sendgrid()
    else:
        print("用法: python3 sendgrid_sender.py --test")
        print(f"\n配置文件: {CONFIG_FILE}")
