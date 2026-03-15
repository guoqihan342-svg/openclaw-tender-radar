-- OpenClaw 招标雷达 - 重构后数据库Schema
-- 阶段1：核心闭环完善

-- 1. 来源追踪表
CREATE TABLE IF NOT EXISTS source_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT NOT NULL,  -- 来源名称：gov_cn, medical, education
    source_url TEXT,
    run_date DATE DEFAULT CURRENT_DATE,
    status TEXT DEFAULT 'running',  -- running/success/failed
    items_count INTEGER DEFAULT 0,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. 原始抓取数据（未清洗）
CREATE TABLE IF NOT EXISTS raw_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_run_id INTEGER,
    external_id TEXT,  -- 外部ID（如招标编号）
    raw_title TEXT,
    raw_content TEXT,
    raw_budget TEXT,  -- 原始预算字符串
    raw_region TEXT,
    raw_deadline TEXT,
    raw_purchaser TEXT,
    source_url TEXT,
    crawled_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_run_id) REFERENCES source_runs(id)
);

-- 3. 标准化后的招标数据（清洗后）
CREATE TABLE IF NOT EXISTS tenders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_item_id INTEGER,
    
    -- 标准化字段（事实层，不由AI生成）
    title TEXT NOT NULL,
    budget_min INTEGER,
    budget_max INTEGER,
    region TEXT,
    deadline DATE,
    purchaser TEXT,
    industry TEXT,  -- IT/医疗/教育等
    category TEXT,  -- 货物/服务/工程
    
    -- AI生成字段（润色层）
    ai_summary TEXT,  -- AI摘要
    ai_recommendation TEXT,  -- 推荐理由
    ai_score INTEGER,  -- AI评分0-100
    
    -- 元数据
    source_url TEXT,
    status TEXT DEFAULT 'active',  -- active/ended/cancelled
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (raw_item_id) REFERENCES raw_items(id)
);

-- 4. 去重记录
CREATE TABLE IF NOT EXISTS dedupe_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tender_id INTEGER,
    duplicate_of_id INTEGER,  -- 指向重复的主记录
    similarity_score REAL,  -- 相似度0-1
    deduped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tender_id) REFERENCES tenders(id),
    FOREIGN KEY (duplicate_of_id) REFERENCES tenders(id)
);

-- 5. 订阅用户（扩展版）
CREATE TABLE IF NOT EXISTS subscribers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    name TEXT,
    phone TEXT,
    feishu_id TEXT,  -- 飞书用户ID
    
    -- 订阅配置
    plan TEXT DEFAULT 'free',  -- free/standard/premium
    status TEXT DEFAULT 'active',  -- active/paused/cancelled
    
    -- 用户偏好（用于个性化推送）
    preferred_regions TEXT,  -- JSON数组：["北京", "上海"]
    preferred_industries TEXT,  -- JSON数组：["IT", "医疗"]
    min_budget INTEGER DEFAULT 0,  -- 最低预算关注
    
    -- 时间追踪
    subscribe_date DATE DEFAULT CURRENT_DATE,
    trial_end_date DATE,  -- 试用期结束
    paid_until DATE,  -- 付费到期日
    last_delivery_date DATE,  -- 上次发送日期
    
    -- 统计数据
    total_deliveries INTEGER DEFAULT 0,
    total_opens INTEGER DEFAULT 0,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 6. 支付记录（半自动化状态机）
CREATE TABLE IF NOT EXISTS payment_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subscriber_id INTEGER,
    
    -- 支付信息
    amount INTEGER,  -- 金额（分）
    plan TEXT,  -- 购买的套餐
    payment_method TEXT,  -- wechat/alipay
    
    -- 状态机
    status TEXT DEFAULT 'pending',  -- pending/confirmed/active/expired/refunded
    
    -- 凭证
    payment_proof TEXT,  -- 付款截图路径
    transaction_id TEXT,  -- 商户订单号
    
    -- 时间线
    paid_at DATETIME,  -- 用户声称付款时间
    confirmed_at DATETIME,  -- 人工确认时间
    activated_at DATETIME,  -- 服务开通时间
    expires_at DATETIME,  -- 服务到期时间
    
    -- 操作记录
    confirmed_by TEXT,  -- 确认人
    notes TEXT,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subscriber_id) REFERENCES subscribers(id)
);

-- 7. 推送任务队列
CREATE TABLE IF NOT EXISTS delivery_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subscriber_id INTEGER,
    
    -- 任务内容
    job_type TEXT DEFAULT 'daily',  -- daily/weekly/welcome/reminder
    content_summary TEXT,  -- 内容摘要
    
    -- 状态
    status TEXT DEFAULT 'pending',  -- pending/sent/failed/retrying
    
    -- 渠道
    channel TEXT DEFAULT 'feishu',  -- feishu/email
    
    -- 时间追踪
    scheduled_at DATETIME,  -- 计划发送时间
    sent_at DATETIME,  -- 实际发送时间
    
    -- 结果
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subscriber_id) REFERENCES subscribers(id)
);

-- 8. 推送结果记录
CREATE TABLE IF NOT EXISTS delivery_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    delivery_job_id INTEGER,
    subscriber_id INTEGER,
    
    -- 发送内容
    content TEXT,
    
    -- 结果
    status TEXT,  -- success/failed
    error_message TEXT,
    
    -- 用户互动（如有追踪）
    opened_at DATETIME,
    clicked_at DATETIME,
    
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (delivery_job_id) REFERENCES delivery_jobs(id),
    FOREIGN KEY (subscriber_id) REFERENCES subscribers(id)
);

-- 9. 审计日志（完整版）
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_type TEXT NOT NULL,  -- 操作类型
    entity_type TEXT,  -- 操作对象类型
    entity_id INTEGER,  -- 操作对象ID
    user_id TEXT,  -- 操作用户
    old_value TEXT,  -- 旧值
    new_value TEXT,  -- 新值
    ip_address TEXT,
    result TEXT,  -- success/failed
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 索引优化
CREATE INDEX IF NOT EXISTS idx_tenders_deadline ON tenders(deadline);
CREATE INDEX IF NOT EXISTS idx_tenders_region ON tenders(region);
CREATE INDEX IF NOT EXISTS idx_tenders_industry ON tenders(industry);
CREATE INDEX IF NOT EXISTS idx_tenders_status ON tenders(status);
CREATE INDEX IF NOT EXISTS idx_subscribers_email ON subscribers(email);
CREATE INDEX IF NOT EXISTS idx_subscribers_status ON subscribers(status);
CREATE INDEX IF NOT EXISTS idx_payment_events_status ON payment_events(status);
CREATE INDEX IF NOT EXISTS idx_delivery_jobs_status ON delivery_jobs(status);
CREATE INDEX IF NOT EXISTS idx_delivery_jobs_scheduled ON delivery_jobs(scheduled_at);
