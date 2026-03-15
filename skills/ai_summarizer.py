#!/usr/bin/env python3
"""
OpenClaw 招标雷达 - AI 摘要生成器
使用 MiniMax API 为每条招标生成:
  1. 100字内摘要
  2. 推荐理由（为什么值得关注）

支持:
  - 批量处理未摘要的招标
  - 失败重试
  - 本地 fallback（API 不可用时基于规则生成）
"""

import sqlite3
import json
import os
import time
import requests
from datetime import datetime

PROJECT_DIR = "/home/daministrator/.openclaw/workspace/openclaw-income-factory"
DB_PATH = f"{PROJECT_DIR}/data/tender_radar.db"
LOG_DIR = f"{PROJECT_DIR}/logs"

# MiniMax API 配置
# 从环境变量或配置文件读取
MINIMAX_API_KEY = os.environ.get('MINIMAX_API_KEY', '')
MINIMAX_GROUP_ID = os.environ.get('MINIMAX_GROUP_ID', '')
MINIMAX_API_URL = 'https://api.minimax.chat/v1/text/chatcompletion_v2'


def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] [ai_summarizer] {message}"
    print(log_msg)
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = f"{LOG_DIR}/summarizer_{datetime.now().strftime('%Y%m%d')}.log"
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    except Exception:
        pass


def format_budget_text(budget):
    """格式化预算为可读文本"""
    if not budget:
        return '未公布'
    try:
        budget = float(budget)
    except (ValueError, TypeError):
        return str(budget)

    if budget >= 100000000:
        return f'{budget / 100000000:.1f}亿元'
    elif budget >= 10000:
        return f'{budget / 10000:.0f}万元'
    else:
        return f'{budget:.0f}元'


