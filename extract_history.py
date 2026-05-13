#!/usr/bin/env python3
import json
import datetime
from collections import Counter

# 读取 content.json 的前半部分（干净数据）
with open('/root/.openclaw/workspace/ai-news-site/data/content.json', 'r', encoding='utf-8') as f:
    raw = f.read()

# 找到 articles 部分的开始位置，截断
articles_pos = raw.find('"articles":')
if articles_pos > 0:
    # 截断到 articles 之前
    clean_json = raw[:articles_pos].rstrip().rstrip(',') + '\n}'
else:
    clean_json = raw

# 修复可能的中文引号（在截断后的内容里）
clean_json = clean_json.replace('"', '「').replace('"', '」')

try:
    data = json.loads(clean_json)
    print('✅ 提取成功！')
    print(f'更新日期: {data["meta"]["updateDate"]}')
    print(f'featured: {len(data["featured"])}')
    print(f'todayNews.items: {len(data["todayNews"]["items"])}')
except Exception as e:
    print(f'❌ 失败: {e}')
    exit(1)

# 转换为新的 current.json 格式
date_str = data['meta']['updateDate']  # 2026-04-27

# breaking
breaking = []
for i, item in enumerate(data.get('featured', [])):
    breaking.append({
        "id": f"news-{date_str}-{i+1:03d}",
        "title_zh": item.get('title', ''),
        "title_en": item.get('titleEn', ''),
        "summary_zh": item.get('summary', ''),
        "summary_en": item.get('summaryEn', ''),
        "date": item.get('date', '').replace('2026-', '').replace('-', ''),
        "source": item.get('source', 'AI前线'),
        "category": "breaking",
        "url": item.get('url', 'https://github.com/mjinjiu/ai-news-daily')
    })

# daily
daily = []
for i, item in enumerate(data.get('todayNews', {}).get('items', [])):
    raw_date = item.get('date', '04-27')
    if '-' in raw_date:
        parts = raw_date.split('-')
        if len(parts) == 2:
            display_date = f"{parts[0]}-{parts[1]}"
        else:
            display_date = raw_date
    else:
        display_date = raw_date
    
    daily.append({
        "id": f"news-{date_str}-{i+1:03d}",
        "title_zh": item.get('title', ''),
        "title_en": item.get('titleEn', ''),
        "excerpt_zh": item.get('excerpt', ''),
        "excerpt_en": item.get('excerptEn', ''),
        "date": display_date,
        "source": item.get('source', 'AI前线'),
        "category": item.get('category', 'tech'),
        "url": item.get('url', 'https://github.com/mjinjiu/ai-news-daily')
    })

# 构建历史归档文件
archive = {
    "meta": {
        "date": date_str,
        "updatedAt": f"{date_str}T08:00:00+08:00",
        "total": len(daily),
        "weekRange": "4.27 — 4.27",
        "daysCount": 1
    },
    "breaking": breaking,
    "daily": daily,
    "weekly": [],
    "stats": [{"num": str(len(daily)), "label_zh": "今日新闻", "label_en": "News Today"}],
    "hotList": [],
    "tags": [],
    "sources": list(set([item["source"] for item in daily])),
    "archiveDates": [date_str]
}

# 生成 hotList
source_counts = Counter([item['source'] for item in daily])
for idx, (source, count) in enumerate(source_counts.most_common(5)):
    archive['hotList'].append({
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
for item in daily:
    cat = item.get('category', 'tech')
    all_tags.extend(category_tags.get(cat, ['AI前沿']))
archive['tags'] = list(dict.fromkeys(all_tags))[:8]

# 保存历史文件
with open(f'/root/.openclaw/workspace/ai-news-site/data/news/{date_str}.json', 'w', encoding='utf-8') as f:
    json.dump(archive, f, ensure_ascii=False, indent=2)

print(f'✅ 历史归档已保存: data/news/{date_str}.json')
print(f'   Breaking: {len(breaking)} 条')
print(f'   Daily: {len(daily)} 条')
