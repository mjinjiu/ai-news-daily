import json
from collections import Counter

# 读取 current.json
with open('data/news/current.json', 'r') as f:
    data = json.load(f)

# ===== 1. 更新 meta =====
data['meta']['date'] = '2026-05-17'
data['meta']['updatedAt'] = '2026-05-17T08:42:03+08:00'
data['meta']['total'] = 43

# ===== 2. 添加5月17日重磅新闻 =====
new_breaking = [
    {
        "id": "news-2026-05-17-001",
        "title_zh": "OpenAI启动40亿美元新公司，专为企业部署AI解决方案",
        "title_en": "OpenAI Starts $4B Company to Help Businesses Deploy AI",
        "summary_zh": "OpenAI成立一家价值40亿美元的新公司，专门帮助企业部署AI解决方案。这标志着OpenAI从模型提供商向企业服务平台转型的关键一步，将直接挑战传统IT咨询和系统集成商的市场地位。",
        "summary_en": "OpenAI starts a $4B company dedicated to helping businesses deploy AI solutions, marking a key shift from model provider to enterprise service platform.",
        "date": "05-17",
        "source": "Singularity.Kiwi / Reuters",
        "category": "breaking",
        "url": "https://singularity.kiwi/daily-news-2026-05-17/"
    },
    {
        "id": "news-2026-05-17-002",
        "title_zh": "美国政府扩展前沿AI预测试，Google/Microsoft/xAI正式加入",
        "title_en": "US Government Expands Frontier AI Pre-Testing, Google/Microsoft/xAI Join",
        "summary_zh": "Google、Microsoft和xAI同意让美国商务部在发布前评估其AI模型，加入OpenAI和Anthropic的行列。评估将涵盖生物武器设计、网络安全攻击能力和社会级操纵等潜在风险。这是美国最接近正式AI评估制度的举措。",
        "summary_en": "Google, Microsoft and xAI agree to give US Commerce Department pre-release access to evaluate their AI models, joining OpenAI and Anthropic. Evaluations cover bioweapons, cyber offensive capabilities and societal-scale manipulation risks.",
        "date": "05-17",
        "source": "Singularity.Kiwi / Reuters",
        "category": "breaking",
        "url": "https://singularity.kiwi/daily-news-2026-05-17/"
    }
]

data['breaking'] = new_breaking + data['breaking']

# ===== 3. 添加5月17日日常新闻 =====
new_daily = [
    {
        "id": "news-2026-05-17-003",
        "title_zh": "OpenAI与Plaid达成合作，ChatGPT将接入个人银行数据",
        "title_en": "OpenAI Partners with Plaid for Personal Finance in ChatGPT",
        "excerpt_zh": "OpenAI与Plaid合作，让用户可以连接银行账户、信用卡和投资账户，然后向ChatGPT咨询支出、预算和财务规划问题。这是主流AI助手首次深度整合消费金融数据。",
        "excerpt_en": "OpenAI partners with Plaid to let users connect bank accounts and ask ChatGPT about spending, budgeting and financial planning.",
        "date": "05-17",
        "source": "Bloomberg / Singularity.Kiwi",
        "category": "industry",
        "url": "https://singularity.kiwi/daily-news-2026-05-17/"
    },
    {
        "id": "news-2026-05-17-004",
        "title_zh": "Intercom更名为Fin，推出首个'AI管理AI'的元代理",
        "title_en": "Intercom Becomes Fin, Launches AI Agent That Manages AI Agents",
        "excerpt_zh": "Intercom更名为Fin，推出Fin Operator——一个专门管理其他AI客服代理的AI代理。这是首个'元代理'商业化案例：AI监督AI，人类从监督回路中被移除。",
        "excerpt_en": "Intercom renames to Fin and launches Fin Operator, an AI agent that manages other AI agents. First commercial meta-agent case.",
        "date": "05-17",
        "source": "TechCrunch / Singularity.Kiwi",
        "category": "industry",
        "url": "https://singularity.kiwi/daily-news-2026-05-17/"
    },
    {
        "id": "news-2026-05-17-005",
        "title_zh": "微软Superintelligence团队再挖角，Ali Farhadi等10名AI研究员加盟",
        "title_en": "Microsoft Hires 10 More AI Researchers from Allen Institute",
        "excerpt_zh": "至少10名前Allen Institute for AI研究员加入微软Superintelligence团队，包括前CEO Ali Farhadi。这引发对独立AI研究机构能否与Big Tech竞争的担忧。",
        "excerpt_en": "At least 10 former Allen Institute researchers join Microsoft Superintelligence team, including former CEO Ali Farhadi.",
        "date": "05-17",
        "source": "GeekWire / Singularity.Kiwi",
        "category": "industry",
        "url": "https://singularity.kiwi/daily-news-2026-05-17/"
    },
    {
        "id": "news-2026-05-17-006",
        "title_zh": "欧盟正式推迟高风险AI规则实施超一年",
        "title_en": "EU Postpones High-Risk AI Rules for Over a Year",
        "excerpt_zh": "欧盟正式推迟高风险AI系统的监管规则实施时间表，为企业争取更多合规准备时间。原定于近期生效的AI法案实施细则被延后。",
        "excerpt_en": "EU officially postpones implementation of high-risk AI system regulations by over a year.",
        "date": "05-17",
        "source": "EU Official / Singularity.Kiwi",
        "category": "policy",
        "url": "https://singularity.kiwi/daily-news-2026-05-17/"
    }
]

