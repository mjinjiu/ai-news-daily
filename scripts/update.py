#!/usr/bin/env python3
"""
AI前线 — 每周归档制自动更新脚本 v5 (RSS抓取版)

不再依赖 KIMI_API_KEY，改用 RSS 源抓取真实新闻。
"""

import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import requests

# ========== 配置 ==========
ROOT = Path(__file__).parent.parent
NEWS_DIR = ROOT / "data" / "news"
INDEX_FILE = NEWS_DIR / "index.json"
CURRENT_FILE = NEWS_DIR / "current.json"
LEGACY_FILE = ROOT / "data" / "news.json"

# RSS 源配置
RSS_SOURCES = [
    {
        "name": "机器之心",
        "url": "https://www.jiqizhixin.com/rss",
        "category": "tech",
    },
    {
        "name": "量子位",
        "url": "https://www.qbitai.com/feed/",
        "category": "tech",
    },
    {
        "name": "36氪",
        "url": "https://36kr.com/feed",
        "category": "industry",
    },
]

# ========== 工具函数 ==========
def get_today() -> datetime:
    return datetime.now()


def get_today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def get_today_display() -> str:
    return datetime.now().strftime("%m-%d")


def get_week_start(today: Optional[datetime] = None) -> str:
    if today is None:
        today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    return monday.strftime("%Y-%m-%d")


def get_week_end(today: Optional[datetime] = None) -> str:
    if today is None:
        today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return sunday.strftime("%Y-%m-%d")


def get_week_label(today: Optional[datetime] = None) -> str:
    if today is None:
        today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return f"{monday.month}.{monday.day:02d} — {sunday.month}.{sunday.day:02d}"


def is_sunday(today: Optional[datetime] = None) -> bool:
    if today is None:
        today = datetime.now()
    return today.weekday() == 6


def save_json(data: dict, filepath: Path) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 已保存 {filepath}")


def load_json(filepath: Path) -> Optional[dict]:
    if not filepath.exists():
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ 读取失败 {filepath}: {e}")
        return None


def clean_sources(sources: list) -> list:
    all_sources = []
    seen = set()
    for src in sources:
        parts = [p.strip() for p in src.split("/")]
        for part in parts:
            if part and part not in seen:
                seen.add(part)
                all_sources.append(part)
    return sorted(all_sources)


# ========== current.json 管理 ==========
def load_current() -> dict:
    data = load_json(CURRENT_FILE)
    if data:
        return data
    today = get_today()
    return {
        "meta": {
            "weekStart": get_week_start(today),
            "weekEnd": get_week_end(today),
            "weekLabel": get_week_label(today),
            "total": 0,
            "updatedAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
        },
        "breaking": [],
        "daily": [],
        "sources": []
    }


def save_current(data: dict) -> None:
    save_json(data, CURRENT_FILE)
    save_json(data, LEGACY_FILE)


