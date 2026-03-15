#!/usr/bin/env python3
"""
OpenClaw 招标雷达 - 全自动主控 V2
完整流程: 抓取 → AI摘要 → 生成日报 → 飞书发送

用法:
  python auto_run_v2.py          # 执行每日全流程
  python auto_run_v2.py daily    # 同上
  python auto_run_v2.py init     # 初始化系统
  python auto_run_v2.py stats    # 显示统计
  python auto_run_v2.py collect  # 仅抓取数据
  python auto_run_v2.py send     # 仅发送飞书
"""

import os
import sys
import sqlite3
import traceback
from datetime import datetime

PROJECT_DIR = "/home/daministrator/.openclaw/workspace/openclaw-income-factory"
DB_PATH = f"{PROJECT_DIR}/data/tender_radar.db"
os.chdir(PROJECT_DIR)

# 将项目目录加入 Python 路径，方便导入模块
sys.path.insert(0, PROJECT_DIR)


def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] [auto_run] {message}"
    print(log_msg)

    log_file = f"{PROJECT_DIR}/logs/auto_run_{datetime.now().strftime('%Y%m%d')}.log"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    except Exception:
        pass


def run_step(step_name, func, *args, **kwargs):
    """执行步骤，返回 (成功?, 结果)"""
    log(f">>> Step: {step_name}")
    try:
        result = func(*args, **kwargs)
        log(f"<<< {step_name} 完成")
        return True, result
    except Exception as e:
        log(f"!!! {step_name} 失败: {e}")
        traceback.print_exc()
        return False, None


# ========== 各步骤函数 ==========

def step_collect():
    """Step 1: 抓取招标数据"""
    from skills.source_collector_v2 import collect
    return collect()


def step_summarize():
    """Step 2: AI 摘要生成"""
    from skills.ai_summarizer import summarize_all
    return summarize_all(limit=30)


def step_generate_report():
    """Step 3: 生成日报"""
    result = os.system(f"python3 {PROJECT_DIR}/scripts/generate_daily_report_v2.py")
    if result != 0:
        raise RuntimeError("日报生成脚本退出码非零")

    today = datetime.now().strftime('%Y%m%d')
    report_path = f"{PROJECT_DIR}/reports/daily/daily_report_{today}.md"
    if not os.path.exists(report_path):
        raise FileNotFoundError(f"日报文件不存在: {report_path}")

    return report_path


def step_send_feishu(report_path=None):
    """Step 4: 飞书发送"""
    from skills.feishu_sender import send_daily_report
    success, msg = send_daily_report(report_path=report_path)
    if not success:
        log(f"飞书发送失败: {msg}")
    return success, msg


# ========== 主流程 ==========

def daily_run():
    """每日全自动运行: 抓取 → AI摘要 → 日报 → 飞书"""
    log("=" * 60)
    log("OpenClaw 招标雷达 - 每日自动运行启动")
    log("=" * 60)

    results = {}

    # Step 1: 抓取招标数据
    ok, count = run_step("抓取招标数据", step_collect)
    results['collect'] = {'ok': ok, 'count': count}
    if not ok:
        log("数据抓取失败，将使用历史数据继续")

    # Step 2: AI 摘要生成
    ok, count = run_step("AI摘要生成", step_summarize)
    results['summarize'] = {'ok': ok, 'count': count}
    if not ok:
        log("AI 摘要生成失败，日报将不含摘要")

    # Step 3: 生成日报
    ok, report_path = run_step("生成日报", step_generate_report)
    results['report'] = {'ok': ok, 'path': report_path}
    if not ok:
        log("日报生成失败，终止运行")
        return False

    # Step 4: 飞书发送
    ok, send_result = run_step("飞书发送", step_send_feishu, report_path)
    results['feishu'] = {'ok': ok, 'result': send_result}

    # 统计信息
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')

        cursor.execute("SELECT COUNT(*) FROM tenders WHERE created_date=?", (today,))
        today_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM subscribers
            WHERE status='active' AND plan IN ('standard', 'premium')
        """)
        paid_users = cursor.fetchone()[0]

        conn.close()

        log(f"今日招标: {today_count} 条")
        log(f"付费用户: {paid_users} 人")
    except Exception as e:
        log(f"统计查询失败: {e}")

    # 汇总
    log("=" * 60)
    log("运行结果汇总:")
    log(f"  抓取: {'成功' if results['collect']['ok'] else '失败'} (新增 {results['collect'].get('count', 0)} 条)")
    log(f"  摘要: {'成功' if results['summarize']['ok'] else '失败'} (处理 {results['summarize'].get('count', 0)} 条)")
    log(f"  日报: {'成功' if results['report']['ok'] else '失败'} ({results['report'].get('path', '')})")
    log(f"  飞书: {'成功' if results['feishu']['ok'] else '失败/跳过'}")
    log("=" * 60)

    return True


def init_system():
    """初始化系统"""
    log("初始化系统...")

    # 创建必要目录
    dirs = ['data', 'logs', 'reports/daily', 'reports/weekly', 'skills']
    for d in dirs:
        os.makedirs(f"{PROJECT_DIR}/{d}", exist_ok=True)

    # 初始化数据库
    result = os.system(f"python3 {PROJECT_DIR}/scripts/init_db.py")
    if result == 0:
        log("数据库初始化完成")
    else:
        log("数据库初始化失败")

    # 升级 schema（添加新列）
    try:
        from skills.source_collector_v2 import ensure_db_schema
        ensure_db_schema()
        log("数据库 schema 升级完成")
    except Exception as e:
        log(f"schema 升级失败: {e}")

    log("系统初始化完成")


def show_stats():
    """显示统计"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    today = datetime.now().strftime('%Y-%m-%d')

    cursor.execute("SELECT COUNT(*) FROM tenders WHERE created_date=?", (today,))
    today_tenders = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tenders")
    total_tenders = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tenders WHERE summary IS NOT NULL AND summary != ''")
    summarized = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM subscribers WHERE status='active'")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT plan, COUNT(*) FROM subscribers WHERE status='active' GROUP BY plan")
    plan_dist = cursor.fetchall()

    conn.close()

    log("系统统计")
    log(f"  今日招标: {today_tenders} 条")
    log(f"  累计招标: {total_tenders} 条")
    log(f"  已摘要:   {summarized} 条")
    log(f"  订阅用户: {total_users} 人")
    for plan, count in plan_dist:
        log(f"    - {plan}: {count} 人")


def only_collect():
    """仅执行数据抓取"""
    run_step("抓取招标数据", step_collect)
    run_step("AI摘要生成", step_summarize)


def only_send():
    """仅发送飞书"""
    today = datetime.now().strftime('%Y%m%d')
    report_path = f"{PROJECT_DIR}/reports/daily/daily_report_{today}.md"
    if os.path.exists(report_path):
        run_step("飞书发送", step_send_feishu, report_path)
    else:
        log(f"今日日报不存在: {report_path}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'daily'

    commands = {
        'init': init_system,
        'daily': daily_run,
        'stats': show_stats,
        'collect': only_collect,
        'send': only_send,
    }

    if cmd in commands:
        commands[cmd]()
    else:
        print("用法: python auto_run_v2.py [init|daily|stats|collect|send]")
        print("  init    - 初始化系统")
        print("  daily   - 执行每日全流程（默认）")
        print("  stats   - 显示统计")
        print("  collect - 仅抓取+摘要")
        print("  send    - 仅发送飞书")
