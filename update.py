#!/usr/bin/env python3
"""
AI新闻自动更新脚本
每天自动抓取最新AI新闻，生成网站HTML，并发送摘要
"""

import json
import subprocess
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 配置
SITE_DIR = Path("/root/.openclaw/workspace/ai-news-site")
NEWS_LOG = Path("/root/.openclaw/workspace/ai-news-site/news-log.json")

def get_today_date():
    return datetime.now().strftime("%Y年%m月%d日")

def get_iso_date():
    return datetime.now().strftime("%Y-%m-%d")

def search_ai_news():
    """搜索最新AI新闻"""
    # 这里我们会调用 kimi_search 工具，但由于这是Python脚本，
    # 实际执行时会由OpenClaw agent调用
    print(f"[{get_iso_date()}] 开始抓取AI新闻...")
    return []

def generate_news_html(news_items):
    """生成新闻HTML卡片"""
    html = ""
    for item in news_items:
        tag_class = item.get('tag', 'industry')
        tag_name = {
            'breaking': '重磅',
            'industry': '行业', 
            'tech': '技术',
            'policy': '政策',
            'funding': '融资'
        }.get(tag_class, '资讯')
        
        html += f'''
            <article class="news-card">
                <div class="news-tag tag-{tag_class}">{tag_name}</div>
                <h3>{item['title']}</h3>
                <p class="news-date">{item['date']}</p>
                <p class="news-summary">{item['summary']}</p>
            </article>
        '''
    return html

def generate_site(news_items):
    """生成完整网站"""
    news_html = generate_news_html(news_items)
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI前线 - 最新人工智能资讯</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <div class="container">
            <h1>⚡ AI前线</h1>
            <p class="subtitle">每日最新人工智能资讯与动态</p>
            <p class="update-time">最后更新：{get_today_date()}</p>
        </div>
    </header>

    <main class="container">
        <section class="news-grid">
            {news_html}
        </section>
    </main>

    <footer>
        <div class="container">
            <p>AI前线 © 2026 | 每日更新人工智能最新动态</p>
            <p class="footer-note">数据来源：公开网络资讯整理</p>
        </div>
    </footer>

    <script src="app.js"></script>
</body>
</html>
'''
    
    index_path = SITE_DIR / "index.html"
    index_path.write_text(html, encoding='utf-8')
    print(f"网站已生成: {index_path}")

def save_news_log(news_items):
    """保存新闻日志"""
    log_data = {
        "date": get_iso_date(),
        "count": len(news_items),
        "items": news_items
    }
    NEWS_LOG.write_text(json.dumps(log_data, ensure_ascii=False, indent=2), encoding='utf-8')

def main():
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    
    # 这里实际的新闻抓取由OpenClaw agent完成
    # 这个脚本作为骨架，实际内容会被填充
    print("AI新闻自动更新脚本已准备就绪")
    print(f"站点目录: {SITE_DIR}")
    
    # 生成当前日期的占位内容
    today_news = [
        {
            "title": "等待今日新闻抓取...",
            "date": get_today_date(),
            "summary": "新闻正在抓取中，请稍候查看更新内容。",
            "tag": "tech"
        }
    ]
    
    generate_site(today_news)
    save_news_log(today_news)

if __name__ == "__main__":
    main()
