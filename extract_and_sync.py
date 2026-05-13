#!/usr/bin/env python3
import json
import datetime
from collections import Counter

# 读取 content.json，只提取有效的 featured 和 todayNews 部分
with open('/root/.openclaw/workspace/ai-news-site/data/content.json', 'r', encoding='utf-8') as f:
    raw = f.read()

# 手动解析：找到 featured 数组和 todayNews 对象
# 策略：逐行扫描，提取需要的字段

# 先找到 featured 和 todayNews 的起始位置
featured_start = raw.find('"featured": [')
today_news_start = raw.find('"todayNews": {')

# 提取 todayNews 的 items
items = []
# 查找 todayNews 里的 items 数组
items_start = raw.find('"items": [', today_news_start)
if items_start > 0:
    # 找到 items 数组的结束位置（匹配的 ]）
    bracket_count = 0
    in_array = False
    for i in range(items_start, len(raw)):
        if raw[i] == '[':
            if not in_array:
                in_array = True
                bracket_count = 1
            else:
                bracket_count += 1
        elif raw[i] == ']':
            bracket_count -= 1
            if bracket_count == 0:
                items_end = i + 1
                break
    
    # 提取 items 数组文本
    items_text = raw[items_start:items_end]
    # 替换中文引号为书名号
    items_text = items_text.replace('"', '「').replace('"', '」')
    
    try:
        items_data = json.loads(items_text)
        items = items_data.get('items', [])
    except:
        print("Warning: Could not parse items array")

# 提取 featured 数组
featured = []
if featured_start > 0:
    # 找到 featured 数组的结束
    bracket_count = 0
    in_array = False
    for i in range(featured_start, len(raw)):
        if raw[i] == '[':
            if not in_array:
                in_array = True
                bracket_count = 1
            else:
                bracket_count += 1
        elif raw[i] == ']':
            bracket_count -= 1
            if bracket_count == 0:
                featured_end = i + 1
                break
    
    featured_text = raw[featured_start:featured_end]
    featured_text = featured_text.replace('"', '「').replace('"', '」')
    
    try:
        featured_data = json.loads(featured_text)
        featured = featured_data.get('featured', [])
    except:
        print("Warning: Could not parse featured array")

# 如果都失败了，使用 update_news_data.py 里的硬编码数据
if len(items) == 0 and len(featured) == 0:
    print("从 content.json 提取失败，使用备用数据")
    # 这里可以嵌入 update_news_data.py 的数据
    # 但目前先尝试用更简单的方法

# 构建 current.json
today = datetime.datetime.now().strftime('%Y-%m-%d')

current = {
    "meta": {
        "date": today,
        "updatedAt": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00'),
        "total": len(items),
        "weekRange": "5.12 — 5.18",
        "daysCount": 1
    },
    "breaking": [],
    "daily": [],
    "weekly": [],
    "stats": [],
    "hotList": [],
    "tags": [],
    "sources": [],
    "archiveDates": [today]
}

# 转换 featured -> breaking
for i, item in enumerate(featured):
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

# 转换 items -> daily
for i, item in enumerate(items):
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

# 去重
current['sources'] = list(set(current['sources']))

# stats
total = len(current['daily'])
current['stats'] = [{"num": str(total), "label_zh": "今日新闻", "label_en": "News Today"}]

# hotList
source_counts = Counter([item['source'] for item in current['daily']])
for idx, (source, count) in enumerate(source_counts.most_common(5)):
    current['hotList'].append({
        "rank": idx + 1,
        "title_zh": f"{source} 报道 {count} 条",
        "title_en": f"{count} from {source}",
        "heat": min(count * 15, 100)
    })

# tags
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

current['tags'] = list(dict.fromkeys(all_tags))[:8]

# 写入文件
with open('/root/.openclaw/workspace/ai-news-site/data/news/current.json', 'w', encoding='utf-8') as f:
    json.dump(current, f, ensure_ascii=False, indent=2)

with open('/root/.openclaw/workspace/ai-news-site/data/news.json', 'w', encoding='utf-8') as f:
    json.dump(current, f, ensure_ascii=False, indent=2)

print(f"✅ 已生成 current.json: {total} 条新闻")
print(f"   Breaking: {len(current['breaking'])} 条")
print(f"   Daily: {len(current['daily'])} 条")
print(f"   Sources: {len(current['sources'])} 个")