def append_news_to_current(current: dict, new_data: dict) -> dict:
    today = get_today()
    current["meta"]["weekStart"] = get_week_start(today)
    current["meta"]["weekEnd"] = get_week_end(today)
    current["meta"]["weekLabel"] = get_week_label(today)
    current["meta"]["updatedAt"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    
    seen_ids = set()
    for item in current.get("breaking", []):
        if item.get("id"):
            seen_ids.add(item["id"])
    for item in current.get("daily", []):
        if item.get("id"):
            seen_ids.add(item["id"])
    
    for item in new_data.get("breaking", []):
        if item.get("id") and item["id"] not in seen_ids:
            seen_ids.add(item["id"])
            current["breaking"].append(item)
    
    for item in new_data.get("daily", []):
        if item.get("id") and item["id"] not in seen_ids:
            seen_ids.add(item["id"])
            current["daily"].append(item)
    
    all_sources = set(current.get("sources", []))
    all_sources.update(new_data.get("sources", []))
    current["sources"] = clean_sources(list(all_sources))
    current["meta"]["total"] = len(current["breaking"]) + len(current["daily"])
    return current


# ========== 归档 ==========
def archive_week() -> bool:
    current = load_json(CURRENT_FILE)
    if not current:
        print("⚠️ current.json 不存在，无需归档")
        return False
    
    total = len(current.get("breaking", [])) + len(current.get("daily", []))
    if total == 0:
        print("⚠️ 本周无新闻，跳过归档")
        return False
    
    week_start = current["meta"].get("weekStart", get_week_start())
    archive_path = NEWS_DIR / f"{week_start}.json"
    
    save_json(current, archive_path)
    
    index = load_json(INDEX_FILE) or []
    if week_start not in index:
        index.append(week_start)
        index.sort(reverse=True)
        save_json(index, INDEX_FILE)
    
    print(f"📦 已归档本周数据到 {archive_path} ({total} 条)")
    
    empty_current = {
        "meta": {
            "weekStart": get_week_start(),
            "weekEnd": get_week_end(),
            "weekLabel": get_week_label(),
            "total": 0,
            "updatedAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
        },
        "breaking": [],
        "daily": [],
        "sources": []
    }
    save_current(empty_current)
    print("🆕 已创建新的 current.json 空模板")
    return True


# ========== RSS 抓取 ==========
def parse_rss_feed(xml_content: str, source_name: str, source_url: str) -> list:
    """解析 RSS XML，返回新闻条目列表"""
    items = []
    try:
        root = ET.fromstring(xml_content)
        # 处理 RSS 2.0 和 Atom 格式
        channel = root.find("channel") if root.tag == "rss" else root
        if channel is None:
            channel = root
        
        for item in channel.findall(".//item"):
            title = item.find("title")
            link = item.find("link")
            desc = item.find("description")
            pub_date = item.find("pubDate")
            
            title_text = title.text.strip() if title is not None and title.text else ""
            link_text = link.text.strip() if link is not None and link.text else ""
            desc_text = desc.text.strip() if desc is not None and desc.text else ""
            date_text = pub_date.text.strip() if pub_date is not None and pub_date.text else ""
            
            if not title_text or not link_text:
                continue
            
            # 清理描述中的 HTML 标签
            import re
            desc_clean = re.sub(r'<[^>]+>', '', desc_text)
            desc_clean = re.sub(r'\s+', ' ', desc_clean).strip()
            if len(desc_clean) > 200:
                desc_clean = desc_clean[:200] + "..."
            
            items.append({
                "title": title_text,
                "url": link_text,
                "description": desc_clean,
                "date": date_text,
                "source": source_name,
            })
    except Exception as e:
        print(f"⚠️ 解析 {source_name} RSS 失败: {e}")
    
    return items


def fetch_news_from_rss() -> dict:
    """从 RSS 源抓取新闻"""
    all_items = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    for source in RSS_SOURCES:
        try:
            print(f"📡 正在抓取 {source['name']} ...")
            resp = requests.get(source["url"], headers=headers, timeout=30)
            resp.raise_for_status()
            items = parse_rss_feed(resp.text, source["name"], source["url"])
            print(f"✅ {source['name']} 获取 {len(items)} 条")
            all_items.extend(items)
        except Exception as e:
            print(f"❌ {source['name']} 抓取失败: {e}")
    
    if not all_items:
        print("⚠️ 所有 RSS 源均失败，返回空数据")
        return {"breaking": [], "daily": [], "sources": []}
    
    # 构建输出数据结构
    today = get_today_str()
    today_display = get_today_display()
    breaking = []
    daily = []
    sources = set()
    
    # 取前 2 条作为 breaking，其余作为 daily
    for i, item in enumerate(all_items[:10]):
        news_id = f"news-{today}-{i+1:03d}"
        entry = {
            "id": news_id,
            "title_zh": item["title"],
            "title_en": "",  # RSS 抓取不生成英文标题
            "summary_zh": item["description"],
            "summary_en": "",
            "excerpt_zh": item["description"],
            "excerpt_en": "",
            "date": today_display,
            "source": item["source"],
            "category": item.get("category", "industry"),
            "url": item["url"],
        }
        
        if i < 2:
            entry["category"] = "breaking"
            breaking.append(entry)
        else:
            entry["category"] = "industry"
            daily.append(entry)
        
        sources.add(item["source"])
    
    total = len(breaking) + len(daily)
    return {
        "meta": {
            "date": today,
            "updatedAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
            "total": total,
        },
        "breaking": breaking,
        "daily": daily,
        "sources": sorted(list(sources)),
    }


# ========== Git 操作 ==========
def git_commit_push() -> bool:
    try:
        subprocess.run(["git", "add", "-A"], cwd=ROOT, check=True, capture_output=True)
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=ROOT, capture_output=True
        )
        if result.returncode == 0:
            print("📝 无变更，跳过提交")
            return True
        
        subprocess.run(
            ["git", "commit", "-m", f"📰 自动更新 - {get_today_str()}"],
            cwd=ROOT, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "push", "origin", "master"],
            cwd=ROOT, check=True, capture_output=True
        )
        print("🚀 Git 推送完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 操作失败: {e}")
        return False


# ========== 主流程 ==========
def main() -> int:
    print(f"🚀 AI前线每周归档更新启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    NEWS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. 周日归档
    if is_sunday():
        print("📦 今天是周日，执行本周归档...")
        archive_week()
    else:
        print(f"📅 今天不是归档日（周日），跳过归档")
    
    # 2. 从 RSS 抓取新闻
    print("📰 从 RSS 源抓取新闻...")
    new_data = fetch_news_from_rss()
    
    if not new_data.get("breaking") and not new_data.get("daily"):
        print("⚠️ 未获取到新闻，跳过更新")
        return 1
    
    # 3. 追加到 current.json
    print("📝 追加到 current.json...")
    current = load_current()
    
    current_week_start = current["meta"].get("weekStart", "")
    this_week_start = get_week_start()
    if current_week_start and current_week_start != this_week_start:
        print(f"⚠️ 检测到跨周！current.json 是 {current_week_start}，本周是 {this_week_start}")
        print("📦 先归档旧周...")
        archive_week()
        current = load_current()
    
    current = append_news_to_current(current, new_data)
    save_current(current)
    
    total = current["meta"]["total"]
    breaking_count = len(current["breaking"])
    daily_count = len(current["daily"])
    print(f"✅ 更新完成：本周累计 {total} 条（重磅 {breaking_count}，日常 {daily_count}）")
    
    # 4. Git 提交推送
    print("🔄 Git 提交推送...")
    git_commit_push()
    
    print("=" * 50)
    print("✅ 全部完成！")
    return 0


if __name__ == "__main__":
    sys.exit(main())
