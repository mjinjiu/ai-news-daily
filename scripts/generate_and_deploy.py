#!/usr/bin/env python3
"""
AI前线 - 自动更新流水线
从 data/news_YYYY-MM-DD.json 读取新闻数据，生成 HTML 并部署
"""

import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 路径配置
SITE_ZH = Path("/root/.openclaw/workspace/ai-news-site")
SITE_EN = Path("/root/.openclaw/workspace/ai-news-site-en")
DATA_DIR_ZH = SITE_ZH / "data"
DATA_DIR_EN = SITE_EN / "data"

def load_news(date_str: str):
    """加载指定日期的新闻数据"""
    path = DATA_DIR_ZH / f"news_{date_str}.json"
    if not path.exists():
        print(f"❌ 新闻数据文件不存在: {path}")
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_featured_cards(news_data):
    """生成头条卡片 HTML"""
    featured = news_data.get("featured", [])
    if not featured:
        return ""
    
    cards = []
    for item in featured[:2]:
        card = f'''                            <article class="card featured" data-source-url="{item.get("source_url", "#")}">
                                <div class="card-tag tag-breaking" data-zh="重磅" data-en="Breaking">重磅 Breaking</div>
                                <h2 data-zh="{item["title"]}" data-en="{item.get("title_en", item["title"])}">{item["title"]}</h2>
                                <p class="card-meta">{item.get("date", "")} · {item["source"]}</p>
                                <p class="card-summary" data-zh="{item["summary"]}" data-en="{item.get("summary_en", item["summary"])}">{item["summary"]}</p>
                            </article>'''
        cards.append(card)
    return "\n".join(cards)

def generate_news_list(news_data):
    """生成今日新闻列表 HTML"""
    news = news_data.get("news", [])
    if not news:
        return ""
    
    category_map = {
        "tech": ("tech", "技术", "Tech"),
        "industry": ("industry", "行业", "Industry"),
        "policy": ("policy", "政策", "Policy"),
        "funding": ("funding", "融资", "Funding"),
        "product": ("product", "产品", "Product"),
    }
    
    items = []
    for item in news[:10]:
        cat_class, cat_zh, cat_en = category_map.get(item.get("category", "tech"), ("tech", "技术", "Tech"))
        
        news_item = f'''                                <div class="news-item" data-category="{cat_class}" data-source-url="{item.get("source_url", "#")}">
                                    <div class="news-bar {cat_class}"></div>
                                    <div class="news-body">
                                        <h3 data-zh="{item["title"]}" data-en="{item.get("title_en", item["title"])}">{item["title"]}</h3>
                                        <p class="news-excerpt" data-zh="{item["excerpt"]}" data-en="{item.get("excerpt_en", item["excerpt"])}">{item["excerpt"]}</p>
                                        <div class="news-footer">
                                            <span class="news-tag tag-{cat_class}" data-zh="{cat_zh}" data-en="{cat_en}">{cat_zh} {cat_en}</span>
                                            <span class="news-source">{item["source"]}</span>
                                            <span class="news-date">{item.get("date", "")}</span>
                                        </div>
                                    </div>
                                </div>'''
        items.append(news_item)
    return "\n".join(items)

def generate_week_timeline(news_data):
    """生成本周回顾时间线 HTML"""
    week = news_data.get("week_review", [])
    if not week:
        return ""
    
    day_groups = []
    for day in week[:5]:
        items_html = []
        for li in day.get("items", []):
            dot_class = li.get("category", "tech")
            link = f'''                                        <li><span class="dot {dot_class}"></span><a href="{li.get("url", "#")}" target="_blank" rel="noopener" data-zh="{li["title"]}" data-en="{li.get("title_en", li["title"])}">{li["title"]}</a></li>'''
            items_html.append(link)
        
        if not items_html:
            items_html = ['                                        <li class="empty" data-zh="暂无新闻" data-en="No news">暂无新闻</li>']
        
        day_group = f'''                                <div class="day-group">
                                    <div class="day-header">
                                        <span class="day-name" data-zh="{day["day_name"]}" data-en="{day.get("day_name_en", day["day_name"])}">{day["day_name"]}</span>
                                        <span class="day-date">{day["date"]}</span>
                                        <span class="day-count" data-zh="{day.get("count", "—")} 条" data-en="{day.get("count_en", day.get("count", "—"))} articles">{day.get("count", "—")} 条</span>
                                    </div>
                                    <ul class="day-list">
{chr(10).join(items_html)}
                                    </ul>
                                </div>'''
        day_groups.append(day_group)
    return "\n".join(day_groups)

