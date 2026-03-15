#!/usr/bin/env python3
"""
全自动获客渠道 - Phase 1 立即启动
无需人工发文案，全自动引流
"""

import os
import sqlite3
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

PROJECT_DIR = "/home/daministrator/.openclaw/workspace/openclaw-income-factory"
DB_PATH = f"{PROJECT_DIR}/data/tender_radar.db"
SITE_DIR = f"{PROJECT_DIR}/site"

class Phase1AutoAcquisition:
    """Phase 1: 今天就能跑的全自动获客"""
    
    def __init__(self):
        os.makedirs(f"{SITE_DIR}/feed", exist_ok=True)
    
    def generate_rss_feed(self):
        """
        渠道1: RSS Feed 自动生成
        被动获客 - 用户通过RSS阅读器订阅
        全自动，无需人工
        """
        print("📡 生成RSS订阅源...")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 获取最近10条招标
        cursor.execute('''
        SELECT title, budget, region, deadline, purchaser, url, created_date
        FROM tenders
        ORDER BY created_date DESC, budget DESC
        LIMIT 10
        ''')
        
        tenders = cursor.fetchall()
        conn.close()
        
        # 生成RSS XML
        rss = ET.Element('rss', version='2.0')
        channel = ET.SubElement(rss, 'channel')
        
        # 频道信息
        ET.SubElement(channel, 'title').text = 'OpenClaw 招标雷达 - 每日政府采购商机'
        ET.SubElement(channel, 'link').text = 'https://openclaw-tender-radar.surge.sh'
        ET.SubElement(channel, 'description').text = '每日精选政府采购招标信息，助你抢占商机'
        ET.SubElement(channel, 'language').text = 'zh-CN'
        ET.SubElement(channel, 'lastBuildDate').text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # 添加条目
        for tender in tenders:
            title, budget, region, deadline, purchaser, url, created_date = tender
            
            item = ET.SubElement(channel, 'item')
            ET.SubElement(item, 'title').text = title
            
            budget_str = f'{int(budget)/10000:.0f}万' if budget else '未公布'
            description = f"""
            预算: {budget_str}
            地区: {region or '未注明'}
            截止: {deadline or '未注明'}
            采购方: {purchaser or '未注明'}
            
            💡 订阅完整版获取更多商机: https://openclaw-tender-radar.surge.sh/payment/
            """
            ET.SubElement(item, 'description').text = description
            ET.SubElement(item, 'link').text = url or 'https://openclaw-tender-radar.surge.sh'
            ET.SubElement(item, 'pubDate').text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
            ET.SubElement(item, 'category').text = '政府采购'
        
        # 美化XML
        xml_str = minidom.parseString(ET.tostring(rss)).toprettyxml(indent="  ")
        
        # 保存
        feed_path = f"{SITE_DIR}/feed.xml"
        with open(feed_path, 'w', encoding='utf-8') as f:
            f.write(xml_str)
        
        print(f"✅ RSS Feed 已生成: {feed_path}")
        print(f"   订阅链接: https://your-domain/feed.xml")
        return feed_path
    
    def generate_json_feed(self):
        """
        渠道2: JSON Feed (现代化API)
        供开发者/第三方平台调用
        """
        print("📡 生成JSON Feed...")
        
        import json
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT title, budget, region, deadline, purchaser, url, created_date
        FROM tenders
        ORDER BY created_date DESC
        LIMIT 20
        ''')
        
        tenders = cursor.fetchall()
        conn.close()
        
        feed = {
            'version': 'https://jsonfeed.org/version/1.1',
            'title': 'OpenClaw 招标雷达',
            'description': '每日精选政府采购招标信息',
            'home_page_url': 'https://openclaw-tender-radar.surge.sh',
            'feed_url': 'https://openclaw-tender-radar.surge.sh/feed.json',
            'items': []
        }
        
        for tender in tenders:
            title, budget, region, deadline, purchaser, url, created_date = tender
            
            budget_str = f'{int(budget)/10000:.0f}万' if budget else '未公布'
            
            feed['items'].append({
                'id': f"tender-{hash(title) % 10000000}",
                'title': title,
                'content_text': f"预算: {budget_str}, 地区: {region}, 截止: {deadline}",
                'url': url or 'https://openclaw-tender-radar.surge.sh',
                'date_published': created_date,
                'tags': ['政府采购', '招标', region[:2] if region else '全国']
            })
        
        # 保存
        json_path = f"{SITE_DIR}/feed.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(feed, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON Feed 已生成: {json_path}")
        return json_path
    
    def generate_sitemap(self):
        """
        渠道3: SEO优化 - 自动生成Sitemap
        提升搜索引擎收录
        """
        print("🗺️ 生成网站地图...")
        
        sitemap = ET.Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
        
        # 首页
        url = ET.SubElement(sitemap, 'url')
        ET.SubElement(url, 'loc').text = 'https://openclaw-tender-radar.surge.sh/'
        ET.SubElement(url, 'changefreq').text = 'daily'
        ET.SubElement(url, 'priority').text = '1.0'
        
        # 收款页
        url = ET.SubElement(sitemap, 'url')
        ET.SubElement(url, 'loc').text = 'https://openclaw-tender-radar.surge.sh/payment/'
        ET.SubElement(url, 'changefreq').text = 'weekly'
        ET.SubElement(url, 'priority').text = '0.9'
        
        # 文章页
        blog_dir = f"{SITE_DIR}/content/blog"
        if os.path.exists(blog_dir):
            for article in os.listdir(blog_dir):
                if article.endswith('.md'):
                    url = ET.SubElement(sitemap, 'url')
                    ET.SubElement(url, 'loc').text = f'https://openclaw-tender-radar.surge.sh/blog/{article.replace(".md", ".html")}'
                    ET.SubElement(url, 'changefreq').text = 'weekly'
                    ET.SubElement(url, 'priority').text = '0.7'
        
        # 保存
        xml_str = minidom.parseString(ET.tostring(sitemap)).toprettyxml(indent="  ")
        sitemap_path = f"{SITE_DIR}/sitemap.xml"
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            f.write(xml_str)
        
        print(f"✅ Sitemap 已生成: {sitemap_path}")
        return sitemap_path
    
    def generate_robots_txt(self):
        """
        生成 robots.txt
        引导搜索引擎爬虫
        """
        print("🤖 生成 robots.txt...")
        
        content = """User-agent: *
Allow: /
Allow: /blog/
Allow: /payment/
Allow: /feed.xml
Allow: /feed.json
Allow: /sitemap.xml

Sitemap: https://openclaw-tender-radar.surge.sh/sitemap.xml

# 搜索引擎收录引导
# 百度: https://ziyuan.baidu.com/linksubmit
# Google: https://search.google.com/search-console
# Bing: https://www.bing.com/webmasters
"""
        
        robots_path = f"{SITE_DIR}/robots.txt"
        with open(robots_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ robots.txt 已生成: {robots_path}")
        return robots_path
    
    def generate_auto_submit_script(self):
        """
        自动生成搜索引擎提交脚本
        帮助快速被收录
        """
        print("📝 生成搜索引擎提交脚本...")
        
        script = '''#!/bin/bash
