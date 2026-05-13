#!/usr/bin/env python3
import json
import datetime
from collections import Counter

# 从 update_news_data.py 的数据创建 05-07 历史归档

date_str = "2026-05-07"

breaking = [
    {
        "id": f"news-{date_str}-001",
        "title_zh": "苹果支付2.5亿美元和解Siri AI功能延迟诉讼",
        "title_en": "Apple to Pay $250M to Settle Lawsuit Over Siri's Delayed AI Features",
        "summary_zh": "苹果公司同意支付2.5亿美元和解因Siri AI功能延迟推出的集体诉讼。此案凸显了科技巨头在AI承诺与实际交付之间的法律风险。",
        "summary_en": "Apple agrees to pay $250M to settle class-action lawsuit over delayed Siri AI features. The case highlights legal risks for tech giants between AI promises and actual delivery.",
        "date": "05-07",
        "source": "TechCrunch / Reuters",
        "category": "breaking",
        "url": "https://techcrunch.com/2026/05/06/apple-to-pay-250m-to-settle-lawsuit-over-siris-delayed-ai-features/"
    },
    {
        "id": f"news-{date_str}-002",
        "title_zh": "AI热潮推动三星市值突破1万亿美元",
        "title_en": "AI Boom Pushes Samsung to $1 Trillion Valuation",
        "summary_zh": "受AI芯片需求激增推动，三星电子市值突破1万亿美元大关，成为亚洲第二家达到此里程碑的科技企业。其HBM内存和先进制程订单已排至2027年。",
        "summary_en": "Driven by surging AI chip demand, Samsung Electronics market cap breaks $1 trillion, becoming Asia's second tech company to reach this milestone. HBM memory and advanced process orders booked through 2027.",
        "date": "05-07",
        "source": "TechCrunch / Bloomberg",
        "category": "breaking",
        "url": "https://techcrunch.com/2026/05/06/ai-boom-pushes-samsung-to-1t/"
    }
]

daily = [
    {"id": f"news-{date_str}-003", "title_zh": "DeepSeek首轮融资估值或达450亿美元", "title_en": "DeepSeek Could Hit $45B Valuation from First Investment Round", "excerpt_zh": "中国AI独角兽DeepSeek正在进行首轮融资，估值可能高达450亿美元。其低成本高性能的推理模型正在全球范围内挑战OpenAI和Anthropic的主导地位。", "excerpt_en": "Chinese AI unicorn DeepSeek is in its first funding round with potential $45B valuation.", "date": "05-07", "source": "TechCrunch / Bloomberg", "category": "industry", "url": "https://techcrunch.com/2026/05/06/deepseek-could-hit-45b-valuation-from-its-first-investment-round/"},
    {"id": f"news-{date_str}-004", "title_zh": "谷歌AI搜索新增Reddit等社区引用功能", "title_en": "Google Updates AI Search to Include Quotes from Reddit and Other Sources", "excerpt_zh": "谷歌更新AI搜索体验，开始在AI概览中引用Reddit等社区平台的真实用户观点。", "excerpt_en": "Google updates AI search to cite real user opinions from Reddit.", "date": "05-07", "source": "TechCrunch / Sina Tech", "category": "tech", "url": "https://techcrunch.com/2026/05/06/google-updates-ai-search-to-include-quotes-from-reddit-and-other-sources/"},
    {"id": f"news-{date_str}-005", "title_zh": "马斯克如何离开OpenAI？Greg Brockman首次详细披露内幕", "title_en": "How Elon Musk Left OpenAI, According to Greg Brockman", "excerpt_zh": "OpenAI联合创始人Greg Brockman首次详细披露了马斯克2018年离开公司的内幕。", "excerpt_en": "OpenAI co-founder Greg Brockman details Elon Musk's 2018 departure.", "date": "05-07", "source": "TechCrunch / Reuters", "category": "industry", "url": "https://techcrunch.com/2026/05/06/how-elon-musk-left-openai-according-to-greg-brockman/"},
    {"id": f"news-{date_str}-006", "title_zh": "AI评估平台Braintrust确认数据泄露，要求所有客户轮换密钥", "title_en": "AI Evaluation Startup Braintrust Confirms Breach", "excerpt_zh": "AI模型评估平台Braintrust确认遭遇安全入侵，攻击者获取了敏感客户数据。", "excerpt_en": "AI model evaluation platform Braintrust confirms security breach.", "date": "05-07", "source": "TechCrunch / Security", "category": "tech", "url": "https://techcrunch.com/2026/05/06/ai-evaluation-startup-braintrust-confirms-breach/"},
    {"id": f"news-{date_str}-007", "title_zh": "SAP豪掷11.6亿美元收购德国18个月大AI实验室NemoClaw", "title_en": "SAP Bets $1.16B on 18-Month-Old German AI Lab NemoClaw", "excerpt_zh": "德国软件巨头SAP以11.6亿美元收购成立仅18个月的AI实验室NemoClaw。", "excerpt_en": "German software giant SAP acquires 18-month-old AI lab NemoClaw for $1.16B.", "date": "05-07", "source": "TechCrunch / 极客公园", "category": "industry", "url": "https://techcrunch.com/2026/05/06/sap-bets-1-16b-on-18-month-old-german-ai-lab/"},
    {"id": f"news-{date_str}-008", "title_zh": "Meta收购机器人初创公司，加码人形AI机器人布局", "title_en": "Meta Buys Robotics Startup to Bolster Humanoid AI Ambitions", "excerpt_zh": "Meta低调收购一家专注于人形机器人控制的AI初创公司。", "excerpt_en": "Meta quietly acquires an AI startup focused on humanoid robot control.", "date": "05-06~07", "source": "TechCrunch / 芯智讯", "category": "tech", "url": "https://techcrunch.com/2026/05/01/meta-buys-robotics-startup/"},
    {"id": f"news-{date_str}-009", "title_zh": "五角大楼与英伟达、微软、AWS签约部署机密网络AI", "title_en": "Pentagon Inks Deals with Nvidia, Microsoft, AWS", "excerpt_zh": "美国国防部与三大云/芯片巨头签订协议，在机密军事网络中部署AI系统。", "excerpt_en": "US Department of Defense signs agreements to deploy AI on classified networks.", "date": "05-07", "source": "TechCrunch / Reuters", "category": "policy", "url": "https://techcrunch.com/2026/05/01/pentagon-inks-deals-with-nvidia-microsoft-and-aws/"},
    {"id": f"news-{date_str}-010", "title_zh": "谷歌、英伟达押注40亿美元自学习AI公司，目标'替代科学家'", "title_en": "Google & Nvidia Back $4B Self-Learning AI Company", "excerpt_zh": "获得谷歌和英伟达投资的自学习AI公司估值已达40亿美元。", "excerpt_en": "Self-learning AI company backed by Google and Nvidia reaches $4B valuation.", "date": "05-07", "source": "极客公园 / Sina Tech", "category": "tech", "url": "https://cj.sina.cn/articles/view/5953740931/162dee083067035db4"}
]

