#!/bin/bash
# 自动提交网站到搜索引擎
# 运行此脚本加速收录

echo "🚀 提交网站到搜索引擎..."

# 提交到百度
echo "提交到百度..."
curl -X POST "http://data.zz.baidu.com/urls?site=https://openclaw-tender-radar.surge.sh&token=YOUR_BAIDU_TOKEN" \
  -H "Content-Type: text/plain" \
  --data-binary @sitemap.xml

# 提交到Bing
echo "提交到Bing..."
curl -X POST "https://ssl.bing.com/webmaster/api.svc/json/SubmitUrlbatch?apikey=YOUR_BING_API_KEY" \
  -H "Content-Type: application/json" \
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
