# OpenClaw 招标雷达 - 全自动部署指南

## 🎯 系统概览

**全自动程度**: 95%
- ✅ 自动获客（SEO内容站）
- ✅ 自动转化（表单+跟进）
- ✅ 自动生成日报
- ✅ 自动发送给付费用户
- ⚠️ 收款确认（初期需手动）

**你的工作量**: 每天5分钟查看状态，确认收款

---

## 🚀 快速启动（30分钟）

### Step 1: 部署获客网站（10分钟）

**选项A: Vercel（推荐）**
```bash
# 安装 Vercel CLI
npm i -g vercel

# 部署
cd /home/daministrator/.openclaw/workspace/openclaw-income-factory/site
vercel --prod

# 获得域名: https://openclaw-tender-radar.vercel.app
```

**选项B: Netlify**
```bash
# 安装 Netlify CLI
npm i -g netlify-cli

# 部署
cd /home/daministrator/.openclaw/workspace/openclaw-income-factory/site
netlify deploy --prod
```

### Step 2: 配置定时任务（5分钟）

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每天早8点自动运行）
0 8 * * * cd /home/daministrator/.openclaw/workspace/openclaw-income-factory && python3 scripts/auto_master.py daily >> logs/cron.log 2>&1

# 保存退出
```

### Step 3: 测试运行（5分钟）

```bash
# 执行一次完整流程
cd /home/daministrator/.openclaw/workspace/openclaw-income-factory
python3 scripts/auto_master.py daily

# 查看生成的报告
cat reports/daily/daily_report_$(date +%Y%m%d).md
```

### Step 4: 配置收款（10分钟）

1. **支付宝收款码**
   - 打开支付宝 → 收钱 → 保存收款码
   - 上传到网站 `site/images/alipay-qr.png`

2. **微信收款码**
   - 打开微信 → 我 → 服务 → 收付款 → 二维码收款
   - 保存并上传 `site/images/wechat-qr.png`

---

## 🤖 全自动运行流程

### 每天自动执行（08:00）

```
08:00 系统自动启动
  ↓
08:01 抓取昨日新增招标信息
  ↓
08:05 AI生成精选日报（Top 10）
  ↓
08:10 获取付费用户列表
  ↓
08:15 自动发送日报给付费用户（飞书/邮件）
  ↓
08:20 执行自动转化跟进（线索 nurture）
  ↓
08:25 记录运行日志
  ↓
08:30 运行完成，等待明日
```

### 用户转化流程（全自动）

```
用户访问网站
  ↓
填写邮箱订阅免费试用
  ↓
系统自动发送欢迎邮件+今日样刊
  ↓
Day 2: 自动发送使用技巧
  ↓
Day 4: 自动发送成功案例
  ↓
Day 7: 自动发送转化优惠（试用期结束）
  ↓
用户付款（扫码支付）
  ↓
你确认收款，手动添加为付费用户
  ↓
系统自动每日发送完整日报
```

---

## 🛠️ Claude Code 开发工作流

### 添加新功能

```bash
# 使用开发脚本
./scripts/dev_with_claude.sh "写一个抓取XX网站招标信息的爬虫"

# Claude Code 会自动：
# 1. 分析需求
# 2. 编写代码
# 3. 添加注释
# 4. 测试运行
```

### 修改现有功能

```bash
# 告诉 Claude Code 要改什么
claude "修改 daily_run.py，增加预算筛选功能，只抓取100万以上的项目"
```

### 调试问题

```bash
# 查看日志，让 Claude Code 分析
tail -f logs/auto_run_$(date +%Y%m%d).log | claude "分析这个错误并修复"
```

---

## 📊 日常运营（每天5分钟）

### 每日必做（早上）

```bash
# 1. 检查运行状态（1分钟）
python3 scripts/auto_master.py stats

# 2. 查看昨日收入（2分钟）
# 检查支付宝/微信收款通知

# 3. 确认新付费用户（2分钟）
python3 scripts/daily_run.py add_payment 用户ID 金额 套餐
```

### 每周必做（周一）

```bash
# 1. 查看转化数据
python3 scripts/auto_conversion.py stats

# 2. 优化SEO文章（可选）
# 查看网站访问数据，优化关键词

# 3. 生成周报
python3 scripts/weekly_run.py
```

---

## 💰 收入最大化技巧

### 1. 自动升级提示

在日报底部添加：
```
💡 你看到3条，标准版用户看到10条
👉 升级仅需 ¥99/月
```

### 2. 紧急项目溢价

高价值项目（500万+）单独推送：
```
🚨 紧急：XX项目预算500万，3天后截止
   仅高级版用户可见完整信息
```

### 3. 转介绍自动化

邮件签名添加：
```
🎁 推荐1位朋友订阅，各得1个月免费
   推荐链接：https://your-site.com/?ref=用户ID
```

---

## 🚨 故障处理

### 日报未生成

```bash
# 检查日志
tail logs/auto_run_$(date +%Y%m%d).log

# 手动重新运行
python3 scripts/auto_master.py daily
```

### 用户未收到邮件

```bash
# 查看待发列表
sqlite3 data/tender_radar.db "SELECT email, plan FROM subscribers WHERE status='active'"

# 手动补发（替换为实际用户ID）
python3 scripts/resend.py --user=用户ID --date=$(date +%Y%m%d)
```

### 网站访问异常

```bash
# 检查 Vercel/Netlify 状态
vercel --version  # 或 netlify status

# 重新部署
cd site && vercel --prod
```

---

## 📈 扩展路径

### Month 1: 验证（目标：3个付费用户）
- 全自动运行
- 手动收款确认
- 优化转化漏斗

### Month 2: 增长（目标：10个付费用户）
- 增加SEO文章（每周2篇）
- 优化落地页转化率
- 接入自动支付

### Month 3: 规模化（目标：30个付费用户）
- 增加更多数据源
- 推出高级版功能
- 建立转介绍体系

---

## 🔗 重要链接

| 资源 | 路径 |
|------|------|
| 项目目录 | `~/openclaw-income-factory/` |
| 数据库 | `data/tender_radar.db` |
| 日报 | `reports/daily/` |
| 获客网站 | `site/` |
| 日志 | `logs/` |
| 主控脚本 | `scripts/auto_master.py` |

---

## ⚠️ 关键提醒

1. **每日检查收款** - 用户付款后需要手动确认
2. **每周检查转化** - 优化自动跟进邮件内容
3. **每月检查SEO** - 确保网站被搜索引擎收录

**你的角色**：监控者 + 决策者
**系统的角色**：执行者 + 运营者

---

## 🚀 立即执行

```bash
# 1. 部署网站（现在）
cd site && vercel --prod

# 2. 配置定时任务
crontab -e
# 添加: 0 8 * * * cd ~/openclaw-income-factory && python3 scripts/auto_master.py daily

# 3. 测试运行
python3 scripts/auto_master.py daily

# 4. 查看结果
cat reports/daily/daily_report_$(date +%Y%m%d).md
```

**30分钟后，系统将全自动运行。你只需每天查看收入。**