def generate_hot_topics(news_data):
    """生成本周热榜 HTML"""
    hot = news_data.get("hot_topics", [])
    if not hot:
        return ""
    
    lis = []
    for i, item in enumerate(hot[:8], 1):
        li = f'''                                <li><a href="{item.get("url", "#")}" target="_blank" rel="noopener" data-zh="{item["title"]}" data-en="{item.get("title_en", item["title"])}">{item["title"]}</a></li>'''
        lis.append(li)
    return "\n".join(lis)

def generate_stats(news_data):
    """生成统计速览 HTML"""
    stats = news_data.get("stats", [])
    if not stats:
        return ""
    
    items = []
    for s in stats[:4]:
        item = f'''                                <div class="stat-item"><span class="stat-num">{s["num"]}</span><span class="stat-label" data-zh="{s["label"]}" data-en="{s.get("label_en", s["label"])}">{s["label"]}</span></div>'''
        items.append(item)
    return "\n".join(items)

def update_index_zh(news_data, date_str):
    """更新中文站 index.html"""
    index_path = SITE_ZH / "index.html"
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 更新日期
    content = re.sub(
        r'<p class="update-time"[^>]*>.*?</p>',
        f'<p class="update-time" data-zh="更新于：{date_str}" data-en="Updated: {date_str}">更新于：{date_str}</p>',
        content
    )
    
    # 更新日期badge
    month_day = date_str[5:].replace("-", "月") + "日"
    content = re.sub(
        r'<span class="date-badge"[^>]*>.*?</span>',
        f'<span class="date-badge" data-zh="{month_day}" data-en="{month_day}">{month_day}</span>',
        content
    )
    
    # 更新统计数
    news_count = len(news_data.get("news", []))
    content = re.sub(
        r'<span class="count"[^>]*>.*?</span>',
        f'<span class="count" data-zh="{news_count} 条" data-en="{news_count} articles">{news_count} 条</span>',
        content
    )
    
    # 替换头条区
    featured_html = generate_featured_cards(news_data)
    content = re.sub(
        r'<!-- 头条区 -->\s*<div class="featured-row">.*?</div>\s*<!-- /头条区 -->',
        f'<!-- 头条区 -->\n                        <div class="featured-row">\n{featured_html}\n                        </div>\n                        <!-- /头条区 -->',
        content,
        flags=re.DOTALL
    )
    # 如果上面的正则没匹配到（格式可能不同），尝试直接匹配
    if "<!-- 头条区 -->" not in content and featured_html:
        content = re.sub(
            r'(<div class="featured-row">)(.*?)(</div>)',
            f'\1\n{featured_html}\n                        \3',
            content,
            count=1,
            flags=re.DOTALL
        )
    
    # 替换新闻列表
    news_html = generate_news_list(news_data)
    # 找到 news-list 容器并替换内容
    pattern = r'(<div class="news-list">)(.*?)(</div>\s*</div>\s*<!-- 信息流广告位 -->)'
    replacement = f'\1\n{news_html}\n                            \3'
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # 替换本周回顾
    week_html = generate_week_timeline(news_data)
    pattern = r'(<div class="week-timeline">)(.*?)(</div>\s*</div>\s*<!-- 统计速览 -->)'
    replacement = f'\1\n{week_html}\n                            \3'
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # 替换热榜
    hot_html = generate_hot_topics(news_data)
    pattern = r'(<ol class="hot-list">)(.*?)(</ol>)'
    replacement = f'\1\n{hot_html}\n                            \3'
    content = re.sub(pattern, replacement, content, count=1, flags=re.DOTALL)
    
    # 替换统计
    stats_html = generate_stats(news_data)
    pattern = r'(<div class="stats-row">)(.*?)(</div>)'
    replacement = f'\1\n{stats_html}\n                            \3'
    content = re.sub(pattern, replacement, content, count=1, flags=re.DOTALL)
    
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ 中文站已更新: {index_path}")
    return True

