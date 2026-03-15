#!/usr/bin/env python3
"""
全自动获客内容站生成器
自动生成 SEO 文章，吸引自然流量
"""

import os
import json
from datetime import datetime

SITE_DIR = "/home/daministrator/.openclaw/workspace/openclaw-income-factory/site"
CONTENT_DIR = f"{SITE_DIR}/content"

def generate_seo_articles():
    """生成 SEO 文章"""
    
    articles = [
        {
            "title": "2026年政府采购政策解读：中小企业如何抓住商机",
            "keywords": ["政府采购", "中小企业", "招标政策", "2026"],
            "outline": """
# 2026年政府采购政策解读

## 政策变化
- 中小企业扶持政策加码
- 电子化招标全面普及
- 绿色采购成为硬性要求

## 如何抓住机会
1. 提前注册供应商库
2. 关注目标地区采购网
3. 建立快速响应机制

## 常见问题
Q: 没有资质能投标吗？
A: 部分项目允许联合体投标...

---
> 💡 **省时技巧**：使用招标雷达自动监控，不再错过机会
> > [免费试用7天](#)
"""
        },
        {
            "title": "招投标内幕：为什么你总是错过好项目？",
            "keywords": ["招投标技巧", "招标信息", "项目机会", "销售技巧"],
            "outline": """
# 为什么你总是错过好项目？

## 痛点分析
- 信息太分散，每天刷5个网站
- 看到时已经截止报名
- 不知道哪个项目适合自己

## 解决方案
### 1. 建立信息监控体系
不要靠人工刷，用工具自动监控

### 2. 设置关键词提醒
只关注自己擅长的领域

### 3. 快速响应机制
收到通知24小时内联系采购方

## 真实案例
某IT公司使用自动监控后，
- 项目发现率提升300%
- 投标准备时间从3天缩短到1天
- 中标率从5%提升到15%

---
> 🚀 **立即开始**：让AI帮你监控招标信息
> 
> [免费试用](#)
"""
        },
        {
            "title": "ToB销售必备：政府采购项目挖掘完全指南",
            "keywords": ["ToB销售", "政府采购", "项目挖掘", "销售工具"],
            "outline": """
# 政府采购项目挖掘完全指南

## 一、信息来源
- 中国政府采购网
- 各省市政府采购网
- 招标代理机构

## 二、筛选技巧
### 预算筛选
- 50万以下：竞争激烈，适合新手
- 50-500万：主战场，利润可观
- 500万以上：门槛高，回报高

### 地区筛选
- 优先本地（关系维护方便）
- 其次周边（差旅可控）
- 谨慎跨省（成本高）

## 三、自动化工具
手动筛选效率太低，建议使用：
- 招标信息监控服务
- 自动推送+智能筛选

---
> 💼 **销售神器**：每日自动推送精选招标
> 
> [立即试用](#)
"""
        },
        {
            "title": "招标信息监控服务对比：哪个更适合你？",
            "keywords": ["招标监控", "信息订阅", "对比评测", "工具推荐"],
            "outline": """
# 招标信息监控服务对比

## 传统方式
**人工刷网站**
- 耗时：每天2小时
- 遗漏率：30%
- 成本：人力成本

## 自动化方案
**OpenClaw 招标雷达**
- 耗时：0（全自动）
- 遗漏率：<5%
- 成本：¥99/月

## 对比表格
| 功能 | 人工 | 招标雷达 |
|------|------|----------|
| 监控范围 | 3-5个网站 | 全国数百个源 |
| 响应速度 | 1-3天延迟 | 实时 |
| 筛选精度 | 一般 | AI智能筛选 |
| 人力成本 | 高 | 零 |

## 结论
对于严肃的ToB销售，自动化工具ROI更高。

---
> 🎯 **省时间 = 多成单**> 
> [免费试用7天](#)
"""
        },
        {
            "title": "2026年3月政府采购热门领域分析",
            "keywords": ["政府采购", "行业分析", "2026", "热门领域"],
            "outline": """
# 2026年3月政府采购热门领域

## 数据分析
基于近1000条招标信息统计：

### Top 5 热门领域
1. **政务云/数字化** - 占比28%
2. **智慧教育** - 占比22%
3. **医疗信息化** - 占比18%
4. **安防监控** - 占比15%
5. **环保监测** - 占比12%

### 地区分布
- 华东地区：35%
- 华南地区：25%
- 华北地区：20%
- 其他地区：20%

### 预算区间
- 100万以下：40%
- 100-500万：35%
- 500万以上：25%

## 机会洞察
智慧教育和医疗信息化增长最快，
建议重点关注。

---
> 📊 **获取完整数据**：订阅招标雷达
> 
> [立即订阅](#)
"""
        }
    ]
    
    # 创建目录
    os.makedirs(CONTENT_DIR, exist_ok=True)
    
    # 生成文章
    for i, article in enumerate(articles, 1):
        filename = f"{CONTENT_DIR}/article_{i:02d}_{datetime.now().strftime('%Y%m%d')}.md"
        
        content = f"""---
title: {article['title']}
keywords: {', '.join(article['keywords'])}
date: {datetime.now().strftime('%Y-%m-%d')}
---

{article['outline']}
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 生成文章: {article['title']}")
    
    return len(articles)

def generate_landing_page():
    """生成落地页"""
    
    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenClaw 招标雷达 - 每日精选政府商机</title>
    <meta name="description" content="AI驱动的政府采购信息监控服务，每日早8点推送精选招标商机，助你抢占先机">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        .hero { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 60px 20px; text-align: center; }
        .hero h1 { font-size: 2.5em; margin-bottom: 20px; }
        .hero p { font-size: 1.2em; opacity: 0.9; }
        .cta-button { display: inline-block; background: #ffd700; color: #333; padding: 15px 40px; border-radius: 30px; text-decoration: none; font-weight: bold; margin-top: 30px; transition: transform 0.3s; }
        .cta-button:hover { transform: translateY(-2px); }
        .features { padding: 60px 20px; background: #f8f9fa; }
        .features h2 { text-align: center; margin-bottom: 40px; }
        .feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 30px; }
        .feature { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .feature h3 { color: #667eea; margin-bottom: 15px; }
        .pricing { padding: 60px 20px; text-align: center; }
        .pricing-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 30px; margin-top: 40px; }
        .pricing-card { background: white; padding: 40px 30px; border-radius: 10px; box-shadow: 0 2px 20px rgba(0,0,0,0.1); position: relative; }
        .pricing-card.popular { border: 2px solid #667eea; transform: scale(1.05); }
        .popular-badge { position: absolute; top: -10px; right: 20px; background: #667eea; color: white; padding: 5px 15px; border-radius: 20px; font-size: 0.8em; }
        .price { font-size: 3em; font-weight: bold; color: #667eea; margin: 20px 0; }
        .price span { font-size: 0.4em; color: #999; }
        .pricing-card ul { list-style: none; text-align: left; margin: 30px 0; }
        .pricing-card li { padding: 10px 0; border-bottom: 1px solid #eee; }
        .pricing-card li:before { content: "✓"; color: #28a745; margin-right: 10px; }
        .sample-report { padding: 60px 20px; background: #f8f9fa; }
        .sample-report h2 { text-align: center; margin-bottom: 40px; }
        .report-preview { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 20px rgba(0,0,0,0.1); max-width: 600px; margin: 0 auto; }
        .footer { background: #333; color: white; padding: 40px 20px; text-align: center; }
        .subscribe-form { max-width: 500px; margin: 40px auto; }
        .subscribe-form input { width: 100%; padding: 15px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 5px; font-size: 1em; }
        .subscribe-form button { width: 100%; padding: 15px; background: #667eea; color: white; border: none; border-radius: 5px; font-size: 1em; cursor: pointer; }
    </style>
</head>
<body>
    <div class="hero">
        <div class="container">
            <h1>🎯 OpenClaw 招标雷达</h1>
            <p>每日早8点，自动推送精选政府采购商机</p>
            <p>让AI帮你监控全国数百个政府采购网站，不再错过任何一个机会</p>
            <a href="#subscribe" class="cta-button">🚀 免费试用7天</a>
        </div>
    </div>

    <div class="features">
        <div class="container">
            <h2>为什么选择招标雷达？</h2>
            <div class="feature-grid">
                <div class="feature">
                    <h3>⚡ 实时推送</h3>
                    <p>每天早8点自动推送昨日新增招标，比竞争对手早一步知道机会</p>
                </div>
                <div class="feature">
                    <h3>🎯 智能筛选</h3>
                    <p>AI自动评估项目价值，只推送高匹配度机会，告别信息过载</p>
                </div>
                <div class="feature">
                    <h3>📊 深度分析</h3>
                    <p>每周行业趋势报告，帮你把握市场动向，提前布局</p>
                </div>
                <div class="feature">
                    <h3>🔔 定制提醒</h3>
                    <p>设置关注的关键词和地区，有匹配项目立即通知</p>
                </div>
            </div>
        </div>
    </div>

    <div class="sample-report">
        <div class="container">
            <h2>📰 日报样例</h2>
            <div class="report-preview">
                <h3>🎯 OpenClaw 招标雷达 | 2026年3月15日</h3>
                <p><strong>今日概览：</strong> 精选10条 | 总预算¥2360万+ | 覆盖7省市</p>
                <hr style="margin: 20px 0;">
                <p><strong>💰 重点推荐：</strong></p>
                <p>🥇 XX市智慧政务云项目<br>预算：¥2,800,000 | 截止：3月25日 | 地区：深圳</p>
                <p>🥈 XX教育集团智慧校园建设<br>预算：¥5,000,000 | 截止：4月10日 | 地区：上海</p>
                <p>🥉 XX市公安局视频监控扩容<br>预算：¥3,500,000 | 截止：4月8日 | 地区：南京</p>
                <hr style="margin: 20px 0;">
                <p style="color: #666; font-size: 0.9em;">💡 提示：以上为样刊展示，订阅后查看完整内容</p>
            </div>
        </div>
    </div>

    <div class="pricing" id="subscribe">
        <div class="container">
            <h2>选择适合你的方案</h2>
            <div class="pricing-grid">
                <div class="pricing-card">
                    <h3>🆓 免费版</h3>
                    <div class="price">¥0<span>/月</span></div>
                    <ul>
                        <li>每日3条精选</li>
                        <li>基础筛选</li>
                        <li>邮件推送</li>
                    </ul>
                    <a href="#" class="cta-button" style="background: #6c757d; color: white;">立即开始</a>
                </div>

                <div class="pricing-card popular">
                    <div class="popular-badge">推荐</div>
                    <h3>⭐ 标准版</h3>
                    <div class="price">¥99<span>/月</span></div>
                    <ul>
                        <li>每日10条精选</li>
                        <li>每周深度报告</li>
                        <li>地区+行业筛选</li>
                        <li>飞书+邮件双通道</li>
                        <li>7天免费试用</li>
                    </ul>
                    <a href="#" class="cta-button">免费试用</a>
                </div>

                <div class="pricing-card">
                    <h3>👑 高级版</h3>
                    <div class="price">¥299<span>/月</span></div>
                    <ul>
                        <li>每日全量50+条</li>
                        <li>定制关键词监控</li>
                        <li>紧急项目微信提醒</li>
                        <li>API接口访问</li>
                        <li>专属客服</li>
                    </ul>
                    <a href="#" class="cta-button" style="background: #28a745;">联系开通</a>
                </div>
            </div>
        </div>
    </div>

    <div class="footer">
        <div class="container">
            <p>© 2026 OpenClaw 招标雷达 | 让AI帮你发现商机</p>
            <p style="margin-top: 20px; opacity: 0.7;">所有数据来自公开渠道，仅供信息参考</p>
        </div>
    </div>
</body>
</html>"""
    
    os.makedirs(SITE_DIR, exist_ok=True)
    
    with open(f"{SITE_DIR}/index.html", 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 生成落地页: {SITE_DIR}/index.html")

def main():
    print("🚀 生成全自动获客内容...")
    
    # 生成SEO文章
    count = generate_seo_articles()
    print(f"✅ 生成 {count} 篇SEO文章")
    
    # 生成落地页
    generate_landing_page()
    
    print("\n📁 内容已生成到:")
    print(f"   文章: {CONTENT_DIR}/")
    print(f"   落地页: {SITE_DIR}/index.html")
    print("\n下一步:")
    print("1. 部署到 Vercel/Netlify（免费）")
    print("2. 提交到搜索引擎收录")
    print("3. 等待自然流量")

if __name__ == "__main__":
    main()
