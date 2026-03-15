#!/usr/bin/env python3
"""
OpenClaw 招标雷达 - 飞书发送模块
功能:
  1. 读取日报 Markdown 文件
  2. 转换为飞书富文本格式
  3. 通过飞书机器人 Webhook 发送
  4. 支持卡片消息（更美观）

飞书 Webhook 文档:
  https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot
"""

import json
import os
import re
import requests
from datetime import datetime

PROJECT_DIR = "/home/daministrator/.openclaw/workspace/openclaw-income-factory"
REPORT_DIR = f"{PROJECT_DIR}/reports/daily"
LOG_DIR = f"{PROJECT_DIR}/logs"

# 飞书 Webhook URL - 从环境变量或配置文件读取
FEISHU_WEBHOOK_URL = os.environ.get('FEISHU_WEBHOOK_URL', '')

# 飞书消息签名密钥（可选，增强安全性）
FEISHU_SECRET = os.environ.get('FEISHU_SECRET', '')


def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] [feishu_sender] {message}"
    print(log_msg)
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = f"{LOG_DIR}/feishu_{datetime.now().strftime('%Y%m%d')}.log"
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    except Exception:
        pass


def gen_sign(timestamp, secret):
    """生成飞书签名（如果配置了密钥）"""
    if not secret:
        return None

    import hashlib
    import hmac
    import base64

    string_to_sign = f'{timestamp}\n{secret}'
    hmac_code = hmac.new(
        string_to_sign.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    sign = base64.b64encode(hmac_code).decode('utf-8')
    return sign


# ========== Markdown 转飞书富文本 ==========

def markdown_to_feishu_post(markdown_text):
    """
    将 Markdown 转换为飞书富文本 (post) 格式
    飞书 post 格式: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/im-v1/message/create_json#45e0953e
    """
    lines = markdown_text.split('\n')
    content = []
    current_paragraph = []

    for line in lines:
        line = line.strip()

        if not line:
            # 空行 - 结束当前段落
            if current_paragraph:
                content.append(current_paragraph)
                current_paragraph = []
            continue

        # 标题 (H1-H3)
        h_match = re.match(r'^(#{1,3})\s+(.+)', line)
        if h_match:
            if current_paragraph:
                content.append(current_paragraph)
                current_paragraph = []
            level = len(h_match.group(1))
            title_text = h_match.group(2).strip()
            # 清理 emoji
            title_text = re.sub(r'[^\w\s\u4e00-\u9fff|/()（）,，。、：:·\-]', '', title_text).strip()
            content.append([{"tag": "text", "text": title_text, "style": ["bold"]}])
            continue

        # 分隔线
        if line.startswith('---') or line.startswith('***'):
            if current_paragraph:
                content.append(current_paragraph)
                current_paragraph = []
            content.append([{"tag": "text", "text": "————————————"}])
            continue

        # 引用块
        if line.startswith('>'):
            text = line.lstrip('> ').strip()
            current_paragraph.append({"tag": "text", "text": f"  {text}"})
            continue

        # 表格行 - 简化为文本
        if line.startswith('|') and line.endswith('|'):
            # 跳过分隔行
            if re.match(r'^\|[\s\-|:]+\|$', line):
                continue
            cells = [c.strip() for c in line.strip('|').split('|')]
            row_text = '  |  '.join(cells)
            current_paragraph.append({"tag": "text", "text": row_text})
            content.append(current_paragraph)
            current_paragraph = []
            continue

        # 列表项
        list_match = re.match(r'^[-*]\s+(.+)', line)
        if list_match:
            text = list_match.group(1)
            # 处理粗体
            text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
            current_paragraph.append({"tag": "text", "text": f"  · {text}"})
            content.append(current_paragraph)
            current_paragraph = []
            continue

        # 有序列表
        ol_match = re.match(r'^(\d+)\.\s+(.+)', line)
        if ol_match:
            num = ol_match.group(1)
            text = ol_match.group(2)
            text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
            current_paragraph.append({"tag": "text", "text": f"  {num}. {text}"})
            content.append(current_paragraph)
            current_paragraph = []
            continue

        # 普通文本 - 处理粗体和链接
        # 处理链接 [text](url)
        line = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', lambda m: m.group(1), line)
        # 处理粗体
        line = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
        # 处理斜体
        line = re.sub(r'\*(.+?)\*', r'\1', line)

        current_paragraph.append({"tag": "text", "text": line})
        content.append(current_paragraph)
        current_paragraph = []

    if current_paragraph:
        content.append(current_paragraph)

    # 限制飞书消息长度（最多50行）
    if len(content) > 50:
        content = content[:48]
        content.append([{"tag": "text", "text": "...（更多内容请查看完整日报）"}])

    return content


def build_card_message(report_text, title=None):
    """
    构建飞书卡片消息（更美观的展示方式）
    """
    if not title:
        today = datetime.now().strftime('%Y年%m月%d日')
        title = f"OpenClaw 招标雷达 | {today}"

    # 从报告中提取关键信息
    lines = report_text.split('\n')

    # 提取概览部分
    overview_lines = []
    in_overview = False
    for line in lines:
        if '今日概览' in line:
            in_overview = True
            continue
        if in_overview:
            if line.startswith('---') or (line.startswith('#') and '概览' not in line):
                break
            if line.strip().startswith('-') or line.strip().startswith('*'):
                clean = re.sub(r'[*\-]', '', line).strip()
                clean = re.sub(r'[^\w\s\u4e00-\u9fff|/()（），。、：:·\-¥%]', '', clean).strip()
                if clean:
                    overview_lines.append(clean)

    overview_text = '\n'.join(overview_lines[:5]) if overview_lines else '暂无数据'

    # 提取重点推荐（前3条）
    highlights = []
    in_highlight = False
    current_item = []
    for line in lines:
        if '重点推荐' in line or '百万级大单' in line:
            in_highlight = True
            continue
        if in_highlight:
            if line.startswith('---') and current_item:
                break
            if line.startswith('**') and line.endswith('**'):
                if current_item:
                    highlights.append('\n'.join(current_item))
                current_item = [re.sub(r'\*\*', '', line)]
            elif line.strip().startswith('-') and current_item:
                clean = re.sub(r'[*]', '', line).strip().lstrip('- ')
                clean = re.sub(r'[^\w\s\u4e00-\u9fff|/()（），。、：:·\-¥%\[\]]', '', clean).strip()
                if clean:
                    current_item.append(f"  {clean}")

    if current_item:
        highlights.append('\n'.join(current_item))

    highlights_text = '\n\n'.join(highlights[:3]) if highlights else '暂无重点推荐'

    # 构建卡片
    card = {
        "msg_type": "interactive",
        "card": {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": title
                },
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**今日概览**\n{overview_text}"
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**重点推荐**\n{highlights_text}"
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": f"OpenClaw 招标雷达 | 自动生成于 {datetime.now().strftime('%H:%M')}"
                        }
                    ]
                }
            ]
        }
    }

    return card


