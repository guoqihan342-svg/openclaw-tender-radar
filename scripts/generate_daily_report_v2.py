#!/usr/bin/env python3
"""
招标日报生成器 V2 - 使用数据库真实数据
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = "/home/daministrator/.openclaw/workspace/openclaw-income-factory/data/tender_radar.db"
REPORT_DIR = "/home/daministrator/.openclaw/workspace/openclaw-income-factory/reports/daily"

def get_today_tenders():
    """获取今日招标数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    cursor.execute('''
    SELECT title, budget, region, deadline, purchaser, url, source, category
    FROM tenders
    WHERE created_date = ?
    ORDER BY CAST(budget AS REAL) DESC
    LIMIT 10
    ''', (today,))
    
    tenders = cursor.fetchall()
    conn.close()
    
    return tenders

def get_stats():
    """获取统计数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 今日总数
    cursor.execute('SELECT COUNT(*) FROM tenders WHERE created_date = ?', (today,))
    total_count = cursor.fetchone()[0]
    
    # 总预算
    cursor.execute('SELECT SUM(budget) FROM tenders WHERE created_date = ?', (today,))
    total_budget = cursor.fetchone()[0] or 0
    
    # 地区分布
    cursor.execute('''
    SELECT region, COUNT(*) as count 
    FROM tenders 
    WHERE created_date = ?
    GROUP BY region
    ORDER BY count DESC
    LIMIT 5
    ''', (today,))
    regions = cursor.fetchall()
    
    conn.close()
    
    return {
        'total_count': total_count,
        'total_budget': total_budget,
        'regions': regions
    }

def categorize_tender(title):
    """根据标题分类 - 按优先级匹配，具体领域优先于泛IT"""
    if not title:
        return '其他'

    rules = [
        (['医疗', '医院', '病历', '卫生', '健康', '药品'], '医疗/健康'),
        (['教育', '学校', '校园', '教学', '高校', '大学'], '教育/校园'),
        (['安防', '监控', '视频', '门禁'], '安防/监控'),
        (['环保', '环境', '监测', '生态', '污水', '垃圾'], '环保/监测'),
        (['社区', '街道', '民政', '养老'], '社区/民生'),
        (['交通', '公路', '道路', '桥梁', '地铁', '信号'], '交通/基建'),
        (['农业', '水利', '林业', '渔业'], '农林水利'),
        (['政务', '电子政务', '行政'], '政务/平台'),
        (['网络', '信息化', '数字化', '数据', '云', '平台', '系统', '软件'], 'IT/信息化'),
    ]

    for keywords, category in rules:
        if any(kw in title for kw in keywords):
            return category

    return '其他'

def format_budget(budget):
    """格式化预算显示"""
    if not budget:
        return '未公布'
    
    # 转换为整数
    try:
        budget = int(budget)
    except:
        return str(budget)
    
    if budget >= 100000000:
        return f'{budget/100000000:.1f}亿'
    elif budget >= 10000:
        return f'{budget/10000:.0f}万'
    else:
        return f'{budget:.0f}元'

def generate_daily_report():
    """生成日报"""
    
    tenders = get_today_tenders()
    stats = get_stats()
    
    if not tenders:
        print("⚠️ 今日无数据，请先运行 source_collector.py")
        return None
    
    today_str = datetime.now().strftime('%Y年%m月%d日')
    date_code = datetime.now().strftime('%Y%m%d')
    
    # 分类统计 - 优先使用DB中的category字段，否则从标题推断
    categories = {}
    for tender in tenders:
        # tender[7] = category (from DB), tender[0] = title
        category = tender[7] if len(tender) > 7 and tender[7] else categorize_tender(tender[0])
        categories[category] = categories.get(category, 0) + 1

    # 高价值项目（预算>200万）
    high_value = [t for t in tenders if t[1] and float(t[1]) > 2000000]
    
    report = f"""# 🎯 OpenClaw 招标雷达 | {today_str}

