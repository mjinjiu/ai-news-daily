#!/usr/bin/env python3
"""
AI前线 — 每周归档制自动更新脚本 v4

流程：
1. 每天运行：获取当天新闻 → 追加到 current.json（本周累积）
2. 每周日 23:59（或周一 00:00）归档：
   a. current.json → data/news/YYYY-MM-DD.json（本周周一日期）
   b. 更新 data/news/index.json
   c. 清空 current.json 开始新周

数据格式（current.json / 历史周 JSON）：
{
  "meta": {
    "weekStart": "2026-05-12",
    "weekEnd": "2026-05-18",
    "weekLabel": "5.12 — 5.18",
    "total": 8,
    "updatedAt": "2026-05-13T21:00:00+08:00"
  },
  "breaking": [...],
  "daily": [...],
  "sources": ["Reuters", "Bloomberg", ...]
}

新格式特点：
- 去掉 weekly、stats、hotList、tags 等前端已废弃字段
- sources 拆分为独立来源，去 TechCrunch 前缀
- 一周一份 JSON，历史周自动归档
"""

import json
import os
import subprocess
import sys
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

KIMI_API_KEY = os.environ.get("KIMI_API_KEY", "")
DEBUG_MODE = os.environ.get("DEBUG_MODE", "false").lower() == "true"


# ========== 工具函数 ==========
def get_today() -> datetime:
    return datetime.now()


def get_today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def get_today_display() -> str:
    return datetime.now().strftime("%m-%d")


def get_week_start(today: Optional[datetime] = None) -> str:
    """获取本周周一的日期字符串 YYYY-MM-DD"""
    if today is None:
        today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    return monday.strftime("%Y-%m-%d")


def get_week_end(today: Optional[datetime] = None) -> str:
    """获取本周周日的日期字符串 YYYY-MM-DD"""
    if today is None:
        today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return sunday.strftime("%Y-%m-%d")


def get_week_label(today: Optional[datetime] = None) -> str:
    """获取周标签，如 '5.12 — 5.18'"""
    if today is None:
        today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return f"{monday.month}.{monday.day:02d} — {sunday.month}.{sunday.day:02d}"


def is_sunday(today: Optional[datetime] = None) -> bool:
    """判断今天是否是周日（归档日）"""
    if today is None:
        today = datetime.now()
    return today.weekday() == 6  # 周日=6


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
    """清理信源：拆分 'X / Y' 为独立来源，去重，去 TechCrunch 前缀"""
    all_sources = []
    seen = set()
    for src in sources:
        # 按 / 拆分
        parts = [p.strip() for p in src.split("/")]
        for part in parts:
            if part and part not in seen:
                seen.add(part)
                all_sources.append(part)
    return sorted(all_sources)


# ========== current.json 管理 ==========
def load_current() -> dict:
    """加载 current.json，不存在则创建空模板"""
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
    """保存 current.json 并同步 legacy news.json"""
    save_json(data, CURRENT_FILE)
    # 同步旧格式兼容文件
    save_json(data, LEGACY_FILE)


