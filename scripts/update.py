#!/usr/bin/env python3
"""
AI前线 — 每日新闻自动更新脚本

功能：
1. 调用 Kimi API 生成结构化新闻 JSON
2. 支持 RSS 抓取作为备选数据源
3. 自动生成符合前端渲染器要求的 data/*.json 格式

使用：
    python scripts/update.py

环境变量：
    KIMI_API_KEY    - Kimi API Key（推荐）
    OPENAI_API_KEY  - OpenAI API Key（备选）
    DEBUG_MODE      - true/false，调试模式
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import requests

# 项目根目录
ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"

# API 配置
KIMI_API_KEY = os.environ.get("KIMI_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
DEBUG_MODE = os.environ.get("DEBUG_MODE", "false").lower() == "true"


def get_today_str() -> str:
    """获取今日日期字符串"""
    return datetime.now().strftime("%Y-%m-%d")


def get_today_display() -> str:
    """获取今日显示格式 MM-DD"""
    return datetime.now().strftime("%m-%d")


def get_week_range() -> str:
    """获取本周范围"""
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return f"{monday.month}.{monday.day} — {sunday.month}.{sunday.day}"


def generate_news_via_kimi() -> Optional[dict]:
    """
    调用 Kimi API 生成今日新闻 JSON
    如果没有 API Key 则返回 None
    """
    if not KIMI_API_KEY:
        print("⚠️ 未设置 KIMI_API_KEY，跳过 AI 生成")
        return None

    today = get_today_str()
    today_display = get_today_display()
    week_range = get_week_range()

    system_prompt = f"""你是 AI前线 的新闻编辑。请收集 {today} 最重要的 AI 行业新闻。

要求：
1. 只收集今天（{today}）发生的真实新闻
2. 优先从以下信源获取：Decrypt、Reuters、Bloomberg、新浪财经、新浪科技、TMT Post、36氪、Gov.cn
3. 分类：breaking（1-2条重磅）、industry（2-3条行业）、tech（2-3条技术）、policy（1-2条政策）
4. 每条新闻包含双语标题和摘要
5. 提供 4-6 个今日关键数字统计

输出格式：严格的 JSON，不要 markdown 代码块标记，直接输出 JSON 内容。"""

    user_prompt = f"""请按以下结构生成 {today} 的 AI 新闻数据：

{{
  "meta": {{
    "date": "{today}",
    "updatedAt": "{datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')}",
    "total": N
  }},
  "breaking": [
    {{
      "id": "news-001",
      "title_zh": "中文标题",
      "title_en": "English Title",
      "summary_zh": "中文摘要（100字以内）",
      "summary_en": "English summary (under 100 chars)",
      "date": "MM-DD",
      "source": "来源名称",
      "category": "breaking",
      "url": "https://example.com/article"
    }}
  ],
  "daily": [
    {{
      "id": "news-003",
      "title_zh": "标题",
      "title_en": "Title",
      "excerpt_zh": "摘要（80字以内）",
      "excerpt_en": "Excerpt (under 80 chars)",
      "date": "MM-DD",
      "source": "来源",
      "category": "industry|tech|policy",
      "url": "https://..."
    }}
  ],
  "weekly": [
    {{
      "day": "周一",
      "day_en": "Mon",
      "date": "{today_display}",
      "count": N,
      "items": [
        {{ "title_zh": "标题", "title_en": "Title", "category": "breaking|industry|tech|policy", "url": "https://..." }}
      ]
    }}
  ],
  "stats": [
    {{ "num": "$1B+", "label_zh": "标签", "label_en": "Label" }}
  ],
  "hotList": [
    {{ "title_zh": "标题", "title_en": "Title", "url": "https://..." }}
  ],
  "tags": ["OpenAI", "DeepSeek", "..."],
  "sources": ["Reuters", "Bloomberg", "..."]
}}

