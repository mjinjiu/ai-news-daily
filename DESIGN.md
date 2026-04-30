# AI前线 — 项目设计文档（Design Document）
> 版本：v4.1 | 日期：2026-04-28 | 类型：静态站点 + 数据驱动渲染

---

## 1. 项目概述

### 1.1 项目定位
AI前线是一个**每日自动更新的 AI 行业资讯聚合站点**，面向中文和英文读者，提供新闻浏览、深度解读、API 定价对比三大核心功能。

### 1.2 设计哲学
- **零成本托管**：GitHub Pages 免费部署，无服务器费用
- **内容与表现分离**：数据（JSON）与渲染（JS）解耦，支持自动化更新
- **渐进增强**：基础功能无 JS 也能访问，高级功能通过 JS 增强
- **国际化优先**：所有文本内容内置双语支持

### 1.3 技术约束
| 约束 | 说明 |
|------|------|
| 托管平台 | GitHub Pages（仅支持静态文件） |
| 无后端运行时 | 无法运行 Node.js/Python 服务端代码 |
| 无数据库 | 数据以 JSON 文件形式存储 |
| 免费优先 | 所有依赖服务必须免费或零成本 |

---

## 2. 需求分析

### 2.1 功能需求（Functional Requirements）

#### FR-01 新闻浏览
- 展示每日 AI 行业新闻，含头条区（Breaking）和日常新闻列表
- 新闻分类：重磅（Breaking）、行业（Industry）、技术（Tech）、政策（Policy）
- 每条新闻包含：标题（中英双语）、摘要、来源、日期、原文链接
- 本周回顾时间线，按周一至周日聚合

#### FR-02 深度解读
- 对重要事件提供深度分析文章
- 每篇含：反直觉观点（3条）、争议焦点（正反方）、未来预测
- 支持分页浏览历史解读

#### FR-03 API 定价对比
- 国际模型（USD）与国产模型（RMB）价格表
- 订阅方案对比卡片
- 价格档位视觉标识（旗舰/均衡/超值/免费）

#### FR-04 国际化
- 一键中英语言切换
- 所有用户可见文本支持双语
- 语言偏好本地持久化（localStorage）

#### FR-05 广告位预留
- 顶部横幅、信息流、侧边栏、底部四个广告位
- 支持通过配置启用/禁用，未启用时显示占位提示

### 2.2 非功能需求（Non-Functional Requirements）

#### NFR-01 性能
- 首屏加载 < 2s（国内 4G 网络）
- JSON 数据文件 < 100KB
- 支持浏览器缓存（静态文件 hash 或版本控制）

#### NFR-02 可访问性（Accessibility）
- 符合 WCAG 2.1 AA 标准
- 支持键盘导航（Tab/Enter）
- 屏幕阅读器友好（ARIA 标签）
- 支持跳过导航（Skip Link）

#### NFR-03 SEO
- 可被搜索引擎完整索引（预渲染或 SSR 效果）
- 每个板块有独立标题和 meta 描述
- 支持 Open Graph 和 Twitter Card 社交分享

#### NFR-04 安全性
- 无 XSS 漏洞（所有动态内容必须转义）
- 内容审核流程（AI 生成内容需人工确认）
- 来源可信度验证

#### NFR-05 可维护性
- 代码模块化，职责分离
- 数据格式版本化，向后兼容
- 自动化更新工作流

---

## 3. 架构设计

