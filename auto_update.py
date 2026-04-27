#!/usr/bin/env python3
"""
AI前线 - 自动新闻更新系统
调用 kimi_search 获取最新AI新闻，生成网站HTML
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

SITE_DIR = Path("/root/.openclaw/workspace/ai-news-site")
INDEX_FILE = SITE_DIR / "index.html"

def get_today():
    return datetime.now().strftime("%Y年%m月%d日")

def generate_html(news_list):
    cards = ""
    for news in news_list:
        tag_map = {
            "重磅": "breaking",
            "行业": "industry", 
            "技术": "tech",
            "政策": "policy",
            "融资": "funding"
        }
        tag_class = tag_map.get(news.get("tag", "行业"), "industry")
        tag_name = news.get("tag", "行业")
        
        cards += f'''
            <article class="news-card">
                <div class="news-tag tag-{tag_class}">{tag_name}</div>
                <h3>{news["title"]}</h3>
                <p class="news-date">{news.get("date", get_today())}</p>
                <p class="news-summary">{news["summary"]}</p>
            </article>
        '''
    
    return f'''<!DOCTYPE html>
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
            <p class="update-time">最后更新：{get_today()}</p>
        </div>
    </header>
    <main class="container">
        <section class="news-grid">
            {cards}
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
</html>'''

def main():
    # 默认新闻（等待实际抓取）
    default_news = [
        {"title": "网站初始化完成", "date": get_today(), "summary": "AI前线已启动，等待每日自动更新...", "tag": "技术"}
    ]
    
    html = generate_html(default_news)
    INDEX_FILE.write_text(html, encoding='utf-8')
    print(f"[{datetime.now()}] 网站已更新")

if __name__ == "__main__":
    main()
