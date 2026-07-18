# 邮件发送配置指南（MVP版）

## 方案1: QQ邮箱（最简单，5分钟搞定）

### 步骤1: 开启SMTP
1. 登录QQ邮箱网页版
2. 设置 → 账户 → 开启SMTP服务
3. 获取授权码（不是密码！）

### 步骤2: 配置环境变量

```bash
export SMTP_HOST=smtp.qq.com
export SMTP_PORT=465
export SMTP_USER=sender@example.com
export FROM_EMAIL=sender@example.com
read -rsp 'SMTP 授权码: ' SMTP_PASS && export SMTP_PASS
```

也可以复制 `config/email.conf.example` 为 `config/email.conf` 后在本机填写。
`config/email.conf` 已加入 `.gitignore`，不要把真实授权码提交到仓库。

### 步骤3: 测试发送

```bash
python3 skills/email_sender.py --test
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
export SENDGRID_FROM_EMAIL=sender@example.com
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
python3 skills/email_sender.py --test
```

配置完成后，系统就能自动发送欢迎邮件和日报了！
