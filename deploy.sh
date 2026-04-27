#!/bin/bash
# AI前线 - 一键部署脚本
# 支持：GitHub Pages / Vercel / Netlify

set -e

SITE_DIR="/root/.openclaw/workspace/ai-news-site"
echo "🚀 AI前线部署脚本"
echo "=================="

# 检查git
echo "📦 检查环境..."
if ! command -v git &> /dev/null; then
    echo "❌ 需要安装 git"
    exit 1
fi

cd "$SITE_DIR"

# 初始化git（如果没有）
if [ ! -d .git ]; then
    echo "🔧 初始化Git仓库..."
    git init
    git branch -m main
fi

echo ""
echo "请选择部署平台："
echo "1) GitHub Pages (推荐 - 免费稳定)"
echo "2) Vercel (推荐 - 自动部署)"
echo "3) Netlify (推荐 - 拖拽部署)"
echo "4) 仅本地预览"
echo ""

read -p "输入选项 [1-4]: " choice

case $choice in
    1)
        echo "📋 GitHub Pages 部署指南："
        echo ""
        echo "1. 在 GitHub 创建新仓库 (如: ai-news-daily)"
        echo "2. 运行以下命令："
        echo ""
        echo "   git remote add origin https://github.com/你的用户名/ai-news-daily.git"
        echo "   git add ."
        echo "   git commit -m 'Initial commit'"
        echo "   git push -u origin main"
        echo ""
        echo "3. 进入仓库 Settings → Pages → Source 选择 main 分支"
        echo "4. 访问 https://你的用户名.github.io/ai-news-daily"
        echo ""
        ;;
    2)
        echo "📋 Vercel 部署指南："
        echo ""
        echo "1. 安装 Vercel CLI: npm i -g vercel"
        echo "2. 运行: vercel --prod"
        echo "3. 按提示登录并部署"
        echo ""
        ;;
    3)
        echo "📋 Netlify 部署指南："
        echo ""
        echo "1. 访问 https://app.netlify.com/drop"
        echo "2. 将 $SITE_DIR 文件夹拖拽上传"
        echo "3. 自动获得公网链接"
        echo ""
        ;;
    4)
        echo "🖥️  本地预览模式"
        echo "运行: python3 -m http.server 8080"
        echo "访问: http://localhost:8080"
        ;;
    *)
        echo "无效选项"
        exit 1
        ;;
esac

echo "✅ 部署指南已显示"