### 3.1 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      用户浏览器                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  GitHub Pages │  │  fetch API   │  │ localStorage │     │
│  │  (静态资源)    │  │ (JSON数据)   │  │ (语言偏好)   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────┐
│                    GitHub 仓库 (master)                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐  │
│  │index.html│ │ css/     │ │ js/      │ │ data/*.json  │  │
│  │(模板)    │ │ style.css│ │i18n.js   │ │ news.json    │  │
│  │          │ │          │ │renderer.js│ │ analysis.json│  │
│  │          │ │          │ │app.js    │ │ pricing.json │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────┐
│              GitHub Actions (定时触发)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ 检出代码      │  │ 运行Python   │  │ 提交并推送    │      │
│  │ checkout@v4  │  │ update.py    │  │ git push     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────┐
│                   外部服务 (API调用)                         │
│  ┌─────────────────────┐  ┌─────────────────────┐             │
│  │   Kimi API          │  │   OpenAI API        │             │
│  │   (新闻生成)         │  │   (备选)            │             │
│  │   model=kimi-latest │  │   model=gpt-4o-mini │             │
│  └─────────────────────┘  └─────────────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 模块职责

| 模块 | 文件 | 职责 | 依赖 |
|------|------|------|------|
| **国际化** | `js/i18n.js` | 翻译字典、语言切换、插值、持久化 | 无 |
| **渲染引擎** | `js/renderer.js` | 从 JSON 加载数据，生成 DOM | i18n.js |
| **应用逻辑** | `js/app.js` | 导航、事件委托、动画、广告 | i18n.js, renderer.js |
| **更新脚本** | `scripts/update.py` | 调用 API 生成 JSON 数据 | requests |
| **工作流** | `.github/workflows/auto-update.yml` | 定时触发更新 | GitHub Actions |

### 3.3 数据流

```
1. 定时触发 (GitHub Actions cron)
   ↓
2. Python 脚本调用 AI API 生成结构化 JSON
   ↓
3. JSON 文件写入 data/ 目录
   ↓
4. git commit & push 到 master
   ↓
5. GitHub Pages 自动部署（约 30 秒）
   ↓
6. 用户浏览器加载 index.html
   ↓
7. renderer.js fetch(data/*.json) → 解析 → 生成 DOM
   ↓
8. 用户看到最新内容
```

### 3.4 数据格式规范

#### news.json 结构
```json
{
  "meta": {
    "date": "YYYY-MM-DD",
    "updatedAt": "YYYY-MM-DDTHH:MM:SS+08:00",
    "total": 8
  },
  "breaking": [
    {
      "id": "news-001",
      "title_zh": "中文标题",
      "title_en": "English Title",
      "summary_zh": "摘要（100字以内）",
      "summary_en": "Summary (under 150 chars)",
      "date": "MM-DD",
      "source": "来源名称",
      "category": "breaking|industry|tech|policy",
      "url": "https://..."
    }
  ],
  "daily": [...],
  "weekly": [...],
  "stats": [
    { "num": "$135B+", "label_zh": "标签", "label_en": "Label" }
  ],
  "hotList": [...],
  "tags": ["OpenAI", "DeepSeek"],
  "sources": ["Reuters", "Bloomberg"]
}
```

#### 关键设计决策
- **所有文本字段带 `_zh` / `_en` 后缀**：确保语言切换时无需重新请求数据
- **`id` 字段**：用于前端状态管理和追踪，格式统一为 `news-XXX` 或 `analysis-XXX`
- **`url` 必须可访问**：所有新闻链接需为真实 URL，不允许空值
- **`meta.total`**：必须与 `breaking.length + daily.length` 一致，前端校验

---

## 4. 技术选型与理由

### 4.1 前端技术栈

| 技术 | 版本 | 理由 |
|------|------|------|
| 原生 HTML5 | — | 零构建步骤，GitHub Pages 直接托管 |
| 原生 CSS3 | — | 无 CSS 框架依赖，体积最小 |
| Vanilla JS (ES5) | — | 无构建工具，兼容性最好（支持 IE11） |
| Fetch API | — | 现代浏览器原生支持，无需 polyfill |

**不选框架的原因**：
- React/Vue 需要构建步骤和 bundler，增加部署复杂度
- 项目交互简单（切换板块、语言切换、分页），原生 JS 足够
- 首屏性能：无框架开销，HTML 直接渲染

### 4.2 部署技术栈

| 技术 | 理由 |
|------|------|
| GitHub Pages | 免费、稳定、自动部署、CDN 全球分发 |
| GitHub Actions | 原生集成、定时触发、免费额度充足 |
| Python 3.11 | 脚本语言简洁、requests 库成熟 |

### 4.3 未来可扩展技术

| 能力 | 推荐技术 | 何时引入 |
|------|---------|---------|
| 后端 API | Vercel Serverless Functions | 需要用户系统或复杂计算 |
| 数据库 | MongoDB Atlas 免费层 / Supabase | 数据量 > 500 条/天或需要全文搜索 |
| 搜索 | Algolia 免费层 | 需要站内搜索 |
| 订阅推送 | Resend / SendGrid 免费层 | 需要邮件订阅 |

---

## 5. 开发流程（Development Workflow）

### 5.1 标准开发流程

```
需求分析 → 数据结构设计 → 模板开发 → 渲染逻辑 → 交互逻辑 → 样式开发 → 测试 → 部署
```

#### Step 1: 需求分析
- 明确功能需求（FR）和非功能需求（NFR）
- 确认数据格式（参考第 3.4 节）
- 评估是否需要新增板块或修改数据结构

#### Step 2: 数据结构设计
- 更新 `data/*.json` 的 schema（如果有新增字段）
- 确保向后兼容（旧数据在新代码中不报错）
- 编写 JSON schema 校验（可选，用于 CI）

#### Step 3: 模板开发（index.html）
- 添加新板块容器（`<section>` + `<div id="xxx">`）
- 添加 ARIA 标签（`aria-labelledby`、`role`）
- 确保 Skip Link 可跳转到新内容

#### Step 4: 渲染逻辑（renderer.js）
- 新增渲染函数（如 `renderNewSection(containerId, data)`）
- 使用 `escapeHtml()` 防止 XSS
- 使用 `getText(item, field)` 获取当前语言文本
- 将新函数加入 `loadAll()` 调用链

#### Step 5: 交互逻辑（app.js）
- 如需新交互，使用**事件委托**（`document.addEventListener`）
- 如需新动画，添加 `anim-initial` → `anim-visible` 类
- 如需新状态，使用模块级闭包变量（不污染全局）

#### Step 6: 样式开发（style.css）
- 遵循现有命名规范（BEM 风格）
- 确保响应式（mobile-first，断点：768px, 1024px）
- 使用 CSS 变量，不硬编码颜色值

#### Step 7: 测试
- **本地测试**：`python3 -m http.server 8080`
- **功能测试**：切换语言、切换板块、点击新闻、分页、动画
- **可访问性测试**：Tab 键导航、屏幕阅读器
- **性能测试**：Lighthouse 评分 > 90

#### Step 8: 部署
- `git add . && git commit -m "feat: xxx" && git push origin master`
- GitHub Pages 自动更新（约 30 秒）

### 5.2 代码规范

#### JavaScript
```javascript
// 使用 IIFE 封装模块，避免全局污染
const Module = (function() {
  'use strict';
  // 私有变量
  let privateVar = 0;
  
  // 工具函数
  function helper() { }
  
  // 公开 API
  return {
    publicMethod: function() { }
  };
})();

// 使用 var 而非 const/let（ES5 兼容）
// 字符串拼接用 +，不使用模板字符串
```

#### CSS
```css
/* 命名规范：kebab-case */
.news-item { }
.card-featured { }

