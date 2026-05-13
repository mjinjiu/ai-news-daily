/**
 * AI前线 — 数据渲染引擎 (renderer.js)
 * 职责：从 JSON 数据渲染所有动态内容到页面
 * 原则：零硬编码，所有内容来自 data/*.json
 */

const Renderer = (function () {
  'use strict';

  // ===== 工具函数 =====
  function escapeHtml(str) {
    if (!str) return '';
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  function getText(item, field) {
    var lang = I18N.getLang();
    var val = item[field + '_' + lang];
    if (!val) val = item[field + '_zh'] || item[field] || '';
    return val;
  }

  function categoryClass(cat) {
    var map = { breaking: 'breaking', industry: 'industry', tech: 'tech', policy: 'policy', finance: 'finance' };
    return map[cat] || 'industry';
  }

  function categoryLabel(cat) {
    var key = 'category' + cat.charAt(0).toUpperCase() + cat.slice(1);
    return I18N.t(key);
  }

  // ===== 1. 渲染重磅新闻 =====
  function renderBreaking(containerId, items) {
    var container = document.getElementById(containerId);
    if (!container || !items) return;
    container.innerHTML = items.map(function (item) {
      return (
        '<article class="card featured anim-fade-up" data-source-url="' + escapeHtml(item.url) + '" data-id="' + item.id + '" tabindex="0" role="link" aria-label="' + escapeHtml(getText(item, 'title')) + '">' +
          '<div class="card-tag tag-breaking">' + categoryLabel('breaking') + ' Breaking</div>' +
          '<h2>' + escapeHtml(getText(item, 'title')) + '</h2>' +
          '<p class="card-meta">' + escapeHtml(item.date) + ' · ' + escapeHtml(item.source) + '</p>' +
          '<p class="card-summary">' + escapeHtml(getText(item, 'summary')) + '</p>' +
        '</article>'
      );
    }).join('');
  }

  // ===== 2. 渲染今日新闻列表 =====
  function renderDailyNews(containerId, items, meta) {
    var container = document.getElementById(containerId);
    if (!container || !items) return;

    // 更新计数和日期
    var countEl = document.querySelector('.news-count');
    if (countEl && meta) countEl.textContent = meta.total + ' ' + I18N.t('units');

    var dateEl = document.querySelector('.date-badge');
    if (dateEl && meta) {
      var lang = I18N.getLang();
      var d = meta.date ? meta.date.split('-') : ['04', '28'];
      dateEl.textContent = (lang === 'zh' ? d[1] + '月' + d[2] + '日' : d[1] + '/' + d[2]);
    }

    container.innerHTML = items.map(function (item) {
      var catCls = categoryClass(item.category);
      return (
        '<div class="news-item anim-fade-up" data-source-url="' + escapeHtml(item.url) + '" data-id="' + item.id + '" tabindex="0" role="link" aria-label="' + escapeHtml(getText(item, 'title')) + '">' +
          '<div class="news-bar ' + catCls + '"></div>' +
          '<div class="news-body">' +
            '<h3>' + escapeHtml(getText(item, 'title')) + '</h3>' +
            '<p class="news-excerpt">' + escapeHtml(getText(item, 'excerpt')) + '</p>' +
            '<div class="news-footer">' +
              '<span class="news-tag tag-' + catCls + '">' + categoryLabel(item.category) + ' ' + item.category.charAt(0).toUpperCase() + item.category.slice(1) + '</span>' +
              '<span class="news-source">' + escapeHtml(item.source) + '</span>' +
              '<span class="news-date">' + escapeHtml(item.date) + '</span>' +
            '</div>' +
          '</div>' +
        '</div>'
      );
    }).join('');
  }

  // ===== 3. 渲染本周回顾 =====
  function renderWeekly(containerId, days) {
    var container = document.getElementById(containerId);
    if (!container || !days) return;
    container.innerHTML = days.map(function (day) {
      var dayName = I18N.getLang() === 'zh' ? day.day : day.day_en;
      var listHtml = day.items && day.items.length > 0
        ? day.items.map(function (it) {
            var cls = categoryClass(it.category);
            return '<li data-source-url="' + escapeHtml(it.url) + '" tabindex="0" role="link"><span class="dot ' + cls + '"></span><a href="' + escapeHtml(it.url) + '" target="_blank" rel="noopener noreferrer">' + escapeHtml(getText(it, 'title')) + '</a></li>';
          }).join('')
        : '<li class="empty">' + I18N.t('emptyNews') + '</li>';
      return (
        '<div class="day-group anim-fade-up">' +
          '<div class="day-header">' +
            '<span class="day-name">' + escapeHtml(dayName) + '</span>' +
            '<span class="day-date">' + escapeHtml(day.date) + '</span>' +
            '<span class="day-count">' + day.count + ' ' + I18N.t('units') + '</span>' +
          '</div>' +
          '<ul class="day-list">' + listHtml + '</ul>' +
        '</div>'
      );
    }).join('');
  }

  // ===== 4. 渲染统计速览 =====
  function renderStats(containerId, stats) {
    var container = document.getElementById(containerId);
    if (!container || !stats) return;
    container.innerHTML = stats.map(function (s) {
      return (
        '<div class="stat-item anim-scale-in">' +
          '<span class="stat-num">' + escapeHtml(s.num) + '</span>' +
          '<span class="stat-label">' + escapeHtml(getText(s, 'label')) + '</span>' +
        '</div>'
      );
    }).join('');
  }

  // ===== 5. 渲染热榜 =====
  function renderHotList(containerId, items) {
    var container = document.getElementById(containerId);
    if (!container || !items) return;
    container.innerHTML = items.map(function (item, idx) {
      var rankClass = idx < 3 ? 'rank-top' + (idx + 1) : '';
      return (
        '<li class="' + rankClass + '">' +
          '<a href="' + escapeHtml(item.url) + '" target="_blank" rel="noopener noreferrer">' + escapeHtml(getText(item, 'title')) + '</a>' +
        '</li>'
      );
    }).join('');
  }

  // ===== 6. 渲染标签云 =====
  function renderTags(containerId, tags) {
    var container = document.getElementById(containerId);
    if (!container || !tags) return;
    container.innerHTML = tags.map(function (tag) {
      return '<span class="tag">' + escapeHtml(tag) + '</span>';
    }).join('');
  }

  // ===== 7. 渲染信源 =====
  function renderSources(containerId, sources) {
    var container = document.getElementById(containerId);
    if (!container || !sources) return;
    container.innerHTML = sources.map(function (src) {
      return '<span class="source-tag">' + escapeHtml(src) + '</span>';
    }).join('');
  }

  // ===== 8. 渲染深度解读（已废弃） =====
  var analysisPage = 0;
  var analysisPerPage = 8;
  var analysisItems = [];
  function parseDate(d) { return 0; }
  function renderAnalysis(containerId, items) { /* 栏目已移除 */ }
  function updateAnalysisPage() { /* 栏目已移除 */ }
  function nextAnalysisPage() { /* 栏目已移除 */ }
  function prevAnalysisPage() { /* 栏目已移除 */ }

  // ===== 9. 渲染API定价（已废弃） =====
  function renderPricing(data) { /* 栏目已移除 */ }

  // ===== 主入口：加载所有数据 =====
  function loadAll() {
    // News data
    fetchData('data/news.json', function (news) {
      if (!news) return;
      renderBreaking('featuredRow', news.breaking);
      renderDailyNews('newsList', news.daily, news.meta);
      renderWeekly('weekTimeline', news.weekly);
      renderStats('statsRow', news.stats);
      renderHotList('hotList', news.hotList);
      renderTags('tagCloud', news.tags);
      renderSources('sourceList', news.sources);

      // Update timestamps
      updateTimestamps(news.meta);
    });

    // Analysis / Pricing 栏目已移除，不再加载对应数据
  }

  function fetchData(url, callback) {
    fetch(url)
      .then(function (res) { return res.json(); })
      .then(function (data) { callback(data); })
      .catch(function (err) {
        console.error('Failed to load ' + url + ':', err);
        callback(null);
      });
  }

  function updateTimestamps(meta) {
    var lang = I18N.getLang();
    var prefix = lang === 'zh' ? '\u66f4\u65b0\u4e8e\uff1a' : 'Updated: ';
    var dateStr = meta && meta.updatedAt ? meta.updatedAt.split('T')[0] : '';
    if (lang === 'zh') dateStr = dateStr.replace(/-/g, '/');

    document.querySelectorAll('.update-time').forEach(function (el) {
      el.textContent = prefix + dateStr;
    });
  }

  // Re-render on language change
  I18N.onChange(function () {
    loadAll();
  });

  return {
    loadAll: loadAll
  };
})();
