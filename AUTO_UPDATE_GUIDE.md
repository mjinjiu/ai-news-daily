# AI前线 — 自动化工作流设计

## 方案一：GitHub Actions + AI API（推荐）

每日定时调用 AI 接口生成新闻 JSON，自动推送到仓库。

### 文件结构

```
.github/
  workflows/
    auto-update.yml    # GitHub Actions 定时任务
scripts/
  update.py            # Python 更新脚本
  sources.py           # 新闻源配置
  requirements.txt     # Python 依赖
```

### 配置步骤

**1. 设置 GitHub Secrets**

访问仓库 Settings → Secrets and variables → Actions → New repository secret

| Secret 名称 | 说明 | 值示例 |
|------------|------|--------|
| `KIMI_API_KEY` | Kimi API Key | `sk-xxxxxxxx` |
| `GITHUB_TOKEN` | GitHub Token（自动提供） | `${{ secrets.GITHUB_TOKEN }}` |

**2. 启用 GitHub Pages**

Settings → Pages → Source 选择 `master` 分支 → `/` (root)

**3. 工作流自动运行**

- 每天北京时间 08:00 自动触发
- 抓取最新 AI 新闻 → 生成 JSON → 推送 → 网站自动更新

## 方案二：Kimi Agent 辅助

如果你有一个 Kimi Agent，可以用这个 Prompt 让它按格式输出 JSON：

```
你是 AI前线 的新闻编辑。请收集今日（{date}）最重要的 AI 行业新闻，按以下 JSON 格式输出：

{
  "meta": { "date": "YYYY-MM-DD", "total": N },
  "breaking": [...],  // 1-2 条重磅
  "daily": [...],     // 6-10 条日常
  "weekly": [...],     // 本周回顾
  "stats": [...],      // 关键数字
  "hotList": [...],    // 8 条热榜
  "tags": [...],       // 热门标签
  "sources": [...]     // 信源列表
}

分类标签：breaking（重磅）、industry（行业）、tech（技术）、policy（政策）
每条新闻必须包含：title_zh、title_en、excerpt_zh、excerpt_en、source、url、category、date
```

## 方案三：混合方案（最实用）

1. GitHub Actions 每天定时运行 Python 脚本
2. Python 脚本调用 Kimi API 生成结构化内容
3. 自动提交 JSON 文件并推送到 GitHub
4. GitHub Pages 自动部署更新

---

## 监控与调试

- 每次运行结果可在 Actions 标签页查看
- 失败时会自动发送邮件通知
- 可手动触发运行（Actions → auto-update → Run workflow）
