# OpenClaw 招标雷达

## 项目简介

OpenClaw 招标雷达是一个全自动的政府采购/招投标信息监控与分发系统。

通过自动化抓取公开招标信息，AI智能筛选和摘要，为中小企业销售团队提供精准的商业机会情报。

## 核心价值

- **省时**：自动监控数百个政府采购网站，无需人工浏览
- **精准**：AI智能筛选，只推送高价值机会
- **及时**：每日早8点推送，抢先竞争对手
- **便宜**：99元/月，远低于人工监控成本

## 项目结构

```
openclaw-income-factory/
├── config/          # 配置文件
├── data/            # 数据目录
│   ├── raw/         # 原始抓取数据
│   ├── processed/   # 清洗后数据
│   ├── export/      # 导出文件
│   └── backup/      # 数据备份
├── logs/            # 运行日志
├── reports/         # 生成报告
│   ├── daily/       # 日报
│   └── weekly/      # 周报
├── skills/          # 技能模块
├── scripts/         # 执行脚本
├── templates/       # 报告模板
└── docs/            # 文档
```

## 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python scripts/init_db.py
```

### 2. 配置

复制 `config/config.example.yaml` 到 `config/config.yaml`，填写：
- Serper API Key（搜索用）
- 飞书机器人 webhook（分发用）

### 3. 运行

```bash
# 手动运行一次
python scripts/daily_run.py

# 或配置定时任务（cron）
# 每天 08:00 运行
0 8 * * * cd /path/to/openclaw-income-factory && python scripts/daily_run.py
```

## 订阅套餐

| 版本 | 内容 | 价格 |
|------|------|------|
| 免费版 | 每日3条精选 | ¥0 |
| 标准版 | 每日10条+周报 | ¥99/月 |
| 高级版 | 全量+定制关键词+API | ¥299/月 |

## 数据来源

- 中国政府采购网 (ccpgp.gov.cn)
- 中国招标投标公共服务平台
- 各省市政府采购网

所有数据均为公开信息，合法合规抓取。

## 技术栈

- Python 3.12+
- SQLite
- Minimax API (AI生成)
- Serper API (搜索增强)
- 飞书 Bot (分发)

## 许可证

MIT License - 仅供学习参考

## 联系方式

如有问题，请通过飞书联系。
