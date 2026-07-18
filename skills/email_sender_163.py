#!/usr/bin/env python3
"""
邮件发送 - 使用163邮箱（备选方案）
如果QQ邮箱不行，用163作为替代
"""

import smtplib
import os
from email.mime.text import MIMEText

# 163邮箱配置
SMTP_HOST = 'smtp.163.com'
SMTP_PORT = 25  # 或 465(SSL)
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
        
        # 163邮箱使用普通连接
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30)
        server.ehlo()
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(FROM_EMAIL, [to_email], msg.as_string())
        server.quit()
        
        print(f"✅ 邮件已发送至: {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False

if __name__ == "__main__":
    # 需要配置163邮箱信息后才能使用
    print("163邮箱备选方案（需配置账号）")
