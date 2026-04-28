#!/bin/bash
# AI前线 - 一键更新脚本
# 用法: ./scripts/update.sh [YYYY-MM-DD]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SITE_DIR="$(dirname "$SCRIPT_DIR")"
DATE="${1:-$(date +%Y-%m-%d)}"

echo "🚀 AI前线自动更新流水线"
echo "📅 日期: $DATE"
echo "=========================="

# 1. 生成HTML
echo "📝 Step 1/3: 生成HTML内容..."
cd "$SITE_DIR"
python3 scripts/generate_and_deploy.py "$DATE"

# 2. 复制到英文站
echo "🌐 Step 2/3: 同步英文站..."
cp -r data/* ../ai-news-site-en/data/ 2>/dev/null || true
cp scripts/generate_and_deploy.py ../ai-news-site-en/scripts/ 2>/dev/null || true
cd ../ai-news-site-en
python3 scripts/generate_and_deploy.py "$DATE"

# 3. 部署中文站
echo "📦 Step 3/3: 部署到 GitHub Pages..."
echo "   中文站..."
cd "$SITE_DIR"
git add .
git commit -m "🤖 Auto-update: $DATE" || true
git push origin main || echo "⚠️ 中文站推送失败，请检查git remote配置"

# 部署英文站
echo "   英文站..."
cd ../ai-news-site-en
git add .
git commit -m "🤖 Auto-update EN: $DATE" || true
git push origin main || echo "⚠️ 英文站推送失败，请检查git remote配置"

echo ""
echo "=========================="
echo "✅ 流水线执行完毕！"
echo "   中文站: https://mjinjiu.github.io/ai-news-daily/"
echo "   英文站: https://mjinjiu.github.io/ai-news-daily/en/"