> 每日精选政府采购商机，助你抢占先机

---

## 📊 今日概览

- **精选招标**：{len(tenders)} 条
- **总预算金额**：{format_budget(stats['total_budget'])}
- **覆盖地区**：{len(stats['regions'])} 个省市
- **热门领域**：{', '.join([f"{k}({v})" for k, v in list(categories.items())[:3]])}

---

## 🔥 重点推荐

"""
    
    # 高价值项目
    if high_value:
        report += "### 💰 百万级大单\n\n"
        for tender in high_value[:3]:
            title, budget, region, deadline, purchaser, url, source = tender[:7]
            report += f"""**{title}**
- 💵 预算：{format_budget(budget)}
- 📍 地区：{region or '未注明'}
- ⏰ 截止：{deadline or '未注明'}
- 🏢 采购方：{purchaser or '未注明'}
- 🔗 [查看详情]({url or '#'})

"""
    
    # 全部项目
    report += "---\n\n## 📋 全部招标清单\n\n"
    report += "| 序号 | 项目名称 | 预算 | 地区 | 截止 |\n"
    report += "|------|----------|------|------|------|\n"
    
    for i, tender in enumerate(tenders, 1):
        title, budget, region, deadline, purchaser, url, source = tender[:7]
        short_title = title[:25] + '...' if len(title) > 25 else title
        report += f"| {i} | {short_title} | {format_budget(budget)} | {region or '-'} | {deadline or '-'} |\n"
    
    # 地区分布
    report += """\n---

## 📈 地区分布

"""
    for region, count in stats['regions'][:5]:
        report += f"- {region}：{count} 条\n"
    
    # 分类统计
    report += """\n---

## 🏷️ 分类统计

| 类别 | 数量 | 占比 |
|------|------|------|
"""
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        pct = count / len(tenders) * 100
        report += f"| {category} | {count} | {pct:.0f}% |\n"
    
    # 洞察和订阅
    report += f"""\n---

## 💡 今日洞察

1. **{max(categories, key=categories.get) if categories else '综合'}项目最多**：今日{max(categories.values()) if categories else 0}个相关招标，建议重点关注

2. **预算分布**：{len([t for t in tenders if t[1] and float(t[1]) > 1000000])}个项目预算超百万，占总数的{len([t for t in tenders if t[1] and float(t[1]) > 1000000])/len(tenders)*100:.0f}%

3. **地区热点**：{stats['regions'][0][0] if stats['regions'] else '各地'}项目最多，{stats['regions'][0][1] if stats['regions'] else 0}条招标信息

---

## 🚀 订阅升级

**免费版**：每日3条精选（当前展示{len(tenders)}条样刊）

**标准版 ¥99/月**：
- ✅ 每日10条精选招标
- ✅ 每周深度分析报告  
- ✅ 按地区+行业筛选
- ✅ 邮件+飞书双通道推送

**高级版 ¥299/月**：
- ✅ 每日全量招标（50+条）
- ✅ 定制关键词监控
- ✅ 紧急项目微信提醒
- ✅ API接口访问

👉 **扫码订阅，7天免费试用，不满意全额退款**

---

*本报告由 OpenClaw 招标雷达自动生成*
*数据仅供参考，请以官方公告为准*
*生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    return report

def main():
    print("🚀 生成招标日报 V2...")
    
    # 确保输出目录存在
    os.makedirs(REPORT_DIR, exist_ok=True)
    
    # 生成报告
    report = generate_daily_report()
    
    if not report:
        return
    
    # 保存文件
    date_str = datetime.now().strftime('%Y%m%d')
    filename = f"{REPORT_DIR}/daily_report_{date_str}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 日报已生成: {filename}")
    print(f"📊 今日招标数: {len(get_today_tenders())} 条")
    
    # 显示预览
    print("\n" + "="*50)
    print(report[:800] + "...")
    print("="*50)

if __name__ == "__main__":
    main()
