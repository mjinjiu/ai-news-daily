# AI前线 — AI News Daily

> ⚡ 每日自动更新的人工智能资讯聚合网站  
> 🌐 在线访问：https://mjinjiu.github.io/ai-news-daily/

## 🆕 v4.1 重构亮点

- ✅ **内容与渲染完全分离** — 所有内容来自 `data/*.json`，前端动态渲染
- ✅ **完整 i18n 国际化** — 中英双语切换，翻译字典集中管理
- ✅ **事件委托架构** — 全局事件监听，动态元素无需重复绑定
- ✅ **CSS 动画安全降级** — 默认 `opacity:1`，JS 渐进增强
- ✅ **完整 SEO + 可访问性** — Open Graph、Twitter Card、ARIA 标签、Skip Link
- ✅ **响应式侧边栏策略** — `<768px` 完全隐藏，`768-1023px` 隐藏，`≥1024px` 显示
- ✅ **模块化代码结构** — `i18n.js` + `renderer.js` + `app.js` 职责分离

## 📁 文件结构

```
ai-news-daily/
├── index.html              # 主页面模板（零硬编码内容）
├── css/
│   └── style.css           # 样式文件（修复所有变量缺失、重复规则）
├── js/
│   ├── i18n.js             # 国际化模块（翻译字典 + 插值）
│   ├── renderer.js         # 数据渲染引擎（从 JSON 渲染所有内容）
│   └── app.js              # 主应用逻辑（事件委托、导航、动画）
├── data/
│   ├── news.json           # 新闻数据（头条 + 今日 + 本周回顾 + 统计）
│   ├── analysis.json       # 深度解读数据（观点 + 争议 + 预测）
│   └── pricing.json        # API定价数据（国际/国产/订阅方案）
├── images/
│   └── og-cover.png        # 社交分享封面图
├── deploy.sh               # 一键部署脚本
└── README.md               # 本文件
```

## 🔄 自动更新架构

1. **数据来源** — 爬虫/脚本抓取新闻 → 生成 `data/*.json`
2. **前端渲染** — `renderer.js` 通过 `fetch()` 加载 JSON，动态生成 DOM
3. **零 HTML 重写** — 无需修改 `index.html`，仅更新数据文件即可
4. **缓存友好** — 静态 HTML + 可缓存的 JSON + 浏览器本地存储语言偏好

## 🌍 部署

### GitHub Pages（推荐）

```bash
# 首次部署
git init
git remote add origin https://github.com/你的用户名/ai-news-daily.git
git add .
git commit -m "v4.1: data-driven rendering"
git push -u origin main

# 然后到 Settings → Pages → Source 选择 main 分支
```

### 本地预览

```bash
cd ai-news-daily
python3 -m http.server 8080
# 访问 http://localhost:8080
```

## 📊 数据来源

- **国际**：Decrypt, Reuters, Bloomberg
- **国内**：新浪财经, 新浪科技, TMT Post, 36氪
- **政策**：Gov.cn
- **技术**：芯智讯, 极客公园, DoNews, 极客公园

## 📜 许可

MIT License — 可自由 fork、修改、商用。