def build_post_message(report_text, title=None):
    """构建飞书富文本 (post) 消息"""
    if not title:
        today = datetime.now().strftime('%Y年%m月%d日')
        title = f"OpenClaw 招标雷达 | {today}"

    content = markdown_to_feishu_post(report_text)

    message = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": title,
                    "content": content
                }
            }
        }
    }

    return message


# ========== 发送 ==========

def send_to_feishu(message_body, webhook_url=None):
    """
    通过飞书 Webhook 发送消息
    返回 (成功?, 响应信息)
    """
    url = webhook_url or FEISHU_WEBHOOK_URL

    if not url:
        log("飞书 Webhook URL 未配置，跳过发送")
        return False, "WEBHOOK_URL 未配置"

    headers = {'Content-Type': 'application/json'}

    # 如果配置了签名密钥，添加签名
    if FEISHU_SECRET:
        import time as _time
        timestamp = str(int(_time.time()))
        sign = gen_sign(timestamp, FEISHU_SECRET)
        message_body['timestamp'] = timestamp
        message_body['sign'] = sign

    try:
        response = requests.post(
            url,
            headers=headers,
            json=message_body,
            timeout=10
        )

        result = response.json()

        if response.status_code == 200 and result.get('code', -1) == 0:
            log("飞书消息发送成功")
            return True, "发送成功"
        else:
            error_msg = result.get('msg', response.text)
            log(f"飞书消息发送失败: {error_msg}")
            return False, error_msg

    except requests.exceptions.Timeout:
        log("飞书发送超时")
        return False, "请求超时"
    except Exception as e:
        log(f"飞书发送异常: {e}")
        return False, str(e)


def send_text_message(text, webhook_url=None):
    """发送简单文本消息（用于调试或通知）"""
    message = {
        "msg_type": "text",
        "content": {
            "text": text
        }
    }
    return send_to_feishu(message, webhook_url)


# ========== 主流程 ==========

def send_daily_report(report_path=None, webhook_url=None, use_card=True):
    """
    发送每日招标报告到飞书
    参数:
      report_path: 报告文件路径，默认为今日报告
      webhook_url: 飞书 Webhook URL，默认从环境变量读取
      use_card: True 使用卡片消息（更美观），False 使用富文本
    返回: (成功?, 消息)
    """
    log("=" * 50)
    log("开始发送飞书日报")
    log("=" * 50)

    # 确定报告路径
    if not report_path:
        today = datetime.now().strftime('%Y%m%d')
        report_path = f"{REPORT_DIR}/daily_report_{today}.md"

    # 检查报告文件
    if not os.path.exists(report_path):
        log(f"日报文件不存在: {report_path}")
        return False, f"文件不存在: {report_path}"

    # 读取报告内容
    with open(report_path, 'r', encoding='utf-8') as f:
        report_text = f.read()

    if not report_text.strip():
        log("日报内容为空")
        return False, "日报内容为空"

    log(f"读取日报: {report_path} ({len(report_text)} 字)")

    # 构建消息
    if use_card:
        log("使用卡片消息格式")
        message = build_card_message(report_text)
    else:
        log("使用富文本消息格式")
        message = build_post_message(report_text)

    # 发送
    success, msg = send_to_feishu(message, webhook_url)

    if success:
        log("日报发送成功")
    else:
        log(f"日报发送失败: {msg}")
        # 如果卡片消息失败，尝试退化为文本消息
        if use_card:
            log("尝试退化为文本消息...")
            # 截取前2000字
            short_text = report_text[:2000]
            if len(report_text) > 2000:
                short_text += "\n\n...（更多内容请查看完整日报）"
            success, msg = send_text_message(short_text, webhook_url)

    return success, msg


if __name__ == "__main__":
    import sys

    # 支持命令行参数
    report_file = None
    webhook = None

    if len(sys.argv) > 1:
        report_file = sys.argv[1]
    if len(sys.argv) > 2:
        webhook = sys.argv[2]

    success, msg = send_daily_report(
        report_path=report_file,
        webhook_url=webhook
    )

    print(f"\n{'='*40}")
    print(f"发送结果: {'成功' if success else '失败'}")
    print(f"详情: {msg}")
    print(f"{'='*40}")
