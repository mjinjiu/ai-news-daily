import json
import datetime

# 读取旧格式的 content.json（真实数据）
with open('/root/.openclaw/workspace/ai-news-site/data/content.json', 'r', encoding='utf-8') as f:
    old = json.load(f)

# 读取现有的 news.json 获取 meta 信息（日期等）
with open('/root/.openclaw/workspace/ai-news-site/data/news.json', 'r', encoding='utf-8') as f:
    news_meta = json.load(f)

today = news_meta.get('meta', {}).get('date', datetime.datetime.now().strftime('%Y-%m-%d'))
updated_at = news_meta.get('meta', {}).get('updatedAt', datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00'))
week_range = news_meta.get('meta', {}).get('weekRange', '5.12 — 5.18')

# 构建新格式 current.json
current = {
    "meta": {
        "date": today,
        "updatedAt": updated_at,
        "total": len(old.get('todayNews', {}).get('items', [])),
        "weekRange": week_range,
        "daysCount": news_meta.get('meta', {}).get('daysCount', 1)
    },
    "breaking": [],
    "daily": [],
    "weekly": [],
    "stats": [],
    "hotList": [],
    "tags": [],
    "sources": [],
    "archiveDates": news_meta.get('archiveDates', [today])
}

# 转换 featured -> breaking
for i, item in enumerate(old.get('featured', [])):
    current['breaking'].append({
        "id": f"news-{today}-{i+1:03d}",
        "title_zh": item.get('title', ''),
        "title_en": item.get('titleEn', ''),
        "summary_zh": item.get('summary', ''),
        "summary_en": item.get('summaryEn', ''),
        "date": item.get('date', '').replace('2026-', '').replace('-', ''),
        "source": item.get('source', 'AI前线'),
        "category": "breaking",
        "url": item.get('url', 'https://github.com/mjinjiu/ai-news-daily')
    })

# 转换 todayNews.items -> daily
for i, item in enumerate(old.get('todayNews', {}).get('items', [])):
    # 处理日期格式
    raw_date = item.get('date', '04-27')
    if '-' in raw_date:
        parts = raw_date.split('-')
        if len(parts) == 2:
            display_date = f"{parts[0]}-{parts[1]}"
        else:
            display_date = raw_date
    else:
        display_date = raw_date
    
    current['daily'].append({
        "id": f"news-{today}-{i+1:03d}",
        "title_zh": item.get('title', ''),
        "title_en": item.get('titleEn', ''),
        "excerpt_zh": item.get('excerpt', ''),
        "excerpt_en": item.get('excerptEn', ''),
        "date": display_date,
        "source": item.get('source', 'AI前线'),
        "category": item.get('category', 'tech'),
        "url": item.get('url', 'https://github.com/mjinjiu/ai-news-daily')
    })
    if item.get('source'):
        current['sources'].append(item['source'])

# 去重 sources
current['sources'] = list(set(current['sources']))

# 生成 stats
total = len(current['daily'])
current['stats'] = [
    {
        "num": str(total),
        "label_zh": "今日新闻",
        "label_en": "News Today"
    }
]

# 生成 hotList（来源频次）
from collections import Counter
source_counts = Counter([item['source'] for item in current['daily']])
for idx, (source, count) in enumerate(source_counts.most_common(5)):
    current['hotList'].append({
        "rank": idx + 1,
        "title_zh": f"{source} 报道 {count} 条",
        "title_en": f"{count} from {source}",
        "heat": min(count * 15, 100)
    })

# 生成 tags
category_tags = {
    'tech': ['技术', 'AI模型', '开源'],
    'industry': ['产业', '融资', '大厂'],
    'policy': ['政策', '监管', '合规'],
    'finance': ['金融', '市场', '股价']
}

all_tags = []
for item in current['daily']:
    cat = item.get('category', 'tech')
    all_tags.extend(category_tags.get(cat, ['AI前沿']))

# 去重并限制数量
current['tags'] = list(dict.fromkeys(all_tags))[:8]

# 写入 current.json
with open('/root/.openclaw/workspace/ai-news-site/data/news/current.json', 'w', encoding='utf-8') as f:
    json.dump(current, f, ensure_ascii=False, indent=2)

# 同时同步到 news.json（保持兼容）
with open('/root/.openclaw/workspace/ai-news-site/data/news.json', 'w', encoding='utf-8') as f:
    json.dump(current, f, ensure_ascii=False, indent=2)

print(f"✅ 已同步 {total} 条新闻到 current.json 和 news.json")
print(f"   Breaking: {len(current['breaking'])} 条")
print(f"   Daily: {len(current['daily'])} 条")
print(f"   Sources: {len(current['sources'])} 个")
print(f"   Tags: {len(current['tags'])} 个")
