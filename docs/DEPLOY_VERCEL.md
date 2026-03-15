# OpenClaw 招标雷达 - Vercel 部署指南

## 账号信息
- **Vercel账号**: guoqihan342-4149
- **邮箱**: guoqihan342@gmail.com

---

## 方式1: 命令行部署（当前环境）

### 步骤1: 运行部署脚本

```bash
cd /home/daministrator/.openclaw/workspace/openclaw-income-factory/site
bash ../scripts/deploy_vercel.sh
```

### 步骤2: 登录验证

运行后会提示浏览器登录：
1. 按回车打开浏览器
2. 用 guoqihan342@gmail.com 登录
3. 授权 CLI 访问

### 步骤3: 完成部署

按提示完成部署，获得公开 URL。

---

## 方式2: GitHub + Vercel（推荐）

### 步骤1: 创建 GitHub 仓库

1. 访问 https://github.com/new
2. 仓库名: `openclaw-tender-radar`
3. 设置为 Public

### 步骤2: 上传代码

```bash
cd /home/daministrator/.openclaw/workspace/openclaw-income-factory/site

# 初始化 git
git init
git add .
git commit -m "Initial commit"

# 添加远程仓库（替换 YOUR_USERNAME）
git remote add origin https://github.com/guoqihan342/openclaw-tender-radar.git
git branch -M main
git push -u origin main
```

### 步骤3: Vercel 连接 GitHub

1. 访问 https://vercel.com/dashboard
2. 用 guoqihan342@gmail.com 登录
3. 点击 "Add New Project"
4. 选择 GitHub 仓库 `openclaw-tender-radar`
5. 点击 Deploy

### 完成 ✅

每次 push 到 GitHub，Vercel 自动重新部署。

---

## 方式3: 手动拖拽部署（最简单）

### 步骤1: 打包网站文件

```bash
cd /home/daministrator/.openclaw/workspace/openclaw-income-factory

# 打包 site 目录
zip -r site-deploy.zip site/

# 下载到本地
# 文件位置: /home/daministrator/.openclaw/workspace/openclaw-income-factory/site-deploy.zip
```

### 步骤2: Vercel 网页上传

1. 访问 https://vercel.com/dashboard
2. 用 guoqihan342@gmail.com 登录
3. 点击 "Add New Project"
4. 选择 "Import Git Repository" 旁边的下拉箭头
5. 选择 "Upload"（上传）
6. 拖拽 `site-deploy.zip` 上传
7. 点击 Deploy

---

## 部署后配置

### 1. 查看网站

部署成功后会获得 URL，如：
`https://openclaw-tender-radar-guoqihan342-4149.vercel.app`

### 2. 配置自定义域名（可选）

1. 在 Vercel Dashboard 进入项目
2. Settings → Domains
3. 添加你的域名

### 3. 更新收款链接

编辑 `site/payment/index.html`，替换链接为你的实际域名。

---

## 故障排除

### 问题: "The specified token is not valid"

解决:
```bash
npx vercel login
# 然后重新部署
```

### 问题: "Project not found"

解决:
```bash
npx vercel link
# 选择你的项目
```

### 问题: 部署成功但页面空白

检查:
1. 确认 index.html 在 site/ 根目录
2. 检查 vercel.json 配置

---

## 推荐方案

| 方案 | 难度 | 推荐度 | 适合场景 |
|------|------|--------|----------|
| 方式1 CLI | ⭐⭐ | ⭐⭐⭐ | 熟悉命令行 |
| 方式2 GitHub | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 长期维护，自动部署 |
| 方式3 拖拽 | ⭐ | ⭐⭐⭐⭐ | 快速验证，一次性 |

**建议**: 先用方式3快速部署验证，后续用方式2长期维护。
