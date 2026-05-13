#!/usr/bin/env python3
"""
AI前线 — 每日新闻自动更新脚本（归档制 v2）

功能：
1. 每天生成独立归档：data/news/YYYY-MM-DD.json
2. 自动合并本周数据到 data/news/current.json（主界面展示用）
3. 每个栏目独立归档目录：news/、github/、api/
4. 保留历史数据，永不覆盖

归档结构：
  data/
    news/
      2026-05-10.json   ← 每日独立归档
      2026-05-11.json
      ...
      current.json      ← 本周合并（主界面读取这个）
    github/
      2026-05-10.json
      current.json
    api/
      2026-05-10.json
      current.json
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import requests

ROOT = Path(__file__).parent.parent

ARCHIVE_DIRS = {
    "news": ROOT / "data" / "news",
    "github": ROOT / "data" / "github",
    "api": ROOT / "data" / "api",
}

KIMI_API_KEY = os.environ.get("KIMI_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
DEBUG_MODE = os.environ.get("DEBUG_MODE", "false").lower() == "true"


def get_today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def get_today_display() -> str:
    return datetime.now().strftime("%m-%d")


def get_week_range() -> str:
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return f"{monday.month}.{monday.day} — {sunday.month}.{sunday.day}"


def get_week_dates(today: Optional[datetime] = None) -> list:
    if today is None:
        today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    return [(monday + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]


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


def merge_weekly_data(archive_dir: Path, dates: list) -> dict:
    """合并本周所有日期数据到 current.json"""
    all_breaking = []
    all_daily = []
    all_stats = []
    all_hotList = []
    all_tags = set()
    all_sources = set()
    latest_date = ""

    for date_str in dates:
        filepath = archive_dir / f"{date_str}.json"
        data = load_json(filepath)
        if not data:
            continue
        if date_str > latest_date:
            latest_date = date_str
        all_breaking.extend(data.get("breaking", []))
        all_daily.extend(data.get("daily", []))
        all_stats.extend(data.get("stats", []))
        all_hotList.extend(data.get("hotList", []))
        all_tags.update(data.get("tags", []))
        all_sources.update(data.get("sources", []))

    # 去重
    seen_ids = set()
    unique_breaking = []
    for item in all_breaking:
        if item.get("id") and item["id"] not in seen_ids:
            seen_ids.add(item["id"])
            unique_breaking.append(item)

    seen_ids = set()
    unique_daily = []
    for item in all_daily:
        if item.get("id") and item["id"] not in seen_ids:
            seen_ids.add(item["id"])
            unique_daily.append(item)

    seen_labels = set()
    unique_stats = []
    for item in all_stats:
        label = item.get("label_zh", "")
        if label and label not in seen_labels:
            seen_labels.add(label)
            unique_stats.append(item)

    seen_titles = set()
    unique_hotList = []
    for item in all_hotList:
        title = item.get("title_zh", "")
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_hotList.append(item)

    return {
        "meta": {
            "date": latest_date or get_today_str(),
            "updatedAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
            "total": len(unique_breaking) + len(unique_daily),
            "weekRange": get_week_range(),
            "daysCount": len([d for d in dates if (archive_dir / f"{d}.json").exists()]),
        },
        "breaking": unique_breaking,
        "daily": unique_daily,
        "weekly": [],
        "stats": unique_stats,
        "hotList": unique_hotList,
        "tags": sorted(list(all_tags)),
        "sources": sorted(list(all_sources)),
        "archiveDates": [d for d in dates if (archive_dir / f"{d}.json").exists()],
    }


def generate_news_via_kimi() -> Optional[dict]:
    if not KIMI_API_KEY:
        print("⚠️ 未设置 KIMI_API_KEY，跳过 AI 生成")
        return None

    today = get_today_str()
    today_display = get_today_display()

    system_prompt = f"""你是 AI前线 的新闻编辑。请收集 {today} 最重要的 AI 行业新闻。
