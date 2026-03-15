#!/bin/bash
# 本地预览服务器 - 临时使用

echo "🚀 启动本地预览服务器..."
echo ""

cd /home/daministrator/.openclaw/workspace/openclaw-income-factory/site

# 启动 Python HTTP 服务器
python3 -m http.server 8080 &
SERVER_PID=$!

echo "✅ 服务器已启动"
echo ""
echo "📱 访问地址:"
echo "   主站: http://localhost:8080"
echo "   收款页: http://localhost:8080/payment/"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

# 等待用户按 Ctrl+C
wait $SERVER_PID
