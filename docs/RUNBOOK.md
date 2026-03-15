# OpenClaw 招标雷达 - 运行手册 (RUNBOOK)

## 日常运行

### 手动运行日报生成

```bash
cd /home/daministrator/.openclaw/workspace/openclaw-income-factory
python scripts/daily_run.py
```

### 查看运行日志

```bash
# 查看最新日志
tail -f logs/daily_$(date +%Y%m%d).log

# 查看所有日志
ls -la logs/
```

### 检查数据库状态

```bash
# 查看今日抓取数量
sqlite3 data/tender_radar.db "SELECT COUNT(*) FROM raw_items WHERE date(crawl_time) = date('now');"

# 查看今日生成的高价值机会
sqlite3 data/tender_radar.db "SELECT COUNT(*) FROM leads_or_opportunities WHERE date(created_time) = date('now');"
```

## 故障处理

### 场景1：数据抓取失败

**现象**：日志显示抓取返回0条数据

**处理步骤**：
1. 检查网络连接
2. 检查目标网站是否可用
3. 查看 `logs/scraper_*.log` 详细错误
4. 如网站结构变化，更新 `skills/source_collector.py`

### 场景2：AI生成失败

**现象**：summary或analysis字段为空

**处理步骤**：
1. 检查MiniMax API额度
2. 查看 `logs/ai_*.log`
3. 如API失败，启用备用文案模板

### 场景3：日报未生成

**现象**：reports/daily/目录下没有今日文件

**处理步骤**：
1. 检查 `logs/daily_*.log` 错误信息
2. 手动运行调试：`python scripts/daily_run.py --debug`
3. 检查磁盘空间

### 场景4：分发失败

**现象**：deliveries表中send_status为failed

**处理步骤**：
1. 检查飞书机器人配置
2. 检查网络连接
3. 手动重发：`python scripts/resend.py --date=YYYYMMDD`

## 定时任务配置

### 使用Cron（推荐）

```bash
# 编辑crontab
crontab -e

# 添加以下行
# 每天早8点运行日报
0 8 * * * cd /home/daministrator/.openclaw/workspace/openclaw-income-factory && python scripts/daily_run.py >> logs/cron.log 2>&1

# 每周一早9点运行周报
0 9 * * 1 cd /home/daministrator/.openclaw/workspace/openclaw-income-factory && python scripts/weekly_run.py >> logs/cron.log 2>&1

# 每天凌晨3点备份数据
0 3 * * * cd /home/daministrator/.openclaw/workspace/openclaw-income-factory && python scripts/backup.py >> logs/backup.log 2>&1
```

## 数据维护

### 清理旧数据

```bash
# 清理30天前的原始HTML（保留结构化数据）
python scripts/cleanup.py --keep-days=30 --target=raw_html

# 清理90天前的审计日志
python scripts/cleanup.py --keep-days=90 --target=audit_logs
```

### 数据库优化

```bash
# 每周运行一次
sqlite3 data/tender_radar.db "VACUUM;"
```

## 新用户订阅

### 添加免费版用户

```bash
python scripts/add_subscriber.py \
  --email=user@example.com \
  --name=张三 \
  --plan=free \
  --channel=feishu \
  --feishu-id=ou_xxx
```

### 升级付费用户

```bash
python scripts/upgrade_subscriber.py \
  --email=user@example.com \
  --plan=standard \
  --amount=99 \
  --months=1
```

## 报告查看

### 查看今日日报

```bash
cat reports/daily/daily_report_$(date +%Y%m%d).md
```

### 导出特定日期范围的数据

```bash
python scripts/export.py \
  --start-date=2026-03-01 \
  --end-date=2026-03-15 \
  --format=csv \
  --output=export/march_data.csv
```

## 监控指标

### 每日检查清单

- [ ] 今日抓取数量 > 100条
- [ ] 今日生成leads > 10条
- [ ] 日报文件已生成
- [ ] 分发成功率 > 95%
- [ ] 无ERROR级别日志

### 关键指标查询

```sql
-- 本周抓取趋势
SELECT date(crawl_time) as day, COUNT(*) as count 
FROM raw_items 
WHERE crawl_time >= date('now', '-7 days') 
GROUP BY day;

-- 各分类占比
SELECT category, COUNT(*) as count 
FROM signals 
WHERE clean_time >= date('now', '-30 days') 
GROUP BY category;

-- 用户订阅分布
SELECT plan_type, COUNT(*) as count 
FROM subscribers 
WHERE status = 'active' 
GROUP BY plan_type;
```

## 安全注意事项

1. **不要提交config.yaml到Git**
2. **定期更换API Key**
3. **审计日志定期审查**
4. **数据库备份加密存储**

## 升级维护

### 更新Skill

```bash
# 备份当前版本
cp skills/source_collector.py skills/source_collector.py.bak

# 更新代码
# 测试
python scripts/test_skill.py --skill=source_collector
```

### 数据库迁移

如需迁移到PostgreSQL：
```bash
python scripts/migrate_to_postgres.py --source=data/tender_radar.db --target=postgresql://...
```

