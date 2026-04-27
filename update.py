#!/usr/bin/env python3
"""
AI前线 v3.7 - 全自动新闻更新系统
流程：获取新闻 → 构建HTML → Git提交推送

用法：
  python3 update.py --fetch    # 搜索并获取新闻
  python3 update.py --build    # 根据news.json构建HTML
  python3 update.py --deploy   # Git提交推送
  python3 update.py --all      # 完整流程

配置文件：config.json（信源、Git仓库、广告设置）
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta

# ========== 配置 ==========
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")
NEWS_FILE = os.path.join(os.path.dirname(__file__), "news.json")

DEFAULT_CONFIG = {
    "sources": [
        {"name": "Reuters", "url": "https://www.reuters.com/technology/", "lang": "en"},
        {"name": "Bloomberg", "url": "https://www.bloomberg.com/news/technology", "lang": "en"},
        {"name": "芯智讯", "url": "https://www.icsmart.cn/", "lang": "zh"},
        {"name": "Sina Tech", "url": "https://tech.sina.com.cn/ai/", "lang": "zh"},
        {"name": "Gov.cn", "url": "https://www.gov.cn/zhengce/zhengceku/", "lang": "zh"},
        {"name": "DoNews", "url": "https://www.donews.com/", "lang": "zh"},
        {"name": "极客公园", "url": "https://www.geekpark.net/", "lang": "zh"},
        {"name": "云头条", "url": "https://www.c114.com.cn/", "lang": "zh"},
        {"name": "Anthropic", "url": "https://www.anthropic.com/news/", "lang": "en"},
        {"name": "OpenAI", "url": "https://openai.com/blog/", "lang": "en"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/category/artificial-intelligence/", "lang": "en"},
        {"name": "The Verge", "url": "https://www.theverge.com/ai-artificial-intelligence", "lang": "en"}
    ],
    "github": {
        "cn_repo": "https://github.com/mjinjiu/ai-news-daily.git",
        "en_repo": "https://github.com/mjinjiu/ai-news-daily-en.git",
        "token_env": "GITHUB_TOKEN"
    },
    "categories": {
        "breaking": {"zh": "重磅", "en": "Breaking", "color": "#ef4444"},
        "tech": {"zh": "技术", "en": "Tech", "color": "#6366f1"},
        "industry": {"zh": "行业", "en": "Industry", "color": "#f59e0b"},
        "policy": {"zh": "政策", "en": "Policy", "color": "#10b981"}
    }
}

# ========== 工具函数 ==========
def load_config():
    """加载配置"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return DEFAULT_CONFIG

def save_config(cfg):
    """保存配置"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

def load_news():
    """加载新闻数据"""
    if os.path.exists(NEWS_FILE):
        with open(NEWS_FILE) as f:
            return json.load(f)
    return {"date": datetime.now().strftime("%Y-%m-%d"), "articles": []}

def save_news(news):
    """保存新闻数据"""
    with open(NEWS_FILE, 'w') as f:
        json.dump(news, f, indent=2, ensure_ascii=False)

def run_cmd(cmd, cwd=None):
    """执行命令"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"❌ 命令失败: {cmd}")
        print(f"   错误: {result.stderr}")
        return False, result.stderr
    return True, result.stdout

def get_github_token():
    """获取GitHub Token"""
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        # 尝试从git remote URL解析
        success, output = run_cmd("git remote get-url origin", cwd=os.path.dirname(__file__))
        if success and "@" in output:
            # 格式: https://user:token@github.com/...
            match = re.search(r'https://[^:]+:([^@]+)@', output.strip())
            if match:
                token = match.group(1)
    return token

# ========== 新闻获取（占位，实际由Agent调用搜索工具后填充） ==========
def fetch_news_placeholder():
    """新闻获取占位 - 实际由Agent通过kimi_search获取后写入news.json"""
    print("⚠️ 新闻获取需要Agent使用 kimi_search 工具")
    print("   搜索关键词建议:")
    for src in DEFAULT_CONFIG["sources"]:
        print(f"   - {src['name']}: AI artificial intelligence ({src['lang']})")
    print(f"\n   搜索后将结果写入: {NEWS_FILE}")
    print("   格式: {{'date': '2026-04-27', 'articles': [...]}}")
    return False

