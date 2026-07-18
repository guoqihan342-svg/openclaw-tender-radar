#!/bin/bash
# Vercel 部署脚本

echo "🚀 OpenClaw 招标雷达 - Vercel 部署脚本"
echo ""

# 检查是否在 site 目录
if [ ! -f "index.html" ]; then
    echo "❌ 错误: 请在 site/ 目录下运行此脚本"
    echo "   cd /home/daministrator/.openclaw/workspace/openclaw-income-factory/site"
    exit 1
fi

echo "📦 步骤1: 安装 Vercel CLI"
npm install -g vercel@latest

echo ""
echo "🔐 步骤2: 登录 Vercel"
echo "   请在浏览器中完成登录"
vercel login

echo ""
echo "🚀 步骤3: 部署网站"
echo "   项目名: openclaw-tender-radar"
echo "   部署到生产环境"
if [ -n "${VERCEL_SCOPE:-}" ]; then
    vercel --prod --yes --scope="$VERCEL_SCOPE"
else
    vercel --prod --yes
fi

echo ""
echo "✅ 部署完成!"
echo ""
echo "📋 部署后操作:"
echo "   1. 访问你的 Vercel Dashboard: https://vercel.com/dashboard"
echo "   2. 查看部署状态"
echo "   3. 获得公开 URL"
echo ""
echo "🔗 配置域名（可选）:"
echo "   vercel domains add openclaw-tender-radar.vercel.app"
