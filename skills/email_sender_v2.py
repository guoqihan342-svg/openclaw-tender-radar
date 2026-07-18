#!/usr/bin/env python3
"""
邮件发送模块 - QQ邮箱专用版
使用SSL 465端口
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# QQ邮箱配置
SMTP_HOST = 'smtp.qq.com'
SMTP_PORT = 465  # SSL端口
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASS = os.environ.get('SMTP_PASS', '')
FROM_EMAIL = os.environ.get('FROM_EMAIL') or SMTP_USER

def send_email(to_email, subject, body):
    """发送邮件 - 简化版"""
    try:
        if not SMTP_USER or not SMTP_PASS or not FROM_EMAIL:
            raise ValueError('缺少 SMTP_USER、SMTP_PASS 或 FROM_EMAIL 配置')
        # 创建邮件
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        
        # 创建SSL上下文
        context = ssl.create_default_context()
        
        # 使用SMTP_SSL连接
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context, timeout=30) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(FROM_EMAIL, [to_email], msg.as_string())
        
        print(f"✅ 邮件已发送至: {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        # 打印更详细的错误信息
        import traceback
        traceback.print_exc()
        return False

def test_email():
    """测试邮件发送"""
    print("🧪 测试邮件发送...")
    print(f"   SMTP服务器: {SMTP_HOST}:{SMTP_PORT}")
    print(f"   发件人: {FROM_EMAIL}")
    print(f"   收件人: {FROM_EMAIL}")
    print()
    
    result = send_email(
        to_email=FROM_EMAIL,
        subject="招标雷达 - 邮件测试",
        body="这是一封测试邮件。如果收到，说明邮件配置成功！\n\n发送时间: " + __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    print()
    if result:
        print("✅ 邮件配置成功！请检查收件箱（包括垃圾箱）")
    else:
        print("❌ 邮件配置失败")
        print("\n可能的原因：")
        print("1. QQ邮箱授权码错误（需要重新生成）")
        print("2. QQ邮箱SMTP服务未开启")
        print("3. 网络连接问题")
        print("\n请检查：")
        print("- QQ邮箱设置 → 账户 → SMTP服务已开启")
        print("- 授权码是最新生成的")
    
    return result

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_email()
    else:
        print("用法: python3 email_sender_v2.py --test")
