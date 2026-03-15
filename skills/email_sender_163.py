#!/usr/bin/env python3
"""
邮件发送 - 使用163邮箱（备选方案）
如果QQ邮箱不行，用163作为替代
"""

import smtplib
from email.mime.text import MIMEText

# 163邮箱配置
SMTP_HOST = 'smtp.163.com'
SMTP_PORT = 25  # 或 465(SSL)
SMTP_USER = '你的163邮箱@163.com'  # 需要用户提供
SMTP_PASS = '你的授权码'  # 需要用户提供
FROM_EMAIL = SMTP_USER

def send_email(to_email, subject, body):
    """发送邮件"""
    try:
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