def get_pending_tenders(limit=20):
    """获取需要生成摘要的招标（summary 为空）"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, title, budget, region, deadline, purchaser, category, url
        FROM tenders
        WHERE (summary IS NULL OR summary = '')
        ORDER BY created_date DESC, id DESC
        LIMIT ?
    ''', (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def update_tender_summary(tender_id, summary, recommendation):
    """更新招标的摘要和推荐理由"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE tenders
        SET summary = ?, recommendation = ?
        WHERE id = ?
    ''', (summary, recommendation, tender_id))

    conn.commit()
    conn.close()


# ========== MiniMax API 调用 ==========

def call_minimax_api(prompt, max_tokens=300):
    """
    调用 MiniMax API 生成文本
    返回生成的文本，失败返回 None
    """
    if not MINIMAX_API_KEY:
        return None

    headers = {
        'Authorization': f'Bearer {MINIMAX_API_KEY}',
        'Content-Type': 'application/json',
    }

    payload = {
        'model': 'MiniMax-Text-01',
        'messages': [
            {
                'role': 'system',
                'content': '你是一位政府采购领域的专业分析师。请用简洁专业的语言分析招标信息。'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ],
        'max_tokens': max_tokens,
        'temperature': 0.7,
    }

    try:
        response = requests.post(
            MINIMAX_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            log(f"MiniMax API 错误: HTTP {response.status_code}")
            return None

        data = response.json()
        # MiniMax 返回格式
        if 'choices' in data and len(data['choices']) > 0:
            return data['choices'][0]['message']['content'].strip()

        return None

    except requests.exceptions.Timeout:
        log("MiniMax API 超时")
        return None
    except Exception as e:
        log(f"MiniMax API 异常: {e}")
        return None


def generate_summary_via_api(tender):
    """通过 MiniMax API 生成摘要和推荐理由"""
    budget_text = format_budget_text(tender.get('budget'))

    prompt = f"""请为以下政府采购招标信息生成摘要和推荐理由：

项目名称：{tender['title']}
预算金额：{budget_text}
所在地区：{tender.get('region', '未注明')}
截止日期：{tender.get('deadline', '未注明')}
采购方：{tender.get('purchaser', '未注明')}
项目类别：{tender.get('category', '其他')}

请按以下格式输出（JSON）：
{{
  "summary": "100字以内的项目摘要，包含项目核心内容和关键信息",
  "recommendation": "50字以内的推荐理由，说明为什么值得关注这个项目"
}}

只输出JSON，不要其他内容。"""

    result = call_minimax_api(prompt)
    if not result:
        return None, None

    try:
        # 解析 JSON 响应
        # 兼容可能的 markdown 代码块包裹
        clean_result = result.strip()
        if clean_result.startswith('```'):
            clean_result = clean_result.split('\n', 1)[1]
            clean_result = clean_result.rsplit('```', 1)[0]

        data = json.loads(clean_result)
        return data.get('summary', ''), data.get('recommendation', '')

    except json.JSONDecodeError:
        log(f"JSON 解析失败: {result[:100]}")
        return None, None


# ========== 本地规则生成（API 不可用时的 fallback） ==========

def _categorize(title):
    """简单分类（避免跨模块依赖）"""
    rules = [
        (['政务', '政府', '行政'], '政务/平台'),
        (['医疗', '医院', '病历', '卫生'], '医疗/健康'),
        (['教育', '学校', '校园'], '教育/校园'),
        (['安防', '监控', '视频'], '安防/监控'),
        (['环保', '环境', '生态'], '环保/监测'),
        (['社区', '民政', '养老'], '社区/民生'),
        (['交通', '公路', '道路'], '交通/基建'),
        (['网络', '信息化', '数据', '云', '平台', '系统', '软件'], 'IT/信息化'),
    ]
    for keywords, cat in rules:
        if any(kw in title for kw in keywords):
            return cat
    return '其他'


def generate_summary_local(tender):
    """
    基于规则本地生成摘要和推荐理由
    当 MiniMax API 不可用时作为 fallback
    """
    title = tender.get('title', '')
    budget = tender.get('budget')
    budget_text = format_budget_text(budget)
    region = tender.get('region', '未注明')
    deadline = tender.get('deadline', '未注明')
    purchaser = tender.get('purchaser', '未注明')
    category = tender.get('category') or _categorize(title)

    # 生成摘要
    summary_parts = []

    # 项目类型描述
    if '建设' in title:
        summary_parts.append(f'{region}地区{category}类新建项目')
    elif '升级' in title or '改造' in title:
        summary_parts.append(f'{region}地区{category}类升级改造项目')
    elif '采购' in title:
        summary_parts.append(f'{region}地区{category}类采购项目')
    elif '扩容' in title:
        summary_parts.append(f'{region}地区{category}类扩容项目')
    else:
        summary_parts.append(f'{region}地区{category}类项目')

    if budget:
        summary_parts.append(f'预算{budget_text}')

    if purchaser and purchaser != '未注明':
        summary_parts.append(f'由{purchaser}发起')

    if deadline and deadline != '未注明':
        summary_parts.append(f'截止{deadline}')

    summary = '，'.join(summary_parts) + '。'

    # 生成推荐理由
    reasons = []

    # 预算维度
    try:
        budget_val = float(budget) if budget else 0
    except (ValueError, TypeError):
        budget_val = 0

    if budget_val >= 5000000:
        reasons.append('大额项目，预算充足')
    elif budget_val >= 2000000:
        reasons.append('中大型项目，预算较好')
    elif budget_val >= 1000000:
        reasons.append('百万级项目')

    # 行业维度
    hot_categories = ['IT/信息化', '政务/平台', '医疗/健康', '教育/校园']
    if category in hot_categories:
        reasons.append(f'{category}领域需求旺盛')

    # 时间维度
    if deadline and deadline != '未注明':
        try:
            dl = datetime.strptime(deadline, '%Y-%m-%d')
            days_left = (dl - datetime.now()).days
            if 5 <= days_left <= 15:
                reasons.append('即将截止，建议尽快响应')
            elif days_left > 15:
                reasons.append('准备时间充裕')
        except ValueError:
            pass

    # 地区维度
    hot_regions = ['广东', '浙江', '江苏', '北京', '上海', '山东']
    if region in hot_regions:
        reasons.append(f'{region}为采购活跃地区')

    recommendation = '；'.join(reasons[:3]) if reasons else '值得关注的政府采购机会'

    return summary, recommendation


# ========== 主流程 ==========

def summarize_all(limit=20):
    """
    为所有未生成摘要的招标批量生成摘要
    优先使用 MiniMax API，失败则使用本地规则
    返回处理数量
    """
    log("=" * 50)
    log("开始 AI 摘要生成")
    log("=" * 50)

    # 检查 API 可用性
    api_available = bool(MINIMAX_API_KEY)
    if api_available:
        log("MiniMax API Key 已配置，将使用 API 生成摘要")
    else:
        log("MiniMax API Key 未配置，将使用本地规则生成摘要")

    pending = get_pending_tenders(limit=limit)
    log(f"待处理招标: {len(pending)} 条")

    if not pending:
        log("没有需要处理的招标")
        return 0

    success_count = 0
    api_count = 0
    local_count = 0

    for tender in pending:
        tender_id = tender['id']
        title = tender['title']

        summary = None
        recommendation = None

        # 优先尝试 API
        if api_available:
            try:
                summary, recommendation = generate_summary_via_api(tender)
                if summary:
                    api_count += 1
                    # API 调用间隔，避免限流
                    time.sleep(0.5)
            except Exception as e:
                log(f"API 生成失败 [{tender_id}]: {e}")

        # API 失败则使用本地规则
        if not summary:
            summary, recommendation = generate_summary_local(tender)
            local_count += 1

        # 更新数据库
        if summary:
            update_tender_summary(tender_id, summary, recommendation or '')
            success_count += 1
            log(f"[{tender_id}] {title[:30]}... -> 摘要生成完成")

    log(f"处理完成: 总计 {success_count}/{len(pending)} 条")
    log(f"  API 生成: {api_count} 条")
    log(f"  本地生成: {local_count} 条")

    return success_count


if __name__ == "__main__":
    count = summarize_all()
    print(f"\n{'='*40}")
    print(f"AI 摘要生成完成: {count} 条")
    print(f"{'='*40}")