要求：
1. 只收集今天（{today}）发生的真实新闻
2. 优先从以下信源获取：Decrypt、Reuters、Bloomberg、新浪财经、新浪科技、36氪
3. 分类：breaking（1-2条重磅）、industry（2-3条行业）、tech（2-3条技术）、policy（1-2条政策）
4. 每条新闻包含双语标题和摘要
5. 提供 4-6 个今日关键数字统计
输出格式：严格的 JSON，不要 markdown 代码块标记。"""

    user_prompt = f"""请按以下结构生成 {today} 的 AI 新闻数据：
{{"meta": {{"date": "{today}", "updatedAt": "{datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')}", "total": N}},
 "breaking": [{{"id": "news-001", "title_zh": "中文标题", "title_en": "Title", "summary_zh": "摘要", "summary_en": "Summary", "date": "MM-DD", "source": "来源", "category": "breaking", "url": "https://..."}}],
 "daily": [{{"id": "news-003", "title_zh": "标题", "title_en": "Title", "excerpt_zh": "摘要", "excerpt_en": "Excerpt", "date": "MM-DD", "source": "来源", "category": "industry|tech|policy", "url": "https://..."}}],
 "weekly": [], "stats": [{{"num": "$1B+", "label_zh": "标签", "label_en": "Label"}}],
 "hotList": [{{"title_zh": "标题", "title_en": "Title", "url": "https://..."}}],
 "tags": ["OpenAI"], "sources": ["Reuters"]}}
注意：weekly 留空，由前端处理。"""

    try:
        print("🤖 正在调用 Kimi API 生成新闻...")
        response = requests.post(
            "https://api.moonshot.cn/v1/chat/completions",
            headers={"Authorization": f"Bearer {KIMI_API_KEY}", "Content-Type": "application/json"},
            json={"model": "kimi-latest", "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ], "temperature": 0.3, "response_format": {"type": "json_object"}},
            timeout=120,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        data = json.loads(content)
        required = ["meta", "breaking", "daily", "stats", "hotList", "tags", "sources"]
        for key in required:
            if key not in data:
                print(f"❌ 缺少字段: {key}")
                return None
        print(f"✅ Kimi API 返回 {data['meta'].get('total', 0)} 条新闻")
        return data
    except Exception as e:
        print(f"❌ Kimi API 调用失败: {e}")
        return None


def generate_fallback_news() -> dict:
    today = get_today_str()
    today_display = get_today_display()
    print("⚠️ 使用示例数据")
    return {
        "meta": {"date": today, "updatedAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"), "total": 1},
        "breaking": [{"id": f"news-{today}-001", "title_zh": f"{today} 示例数据", "title_en": "Sample", "summary_zh": "配置 API Key 后获取真实新闻", "summary_en": "Configure API Key", "date": today_display, "source": "AI前线", "category": "breaking", "url": "https://github.com/mjinjiu/ai-news-daily"}],
        "daily": [], "weekly": [], "stats": [{"num": "0", "label_zh": "今日新闻", "label_en": "News"}],
        "hotList": [], "tags": ["API配置"], "sources": ["AI前线"]
    }


def generate_github_placeholder() -> dict:
    return {"meta": {"date": get_today_str(), "updatedAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"), "total": 0, "note": "placeholder"}, "repositories": [], "categories": []}


def generate_api_placeholder() -> dict:
    return {"meta": {"date": get_today_str(), "updatedAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"), "total": 0, "note": "placeholder"}, "trends": [], "categories": []}


def update_section(section: str, generator) -> None:
    """更新单个栏目：生成今日归档 + 合并本周 current.json"""
    archive_dir = ARCHIVE_DIRS[section]
    today = get_today_str()
    
    # 1. 生成今日数据（如果失败则使用 fallback）
    data = generator()
    if data is None:
        if section == "news":
            data = generate_fallback_news()
        elif section == "github":
            data = generate_github_placeholder()
        else:
            data = generate_api_placeholder()
    
    # 2. 保存每日归档
    daily_path = archive_dir / f"{today}.json"
    save_json(data, daily_path)
    
    # 3. 合并本周数据到 current.json
    week_dates = get_week_dates()
    current_data = merge_weekly_data(archive_dir, week_dates)
    current_path = archive_dir / "current.json"
    save_json(current_data, current_path)
    
    print(f"✅ {section} 栏目更新完成：今日 {data['meta']['total']} 条，本周累计 {current_data['meta']['total']} 条")


def main() -> int:
    print(f"🚀 AI前线归档更新启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # 确保目录存在
    for d in ARCHIVE_DIRS.values():
        d.mkdir(parents=True, exist_ok=True)

    # 更新各栏目
    update_section("news", generate_news_via_kimi if KIMI_API_KEY else generate_fallback_news)
    update_section("github", generate_github_placeholder)
    update_section("api", generate_api_placeholder)

    # 同时保留旧的 data/news.json 兼容（过渡期间）
    news_current = load_json(ARCHIVE_DIRS["news"] / "current.json")
    if news_current:
        save_json(news_current, ROOT / "data" / "news.json")

    print("=" * 50)
    print("✅ 全部更新完成！归档制已生效。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