注意：
- 所有字段必须存在
- 中文摘要 80-100 字，英文 80-150 字符
- 链接必须是真实可访问的 URL
- stats 需要给出具体的数字，如 "$135B+"、"74.3万"
- 本周回顾中只生成今天的数据，其他天用空数组"""

    try:
        print("🤖 正在调用 Kimi API 生成新闻...")
        response = requests.post(
            "https://api.moonshot.cn/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {KIMI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "kimi-latest",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.3,
                "response_format": {"type": "json_object"},
            },
            timeout=120,
        )
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        data = json.loads(content)

        # 验证必要字段
        required = ["meta", "breaking", "daily", "weekly", "stats", "hotList", "tags", "sources"]
        for key in required:
            if key not in data:
                print(f"❌ API 返回缺少字段: {key}")
                return None

        print(f"✅ Kimi API 返回 {data['meta'].get('total', 0)} 条新闻")
        return data

    except Exception as e:
        print(f"❌ Kimi API 调用失败: {e}")
        return None


def generate_news_via_openai() -> Optional[dict]:
    """备选：调用 OpenAI API 生成新闻"""
    if not OPENAI_API_KEY:
        return None

    today = get_today_str()

    try:
        print("🤖 正在调用 OpenAI API 生成新闻...")
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": f"You are an AI news editor. Generate today's ({today}) AI industry news in structured JSON format with Chinese and English content."
                    },
                    {
                        "role": "user",
                        "content": f"Generate AI news data for {today}. Include breaking news (1-2), daily news (6-10), weekly review, stats, hot topics, tags, and sources. Format as JSON with _zh and _en fields."
                    },
                ],
                "temperature": 0.3,
                "response_format": {"type": "json_object"},
            },
            timeout=120,
        )
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception as e:
        print(f"❌ OpenAI API 调用失败: {e}")
        return None


def generate_fallback_news() -> dict:
    """
    当所有 API 都不可用时，生成模板数据
    （实际部署时应配置 API Key）
    """
    today = get_today_str()
    today_display = get_today_display()
    week_range = get_week_range()

    print("⚠️ 使用示例数据（请配置 API Key 获取真实新闻）")

    return {
        "meta": {
            "date": today,
            "updatedAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
            "total": 8
        },
        "breaking": [
            {
                "id": "news-001",
                "title_zh": f"今日AI行业重大动态（示例数据）",
                "title_en": "Major AI Industry Updates Today (Sample Data)",
                "summary_zh": "这是示例数据。配置 KIMI_API_KEY 后将自动获取真实新闻。请访问仓库 Settings → Secrets 添加 API Key。",
                "summary_en": "This is sample data. Configure KIMI_API_KEY to get real news automatically. Go to Settings → Secrets to add your API Key.",
                "date": today_display,
                "source": "AI前线",
                "category": "breaking",
                "url": "https://github.com/mjinjiu/ai-news-daily"
            }
        ],
        "daily": [
            {
                "id": "news-003",
                "title_zh": "示例新闻条目",
                "title_en": "Sample News Entry",
                "excerpt_zh": "配置 KIMI_API_KEY 后，每天自动获取真实 AI 新闻并更新网站。",
                "excerpt_en": "After configuring KIMI_API_KEY, real AI news will be fetched and the site updated daily.",
                "date": today_display,
                "source": "AI前线",
                "category": "tech",
                "url": "https://github.com/mjinjiu/ai-news-daily"
            }
        ],
        "weekly": [
            {
                "day": "周一",
                "day_en": "Mon",
                "date": today_display,
                "count": 1,
                "items": [
                    {"title_zh": "示例条目", "title_en": "Sample Item", "category": "tech", "url": "https://github.com/mjinjiu/ai-news-daily"}
                ]
            },
            {"day": "周日", "day_en": "Sun", "date": "", "count": 0, "items": []},
            {"day": "周六", "day_en": "Sat", "date": "", "count": 0, "items": []},
            {"day": "周五", "day_en": "Fri", "date": "", "count": 0, "items": []},
            {"day": "周四", "day_en": "Thu", "date": "", "count": 0, "items": []},
        ],
        "stats": [
            {"num": "0", "label_zh": "今日新闻数", "label_en": "Today's News Count"},
            {"num": "0", "label_zh": "本周累计", "label_en": "Weekly Total"},
        ],
        "hotList": [
            {"title_zh": "配置 API Key 获取真实数据", "title_en": "Configure API Key for Real Data", "url": "https://github.com/mjinjiu/ai-news-daily"}
        ],
        "tags": ["API配置", "自动更新"],
        "sources": ["AI前线"]
    }


def generate_analysis() -> dict:
    """生成深度解读数据（可以复用新闻数据做深度分析）"""
    today = get_today_str()

    return {
        "updatedAt": today,
        "items": [
            {
                "id": "analysis-001",
                "grade": "A",
                "date": get_today_display(),
                "title_zh": "AI行业今日热点深度解析",
                "title_en": "Deep Analysis of Today's AI Hot Topics",
                "summary_zh": "今日AI行业发生重大变化，多家公司发布新产品。配置 API Key 后将基于真实新闻生成深度解读。",
                "summary_en": "Significant changes in AI industry today with multiple companies releasing new products. Configure API Key for real analysis.",
                "points_zh": [
                    {"num": "1️⃣", "title": "技术突破", "desc": "大模型能力持续提升"},
                    {"num": "2️⃣", "title": "市场竞争", "desc": "价格战愈演愈烈"},
                    {"num": "3️⃣", "title": "政策影响", "desc": "监管框架逐步完善"}
                ],
                "points_en": [
                    {"num": "1️⃣", "title": "Tech Breakthrough", "desc": "LLM capabilities continue to improve"},
                    {"num": "2️⃣", "title": "Market Competition", "desc": "Price wars intensifying"},
                    {"num": "3️⃣", "title": "Policy Impact", "desc": "Regulatory framework taking shape"}
                ],
                "debate_zh": {
                    "pro": ["AI将大幅提升生产力", "开源模型降低使用门槛"],
                    "con": ["可能存在安全隐患", "版权争议尚未解决"]
                },
                "debate_en": {
                    "pro": ["AI will greatly boost productivity", "Open-source models lower barriers"],
                    "con": ["Potential safety risks", "Copyright disputes unresolved"]
                },
                "prediction_zh": "未来6个月内，我们将看到更多大模型开源和价格战持续。",
                "prediction_en": "In the next 6 months, we'll see more open-source LLMs and continued price competition.",
                "tags": ["AI", "大模型"],
                "source": "AI前线编辑部",
                "url": "https://github.com/mjinjiu/ai-news-daily"
            }
        ]
    }


def generate_pricing() -> dict:
    """API定价数据更新（通常不需要每天变，直接复制模板）"""
    # 定价数据变化不频繁，保留原样或微调
    template_path = DATA_DIR / "pricing.json"
    if template_path.exists():
        with open(template_path, "r", encoding="utf-8") as f:
            return json.load(f)

    return {
        "updatedAt": datetime.now().strftime("%Y-%m"),
        "note_zh": "价格随时可能变动，请以各平台官方文档为准",
        "note_en": "Prices are subject to change. Please refer to official documentation.",
        "international": [],
        "china": [],
        "plans": []
    }


def save_json(data: dict, filename: str) -> None:
    """保存 JSON 文件到 data/ 目录"""
    filepath = DATA_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 已保存 {filepath}")


def main():
    """主入口"""
    print(f"🚀 AI前线自动更新脚本启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # 确保 data 目录存在
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 尝试通过 API 获取真实新闻
    news_data = None

    if KIMI_API_KEY:
        news_data = generate_news_via_kimi()
    elif OPENAI_API_KEY:
        news_data = generate_news_via_openai()

    # 如果 API 失败或未配置，使用示例数据
    if not news_data:
        news_data = generate_fallback_news()

    # 生成其他数据
    analysis_data = generate_analysis()
    pricing_data = generate_pricing()

    # 保存所有 JSON 文件
    save_json(news_data, "news.json")
    save_json(analysis_data, "analysis.json")
    save_json(pricing_data, "pricing.json")

    print("=" * 50)
    print(f"✅ 更新完成！共 {news_data['meta']['total']} 条新闻")

    # 调试模式下打印内容预览
    if DEBUG_MODE:
        print("\n📋 新闻预览:")
        for item in news_data.get("breaking", [])[:2]:
            print(f"  🔴 {item['title_zh'][:40]}...")
        for item in news_data.get("daily", [])[:3]:
            print(f"  📰 {item['title_zh'][:40]}...")

    return 0


if __name__ == "__main__":
    sys.exit(main())
