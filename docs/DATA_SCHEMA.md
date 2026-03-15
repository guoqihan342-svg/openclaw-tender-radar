# OpenClaw 招标雷达 - 数据Schema设计

## 数据库选型

使用 **SQLite**，原因：
- 零配置，开箱即用
- 单文件，备份简单
- Python原生支持
- MVP阶段足够，后期可迁移到PostgreSQL

## 表结构

### 1. raw_items - 原始抓取数据

```sql
CREATE TABLE raw_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_url TEXT NOT NULL,           -- 来源URL
    source_name TEXT NOT NULL,          -- 来源名称（如：中国政府采购网）
    external_id TEXT,                   -- 外部ID（如招标编号）
    title TEXT NOT NULL,                -- 标题
    content TEXT,                       -- 正文内容
    publish_date DATE,                  -- 发布日期
    deadline DATE,                      -- 投标截止日期
    budget_min INTEGER,                 -- 预算下限（元）
    budget_max INTEGER,                 -- 预算上限（元）
    region TEXT,                        -- 地区（省/市）
    industry TEXT,                      -- 行业分类
    purchaser TEXT,                     -- 采购单位
    contact_info TEXT,                  -- 联系方式
    raw_html TEXT,                      -- 原始HTML（调试用）
    crawl_time DATETIME DEFAULT CURRENT_TIMESTAMP,  -- 抓取时间
    status INTEGER DEFAULT 0            -- 0=未处理, 1=已处理, -1=异常
);

CREATE INDEX idx_raw_items_date ON raw_items(publish_date);
CREATE INDEX idx_raw_items_status ON raw_items(status);
CREATE INDEX idx_raw_items_source ON raw_items(source_name);
```

### 2. signals - 清洗后的信号

```sql
CREATE TABLE signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_item_id INTEGER,                -- 关联raw_items
    title TEXT NOT NULL,                -- 清洗后的标题
    summary TEXT,                       -- AI生成的摘要
    category TEXT,                      -- 分类（IT/工程/服务/其他）
    subcategory TEXT,                   -- 子分类
    budget_amount INTEGER,              -- 标准化后的预算
    region TEXT,                        -- 地区
    deadline DATE,                      -- 截止日期
    urgency_score REAL,                 -- 紧急度评分（0-100）
    value_score REAL,                   -- 价值评分（0-100）
    match_score REAL,                   -- 匹配度评分（0-100）
    keywords TEXT,                      -- 关键词标签（逗号分隔）
    ai_analysis TEXT,                   -- AI分析结论
    clean_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (raw_item_id) REFERENCES raw_items(id)
);

CREATE INDEX idx_signals_category ON signals(category);
CREATE INDEX idx_signals_scores ON signals(value_score, match_score);
CREATE INDEX idx_signals_date ON signals(clean_time);
```

### 3. leads_or_opportunities - 高价值机会

```sql
CREATE TABLE leads_or_opportunities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    signal_id INTEGER,                  -- 关联signals
    title TEXT NOT NULL,
    summary TEXT,                       -- 推荐理由
    priority INTEGER DEFAULT 3,         -- 优先级 1=高, 2=中, 3=低
    budget_display TEXT,                -- 显示用预算（如："50-100万"）
    deadline_display TEXT,              -- 显示用截止日期
    region_display TEXT,                -- 显示用地区
    industry_display TEXT,              -- 显示用行业
    ai_recommendation TEXT,             -- AI推荐理由
    selected_for_daily BOOLEAN DEFAULT 0,  -- 是否入选日报
    selected_for_weekly BOOLEAN DEFAULT 0, -- 是否入选周报
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (signal_id) REFERENCES signals(id)
);

CREATE INDEX idx_leads_priority ON leads_or_opportunities(priority);
CREATE INDEX idx_leads_selected ON leads_or_opportunities(selected_for_daily);
```

### 4. subscribers - 订阅用户

```sql
CREATE TABLE subscribers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,                  -- 邮箱
    phone TEXT,                         -- 手机号
    name TEXT,                          -- 姓名
    company TEXT,                       -- 公司
    plan_type TEXT DEFAULT 'free',      -- free/standard/premium
    status TEXT DEFAULT 'active',       -- active/paused/cancelled
    keywords TEXT,                      -- 关注的关键词（高级版）
    regions TEXT,                       -- 关注的地区（高级版）
    categories TEXT,                    -- 关注的分类（高级版）
    subscribe_date DATE,                -- 订阅日期
    expire_date DATE,                   -- 到期日期
    payment_status TEXT DEFAULT 'pending', -- pending/paid/failed
    feishu_user_id TEXT,                -- 飞书用户ID
    notes TEXT,                         -- 备注
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_subscribers_plan ON subscribers(plan_type);
CREATE INDEX idx_subscribers_status ON subscribers(status);
```

### 5. deliveries - 分发记录

```sql
CREATE TABLE deliveries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subscriber_id INTEGER,              -- 关联subscribers
    report_type TEXT,                   -- daily/weekly/special
    report_date DATE,                   -- 报告日期
    report_path TEXT,                   -- 报告文件路径
    send_channel TEXT,                  -- 发送渠道（email/feishu）
    send_status TEXT DEFAULT 'pending', -- pending/sent/failed
    send_time DATETIME,                 -- 发送时间
    open_status BOOLEAN DEFAULT 0,      -- 是否打开
    open_time DATETIME,                 -- 打开时间
    error_message TEXT,                 -- 错误信息
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subscriber_id) REFERENCES subscribers(id)
);

CREATE INDEX idx_deliveries_date ON deliveries(report_date);
CREATE INDEX idx_deliveries_status ON deliveries(send_status);
```

### 6. payments_placeholder - 支付记录（预留）

```sql
CREATE TABLE payments_placeholder (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subscriber_id INTEGER,
    amount REAL,                        -- 金额
    currency TEXT DEFAULT 'CNY',        -- 币种
    payment_method TEXT,                -- 支付方式
    payment_status TEXT DEFAULT 'pending', -- pending/completed/failed/refunded
    transaction_id TEXT,                -- 交易号
    paid_time DATETIME,                 -- 支付时间
    expire_time DATETIME,               -- 服务到期时间
    notes TEXT,
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subscriber_id) REFERENCES subscribers(id)
);
```

### 7. audit_logs - 审计日志

```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_type TEXT NOT NULL,          -- 操作类型
    action_detail TEXT,                 -- 操作详情
    entity_type TEXT,                   -- 操作对象类型
    entity_id INTEGER,                  -- 操作对象ID
    user_id TEXT,                       -- 操作用户（如适用）
    ip_address TEXT,                    -- IP地址
    result TEXT,                        -- 结果（success/failed）
    error_message TEXT,                 -- 错误信息
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_time ON audit_logs(created_time);
CREATE INDEX idx_audit_logs_action ON audit_logs(action_type);
```

## 数据流

```
raw_items (原始抓取)
    ↓ 清洗去重
signals (清洗后信号)
    ↓ 打分筛选
leads_or_opportunities (高价值机会)
    ↓ 生成报告
reports (日报/周报)
    ↓ 分发
deliveries (分发记录)
```

## 去重策略

使用 `external_id` + `source_name` 联合唯一索引：
- 同一来源的同一招标，只保留一条
- 不同来源的同一招标，AI判断后合并

## 备份策略

- 每日导出：`data/backup/backup_YYYYMMDD.db`
- 保留30天
- 关键表单独导出CSV

