# 招标雷达 - 数据分析和报表系统

本系统为招标雷达项目提供完整的数据分析和监控报表功能。

## 📁 项目结构

```
openclaw-income-factory/
├── docs/
│   └── METRICS.md              # 核心指标定义文档
├── scripts/
│   ├── analytics/              # 分析报表脚本
│   │   ├── daily_report.py     # 每日数据汇总
│   │   ├── weekly_report.py   # 周报表生成
│   │   ├── monthly_report.py   # 月报表生成
│   │   ├── generate_dashboard_data.py  # 看板数据生成
│   │   └── generate_test_data.py       # 测试数据生成
│   └── monitoring/             # 监控告警配置
│       ├── config.json         # 告警阈值配置
│       ├── monitor_check.py    # 指标监控检查
│       └── feishu_templates.py # 飞书消息模板
├── site/
│   └── dashboard/
│       ├── index.html          # 数据可视化看板
│       └── data.json           # 看板数据
└── reports/
    ├── daily/                  # 日报输出
    ├── weekly/                 # 周报输出
    └── monthly/                # 月报输出
```

## 🚀 快速开始

### 1. 每日报表

```bash
python scripts/analytics/daily_report.py
```

### 2. 周报表

```bash
# 生成上周报告
python scripts/analytics/weekly_report.py

# 生成2周前报告
python scripts/analytics/weekly_report.py 2
```

### 3. 月报表

```bash
# 生成上月报告
python scripts/analytics/monthly_report.py

# 生成2个月前报告
python scripts/analytics/monthly_report.py 2
```

### 4. 数据看板

```bash
# 生成看板数据
python scripts/analytics/generate_dashboard_data.py
```

然后在浏览器中打开 `site/dashboard/index.html`

### 5. 监控检查

```bash
# 运行监控检查
python scripts/monitoring/monitor_check.py

# 干运行模式
python scripts/monitoring/monitor_check.py --dry-run
```

## 📊 核心指标

| 指标 | 说明 |
|-----|------|
| DAU | 日活跃用户数 |
| 新增用户 | 每日新增注册用户 |
| 付费转化率 | 试用用户→付费用户比例 |
| LTV | 用户生命周期价值 |
| ARPU | 每用户平均收入 |
| MRR | 月度经常性收入 |
| 邮件打开率 | 邮件打开比例 |
| 邮件回复率 | 用户回复比例 |

详细指标定义见 [docs/METRICS.md](docs/METRICS.md)

## ⚙️ 告警配置

编辑 `scripts/monitoring/config.json` 修改告警阈值：

```json
{
  "dau": {"min": 10, "max": 1000},
  "revenue": {"min": 100, "max": 100000},
  "email_open_rate": {"min": 10, "max": 100}
}
```

## 📋 报告输出

报表支持两种格式：
- **JSON**: 机器可读，便于程序处理
- **Markdown**: 人类可读，便于查看分享

## 🔄 定时任务建议

可以使用 cron 设置定时任务：

```bash
# 每天 8:00 运行日报
0 8 * * * cd /path/to/project && python scripts/analytics/daily_report.py

# 每周一 9:00 运行周报
0 9 * * 1 cd /path/to/project && python scripts/analytics/weekly_report.py

# 每月1日 10:00 运行月报
0 10 1 * * cd /path/to/project && python scripts/analytics/monthly_report.py

# 每天 9:00 运行监控检查
0 9 * * * cd /path/to/project && python scripts/monitoring/monitor_check.py
```

## 📝 数据源

数据来自 `data/tender_radar.db` 数据库：

| 表名 | 用途 |
|-----|------|
| tenders | 招标信息 |
| leads | 用户/潜在客户 |
| payments | 支付记录 |
| follow_ups | 邮件发送记录 |

---

*生成时间: 2026-03-15*
