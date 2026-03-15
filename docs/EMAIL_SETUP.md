# 邮件发送配置指南（MVP版）

## 方案1: QQ邮箱（最简单，5分钟搞定）

### 步骤1: 开启SMTP
1. 登录QQ邮箱网页版
2. 设置 → 账户 → 开启SMTP服务
3. 获取授权码（不是密码！）

### 步骤2: 配置环境变量

```bash
export SMTP_HOST=smtp.qq.com
export SMTP_PORT=587
export SMTP_USER=你的QQ号@qq.com
export SMTP_PASS=你的授权码
export FROM_EMAIL=你的QQ号@qq.com
```

### 步骤3: 测试发送

```python
python3 scripts/test_email.py
```

---

## 方案2: SendGrid（更专业，免费额度足够）

### 步骤1: 注册
https://signup.sendgrid.com/

### 步骤2: 获取API Key
Settings → API Keys → Create API Key

### 步骤3: 配置

```bash
export SENDGRID_API_KEY=你的API_KEY
export FROM_EMAIL=你的邮箱@example.com
```

---

## 方案3: Resend（最简单，开发者友好）

https://resend.com
- 免费额度：每天100封
- 无需域名验证（MVP阶段可用）

---

## 推荐：MVP阶段用QQ邮箱

理由：
- 5分钟搞定
- 不需要额外注册
- 国内送达率高
- 免费

---

## 测试命令

```bash
cd ~/openclaw-income-factory

# 测试邮件发送
python3 -c "
import smtplib
from email.mime.text import MIMEText

# 配置
smtp_host = 'smtp.qq.com'
smtp_port = 587
smtp_user = '你的QQ@qq.com'
smtp_pass = '你的授权码'

# 创建邮件
msg = MIMEText('这是测试邮件')
msg['Subject'] = '招标雷达 - 测试'
msg['From'] = smtp_user
msg['To'] = '你的测试邮箱@example.com'

# 发送
server = smtplib.SMTP(smtp_host, smtp_port)
server.starttls()
server.login(smtp_user, smtp_pass)
server.send_message(msg)
server.quit()

print('邮件发送成功！')
"
```

配置完成后，系统就能自动发送欢迎邮件和日报了！
