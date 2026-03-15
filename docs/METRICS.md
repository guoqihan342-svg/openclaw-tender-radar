# 招标雷达 - 核心指标设计

## 1. 概述

本文档定义招标雷达系统的关键业务指标，用于数据分析和监控报表。

---

## 2. 核心指标定义

### 2.1 用户相关指标

| 指标名称 | 英文缩写 | 定义 | 数据来源 |
|---------|---------|------|---------|
| 日活跃用户 | DAU | 每日访问系统的独立用户数（去重） | leads表访问日志 |
| 月活跃用户 | MAU | 每月访问系统的独立用户数 | leads表访问日志 |
| 新增用户 | New Users | 每日/周/月新增的注册用户数 | leads.created_date |
| 总用户数 | Total Users | 系统累计注册用户总数 | leads表 |

### 2.2 转化漏斗指标

| 指标名称 | 英文缩写 | 定义 | 计算公式 |
|---------|---------|------|---------|
| 注册转化率 | Reg Rate | 访客→注册用户的转化比例 | 新增用户 / 访客数 × 100% |
| 试用转化率 | Trial Rate | 注册用户→试用用户的比例 | 开始试用用户 / 注册用户 × 100% |
| 付费转化率 | Pay Rate | 试用用户→付费用户的比例 | 付费用户 / 试用用户 × 100% |
| 总体转化率 | Overall CVR | 访客→付费用户的整体转化 | 付费用户 / 访客数 × 100% |

### 2.3 留存率指标

| 指标名称 | 英文缩写 | 定义 | 计算周期 |
|---------|---------|------|---------|
| 次日留存率 | D1 Retention | 注册后第1天回访的用户比例 | 次日回访用户 / 当日新增用户 |
| 7日留存率 | D7 Retention | 注册后第7天回访的用户比例 | 第7天回访用户 / 当日新增用户 |
| 30日留存率 | D30 Retention | 注册后第30天回访的用户比例 | 第30天回访用户 / 当日新增用户 |

### 2.4 收入相关指标

| 指标名称 | 英文缩写 | 定义 | 计算公式 |
|---------|---------|------|---------|
| 生命周期价值 | LTV | 用户在整个生命周期内贡献的收入 | ARPU × 用户生命周期 |
| 每用户平均收入 | ARPU | 总收入 / 总用户数 | 收入 / 活跃用户数 |
| 付费用户平均收入 | ARPP | 付费用户总收入 / 付费用户数 | 收入 / 付费用户数 |
| 月度经常性收入 | MRR | 每月订阅收入 | 所有付费用户月费总和 |
| 年度经常性收入 | ARR | 年化订阅收入 | MRR × 12 |

### 2.5 招标数据指标

| 指标名称 | 英文缩写 | 定义 | 数据来源 |
|---------|---------|------|---------|
| 招标信息总数 | Total Tenders | 系统累计收录的招标数量 | tenders表 |
| 新增招标数 | New Tenders | 每日新增招标信息数量 | tenders.created_date |
| 招标匹配数 | Matched Tenders | 推送给用户的招标数量 | follow_ups表 |
| 招标打开率 | Open Rate | 用户打开招标通知的比例 | follow_ups.opened |
| 招标回复率 | Reply Rate | 用户回复/感兴趣的比例 | follow_ups.replied |

---

## 3. 指标计算逻辑

### 3.1 DAU 计算

```python
def calculate_dau(date):
    """计算指定日期的日活跃用户数"""
    query = """
        SELECT COUNT(DISTINCT user_id) 
        FROM user_activity_log 
        WHERE DATE(activity_time) = ?
    """
    return execute_query(query, (date,))[0][0]
```

### 3.2 转化率计算

```python
def calculate_conversion_rate(visitors, conversions):
    """计算转化率"""
    if visitors == 0:
        return 0
    return (conversions / visitors) * 100
```

### 3.3 留存率计算

```python
def calculate_retention_rate(date, retention_days):
    """计算留存率"""
    # 获取指定日期新增用户
    new_users = get_new_users(date)
    if not new_users:
        return 0
    
    # 获取第N天回访用户
    returning_users = get_returning_users(date, retention_days)
    
    return (returning_users / new_users) * 100
```

### 3.4 LTV 计算

```python
def calculate_ltv(arpu, avg_lifespan_months):
    """计算用户生命周期价值"""
    return arpu * avg_lifespan_months
```

---

## 4. 指标阈值参考

| 指标 | 优秀 | 良好 | 警告 | 危险 |
|-----|-----|-----|-----|-----|
| DAU增长率 | >10% | 5-10% | 0-5% | <0% |
| 付费转化率 | >15% | 10-15% | 5-10% | <5% |
| 次日留存率 | >60% | 45-60% | 30-45% | <30% |
| 月留存率 | >40% | 25-40% | 15-25% | <15% |
| 邮件打开率 | >30% | 20-30% | 10-20% | <10% |
| 月增长率 | >20% | 10-20% | 5-10% | <5% |

---

## 5. 数据更新频率

| 指标类型 | 更新频率 | 报表类型 |
|---------|---------|---------|
| DAU/MAU | 实时/每日 | 日报 |
| 转化率 | 每日 | 日报/周报 |
| 留存率 | 每日 | 周报 |
| LTV/ARPU | 每日 | 月报 |
| 收入指标 | 每日 | 日报/周报/月报 |
| 招标数据 | 实时 | 日报 |

---

## 6. 数据源映射

| 指标 | 数据库表 | 字段 |
|-----|---------|------|
| 新增用户 | leads | created_date |
| 试用用户 | leads | trial_start_date |
| 付费用户 | payments | status='completed' |
| 收入金额 | payments | amount |
| 活跃用户 | leads/follow_ups | 访问记录 |
| 招标信息 | tenders | created_date |
| 邮件发送 | follow_ups | sent_date |
| 邮件打开 | follow_ups | opened |
| 用户回复 | follow_ups | replied |

---

*文档版本: 1.0*
*最后更新: 2026-03-15*