/* 使用 CSS 变量 */
color: var(--text-primary);

/* 响应式断点 */
@media (max-width: 767px) { /* 移动端 */ }
@media (min-width: 768px) and (max-width: 1023px) { /* 平板 */ }
@media (min-width: 1024px) { /* 桌面 */ }
```

#### HTML
```html
<!-- 语义化标签 -->
<nav role="navigation" aria-label="主导航">
<main role="main" id="mainContent">
<aside role="complementary" aria-label="侧边栏">
<footer role="contentinfo">

<!-- 所有可点击元素必须有 data-source-url 或 href -->
<div data-source-url="https://..." tabindex="0" role="link">
```

### 5.3 Git 提交规范

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat:` | 新功能 | `feat: 添加API定价板块` |
| `fix:` | 修复 bug | `fix: 修复CSS变量缺失` |
| `docs:` | 文档更新 | `docs: 更新README部署说明` |
| `refactor:` | 重构 | `refactor: 提取公共渲染函数` |
| `chore:` | 杂项 | `chore: 更新依赖版本` |
| `auto:` | 自动更新 | `auto: 2026-04-28 新闻数据` |

---

## 6. 安全设计

### 6.1 XSS 防护

所有动态渲染的内容必须经过 HTML 转义：

```javascript
function escapeHtml(str) {
  if (!str) return '';
  var div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}
```

**禁止**：
- `element.innerHTML = userContent`
- `document.write(...)`

**允许**：
- `element.textContent = escapeHtml(content)`
- `element.innerHTML = '<safe-tag>' + escapeHtml(content) + '</safe-tag>'`

### 6.2 内容审核流程

```
AI 生成内容 → 自动过滤（敏感词/来源验证） → 待审核（PR/草稿） → 人工确认 → 发布
```

**自动过滤规则**：
- 敏感词黑名单（政治、色情、暴力、谣言）
- 来源可信度评分（< 6 分的来源标记为待核实）
- URL 可访问性检查（HTTP 200）

**人工确认触发条件**（满足任一）：
- 包含政策类新闻
- 涉及诉讼、争议、裁员等敏感话题
- 来源可信度 < 8

