#!/bin/bash
# OpenClaw 招标雷达 - Claude Code 开发工作流
# 用法: ./dev_with_claude.sh <任务描述>

TASK=$1
PROJECT_DIR="/home/daministrator/.openclaw/workspace/openclaw-income-factory"

if [ -z "$TASK" ]; then
    echo "用法: ./dev_with_claude.sh '写一个抓取招标信息的爬虫'"
    exit 1
fi

cd $PROJECT_DIR

# 创建任务上下文
echo "🚀 启动 Claude Code 开发任务"
echo "任务: $TASK"
echo "项目: $PROJECT_DIR"
echo ""

# 构建 Claude Code 提示
PROMPT="""
你是一个专业的 Python 开发工程师。

当前项目: OpenClaw 招标雷达 - 全自动政府采购信息监控服务

项目目录结构:
- scripts/ - 执行脚本
- skills/ - 技能模块  
- data/ - 数据文件
- reports/ - 生成报告
- config/ - 配置文件

你的任务: $TASK

要求:
1. 代码要健壮，有错误处理
2. 添加中文注释
3. 遵循项目现有代码风格
4. 如果修改现有文件，先备份
5. 完成后说明如何测试

请直接执行，不要询问确认。
"""

# 调用 Claude Code
echo "正在调用 Claude Code..."
claude "$PROMPT"

echo ""
echo "✅ 任务完成"
