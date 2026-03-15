# OpenClaw 招标雷达 - 终极全自动部署方案

## 🎯 目标: 部署一次，终身自动

**你需要做的**: 仅需5分钟配置，之后全自动运行

---

## 方案: GitHub + Vercel + GitHub Actions（推荐）

### 为什么选这个方案？

| 特性 | 说明 |
|------|------|
| **全自动** | 代码更新自动部署，无需人工 |
| **免费** | GitHub + Vercel 都免费 |
| **稳定** | 大平台，99.9%可用性 |
| **全球CDN** | 访问速度快 |
| **版本控制** | 每次部署有记录，可回滚 |

---

## 配置步骤（仅需5分钟）

### 步骤1: 创建 GitHub 仓库（1分钟）

1. 访问 https://github.com/new
2. 仓库名: `openclaw-tender-radar`
3. 设置为 **Public**
4. 点击 **Create repository**

### 步骤2: 上传代码（1分钟）

在本地终端执行：

```bash
# 进入项目目录
cd /home/daministrator/.openclaw/workspace/openclaw-income-factory

# 初始化 git
git init
git add .
git commit -m "Initial commit"

# 连接远程仓库（替换 YOUR_USERNAME）
git remote add origin https://github.com/guoqihan342/openclaw-tender-radar.git
git branch -M main
git push -u origin main
```

### 步骤3: Vercel 连接 GitHub（1分钟）

1. 访问 https://vercel.com/dashboard
2. 用 guoqihan342@gmail.com 登录
3. 点击 **Add New Project**
4. 选择 **Import Git Repository**
5. 选择 `openclaw-tender-radar` 仓库
6. 点击 **Import**

### 步骤4: 配置自动部署（2分钟）

在 Vercel 项目设置中：

1. **Framework Preset**: 选择 `Other`
2. **Root Directory**: 设置为 `site`
3. **Build Command**: 留空（静态网站）
4. **Output Directory**: 留空
5. 点击 **Deploy**

完成！🎉

---

## ✅ 部署后全自动流程

```
每天自动运行:
  ↓
生成日报
  ↓
自动更新 site/content/
  ↓
git commit -m "Update daily report"
  ↓
git push
  ↓
GitHub Actions 触发
  ↓
Vercel 自动重新部署
  ↓
网站更新完成（无需人工）
```

---

## 获取 Vercel Token（用于GitHub Actions）

如果需要更高级的自动化，配置Token：

1. 访问 https://vercel.com/account/tokens
2. 点击 **Create Token**
3. 名称: `github-actions`
4. 复制 Token

5. 在 GitHub 仓库设置：
   - Settings → Secrets and variables → Actions
   - 添加 `VERCEL_TOKEN`: 粘贴刚才的Token

---

## 全自动获客 + 全自动部署 = 完全被动收入

| 环节 | 自动化程度 |
|------|-----------|
| 数据抓取 | 100%自动 |
| 日报生成 | 100%自动 |
| 网站部署 | 100%自动 |
| SEO获客 | 100%自动 |
| RSS订阅 | 100%自动 |
| 飞书推送 | 100%自动 |
| **收款确认** | **仅需2分钟/单** |

**你每天只需要**: 查看收款通知，确认到账

---

## 故障处理

### 部署失败

检查 GitHub Actions 日志：
1. 打开 GitHub 仓库
2. Actions 标签
3. 查看失败原因

### 网站内容未更新

检查定时任务：
```bash
# 检查 cron 任务
crontab -l

# 手动运行测试
cd ~/openclaw-income-factory
python3 scripts/auto_run_v2.py daily
```

---

## 监控

部署成功后，你的系统：

- ✅ 每天早8点自动生成日报
- ✅ 自动推送到飞书群
- ✅ 自动更新网站内容
- ✅ 自动部署到 Vercel
- ✅ 被动获客（SEO + RSS）

**完全全自动运行！**

---

## 下一步

1. 按上方步骤配置 GitHub + Vercel
2. 完成后获得公开 URL
3. 配置飞书免费预览群
4. 开始全自动获客

**预计配置时间**: 5分钟  
**之后维护时间**: 每天2分钟（仅确认收款）
