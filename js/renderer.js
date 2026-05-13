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

  // ===== 2. 渲染今日新闻列表（支持本周合并视图） =====
  function renderDailyNews(containerId, items, meta, archiveDate) {
    var container = document.getElementById(containerId);
    if (!container || !items) return;

    // 更新计数和日期
    var countEl = document.querySelector('.news-count');
    if (countEl && meta) {
      var countText = meta.total + ' ' + I18N.t('units');
      if (meta.weekRange) {
        countText = meta.weekRange + ' 共' + countText;
      }
      countEl.textContent = countText;
    }

    var dateEl = document.querySelector('.date-badge');
    if (dateEl && meta) {
      if (meta.weekRange) {
        dateEl.textContent = meta.weekRange;
      } else {
        var lang = I18N.getLang();
        var d = meta.date ? meta.date.split('-') : ['04', '28'];
        dateEl.textContent = (lang === 'zh' ? d[1] + '月' + d[2] + '日' : d[1] + '/' + d[2]);
      }
    }

    // 如果是历史归档视图，显示归档标记
    if (archiveDate && meta) {
      var archiveBadge = document.querySelector('.archive-badge');
      if (archiveBadge) {
        archiveBadge.style.display = 'inline-block';
        archiveBadge.textContent = '📂 ' + archiveDate + ' 归档';
      }
    } else {
      var archiveBadge = document.querySelector('.archive-badge');
      if (archiveBadge) archiveBadge.style.display = 'none';
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
  // 归档制：默认加载 current.json（本周合并），支持指定日期归档
  function loadAll(archiveDate) {
    var newsPath = archiveDate ? 'data/news/' + archiveDate + '.json' : 'data/news/current.json';
    var githubPath = archiveDate ? 'data/github/' + archiveDate + '.json' : 'data/github/current.json';
    var apiPath = archiveDate ? 'data/api/' + archiveDate + '.json' : 'data/api/current.json';

    // News 数据
    fetchData(newsPath, function (news) {
      if (!news) {
        // 如果 current.json 不存在，fallback 到旧的 news.json
        fetchData('data/news.json', function (legacy) {
          if (legacy) renderNewsSection(legacy, archiveDate);
        });
        return;
      }
      renderNewsSection(news, archiveDate);
    });

    // GitHub 趋势数据
    fetchData(githubPath, function (data) {
      if (!data) return;
      renderGithubSection(data, archiveDate);
    });

    // API 趋势数据
    fetchData(apiPath, function (data) {
      if (!data) return;
      renderApiSection(data, archiveDate);
    });
  }

  function renderNewsSection(news, archiveDate) {
    renderBreaking('featuredRow', news.breaking);
    renderDailyNews('newsList', news.daily, news.meta, archiveDate);
    renderWeekly('weekTimeline', news.weekly);
    renderStats('statsRow', news.stats);
    renderHotList('hotList', news.hotList);
    renderTags('tagCloud', news.tags);
    renderSources('sourceList', news.sources);
    updateTimestamps(news.meta);

    // 渲染右侧历史归档入口
    if (news.archiveDates && news.archiveDates.length > 0) {
      renderArchiveLinks('newsArchive', news.archiveDates, 'news');
    }
  }

  function renderGithubSection(data, archiveDate) {
    // GitHub 栏目占位渲染
    var container = document.getElementById('githubContent');
    if (!container) return;

    if (data.meta && data.meta.note === 'placeholder') {
      container.innerHTML = '<div class="github-placeholder"><span class="placeholder-icon">🚧</span><h3>GitHub 趋势正在开发中</h3><p>每日自动扫描 GitHub 热门 AI 项目，即将上线</p></div>';
    }

    if (data.archiveDates && data.archiveDates.length > 0) {
      renderArchiveLinks('githubArchive', data.archiveDates, 'github');
    }
  }

  function renderApiSection(data, archiveDate) {
    // API 趋势栏目占位渲染
    var container = document.getElementById('apiContent');
    if (!container) return;

    if (data.meta && data.meta.note === 'placeholder') {
      container.innerHTML = '<div class="api-placeholder"><span class="placeholder-icon">📈</span><h3>API 调用趋势正在开发中</h3><p>跟踪各大 AI 模型 API 调用量、价格变化，即将上线</p></div>';
    }

    if (data.archiveDates && data.archiveDates.length > 0) {
      renderArchiveLinks('apiArchive', data.archiveDates, 'api');
    }
  }

  // ===== 渲染历史归档链接 =====
  function renderArchiveLinks(containerId, dates, section) {
    var container = document.getElementById(containerId);
    if (!container || !dates) return;
    
    // 去掉今天，只显示历史
    var today = new Date().toISOString().split('T')[0];
    var historyDates = dates.filter(function(d) { return d !== today; }).sort().reverse();
    
    if (historyDates.length === 0) {
      container.innerHTML = '<p class="archive-empty">暂无历史归档</p>';
      return;
    }

    container.innerHTML = historyDates.map(function(dateStr) {
      var parts = dateStr.split('-');
      var display = parts[1] + '-' + parts[2];
      return '<li><a href="#' + section + '/' + dateStr + '" class="archive-link" data-section="' + section + '" data-date="' + dateStr + '">' + display + '</a></li>';
    }).join('');
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
    // 保留当前归档状态重新加载
    var hash = window.location.hash;
    var archiveDate = null;
    if (hash && hash.match(/^#(news|github|api)\/\d{4}-\d{2}-\d{2}$/)) {
      archiveDate = hash.split('/')[1];
    }
    loadAll(archiveDate);
  });

  return {
    loadAll: loadAll
  };
})();