### 6.3 API Key 安全

- 所有 API Key 存储在 GitHub Secrets，不提交到仓库
- 本地开发使用 `.env` 文件（已加入 `.gitignore`）
- Token 定期轮换（建议 90 天）

---

## 7. 性能优化

### 7.1 加载策略

| 资源 | 策略 |
|------|------|
| `index.html` | 直接加载，无阻塞 |
| `css/style.css` | `<head>` 内联或同步加载 |
| `js/*.js` | 底部 `<script>` 异步加载 |
| `data/*.json` | `fetch()` 按需加载，浏览器缓存 |
| `images/og-cover.png` | 预加载或懒加载 |

### 7.2 缓存策略

```html
<!-- 静态文件加版本号（手动或 CI 自动生成） -->
<link rel="stylesheet" href="css/style.css?v=4.1.0">
<script src="js/app.js?v=4.1.0"></script>

<!-- JSON 文件使用时间戳避免缓存 -->
fetch('data/news.json?t=' + Date.now())
```

### 7.3 性能指标

| 指标 | 目标 | 测量工具 |
|------|------|---------|
| FCP (First Contentful Paint) | < 1.5s | Lighthouse |
| LCP (Largest Contentful Paint) | < 2.5s | Lighthouse |
| TTI (Time to Interactive) | < 3s | Lighthouse |
| CLS (Cumulative Layout Shift) | < 0.1 | Lighthouse |
| JSON 加载时间 | < 500ms | DevTools Network |

---

## 8. 扩展路线图

### Phase 1: 内容安全加固（当前）
- [x] 数据与渲染分离
- [x] i18n 国际化
- [x] 事件委托架构
- [ ] 敏感词过滤（scripts/update.py）
- [ ] 来源可信度评分
- [ ] PR 审核流程（GitHub Actions 创建 PR 而非直接推送）

### Phase 2: 功能增强（1-2 个月）
- [ ] 全文搜索（Lunr.js 客户端索引，无需后端）
- [ ] 邮件订阅（Formspree 免费层，无需自建后端）
- [ ] RSS 订阅输出（生成 rss.xml 静态文件）
- [ ] 历史归档分页（按周/按月浏览）
- [ ] 夜间模式（CSS `prefers-color-scheme`）

### Phase 3: 嫁接后端能力（2-3 个月）
- [ ] Vercel Serverless Functions（用户订阅邮箱存储）
- [ ] MongoDB Atlas 免费层（点击量统计）
- [ ] 用户收藏功能（浏览器 IndexedDB + 可选云端同步）
- [ ] 评论系统（Giscus/Utterances，基于 GitHub Issues）

### Phase 4: 商业化探索（3-6 个月）
- [ ] 广告接入（Google AdSense / 百度联盟）
- [ ] 付费深度报告（Stripe 支付 + 内容解锁）
- [ ] API 服务（提供结构化 AI 新闻数据接口）
- [ ] 移动端 App（PWA 封装或小程序）

---

## 9. 故障排查

### 9.1 常见问题

| 现象 | 原因 | 解决 |
|------|------|------|
| 页面空白 | `data/*.json` 404 或格式错误 | 检查文件路径、JSON 语法 |
| 语言切换无效 | `data-zh`/`data-en` 属性缺失 | 确认 renderer.js 正确渲染 |
| 动画不触发 | JS 加载失败或 IntersectionObserver 不支持 | 检查 console、加 fallback |
| 广告位显示异常 | 容器 ID 不匹配 | 检查 HTML id 与 CSS 选择器 |
| 更新不生效 | GitHub Pages 缓存 | 清除浏览器缓存或加版本号 |

### 9.2 调试方法

```javascript
// 在浏览器控制台运行
Renderer.loadAll();          // 手动重新加载数据
I18N.setLang('en');          // 手动切换语言
window.AIFrontline.initAds({top: true});  // 手动启用广告

// 查看当前数据
fetch('data/news.json').then(r => r.json()).then(console.log);
```

---

## 10. 参考文档

- [GitHub Pages 文档](https://docs.github.com/en/pages)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [WCAG 2.1 指南](https://www.w3.org/WAI/WCAG21/quickref/)
- [Kimi API 文档](https://platform.moonshot.cn/)
- [Open Graph 协议](https://ogp.me/)

---

*本文档与代码同步维护。如有变更，同步更新版本号。*
