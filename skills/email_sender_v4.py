#!/usr/bin/env python3
"""
邮件发送 - QQ邮箱（修复版）
禁用默认SSL上下文，手动配置
"""

import smtplib
import ssl
from email.mime.text import MIMEText
import os

SMTP_HOST = 'smtp.qq.com'
SMTP_PORT = 587
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASS = os.environ.get('SMTP_PASS', '')
FROM_EMAIL = os.environ.get('FROM_EMAIL') or SMTP_USER

def send_email(to_email, subject, body):
    """发送邮件"""
    try:
        if not SMTP_USER or not SMTP_PASS or not FROM_EMAIL:
            raise ValueError('缺少 SMTP_USER、SMTP_PASS 或 FROM_EMAIL 配置')
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        
        # 创建验证服务器证书的SSL上下文
        context = ssl.create_default_context()
        
        # 连接
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30)
        server.ehlo()
        
        # 启动TLS并验证服务器证书
        server.starttls(context=context)
        server.ehlo()
        
        # 登录
        server.login(SMTP_USER, SMTP_PASS)
        
        # 发送
        server.sendmail(FROM_EMAIL, [to_email], msg.as_string())
        server.quit()
        
        print(f"✅ 邮件已发送至: {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_email():
    print("🧪 测试邮件发送（修复版）...")
    result = send_email(FROM_EMAIL, "招标雷达测试", "这是一封测试邮件")
    return result

if __name__ == "__main__":
    test_email()
