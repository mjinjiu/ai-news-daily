#!/usr/bin/env python3
"""
AI前线 — GitHub 趋势抓取脚本
从 GitHub Search API 获取最近热门仓库
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

import requests

# ========== 配置 ==========
ROOT = Path(__file__).parent.parent
GITHUB_DIR = ROOT / "data" / "github"
INDEX_FILE = GITHUB_DIR / "index.json"
CURRENT_FILE = GITHUB_DIR / "current.json"

# 搜索配置
SEARCH_QUERIES = [
    "AI",
    "machine learning",
    "LLM",
    "agent",
    "OpenAI",
    "Claude",
]


def get_today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def get_today_display() -> str:
    return datetime.now().strftime("%m-%d")


def get_week_start() -> str:
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    return monday.strftime("%Y-%m-%d")


def save_json(data: dict, filepath: Path) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 已保存 {filepath}")


def load_json(filepath: Path) -> dict:
    if not filepath.exists():
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ 读取失败 {filepath}: {e}")
        return None


def fetch_github_trending() -> list:
    """从 GitHub Search API 获取热门仓库"""
    all_items = []
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "AI-Frontline-Bot",
    }
    
    # 计算7天前的日期，用于搜索最近创建的热门仓库
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    for query in SEARCH_QUERIES[:2]:  # 只搜前2个，避免rate limit
        try:
            url = f"https://api.github.com/search/repositories"
            params = {
                "q": f"{query} created:>{week_ago}",
                "sort": "stars",
                "order": "desc",
                "per_page": "15",
            }
            print(f"📡 搜索 GitHub: {query} ...")
            resp = requests.get(url, headers=headers, params=params, timeout=30)
            
            if resp.status_code == 403:
                print(f"⚠️ GitHub API Rate Limit，跳过")
                break
            
            resp.raise_for_status()
            data = resp.json()
            
            for item in data.get("items", [])[:10]:
                all_items.append({
                    "name": item.get("full_name", ""),
                    "repo": item.get("full_name", ""),
                    "url": item.get("html_url", ""),
                    "description": item.get("description", "") or "No description",
                    "description_zh": "",  # 暂不翻译
                    "language": item.get("language", "Unknown") or "Unknown",
                    "stars_today": str(item.get("stargazers_count", 0)),
                    "score": min(30, item.get("stargazers_count", 0) // 100),
                    "date": get_today(),
                })
            
            print(f"✅ 获取 {len(data.get('items', []))} 个仓库")
            
        except Exception as e:
            print(f"❌ 搜索失败 {query}: {e}")
    
    # 去重
    seen = set()
    unique = []
    for item in all_items:
        if item["repo"] not in seen:
            seen.add(item["repo"])
            unique.append(item)
    
    return unique[:15]  # 最多15个


def generate_output() -> dict:
    """生成 GitHub 趋势输出"""
    projects = fetch_github_trending()
    
    if not projects:
        print("⚠️ 未获取到数据，使用空模板")
        projects = []
    
    # 取前5作为 high_value
    high_value = projects[:5]
    all_projects = projects
    
    today = get_today()
    
    return {
        "date": today,
        "total_scanned": len(all_projects),
        "high_value": high_value,
        "all_projects": all_projects,
    }


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
            ["git", "commit", "-m", f"🔥 GitHub趋势 - {get_today()}"],
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


def main() -> int:
    print(f"🚀 GitHub趋势更新启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    GITHUB_DIR.mkdir(parents=True, exist_ok=True)
    
    # 生成数据
    data = generate_output()
    
    # 保存 current.json
    save_json(data, CURRENT_FILE)
    
    # 更新 index.json
    index = load_json(INDEX_FILE) or []
    week_start = get_week_start()
    if week_start not in index:
        index.append(week_start)
        index.sort(reverse=True)
        save_json(index, INDEX_FILE)
    
    print(f"✅ 更新完成：{len(data['all_projects'])} 个项目")
    
    # Git 提交
    print("🔄 Git 提交推送...")
    git_commit_push()
    
    print("=" * 50)
    print("✅ 全部完成！")
    return 0


if __name__ == "__main__":
    sys.exit(main())
