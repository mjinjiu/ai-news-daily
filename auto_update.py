#!/usr/bin/env python3
"""
AI前线 v2.2 - 自动新闻更新系统
信源：Reuters, Bloomberg, 芯智讯, Sina Tech, Gov.cn, DoNews, Tech Daily, 极客公园

用法：由Agent每天早上调用 kimi_search 搜索新闻后，直接编辑 index.html
此脚本保留作为自动触发入口
"""

from datetime import datetime

SOURCES = [
    "Reuters AI artificial intelligence",
    "Bloomberg AI technology",
    "芯智讯 AI 人工智能 芯片",
    "Sina Tech AI人工智能",
    "Gov.cn 人工智能 政策",
    "DoNews AI人工智能",
    "Tech Daily AI人工智能",
    "极客公园 AI 人工智能 科技"
]

# 自动更新由Agent通过 kimi_search + 直接编辑 index.html 完成
# 此脚本作为cron触发入口

if __name__ == "__main__":
    print(f"[{datetime.now()}] AI前线 v2.2 自动更新系统就绪")
    print("信源:", ", ".join(SOURCES))
    print("请使用 Agent 的 kimi_search 工具搜索新闻后直接更新 index.html")
