#!/usr/bin/env python3
"""
飞书告警消息模板生成器
"""

# 告警消息模板 - 日报类型
DAILY_ALERT_TEMPLATE = {
    "msg_type": "interactive",
    "card": {
        "header": {
            "title": "📊 招标雷达 - 每日数据摘要",
            "template": "blue"
        },
        "elements": [
            {
                "tag": "markdown",
                "content": "**日期**: {date}\n\n## 核心指标"
            },
            {
                "tag": "div",
                "fields": [
                    {"is_short": True, "text": {"tag": "lark_md", "content": "**DAU**\n{dau}"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": "**新增用户**\n{new_users}"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": "**收入**\n¥{revenue}"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": "**新增招标**\n{new_tenders}"}}
                ]
            },
            {
                "tag": "markdown",
                "content": "## 邮件效果"
            },
            {
                "tag": "div",
                "fields": [
                    {"is_short": True, "text": {"tag": "lark_md", "content": "**发送量**\n{emails_sent}"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": "**打开率**\n{open_rate}%"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": "**回复率**\n{reply_rate}%"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": "**总用户**\n{total_users}"}}
                ]
            }
        ]
    }
}

# 告警消息模板 - 异常告警类型
ALERT_TEMPLATE = {
    "msg_type": "interactive",
    "card": {
        "header": {
            "title": "🚨 招标雷达 - 指标异常告警",
            "template": "red"
        },
        "elements": [
            {
                "tag": "markdown",
                "content": "**检测时间**: {timestamp}\n**异常指标数**: {alert_count}"
            },
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "## 异常详情"
                }
            },
            {
                "tag": "markdown",
                "content": "{alert_details}"
            },
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "## 当前指标"
                }
            },
            {
                "tag": "div",
                "fields": [
                    {"is_short": True, "text": {"tag": "lark_md", "content": "**DAU**\n{dau}"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": "**新增用户**\n{new_users}"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": "**收入**\n¥{revenue}"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": "**新增招标**\n{new_tenders}"}}
                ]
            }
        ]
    }
}

# 周报消息模板
WEEKLY_REPORT_TEMPLATE = {
    "msg_type": "interactive",
    "card": {
        "header": {
            "title": "📈 招标雷达 - 周数据报告",
            "template": "green"
        },
        "elements": [
            {
                "tag": "markdown",
                "content": "**周期**: {week_range}\n\n## 本周概况"
            },
            {
                "tag": "div",
                "fields": [
                    {"is_short": True, "text": {"tag": "lark_md", "content": "**新增用户**\n{new_users}"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": "**周收入**\n¥{revenue}"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": "**新增招标**\n{new_tenders}"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": "**邮件打开率**\n{open_rate}%"}}
                ]
            },
            {
                "tag": "markdown",
                "content": "## 留存率"
            },
            {
                "tag": "div",
                "fields": [
                    {"is_short": True, "text": {"tag": "lark_md", "content": "**次日留存**\n{d1_retention}%"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": "**7日留存**\n{d7_retention}%"}}
                ]
            },
            {
                "tag": "markdown",
                "content": "## 累计数据"
            },
            {
                "tag": "div",
                "fields": [
                    {"is_short": True, "text": {"tag": "lark_md", "content": "**总用户**\n{total_users}"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": "**付费用户**\n{total_paid}"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": "**累计收入**\n¥{total_revenue}"}}
                ]
            }
        ]
    }
}

# 月报消息模板
MONTHLY_REPORT_TEMPLATE = {
    "msg_type": "interactive",
    "card": {
        "header": {
            "title": "📊 招标雷达 - 月度数据报告",
            "template": "purple"
        },
        "elements": [
            {
                "tag": "markdown",
                "content": "**{month}**\n\n## 收入指标"
            },
            {
                "tag": "div",
                "fields": [
                    {"is_short": True, "text": {"tag": "lark_md", "content": "**MRR**\n¥{mrr}"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": "**ARR**\n¥{arr}"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": "**ARPU**\n¥{arpu}"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": "**LTV**\n¥{ltv}"}}
                ]
            },
            {
                "tag": "markdown",
                "content": "## 用户增长"
            },
            {
                "tag": "div",
                "fields": [
                    {"is_short": True, "text": {"tag": "lark_md", "content": "**新增用户**\n{new_users}"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": "**新增付费**\n{new_paid}"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": "**付费转化率**\n{pay_conversion_rate}%"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": "**30日留存**\n{d30_retention}%"}}
                ]
            }
        ]
    }
}


def format_daily_alert(stats):
    """格式化日报消息"""
    template = DAILY_ALERT_TEMPLATE.copy()
    content = template["card"]["elements"][1]["fields"]
    
    content[0]["text"]["content"] = f"**DAU**\n{stats.get('dau', 0)}"
    content[1]["text"]["content"] = f"**新增用户**\n{stats.get('new_users', 0)}"
    content[2]["text"]["content"] = f"**收入**\n¥{stats.get('revenue', 0)}"
    content[3]["text"]["content"] = f"**新增招标**\n{stats.get('new_tenders', 0)}"
    
    email_content = template["card"]["elements"][3]["fields"]
    email_content[0]["text"]["content"] = f"**发送量**\n{stats.get('emails_sent', 0)}"
    email_content[1]["text"]["content"] = f"**打开率**\n{stats.get('open_rate', 0)}%"
    email_content[2]["text"]["content"] = f"**回复率**\n{stats.get('reply_rate', 0)}%"
    email_content[3]["text"]["content"] = f"**总用户**\n{stats.get('total_users', 0)}"
    
    # 更新日期
    template["card"]["elements"][0]["content"] = f"**日期**: {stats.get('date', '')}"
    
    return template


def format_weekly_report(report):
    """格式化周报消息"""
    template = WEEKLY_REPORT_TEMPLATE.copy()
    
    # 更新周期
    template["card"]["elements"][0]["content"] = f"**周期**: {report.get('week', '')}"
    
    # 本周概况
    summary = report.get('summary', {})
    fields = template["card"]["elements"][1]["fields"]
    fields[0]["text"]["content"] = f"**新增用户**\n{summary.get('new_users', 0)}"
    fields[1]["text"]["content"] = f"**周收入**\n¥{summary.get('revenue', 0)}"
    fields[2]["text"]["content"] = f"**新增招标**\n{summary.get('new_tenders', 0)}"
    fields[3]["text"]["content"] = f"**邮件打开率**\n{report.get('email_metrics', {}).get('open_rate', 0)}%"
    
    # 留存率
    retention = report.get('retention', {})
    ret_fields = template["card"]["elements"][3]["fields"]
    ret_fields[0]["text"]["content"] = f"**次日留存**\n{retention.get('d1_retention', 0)}%"
    ret_fields[1]["text"]["content"] = f"**7日留存**\n{retention.get('d7_retention', 0)}%"
    
    # 累计数据
    cumulative = report.get('cumulative', {})
    cum_fields = template["card"]["elements"][5]["fields"]
    cum_fields[0]["text"]["content"] = f"**总用户**\n{cumulative.get('total_users', 0)}"
    cum_fields[1]["text"]["content"] = f"**付费用户**\n{cumulative.get('total_paid', 0)}"
    cum_fields[2]["text"]["content"] = f"**累计收入**\n¥{cumulative.get('total_revenue', 0)}"
    
    return template


def format_monthly_report(report):
    """格式化月报消息"""
    template = MONTHLY_REPORT_TEMPLATE.copy()
    
    # 更新月份
    template["card"]["elements"][0]["content"] = f"**{report.get('month', '')}**"
    
    # 收入指标
    financial = report.get('financial', {})
    fields = template["card"]["elements"][1]["fields"]
    fields[0]["text"]["content"] = f"**MRR**\n¥{report.get('summary', {}).get('mrr', 0)}"
    fields[1]["text"]["content"] = f"**ARR**\n¥{report.get('arr', 0)}"
    fields[2]["text"]["content"] = f"**ARPU**\n¥{financial.get('arpu', 0)}"
    fields[3]["text"]["content"] = f"**LTV**\n¥{financial.get('ltv', 0)}"
    
    # 用户增长
    summary = report.get('summary', {})
    user_fields = template["card"]["elements"][3]["fields"]
    user_fields[0]["text"]["content"] = f"**新增用户**\n{summary.get('new_users', 0)}"
    user_fields[1]["text"]["content"] = f"**新增付费**\n{summary.get('new_paid', 0)}"
    user_fields[2]["text"]["content"] = f"**付费转化率**\n{financial.get('pay_conversion_rate', 0)}%"
    user_fields[3]["text"]["content"] = f"**30日留存**\n{report.get('retention', {}).get('d30_retention', 0)}%"
    
    return template


if __name__ == "__main__":
    import json
    
    # 测试日报消息
    test_stats = {
        "date": "2026-03-15",
        "dau": 25,
        "new_users": 8,
        "revenue": 1500,
        "new_tenders": 15,
        "emails_sent": 50,
        "open_rate": 32.5,
        "reply_rate": 8.2,
        "total_users": 120
    }
    
    print("=== 日报消息模板示例 ===")
    print(json.dumps(format_daily_alert(test_stats), ensure_ascii=False, indent=2))
