// renderer.js - AI前线渲染引擎 v4.0
// 从JSON数据动态渲染页面内容，模板与数据分离

(function() {
  'use strict';

  // ========== 配置 ==========
  const CONFIG = {
    dataPath: 'data/content.json',
    lang: 'zh', // 'zh' | 'en'，后续可扩展语言切换
    itemsPerPage: 10
  };

  // ========== 工具函数 ==========
  const $ = (sel, ctx) => (ctx || document).querySelector(sel);
  const $$ = (sel, ctx) => Array.from((ctx || document).querySelectorAll(sel));

  function t(obj, key) {
    // 根据当前语言返回对应文本
    const enKey = key + 'En';
    if (CONFIG.lang === 'en' && obj[enKey]) return obj[enKey];
    return obj[key] || obj[enKey] || '';
  }

  // ========== 渲染函数 ==========

  // 1. 渲染页面头部
  function renderPageHeader(data) {
    const h = data.pageHeader;
    if (!h) return;
    const titleEl = $('.page-header h1');
    const subtitleEl = $('.page-header .subtitle');
    const timeEl = $('.page-header .update-time');
    if (titleEl) titleEl.textContent = t(h, 'title');
    if (subtitleEl) subtitleEl.textContent = t(h, 'subtitle');
    if (timeEl) timeEl.textContent = (CONFIG.lang === 'en' ? 'Updated: ' : '更新于：') + h.updateTime;
  }

  // 2. 渲染头条
  function renderFeatured(data) {
    const container = $('.featured-row');
    if (!container || !data.featured) return;
    container.innerHTML = data.featured.map(item => `
      <article class="card featured" data-source-url="${item.url}">
        <div class="card-tag tag-breaking">${t(item, 'tag')} ${item.tagEn}</div>
        <h2>${t(item, 'title')}</h2>
        <p class="card-meta">${item.date} · ${item.source}</p>
        <p class="card-summary">${t(item, 'summary')}</p>
      </article>
    `).join('');
  }

  // 3. 渲染今日新闻
  function renderTodayNews(data) {
    const section = data.todayNews;
    if (!section) return;

    // 更新头部
    const header = $('.news-today .section-header');
    if (header) {
      header.querySelector('h2').textContent = CONFIG.lang === 'en' ? "📰 Today's News" : "📰 今日新闻";
      header.querySelector('.date-badge').textContent = t(section, 'date');
      header.querySelector('.count').textContent = t(section, 'count');
    }

    // 渲染列表
    const list = $('.news-list');
    if (!list) return;
    list.innerHTML = section.items.map(item => `
      <div class="news-item" data-category="${item.category}" data-source-url="${item.url}">
        <div class="news-bar ${item.category}"></div>
        <div class="news-body">
          <h3>${t(item, 'title')}</h3>
          <p class="news-excerpt">${t(item, 'excerpt')}</p>
          <div class="news-footer">
            <span class="news-tag tag-${item.category}">${tagLabel(item.category)} ${item.category}</span>
            <span class="news-source">${item.source}</span>
            <span class="news-date">${item.date}</span>
          </div>
        </div>
      </div>
    `).join('');
  }

  function tagLabel(cat) {
    const map = { tech: '技术', industry: '行业', policy: '政策' };
    const mapEn = { tech: 'Tech', industry: 'Industry', policy: 'Policy' };
    return CONFIG.lang === 'en' ? (mapEn[cat] || cat) : (map[cat] || cat);
  }

  // 4. 渲染本周回顾
  function renderWeekly(data) {
    const section = data.weeklyReview;
    if (!section) return;

    const header = $('.weekly-review .section-header');
    if (header) {
      header.querySelector('h2').textContent = CONFIG.lang === 'en' ? "📅 Weekly Review" : "📅 本周回顾";
      header.querySelector('.range').textContent = t(section, 'range');
    }

    const timeline = $('.week-timeline');
    if (!timeline) return;
    timeline.innerHTML = section.days.map(day => {
      if (day.empty) {
        return `
          <div class="day-group">
            <div class="day-header">
              <span class="day-name">${t(day, 'name')}</span>
              <span class="day-date">${day.date}</span>
              <span class="day-count">${day.count}</span>
            </div>
            <ul class="day-list"><li class="empty">${CONFIG.lang === 'en' ? 'No news' : '暂无新闻'}</li></ul>
          </div>
        `;
      }
      return `
        <div class="day-group">
          <div class="day-header">
            <span class="day-name">${t(day, 'name')}</span>
            <span class="day-date">${day.date}</span>
            <span class="day-count">${t(day, 'count')}</span>
          </div>
          <ul class="day-list">
            ${day.items.map(it => `
              <li><span class="dot ${it.category}"></span><a href="${it.url}" target="_blank" rel="noopener">${t(it, 'title')}</a></li>
            `).join('')}
          </ul>
        </div>
      `;
    }).join('');
  }

  // 5. 渲染统计速览
  function renderStats(data) {
    const section = data.stats;
    if (!section) return;
    const titleEl = $('.stats-section h2');
    if (titleEl) titleEl.textContent = t(section, 'title');
    const row = $('.stats-row');
    if (!row) return;
    row.innerHTML = section.items.map(item => `
      <div class="stat-item">
        <span class="stat-num">${item.value}</span>
        <span class="stat-label">${t(item, 'label')}</span>
      </div>
    `).join('');
  }

  // 6. 渲染热榜
  function renderHotTopics(data) {
    if (!data.hotTopics) return;
    const list = $('.hot-list');
    if (!list) return;
    list.innerHTML = data.hotTopics.map((item, i) => `
      <li><a href="${item.url}" target="_blank" rel="noopener">${t(item, 'title')}</a></li>
    `).join('');
  }

  // 7. 渲染标签云
  function renderTags(data) {
    if (!data.tags) return;
    const container = $('.tag-cloud .tags');
    if (!container) return;
    const tags = CONFIG.lang === 'en' && data.tagsEn ? data.tagsEn : data.tags;
    container.innerHTML = tags.map(tag => `<span class="tag">${tag}</span>`).join('');
  }

  // 8. 渲染归档
  function renderArchives(data) {
    if (!data.archives) return;
    const list = $('.archive-list');
    if (!list) return;
    list.innerHTML = data.archives.map(item => {
      if (item.empty) {
        return `<li class="archive-empty"><span class="archive-week">${t(item, 'week')}</span><span class="archive-count">${item.count}</span></li>`;
      }
      return `<li><a href="${item.url}"><span class="archive-week">${t(item, 'week')}</span><span class="archive-count">${t(item, 'count')}</span></a></li>`;
    }).join('');
  }

  // 9. 渲染信源
  function renderSources(data) {
    if (!data.sources) return;
    const container = $('.source-list');
    if (!container) return;
    container.innerHTML = data.sources.map(s => `<span class="source-tag">${s}</span>`).join('');
  }

  // 10. 渲染深度解读
  function renderAnalysis(data) {
    const section = data.analysis;
    if (!section) return;

    // 头部
    const header = $('#analysisSection .page-header');
    if (header) {
      header.querySelector('h1').textContent = t(section, 'title');
      header.querySelector('.subtitle').textContent = t(section, 'subtitle');
      header.querySelector('.update-time').textContent = (CONFIG.lang === 'en' ? 'Updated: ' : '更新于：') + section.updateTime;
    }

    const container = $('.analysis-featured');
    if (!container || !section.articles) return;

    container.innerHTML = section.articles.map(article => {
      const sectionsHtml = article.sections.map(sec => {
        if (sec.type === 'summary') {
          return `
            <div class="analysis-section">
              <h3>${t(sec, 'title')}</h3>
              <p>${t(sec, 'content')}</p>
            </div>
          `;
        }
        if (sec.type === 'analysis') {
          const pointsHtml = sec.points.map(p => `
            <div class="point">
              <span class="point-num">${p.num}</span>
              <div class="point-content">
                <strong>${t(p, 'title')}</strong>
                <div class="surface-vs-insight">
                  <p class="surface">${t(p, 'surface')}</p>
                  <p class="insight">${t(p, 'insight')}</p>
                </div>
              </div>
            </div>
          `).join('');
          return `
            <div class="analysis-section">
              <h3>${t(sec, 'title')}</h3>
              <div class="analysis-points">${pointsHtml}</div>
            </div>
          `;
        }
        if (sec.type === 'debate') {
          return `
            <div class="analysis-section debate">
              <h3>${t(sec, 'title')}</h3>
              <div class="debate-grid">
                <div class="debate-side pro">
                  <h4>${t(sec.pro, 'title')}</h4>
                  <ul>${(CONFIG.lang === 'en' ? sec.pro.pointsEn : sec.pro.points).map(pt => `<li>${pt}</li>`).join('')}</ul>
                </div>
                <div class="debate-side con">
                  <h4>${t(sec.con, 'title')}</h4>
                  <ul>${(CONFIG.lang === 'en' ? sec.con.pointsEn : sec.con.points).map(pt => `<li>${pt}</li>`).join('')}</ul>
                </div>
              </div>
            </div>
          `;
        }
        if (sec.type === 'view') {
          return `
            <div class="analysis-section highlight">
              <h3>${t(sec, 'title')}</h3>
              <p>${t(sec, 'content')}</p>
            </div>
          `;
        }
        if (sec.type === 'prediction') {
          return `
            <div class="analysis-section prediction">
              <h3>${t(sec, 'title')}</h3>
              <div class="prediction-box">
                <p>${t(sec, 'content')}</p>
                <p class="prediction-note">${t(sec, 'note')}</p>
              </div>
            </div>
          `;
        }
        if (sec.type === 'data') {
          const dataHtml = sec.items.map(d => `
            <div class="data-item">
              <span class="data-value">${d.value}</span>
              <span class="data-label">${t(d, 'label')}</span>
            </div>
          `).join('');
          return `
            <div class="analysis-data">
              <h3>${t(sec, 'title')}</h3>
              <div class="data-grid">${dataHtml}</div>
            </div>
          `;
        }
        return '';
      }).join('');

      return `
        <div class="analysis-card featured">
          <div class="analysis-header">
            <span class="analysis-tag tag-breaking">${article.tag}</span>
            <span class="analysis-date">${article.date}</span>
          </div>
          <h2>${t(article, 'title')}</h2>
          <div class="analysis-summary">
            <p>${t(article, 'summary')}</p>
          </div>
          <div class="analysis-body">
            ${sectionsHtml}
          </div>
          <div class="analysis-footer">
            <div class="analysis-tags">
              ${article.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
            </div>
            <span class="analysis-source">${CONFIG.lang === 'en' ? article.sourceInfoEn : article.sourceInfo}</span>
          </div>
        </div>
      `;
    }).join('');
  }

  // ========== 主流程 ==========
  async function init() {
    try {
      const resp = await fetch(CONFIG.dataPath + '?v=' + Date.now());
      if (!resp.ok) throw new Error('Failed to load content.json');
      const data = await resp.json();

      renderPageHeader(data);
      renderFeatured(data);
      renderTodayNews(data);
      renderWeekly(data);
      renderStats(data);
      renderHotTopics(data);
      renderTags(data);
      renderArchives(data);
      renderSources(data);
      renderAnalysis(data);

      console.log('[AI Frontline] Content rendered from JSON successfully');
    } catch (err) {
      console.error('[AI Frontline] Render error:', err);
      // 失败时保留HTML中的静态内容作为fallback
    }
  }

  // 页面加载完成后初始化
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