def update_index_en(news_data, date_str):
    """更新英文站 index.html"""
    index_path = SITE_EN / "index.html"
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 更新日期
    content = re.sub(
        r'<p class="update-time"[^>]*>.*?</p>',
        f'<p class="update-time" data-zh="更新于：{date_str}" data-en="Updated: {date_str}">Updated: {date_str}</p>',
        content
    )
    
    month_day_en = date_str[5:]
    content = re.sub(
        r'<span class="date-badge"[^>]*>.*?</span>',
        f'<span class="date-badge">{month_day_en}</span>',
        content
    )
    
    news_count = len(news_data.get("news", []))
    content = re.sub(
        r'<span class="count"[^>]*>.*?</span>',
        f'<span class="count">{news_count} articles</span>',
        content
    )
    
    # 替换头条（英文优先）
    featured = news_data.get("featured", [])
    cards = []
    for item in featured[:2]:
        title = item.get("title_en", item["title"])
        summary = item.get("summary_en", item["summary"])
        card = f'''                            <article class="card featured" data-source-url="{item.get("source_url", "#")}">
                                <div class="card-tag tag-breaking">Breaking</div>
                                <h2>{title}</h2>
                                <p class="card-meta">{item.get("date", "")} · {item["source"]}</p>
                                <p class="card-summary">{summary}</p>
                            </article>'''
        cards.append(card)
    featured_html = "\n".join(cards)
    
    content = re.sub(
        r'(<div class="featured-row">)(.*?)(</div>)',
        f'\1\n{featured_html}\n                        \3',
        content,
        count=1,
        flags=re.DOTALL
    )
    
    # 替换新闻列表（英文）
    news = news_data.get("news", [])
    items = []
    for item in news[:10]:
        cat_class = item.get("category", "tech")
        title = item.get("title_en", item["title"])
        excerpt = item.get("excerpt_en", item["excerpt"])
        cat_en = {"tech": "Tech", "industry": "Industry", "policy": "Policy", "funding": "Funding", "product": "Product"}.get(cat_class, "Tech")
        
        news_item = f'''                                <div class="news-item" data-category="{cat_class}" data-source-url="{item.get("source_url", "#")}">
                                    <div class="news-bar {cat_class}"></div>
                                    <div class="news-body">
                                        <h3>{title}</h3>
                                        <p class="news-excerpt">{excerpt}</p>
                                        <div class="news-footer">
                                            <span class="news-tag tag-{cat_class}">{cat_en}</span>
                                            <span class="news-source">{item["source"]}</span>
                                            <span class="news-date">{item.get("date", "")}</span>
                                        </div>
                                    </div>
                                </div>'''
        items.append(news_item)
    news_html = "\n".join(items)
    
    pattern = r'(<div class="news-list">)(.*?)(</div>\s*</div>\s*<!-- 信息流广告位 -->)'
    content = re.sub(pattern, f'\1\n{news_html}\n                            \3', content, flags=re.DOTALL)
    
    # 替换本周回顾
    week = news_data.get("week_review", [])
    day_groups = []
    for day in week[:5]:
        items_html = []
        for li in day.get("items", []):
            dot_class = li.get("category", "tech")
            title = li.get("title_en", li["title"])
            link = f'''                                        <li><span class="dot {dot_class}"></span><a href="{li.get("url", "#")}" target="_blank" rel="noopener">{title}</a></li>'''
            items_html.append(link)
        if not items_html:
            items_html = ['                                        <li class="empty">No news</li>']
        
        day_group = f'''                                <div class="day-group">
                                    <div class="day-header">
                                        <span class="day-name">{day.get("day_name_en", day["day_name"])}</span>
                                        <span class="day-date">{day["date"]}</span>
                                        <span class="day-count">{day.get("count_en", day.get("count", "—"))} articles</span>
                                    </div>
                                    <ul class="day-list">
{chr(10).join(items_html)}
                                    </ul>
                                </div>'''
        day_groups.append(day_group)
    week_html = "\n".join(day_groups)
    
    pattern = r'(<div class="week-timeline">)(.*?)(</div>\s*</div>\s*<!-- 统计速览 -->)'
    content = re.sub(pattern, f'\1\n{week_html}\n                            \3', content, flags=re.DOTALL)
    
    # 替换热榜
    hot = news_data.get("hot_topics", [])
    lis = []
    for item in hot[:8]:
        title = item.get("title_en", item["title"])
        li = f'''                                <li><a href="{item.get("url", "#")}" target="_blank" rel="noopener">{title}</a></li>'''
        lis.append(li)
    hot_html = "\n".join(lis)
    
    pattern = r'(<ol class="hot-list">)(.*?)(</ol>)'
    content = re.sub(pattern, f'\1\n{hot_html}\n                            \3', content, count=1, flags=re.DOTALL)
    
    # 替换统计
    stats = news_data.get("stats", [])
    stat_items = []
    for s in stats[:4]:
        label = s.get("label_en", s["label"])
        stat_items.append(f'''                                <div class="stat-item"><span class="stat-num">{s["num"]}</span><span class="stat-label">{label}</span></div>''')
    stats_html = "\n".join(stat_items)
    
    pattern = r'(<div class="stats-row">)(.*?)(</div>)'
    content = re.sub(pattern, f'\1\n{stats_html}\n                            \3', content, count=1, flags=re.DOTALL)
    
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ 英文站已更新: {index_path}")
    return True