data['daily'] = new_daily + data['daily']

# ===== 4. 更新 weekly 摘要 =====
existing_weekly = [w for w in data['weekly'] if w['date'] != '05-17']

week_17_items = []
for item in new_breaking:
    week_17_items.append({
        "title_zh": item['title_zh'][:30] + '...' if len(item['title_zh']) > 30 else item['title_zh'],
        "title_en": item['title_en'][:40] + '...' if len(item.get('title_en','')) > 40 else item.get('title_en', ''),
        "category": item['category']
    })
for item in new_daily:
    week_17_items.append({
        "title_zh": item['title_zh'][:30] + '...' if len(item['title_zh']) > 30 else item['title_zh'],
        "title_en": item['title_en'][:40] + '...' if len(item.get('title_en','')) > 40 else item.get('title_en', ''),
        "category": item['category']
    })

data['weekly'] = existing_weekly + [{
    "day": "周日",
    "day_en": "Sun",
    "date": "05-17",
    "count": len(new_breaking) + len(new_daily),
    "items": week_17_items
}]

# ===== 5. 更新 stats =====
data['stats'] = [
    {
        "num": str(len(data['breaking']) + len(data['daily'])),
        "label_zh": "本周新闻",
        "label_en": "News This Week"
    }
]

# ===== 6. 更新 hotList =====
cat_counts = Counter()
for item in data['breaking']:
    cat_counts[item.get('category', 'breaking')] += 1
for item in data['daily']:
    cat_counts[item.get('category', 'industry')] += 1

breaking_count = cat_counts.get('breaking', 0)
industry_count = cat_counts.get('industry', 0)
tech_count = cat_counts.get('tech', 0)
policy_count = cat_counts.get('policy', 0)

data['hotList'] = [
    {"rank": 1, "title_zh": f"重磅新闻 {breaking_count} 条", "title_en": f"{breaking_count} Breaking News", "heat": min(breaking_count * 8, 80)},
    {"rank": 2, "title_zh": f"行业动态 {industry_count} 条", "title_en": f"{industry_count} Industry Updates", "heat": min(industry_count * 3, 75)},
    {"rank": 3, "title_zh": f"技术前沿 {tech_count} 条", "title_en": f"{tech_count} Tech Updates", "heat": min(tech_count * 8, 60)},
    {"rank": 4, "title_zh": f"政策监管 {policy_count} 条", "title_en": f"{policy_count} Policy Updates", "heat": min(policy_count * 10, 50)}
]

# ===== 7. 更新 sources =====
new_sources = ["Singularity.Kiwi", "GeekWire"]
for s in new_sources:
    if s not in data['sources']:
        data['sources'].append(s)

# ===== 8. 保存 =====
with open('data/news/current.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("news/current.json 更新完成")
print(f"总新闻数: {len(data['breaking'])} breaking + {len(data['daily'])} daily = {len(data['breaking']) + len(data['daily'])}")
print(f"本周范围: {data['meta']['weekLabel']}")
print(f"更新日期: {data['meta']['date']}")
