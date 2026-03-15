#!/usr/bin/env python3
"""
OpenClaw 招标雷达 - 监控告警脚本
当运行失败时发送飞书通知
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 飞书机器人 Webhook URL (从环境变量或配置文件读取)
FEISHU_WEBHOOK_URL = os.environ.get('FEISHU_WEBHOOK_URL', '')

# 告警级别
ALERT_LEVELS = {
    'ERROR': '🔴 严重错误',
    'WARNING': '🟡 警告',
    'INFO': '🔵 信息'
}


def send_feishu_message(message: str, level: str = 'INFO') -> bool:
    """发送飞书消息"""
    if not FEISHU_WEBHOOK_URL:
        logger.warning("未配置飞书 Webhook URL")
        return False
    
    import requests
    
    level_emoji = ALERT_LEVELS.get(level, '🔵 信息')
    full_message = f"""
{level_emoji} **招标雷达监控告警**

{message}

⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📍 环境: {os.environ.get('ENV', 'production')}
"""
    
    payload = {
        "msg_type": "text",
        "content": {
            "text": full_message
        }
    }
    
    try:
        response = requests.post(FEISHU_WEBHOOK_URL, json=payload, timeout=10)
        if response.status_code == 200:
            logger.info("飞书消息发送成功")
            return True
        else:
            logger.error(f"飞书消息发送失败: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"发送飞书消息异常: {e}")
        return False


def check_system_health() -> dict:
    """检查系统健康状态"""
    health = {
        'status': 'healthy',
        'issues': []
    }
    
    # 检查日志目录
    log_dir = Path('logs')
    if not log_dir.exists():
        log_dir.mkdir(exist_ok=True)
    
    # 检查配置文件
    config_dir = Path('config')
    if not config_dir.exists():
        health['issues'].append('配置文件目录不存在')
        health['status'] = 'unhealthy'
    
    # 检查数据目录
    data_dir = Path('data')
    if not data_dir.exists():
        health['issues'].append('数据目录不存在')
        health['status'] = 'unhealthy'
    
    return health


def check_recent_errors() -> list:
    """检查最近的错误日志"""
    errors = []
    log_file = Path('logs/error.log')
    
    if log_file.exists():
        try:
            # 读取最近 100 行
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                recent_lines = lines[-100:] if len(lines) > 100 else lines
                
                for line in recent_lines:
                    if 'ERROR' in line or 'CRITICAL' in line:
                        errors.append(line.strip())
        except Exception as e:
            logger.error(f"读取错误日志失败: {e}")
    
    return errors


def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("招标雷达监控系统启动")
    logger.info("=" * 50)
    
    # 健康检查
    health = check_system_health()
    logger.info(f"健康状态: {health['status']}")
    
    if health['status'] != 'healthy':
        message = f"系统健康检查失败:\n" + "\n".join(f"- {i}" for i in health['issues'])
        send_feishu_message(message, 'ERROR')
        sys.exit(1)
    
    # 检查最近错误
    errors = check_recent_errors()
    if errors:
        recent_errors = "\n".join(errors[-5:])  # 只取最近5条
        message = f"检测到 {len(errors)} 个错误:\n{recent_errors}"
        send_feishu_message(message, 'WARNING')
    
    # 如果是定时任务运行，检查是否有长时间未运行的任务
    last_run_file = Path('logs/last_run.txt')
    if last_run_file.exists():
        try:
            last_run_time = float(last_run_file.read_text().strip())
            current_time = time.time()
            elapsed = current_time - last_run_time
            
            # 如果超过 25 小时未运行
            if elapsed > 25 * 3600:
                message = f"警告: 任务已超过 25 小时未运行\n最后运行: {datetime.fromtimestamp(last_run_time).strftime('%Y-%m-%d %H:%M')}"
                send_feishu_message(message, 'WARNING')
        except Exception as e:
            logger.error(f"检查最后运行时间失败: {e}")
    
    logger.info("监控检查完成")
    
    # 更新最后运行时间
    with open(last_run_file, 'w') as f:
        f.write(str(time.time()))
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