def append_news_to_current(current: dict, new_data: dict) -> dict:
    """把当天新闻追加到 current.json，去重"""
    today = get_today()
    
    # 更新 meta
    current["meta"]["weekStart"] = get_week_start(today)
    current["meta"]["weekEnd"] = get_week_end(today)
    current["meta"]["weekLabel"] = get_week_label(today)
    current["meta"]["updatedAt"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    
    # 去重集合
    seen_ids = set()
    for item in current.get("breaking", []):
        if item.get("id"):
            seen_ids.add(item["id"])
    for item in current.get("daily", []):
        if item.get("id"):
            seen_ids.add(item["id"])
    
    # 追加 breaking
    for item in new_data.get("breaking", []):
        if item.get("id") and item["id"] not in seen_ids:
            seen_ids.add(item["id"])
            current["breaking"].append(item)
    
    # 追加 daily
    for item in new_data.get("daily", []):
        if item.get("id") and item["id"] not in seen_ids:
            seen_ids.add(item["id"])
            current["daily"].append(item)
    
    # 合并 sources
    all_sources = set(current.get("sources", []))
    all_sources.update(new_data.get("sources", []))
    current["sources"] = clean_sources(list(all_sources))
    
    # 更新 total
    current["meta"]["total"] = len(current["breaking"]) + len(current["daily"])
    
    return current


# ========== 归档 ==========
def archive_week() -> bool:
    """
    归档本周 current.json 到历史周 JSON
    文件名：data/news/YYYY-MM-DD.json（本周周一日期）
    更新 index.json
    """
    current = load_json(CURRENT_FILE)
    if not current:
        print("⚠️ current.json 不存在，无需归档")
        return False
    
    # 如果本周没有新闻，跳过归档
    total = len(current.get("breaking", [])) + len(current.get("daily", []))
    if total == 0:
        print("⚠️ 本周无新闻，跳过归档")
        return False
    
    # 归档文件名 = 本周周一日期
    week_start = current["meta"].get("weekStart", get_week_start())
    archive_path = NEWS_DIR / f"{week_start}.json"
    
    # 保存归档（直接复制 current.json 内容）
    save_json(current, archive_path)
    
    # 更新 index.json
    index = load_json(INDEX_FILE) or []
    if week_start not in index:
        index.append(week_start)
        index.sort(reverse=True)  # 最新在前
        save_json(index, INDEX_FILE)
    
    print(f"📦 已归档本周数据到 {archive_path} ({total} 条)")
    
    # 清空 current.json（保留空模板）
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


# ========== 新闻生成 ==========
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
5. source 字段只写独立来源名，不要写 "TechCrunch / Reuters" 这种组合，直接写 "Reuters"
输出格式：严格的 JSON，不要 markdown 代码块标记。"""

    user_prompt = f"""请按以下结构生成 {today} 的 AI 新闻数据：
{{"meta": {{"date": "{today}", "updatedAt": "{datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')}", "total": N}},
 "breaking": [{{"id": "news-{today}-001", "title_zh": "中文标题", "title_en": "Title", "summary_zh": "摘要", "summary_en": "Summary", "date": "{today_display}", "source": "Reuters", "category": "breaking", "url": "https://..."}}],
 "daily": [{{"id": "news-{today}-003", "title_zh": "标题", "title_en": "Title", "excerpt_zh": "摘要", "excerpt_en": "Excerpt", "date": "{today_display}", "source": "Bloomberg", "category": "industry|tech|policy", "url": "https://..."}}],
 "sources": ["Reuters", "Bloomberg"]}}
注意：
- source 字段只写单一来源名，不要组合
- 去掉 weekly、stats、hotList、tags 字段
- sources 数组只包含独立来源名"""

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
        
        required = ["meta", "breaking", "daily"]
        for key in required:
            if key not in data:
                print(f"❌ 缺少字段: {key}")
                return None
        
        # 确保 sources 存在
        if "sources" not in data:
            data["sources"] = []
        
        # 清理 sources
        data["sources"] = clean_sources(data["sources"])
        
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
        "daily": [],
        "sources": ["AI前线"]
    }


# ========== Git 操作 ==========
def git_commit_push() -> bool:
    """Git 提交并推送"""
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

    # 确保目录存在
    NEWS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. 检查是否需要归档（周日）
    if is_sunday():
        print("📦 今天是周日，执行本周归档...")
        archive_week()
    else:
        print(f"📅 今天不是归档日（周日），跳过归档")

    # 2. 生成当天新闻
    print("📰 获取当天新闻...")
    new_data = generate_news_via_kimi()
    if new_data is None:
        new_data = generate_fallback_news()

    # 3. 追加到 current.json
    print("📝 追加到 current.json...")
    current = load_current()
    
    # 检查是否跨周（如果 current.json 的 weekStart 不是本周，先归档旧周）
    current_week_start = current["meta"].get("weekStart", "")
    this_week_start = get_week_start()
    if current_week_start and current_week_start != this_week_start:
        print(f"⚠️ 检测到跨周！current.json 是 {current_week_start}，本周是 {this_week_start}")
        print("📦 先归档旧周...")
        archive_week()
        current = load_current()  # 重新加载新的空模板
    
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
