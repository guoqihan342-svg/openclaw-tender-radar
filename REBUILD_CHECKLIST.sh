#!/bin/bash
# OpenClaw 招标雷达 - 重构执行清单
# 按此清单执行重构

echo "🚀 OpenClaw 招标雷达 - 重构执行清单"
echo "====================================="
echo ""

cd /home/daministrator/.openclaw/workspace/openclaw-income-factory

echo "✅ 已完成的重构项："
echo "   1. 新数据库Schema (db/schema_v2.sql)"
echo "   2. 半自动订阅管理 (skills/subscription_manager.py)"
echo "   3. 新主控流水线 (app/main.py)"
echo ""

echo "📋 待执行的迁移步骤："
echo ""

echo "步骤1: 备份旧数据库"
echo "   cp data/tender_radar.db data/tender_radar.db.backup"
echo ""

echo "步骤2: 应用新Schema"
echo "   sqlite3 data/tender_radar.db < db/schema_v2.sql"
echo ""

echo "步骤3: 迁移旧数据"
echo "   python3 scripts/migrate_data.py"
echo ""

echo "步骤4: 测试新主控"
echo "   python3 app/main.py stats"
echo "   python3 app/main.py run"
echo ""

echo "步骤5: 配置推送渠道（选其一）"
echo "   方案A: 配置飞书Bot"
echo "      - 编辑 config/feishu.conf"
echo "      - 添加 FEISHU_WEBHOOK_URL=xxx"
echo ""
echo "   方案B: 配置SendGrid"
echo "      - 优先设置 SENDGRID_API_KEY 环境变量"
echo "      - 或复制 config/sendgrid.conf.example 为被忽略的本地配置文件"
echo ""

echo "步骤6: 更新定时任务"
echo "   crontab -e"
echo "   # 修改为："
echo "   0 8 * * * cd ~/openclaw-income-factory && python3 app/main.py run"
echo ""

echo "步骤7: 验证完整流程"
echo "   - 创建测试用户"
echo "   - 模拟支付流程"
echo "   - 确认支付开通"
echo "   - 验证日报推送"
echo ""

echo "====================================="
echo "💡 建议执行顺序："
echo "   今天: 步骤1-4（数据库+主控）"
echo "   今天: 步骤5（配置推送）"
echo "   今天: 步骤7（获取第一个用户）"
echo "   明天: 观察定时任务是否正常"
echo "====================================="