# ========== HTML构建 ==========
def build_html(lang="zh"):
    """根据news.json构建HTML"""
    news = load_news()
    if not news.get("articles"):
        print("⚠️ 没有新闻数据，请先获取新闻")
        return False
    
    # 读取模板
    template_file = "index.html"
    template_path = os.path.join(os.path.dirname(__file__), template_file)
    
    if not os.path.exists(template_path):
        print(f"❌ 模板文件不存在: {template_path}")
        return False
    
    with open(template_path) as f:
        html = f.read()
    
    # 更新时间
    today = news.get("date", datetime.now().strftime("%Y-%m-%d"))
    if lang == "zh":
        html = re.sub(
            r'class="update-time"[^>]*>[^<]*</p>',
            f'class="update-time" data-zh="更新于：{today}" data-en="Updated: {today}">更新于：{today}</p>',
            html
        )
    else:
        html = re.sub(
            r'class="update-time"[^>]*>[^<]*</p>',
            f'class="update-time" data-zh="更新于：{today}" data-en="Updated: {today}">Updated: {today}</p>',
            html
        )
    
    print(f"✅ HTML构建完成 ({lang})")
    print(f"   日期: {today}")
    print(f"   新闻数: {len(news['articles'])}")
    return True

# ========== Git部署 ==========
def deploy():
    """Git提交并推送"""
    site_dir = os.path.dirname(__file__)
    token = get_github_token()
    
    if not token:
        print("❌ 未找到GitHub Token")
        print("   请设置环境变量 GITHUB_TOKEN=ghp_xxxx")
        return False
    
    # 获取仓库URL
    success, repo_url = run_cmd("git remote get-url origin", cwd=site_dir)
    if not success:
        return False
    
    repo_url = repo_url.strip()
    # 转换为带token的URL
    if repo_url.startswith("https://github.com/"):
        auth_url = repo_url.replace("https://", f"https://mjinjiu:{token}@")
    else:
        auth_url = repo_url
    
    # 设置临时remote
    run_cmd("git remote set-url origin " + auth_url, cwd=site_dir)
    
    # 添加、提交、推送
    today = datetime.now().strftime("%Y-%m-%d")
    cmds = [
        "git add -A",
        f'git commit -m "🤖 Auto-update: {today} daily news" || true',
        "git push origin master"
    ]
    
    for cmd in cmds:
        success, output = run_cmd(cmd, cwd=site_dir)
        if not success and "nothing to commit" not in output:
            # 恢复remote
            run_cmd("git remote set-url origin " + repo_url, cwd=site_dir)
            return False
    
    # 恢复remote
    run_cmd("git remote set-url origin " + repo_url, cwd=site_dir)
    
    print(f"✅ 部署完成: {today}")
    return True

# ========== 归档生成 ==========
def generate_archive():
    """生成本周归档页"""
    news = load_news()
    if not news.get("articles"):
        return False
    
    today = datetime.strptime(news["date"], "%Y-%m-%d")
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    week_str = f"{week_start.strftime('%Y-%m-%d')}_W{week_start.isocalendar()[1]}"
    
    archive_file = os.path.join(os.path.dirname(__file__), "archive", f"{week_str}.html")
    
    # 简化：复制当前index.html作为归档基础
    # 实际应该生成专门的归档页
    print(f"⚠️ 归档生成占位: {archive_file}")
    print("   实际实现需要模板引擎生成专门归档页")
    return True

# ========== 主入口 ==========
def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1]
    
    if cmd == "--fetch":
        fetch_news_placeholder()
    elif cmd == "--build":
        build_html("zh")
        build_html("en")
    elif cmd == "--deploy":
        deploy()
    elif cmd == "--archive":
        generate_archive()
    elif cmd == "--all":
        print("🚀 启动全自动更新流程...")
        print("=" * 50)
        fetch_news_placeholder()
        build_html("zh")
        build_html("en")
        generate_archive()
        deploy()
        print("=" * 50)
        print("✅ 流程完成")
    else:
        print(f"❌ 未知命令: {cmd}")
        print(__doc__)

if __name__ == "__main__":
    main()
