#!/usr/bin/env python3
"""
邮件发送模块 - QQ邮箱（TLS方式）
使用587端口 + STARTTLS
"""

import smtplib
from email.mime.text import MIMEText
import os

# QQ邮箱配置
SMTP_HOST = 'smtp.qq.com'
SMTP_PORT = 587  # TLS端口
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASS = os.environ.get('SMTP_PASS', '')
FROM_EMAIL = os.environ.get('FROM_EMAIL') or SMTP_USER

def send_email(to_email, subject, body):
    """发送邮件 - TLS方式"""
    try:
        if not SMTP_USER or not SMTP_PASS or not FROM_EMAIL:
            raise ValueError('缺少 SMTP_USER、SMTP_PASS 或 FROM_EMAIL 配置')
        # 创建邮件
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        
        # 使用普通连接，然后升级TLS
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30)
        server.set_debuglevel(0)  # 关闭调试输出
        
        # 发送EHLO
        server.ehlo()
        
        # 启动TLS
        server.starttls()
        server.ehlo()
        
        # 登录
        server.login(SMTP_USER, SMTP_PASS)
        
        # 发送
        server.sendmail(FROM_EMAIL, [to_email], msg.as_string())
        server.quit()
        
        print(f"✅ 邮件已发送至: {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_email():
    """测试邮件发送"""
    print("🧪 测试邮件发送（TLS方式）...")
    print(f"   SMTP服务器: {SMTP_HOST}:{SMTP_PORT}")
    print(f"   发件人: {FROM_EMAIL}")
    print()
    
    result = send_email(
        to_email=FROM_EMAIL,
        subject="招标雷达 - 邮件测试",
        body="这是一封测试邮件。如果收到，说明邮件配置成功！\n\n发送时间: " + __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    print()
    if result:
        print("✅ 邮件配置成功！")
    else:
        print("❌ 邮件配置失败")
    
    return result

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_email()
    else:
        print("用法: python3 email_sender_v3.py --test")
