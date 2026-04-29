#!/bin/bash
# AI前线 - 一键部署脚本
# 支持：GitHub Pages

set -e

SITE_ZH="/root/.openclaw/workspace/ai-news-site"
SITE_EN="/root/.openclaw/workspace/ai-news-site-en"

echo "🚀 AI前线 - 一键部署"
echo "======================"

# 中文站
echo "📦 部署中文站..."
cd "$SITE_ZH"
git add .
git commit -m "🤖 Auto-update: $(date +%Y-%m-%d)" || true
git push origin master
echo "✅ 中文站部署成功"

# 英文站
echo "📦 部署英文站..."
cd "$SITE_EN"
git add .
git commit -m "🤖 Auto-update EN: $(date +%Y-%m-%d)" || true
git push origin master
echo "✅ 英文站部署成功"

echo ""
echo "======================"
echo "🎉 双站部署完成！"
echo "   中文: https://mjinjiu.github.io/ai-news-daily/"
echo "   英文: https://mjinjiu.github.io/ai-news-daily/en/"
