#!/bin/bash
# QQ邮箱问题排查脚本

echo "🔍 QQ邮箱连接问题排查"
echo "======================"
echo ""

echo "1. 检查网络连通性..."
ping -c 3 smtp.qq.com 2>/dev/null || echo "❌ ping失败（可能DNS或网络问题）"
echo ""

echo "2. 检查端口开放情况..."
nc -zv smtp.qq.com 587 2>&1 | grep -E "succeeded|Connected" || echo "❌ 587端口不通"
nc -zv smtp.qq.com 465 2>&1 | grep -E "succeeded|Connected" || echo "❌ 465端口不通"
echo ""

echo "3. 检查SSL/TLS支持..."
openssl s_client -connect smtp.qq.com:465 -servername smtp.qq.com </dev/null 2>&1 | head -5

echo ""
echo "4. 可能的解决方案："
echo "   - 使用163邮箱（smtp.163.com）"
echo "   - 使用SendGrid（sendgrid.com）"
echo "   - 使用飞书Bot（推荐）"
echo ""
