#!/usr/bin/env python3
"""
飞书Bot发送模块 - 配置完成
用于自动推送日报到飞书群
"""

import requests
import json
import os
from datetime import datetime

# 配置文件路径
CONFIG_FILE = "/home/daministrator/.openclaw/workspace/openclaw-income-factory/config/feishu.conf"

def load_webhook():
    """加载飞书Webhook"""
    webhook = None
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            for line in f:
                if 'FEISHU_WEBHOOK_URL=' in line and not line.startswith('#'):
                    webhook = line.split('=', 1)[1].strip()
                    break
    return webhook

def send_to_feishu(webhook_url, content, msg_type="text"):
    """
    发送消息到飞书
    
    参数:
        webhook_url: 飞书机器人Webhook地址
        content: 消息内容
        msg_type: 消息类型 (text/markdown)
    """
    if not webhook_url:
        print("❌ 错误: 未配置飞书Webhook")
        return False
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    if msg_type == "markdown":
        data = {
            "msg_type": "interactive",
            "card": {
                "config": {"wide_screen_mode": True},
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "🎯 招标雷达日报"
                    },
                    "template": "blue"
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": content
                        }
                    }
                ]
            }
        }
    else:
        data = {
            "msg_type": "text",
            "content": {
                "text": content
            }
        }
    
    try:
        response = requests.post(webhook_url, headers=headers, json=data, timeout=30)
        result = response.json()
        
        if result.get('code') == 0:
            print(f"✅ 消息已发送到飞书")
            return True
        else:
            print(f"❌ 发送失败: {result.get('msg')}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def send_daily_report(webhook_url, report_content, is_paid=False):
    """发送日报到飞书"""
    today = datetime.now().strftime("%Y年%m月%d日")
    
    if is_paid:
        header = f"**⭐【完整版】招标雷达日报 | {today}**\n\n"
    else:
        header = f"**🎯【免费预览】招标雷达日报 | {today}**\n\n"
    
    footer = "\n\n---\n💡 订阅完整版获取更多商机：https://openclaw-tender-radar.vercel.app/payment/"
    
    content = header + report_content + footer
    
    return send_to_feishu(webhook_url, content, msg_type="markdown")

def send_welcome(webhook_url, user_name=""):
    """发送欢迎消息"""
    content = f"""🎉 欢迎 {user_name or '新用户'} 加入招标雷达！

📰 你的7天免费试用已开启

⏰ 每天早8点，我会自动推送精选招标信息

💡 今日精选（3条预览）：
1️⃣ 深圳市智慧政务云项目 | 预算280万
2️⃣ 长沙市某县人民医院系统升级 | 预算150万
3️⃣ 杭州市某大学图书馆改造 | 预算80万

👉 订阅完整版（¥99/月）获取每日10条+周报分析：
https://openclaw-tender-radar.vercel.app/payment/

有任何问题随时提问！"""
    
    return send_to_feishu(webhook_url, content, msg_type="text")

def test_feishu():
    """测试飞书发送"""
    webhook = load_webhook()
    
    if not webhook:
        print("❌ 未配置飞书Webhook")
        print(f"\n请编辑配置文件: {CONFIG_FILE}")
        print("添加: FEISHU_WEBHOOK_URL=你的Webhook地址")
        return False
    
    print(f"🧪 测试飞书发送...")
    print(f"   Webhook: {webhook[:50]}...")
    
    result = send_to_feishu(
        webhook,
        "🧪 这是一条测试消息\n\n如果收到，说明飞书Bot配置成功！\n\n发送时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        msg_type="text"
    )
    
    return result

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_feishu()
    else:
        print("用法: python3 feishu_sender.py --test")
        print(f"\n配置文件: {CONFIG_FILE}")