archive = {
    "meta": {"date": date_str, "updatedAt": f"{date_str}T08:00:00+08:00", "total": len(daily), "weekRange": "5.05 — 5.11", "daysCount": 1},
    "breaking": breaking,
    "daily": daily,
    "weekly": [{"day": "周三", "day_en": "Wed", "date": "05-07", "count": 10, "items": [{"title_zh": "苹果2.5亿美元和解Siri AI诉讼", "title_en": "Apple $250M Siri AI settlement", "category": "breaking"}, {"title_zh": "三星市值突破1万亿美元", "title_en": "Samsung hits $1T", "category": "breaking"}, {"title_zh": "DeepSeek首轮融资估值450亿美元", "title_en": "DeepSeek $45B", "category": "industry"}, {"title_zh": "谷歌AI搜索引用Reddit", "title_en": "Google cites Reddit", "category": "tech"}, {"title_zh": "Brockman披露马斯克离任内幕", "title_en": "Brockman reveals Musk", "category": "industry"}, {"title_zh": "Braintrust确认数据泄露", "title_en": "Braintrust breach", "category": "tech"}, {"title_zh": "SAP 11.6亿收购AI实验室", "title_en": "SAP acquires lab", "category": "industry"}, {"title_zh": "Meta收购机器人公司", "title_en": "Meta robotics", "category": "tech"}, {"title_zh": "五角大楼部署机密网络AI", "title_en": "Pentagon AI", "category": "policy"}, {"title_zh": "自学习AI公司估值40亿美元", "title_en": "Self-learning AI $4B", "category": "tech"}]}],
    "stats": [{"num": str(len(daily)), "label_zh": "今日新闻", "label_en": "News Today"}],
    "hotList": [],
    "tags": [],
    "sources": list(set([item["source"] for item in daily])),
    "archiveDates": [date_str, "2026-05-13"]
}

source_counts = Counter([item['source'] for item in daily])
for idx, (source, count) in enumerate(source_counts.most_common(5)):
    archive['hotList'].append({"rank": idx + 1, "title_zh": f"{source} 报道 {count} 条", "title_en": f"{count} from {source}", "heat": min(count * 15, 100)})

category_tags = {'tech': ['技术', 'AI模型', '开源'], 'industry': ['产业', '融资', '大厂'], 'policy': ['政策', '监管', '合规'], 'finance': ['金融', '市场', '股价']}
all_tags = []
for item in daily:
    cat = item.get('category', 'tech')
    all_tags.extend(category_tags.get(cat, ['AI前沿']))
archive['tags'] = list(dict.fromkeys(all_tags))[:8]

with open(f'/root/.openclaw/workspace/ai-news-site/data/news/{date_str}.json', 'w', encoding='utf-8') as f:
    json.dump(archive, f, ensure_ascii=False, indent=2)

print(f'✅ 历史归档已保存: data/news/{date_str}.json')
print(f'   Breaking: {len(breaking)}  Daily: {len(daily)}')