def deploy_to_github(site_dir, repo_url, commit_msg):
    """部署到 GitHub Pages"""
    try:
        subprocess.run(["git", "-C", str(site_dir), "add", "."], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(site_dir), "commit", "-m", commit_msg], check=False, capture_output=True)
        result = subprocess.run(["git", "-C", str(site_dir), "push", "origin", "main"], 
                                capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print(f"✅ 部署成功: {repo_url}")
            return True
        else:
            print(f"⚠️ 部署返回: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 部署失败: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        date_str = datetime.now().strftime("%Y-%m-%d")
    else:
        date_str = sys.argv[1]
    
    print(f"🚀 AI前线自动更新流水线启动")
    print(f"📅 目标日期: {date_str}")
    print("=" * 50)
    
    # 1. 加载新闻数据
    news_data = load_news(date_str)
    if not news_data:
        print("❌ 没有找到新闻数据，退出")
        print(f"💡 请先在 {DATA_DIR_ZH}/news_{date_str}.json 放入新闻数据")
        sys.exit(1)
    
    print(f"✅ 加载新闻数据: {len(news_data.get('news', []))} 条新闻, {len(news_data.get('featured', []))} 条头条")
    
    # 2. 更新中文站
    if update_index_zh(news_data, date_str):
        print("✅ 中文站 HTML 生成完成")
    
    # 3. 更新英文站
    if update_index_en(news_data, date_str):
        print("✅ 英文站 HTML 生成完成")
    
    # 4. 复制数据到英文站
    shutil.copy(DATA_DIR_ZH / f"news_{date_str}.json", DATA_DIR_EN / f"news_{date_str}.json")
    
    print("\n" + "=" * 50)
    print("📦 内容生成完毕，等待部署...")
    print("=" * 50)

if __name__ == "__main__":
    main()