# 自动提交网站到搜索引擎
# 运行此脚本加速收录

echo "🚀 提交网站到搜索引擎..."

# 提交到百度
echo "提交到百度..."
curl -X POST "http://data.zz.baidu.com/urls?site=https://openclaw-tender-radar.surge.sh&token=YOUR_BAIDU_TOKEN" \\
  -H "Content-Type: text/plain" \\
  --data-binary @sitemap.xml

# 提交到Bing
echo "提交到Bing..."
curl -X POST "https://ssl.bing.com/webmaster/api.svc/json/SubmitUrlbatch?apikey=YOUR_BING_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "siteUrl": "https://openclaw-tender-radar.surge.sh",
    "urlList": ["https://openclaw-tender-radar.surge.sh/"]
  }'

echo "✅ 提交完成"
echo ""
echo "手动提交地址:"
echo "  百度: https://ziyuan.baidu.com/linksubmit"
echo "  Google: https://search.google.com/search-console"
echo "  Bing: https://www.bing.com/webmasters"
'''
        
        script_path = f"{PROJECT_DIR}/scripts/submit_to_search_engines.sh"
        with open(script_path, 'w') as f:
            f.write(script)
        os.chmod(script_path, 0o755)
        
        print(f"✅ 提交脚本已生成: {script_path}")
        return script_path
    
    def run_all(self):
        """运行所有Phase 1获客渠道"""
        print("="*60)
        print("🚀 启动 Phase 1 全自动获客渠道")
        print("="*60)
        print()
        
        results = {
            'rss_feed': self.generate_rss_feed(),
            'json_feed': self.generate_json_feed(),
            'sitemap': self.generate_sitemap(),
            'robots': self.generate_robots_txt(),
            'submit_script': self.generate_auto_submit_script()
        }
        
        print()
        print("="*60)
        print("✅ Phase 1 获客渠道全部就绪")
        print("="*60)
        print()
        print("🎯 获客效果预期:")
        print("   1. RSS Feed: 被动订阅，技术用户群体")
        print("   2. JSON Feed: 开发者/API用户")
        print("   3. SEO优化: 1-3个月后自然搜索流量")
        print()
        print("📋 下一步:")
        print("   1. 部署网站后，RSS/Feed自动可用")
        print("   2. 手动提交网站到搜索引擎加速收录")
        print("   3. 在相关技术社区分享RSS订阅链接")
        print()
        
        return results

def main():
    engine = Phase1AutoAcquisition()
    return engine.run_all()

if __name__ == "__main__":
    main()
