#!/bin/bash
# OpenClaw 招标雷达 - 全自动部署脚本
# 一键完成 GitHub + Vercel 配置

set -e  # 遇到错误退出

echo "🚀 OpenClaw 招标雷达 - 全自动部署"
echo "===================================="
echo ""

PROJECT_DIR="/home/daministrator/.openclaw/workspace/openclaw-income-factory"
SITE_DIR="$PROJECT_DIR/site"
GITHUB_USER="guoqihan342"
REPO_NAME="openclaw-tender-radar"

cd "$PROJECT_DIR"

# 检查 git 是否已初始化
if [ ! -d ".git" ]; then
    echo "📦 步骤1: 初始化 Git 仓库..."
    git init
    if [ -n "${GIT_AUTHOR_EMAIL:-}" ]; then
        git config user.email "$GIT_AUTHOR_EMAIL"
    elif ! git config user.email >/dev/null 2>&1; then
        echo "❌ 请先设置 GIT_AUTHOR_EMAIL，或配置 git user.email"
        exit 1
    fi
    git config user.name "${GIT_AUTHOR_NAME:-guoqihan342}"
else
    echo "✅ Git 仓库已存在"
fi

# 添加所有文件
echo "📦 步骤2: 添加文件到 Git..."
git add .

# 提交
echo "📦 步骤3: 提交代码..."
git commit -m "Initial commit: OpenClaw 招标雷达全自动系统" || echo "代码已是最新"

# 连接远程仓库
echo "📦 步骤4: 连接 GitHub 远程仓库..."
git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git" 2>/dev/null || echo "远程仓库已配置"

# 推送代码
echo "📦 步骤5: 推送代码到 GitHub..."
git branch -M main
git push -u origin main || echo "推送失败，请检查GitHub仓库是否存在"

echo ""
echo "===================================="
echo "✅ GitHub 配置完成!"
echo ""
echo "🔗 仓库地址: https://github.com/$GITHUB_USER/$REPO_NAME"
echo ""
echo "下一步（请在浏览器中完成）:"
echo ""
echo "1. 访问 https://vercel.com/dashboard"
echo "   使用你自己的 Vercel 账号登录"
echo ""
echo "2. 点击 'Add New Project'"
echo "   选择 'Import Git Repository'"
echo "   选择 '$REPO_NAME' 仓库"
echo ""
echo "3. 配置项目:"
echo "   - Framework Preset: Other"
echo "   - Root Directory: site"
echo "   - Build Command: 留空"
echo "   - Output Directory: 留空"
echo ""
echo "4. 点击 'Deploy'"
echo ""
echo "5. 等待部署完成，获得公开 URL"
echo ""
echo "===================================="
echo "🎉 完成后你将拥有:"
echo "   - 全自动日报生成"
echo "   - 自动推送到飞书"
echo "   - 自动SEO获客"
echo "   - 自动部署更新"
echo ""
echo "⚠️  注意: 当前脚本无法自动完成Vercel登录（需浏览器）"
echo "    这是最后的交互步骤，完成后终身自动！"
echo ""
