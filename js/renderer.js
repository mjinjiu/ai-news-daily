/**
 * AI前线 — 数据渲染引擎 (renderer.js)
 * 职责：从 JSON 数据渲染所有动态内容到页面
 * 原则：零硬编码，所有内容来自 data/*.json
 * 
 * 2026-05-13 重构：
 * - 一周一份JSON，历史周自动归档
 * - 本周回顾 → 历史回顾（缩略重磅 + 点击展开全量）
 * - 信源去重并修复显示
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

  // ===== 1. 渲染重磅新闻（无跳转） =====
  function renderBreaking(containerId, items) {
    var container = document.getElementById(containerId);
    if (!container || !items) return;
    container.innerHTML = items.map(function (item) {
      return (
        '<article class="card featured anim-fade-up" data-id="' + item.id + '">' +
          '<div class="card-tag tag-breaking">' + categoryLabel('breaking') + ' Breaking</div>' +
          '<h2>' + escapeHtml(getText(item, 'title')) + '</h2>' +
          '<p class="card-meta">' + escapeHtml(item.date) + ' · ' + escapeHtml(item.source) + '</p>' +
          '<p class="card-summary">' + escapeHtml(getText(item, 'summary')) + '</p>' +
        '</article>'
      );
    }).join('');
  }

  // ===== 2. 渲染新闻列表项 HTML（复用） =====
  function renderNewsItemHtml(item) {
    var catCls = categoryClass(item.category);
    var title = getText(item, 'title');
    var excerpt = item.excerpt_zh || item.excerpt || item.summary_zh || item.summary || '';
    return (
      '<div class="news-item anim-fade-up" data-id="' + item.id + '">' +
        '<div class="news-bar ' + catCls + '"></div>' +
        '<div class="news-body">' +
          '<h3>' + escapeHtml(title) + '</h3>' +
          '<p class="news-excerpt">' + escapeHtml(excerpt) + '</p>' +
          '<div class="news-footer">' +
            '<span class="news-tag tag-' + catCls + '">' + categoryLabel(item.category) + ' ' + item.category.charAt(0).toUpperCase() + item.category.slice(1) + '</span>' +
            '<span class="news-source">' + escapeHtml(item.source) + '</span>' +
            '<span class="news-date">' + escapeHtml(item.date) + '</span>' +
          '</div>' +
        '</div>' +
      '</div>'
    );
  }

  // ===== 3. 渲染本周新闻列表 =====
  function renderDailyNews(containerId, items, meta) {
    var container = document.getElementById(containerId);
    if (!container || !items) return;

    // 计数：用实际 items.length，兼容旧格式 meta.total 可能为 0 的情况
    var countEl = document.querySelector('.news-count');
    if (countEl) {
      var actualCount = items.length;
      countEl.textContent = actualCount + ' ' + I18N.t('units');
    }

    // 日期标签：兼容旧格式 weekRange / 新格式 weekLabel
    var dateEl = document.querySelector('.date-badge');
    if (dateEl && meta) {
      var label = meta.weekLabel || meta.weekRange || '';
      if (label) dateEl.textContent = label;
    }

    if (items.length === 0) {
      container.innerHTML = '<div class="news-empty">本周暂无新闻，等更新...</div>';
      return;
    }

    container.innerHTML = items.map(renderNewsItemHtml).join('');
  }

  // ===== 4. 渲染历史回顾 =====
  // 缩略显示：每行一个历史周，显示周范围 + 重磅新闻标题
  // 点击展开：显示该周全量新闻（格式同本周新闻）
  // 再次点击：缩回
  var loadedHistoryWeeks = {}; // 缓存已加载的历史周数据

  function renderHistoryReview(containerId, weekList) {
    var container = document.getElementById(containerId);
    if (!container || !weekList || weekList.length === 0) {
      if (container) container.innerHTML = '<div class="history-empty">暂无历史回顾</div>';
      return;
    }

    container.innerHTML = weekList.map(function (weekMeta) {
      var weekId = weekMeta.weekStart;
      var breakingTitle = weekMeta.breakingTitle || '本周无重磅新闻';
      return (
        '<div class="history-week" data-week="' + weekId + '">' +
          '<div class="history-week-header">' +
            '<span class="history-week-label">📅 ' + escapeHtml(weekMeta.weekLabel) + '</span>' +
            '<span class="history-week-breaking">🔥 ' + escapeHtml(breakingTitle) + '</span>' +
            '<span class="history-week-count">' + weekMeta.total + ' 条</span>' +
            '<span class="history-week-toggle">▼</span>' +
          '</div>' +
          '<div class="history-week-content" style="display:none">' +
            '<div class="history-week-loading">加载中...</div>' +
          '</div>' +
        '</div>'
      );
    }).join('');

    // 绑定展开/收起事件
    container.querySelectorAll('.history-week-header').forEach(function (header) {
      header.addEventListener('click', function () {
        var weekEl = header.closest('.history-week');
        var contentEl = weekEl.querySelector('.history-week-content');
        var toggleEl = header.querySelector('.history-week-toggle');
        if (!contentEl || !toggleEl) return;

        var isHidden = contentEl.style.display === 'none';
        var weekId = weekEl.dataset.week;

        if (isHidden) {
          // 展开：加载该周数据
          loadHistoryWeek(weekId, contentEl, toggleEl);
        } else {
          // 收起
          contentEl.style.display = 'none';
          toggleEl.textContent = '▼';
        }
      });
    });
  }

  function loadHistoryWeek(weekId, contentEl, toggleEl) {
    // 如果已缓存，直接渲染
    if (loadedHistoryWeeks[weekId]) {
      renderHistoryWeekContent(contentEl, loadedHistoryWeeks[weekId]);
      contentEl.style.display = 'block';
      toggleEl.textContent = '▲';
      return;
    }

    // 从文件加载
    var path = 'data/news/' + weekId + '.json';
    fetchData(path, function (data) {
      if (!data) {
        contentEl.innerHTML = '<div class="history-week-error">加载失败</div>';
        contentEl.style.display = 'block';
        toggleEl.textContent = '▲';
        return;
      }
      loadedHistoryWeeks[weekId] = data;
      renderHistoryWeekContent(contentEl, data);
      contentEl.style.display = 'block';
      toggleEl.textContent = '▲';
    });
  }

  function renderHistoryWeekContent(contentEl, data) {
    var allItems = [];
    if (data.breaking) allItems = allItems.concat(data.breaking);
    if (data.daily) allItems = allItems.concat(data.daily);

    if (allItems.length === 0) {
      contentEl.innerHTML = '<div class="history-week-empty">该周暂无新闻</div>';
      return;
    }

    contentEl.innerHTML = allItems.map(renderNewsItemHtml).join('');
  }

  // ===== 5. 渲染信源（去重 + 修复显示） =====
  function renderSources(containerId, sources) {
    var container = document.getElementById(containerId);
    if (!container || !sources) return;

    // 拆分 "X / Y" 为独立信源，去重，清理
    var allSources = [];
    var seen = {};
    sources.forEach(function (src) {
      // 按 / 拆分
      var parts = src.split(/\s*\/\s*/);
      parts.forEach(function (part) {
        var clean = part.trim();
        if (clean && !seen[clean]) {
          seen[clean] = true;
          allSources.push(clean);
        }
      });
    });

    container.innerHTML = allSources.map(function (src) {
      return '<span class="source-tag">' + escapeHtml(src) + '</span>';
    }).join('');
  }

  // ===== GitHub趋势渲染 =====
  function renderGithubFeatured(containerId, items) {
    var container = document.getElementById(containerId);
    if (!container || !items) return;
    container.innerHTML = items.map(function (item) {
      var title = getText(item, 'title');
      var desc = getText(item, 'description');
      return (
        '<article class="card featured anim-fade-up" data-id="' + item.id + '">' +
          '<div class="card-tag tag-breaking">🔥 Trending</div>' +
          '<h2>' + escapeHtml(title) + '</h2>' +
          '<p class="card-meta">' + escapeHtml(item.language) + ' · ⭐ +' + escapeHtml(item.stars_today) + '</p>' +
          '<p class="card-summary">' + escapeHtml(desc) + '</p>' +
        '</article>'
      );
    }).join('');
  }

  function renderGithubList(containerId, items, meta) {
    var container = document.getElementById(containerId);
    if (!container || !items) return;
    var countEl = document.querySelector('.github-count');
    if (countEl) countEl.textContent = items.length + ' 个';
    if (items.length === 0) {
      container.innerHTML = '<div class="news-empty">暂无项目数据</div>';
      return;
    }
    container.innerHTML = items.map(function (item) {
      var title = getText(item, 'title');
      var desc = getText(item, 'description');
      var tags = (item.tags || []).map(function (t) { return '<span class="news-tag tag-tech">' + escapeHtml(t) + '</span>'; }).join('');
      return (
        '<div class="news-item anim-fade-up" data-id="' + item.id + '">' +
          '<div class="news-bar tech"></div>' +
          '<div class="news-body">' +
            '<h3>' + escapeHtml(title) + '</h3>' +
            '<p class="news-excerpt">' + escapeHtml(desc) + '</p>' +
            '<div class="news-footer">' +
              tags +
              '<span class="news-source">' + escapeHtml(item.language) + '</span>' +
              '<span class="news-date">⭐ +' + escapeHtml(item.stars_today) + '</span>' +
            '</div>' +
          '</div>' +
        '</div>'
      );
    }).join('');
  }

  function renderGithubLanguages(containerId, languages) {
    var container = document.getElementById(containerId);
    if (!container || !languages) return;
    var total = languages.reduce(function (sum, l) { return sum + l.count; }, 0);
    container.innerHTML = languages.map(function (lang) {
      var pct = Math.round((lang.count / total) * 100);
      return (
        '<div class="lang-bar">' +
          '<span class="lang-name" style="color:' + (lang.color || '#666') + '">● ' + escapeHtml(lang.name) + '</span>' +
          '<span class="lang-count">' + lang.count + ' 个 (' + pct + '%)</span>' +
        '</div>'
      );
    }).join('');
  }

  // ===== API趋势渲染 =====
  function renderApiFeatured(containerId, items) {
    var container = document.getElementById(containerId);
    if (!container || !items) return;
    container.innerHTML = items.map(function (item) {
      var title = getText(item, 'title');
      var desc = getText(item, 'description');
      var changeClass = (item.change || '').startsWith('+') ? 'change-up' : 'change-down';
      return (
        '<article class="card featured anim-fade-up" data-id="' + item.id + '">' +
          '<div class="card-tag tag-breaking">📈 ' + escapeHtml(item.provider) + '</div>' +
          '<h2>' + escapeHtml(title) + '</h2>' +
          '<p class="card-meta">' + escapeHtml(item.metric || '变动') + ' <span class="' + changeClass + '">' + escapeHtml(item.change) + '</span></p>' +
          '<p class="card-summary">' + escapeHtml(desc) + '</p>' +
        '</article>'
      );
    }).join('');
  }

  function renderApiList(containerId, items, meta) {
    var container = document.getElementById(containerId);
    if (!container || !items) return;
    var countEl = document.querySelector('.api-count');
    if (countEl) countEl.textContent = items.length + ' 条';
    if (items.length === 0) {
      container.innerHTML = '<div class="news-empty">暂无API动态</div>';
      return;
    }
    container.innerHTML = items.map(function (item) {
      var desc = item.description_zh || item.description || '';
      var changeClass = (item.change || '').startsWith('+') ? 'change-up' : ((item.change || '').startsWith('-') ? 'change-down' : '');
      return (
        '<div class="news-item anim-fade-up" data-id="' + item.id + '">' +
          '<div class="news-bar ' + (item.category || 'tech') + '"></div>' +
          '<div class="news-body">' +
            '<h3>' + escapeHtml(item.provider + ' · ' + item.model) + '</h3>' +
            '<p class="news-excerpt">' + escapeHtml(desc) + '</p>' +
            '<div class="news-footer">' +
              '<span class="news-tag tag-' + (item.category || 'tech') + '">' + escapeHtml(item.metric || '动态') + '</span>' +
              '<span class="news-source">' + escapeHtml(item.value || '') + '</span>' +
              '<span class="news-date ' + changeClass + '">' + escapeHtml(item.change || '') + '</span>' +
            '</div>' +
          '</div>' +
        '</div>'
      );
    }).join('');
  }

  // ===== 渲染 GitHub/API/杂记占位 =====
  function renderNotesSection(data) { /* 占位 */ }

  // ===== 主入口：加载所有数据 =====
  function loadAll() {
    // 1. 加载本周 current.json (AI新闻)
    fetchData('data/news/current.json', function (news) {
      if (news) {
        renderNewsSection(news);
      } else {
        // fallback 到旧格式
        fetchData('data/news.json', function (legacy) {
          if (legacy) renderNewsSectionLegacy(legacy);
        });
      }
    });

    // 2. 加载历史周列表
    fetchData('data/news/index.json', function (index) {
      if (index && index.length > 0) {
        loadHistoryWeeksMeta(index);
      } else {
        renderHistoryReview('historyTimeline', null);
      }
    });

    // 3. 加载 GitHub趋势
    fetchData('data/github/current.json', function (data) {
      if (data) {
        renderGithubFeatured('githubFeatured', data.featured);
        renderGithubList('githubList', data.projects, data.meta);
        renderGithubLanguages('githubLanguages', data.languages);
        // 更新 GitHub 栏目的时间戳
        var githubDate = data.meta && data.meta.updatedAt ? data.meta.updatedAt.split('T')[0] : '';
        document.querySelectorAll('#githubSection .update-time').forEach(function (el) {
          el.textContent = (I18N.getLang() === 'zh' ? '更新于：' : 'Updated: ') + githubDate;
        });
      }
    });

    // 4. 加载 API趋势
    fetchData('data/api/current.json', function (data) {
      if (data) {
        renderApiFeatured('apiFeatured', data.featured);
        renderApiList('apiList', data.trends, data.meta);
        // 更新 API 栏目的时间戳
        var apiDate = data.meta && data.meta.updatedAt ? data.meta.updatedAt.split('T')[0] : '';
        document.querySelectorAll('#apiSection .update-time').forEach(function (el) {
          el.textContent = (I18N.getLang() === 'zh' ? '更新于：' : 'Updated: ') + apiDate;
        });
      }
    });
  }

  function loadHistoryWeeksMeta(weekIds) {
    var weekList = [];
    var pending = weekIds.length;

    if (pending === 0) {
      renderHistoryReview('historyTimeline', []);
      return;
    }

    weekIds.forEach(function (weekId) {
      var path = 'data/news/' + weekId + '.json';
      fetchData(path, function (data) {
        if (data && data.meta) {
          // 兼容旧格式：weekLabel / weekRange / date
          var weekLabel = data.meta.weekLabel || data.meta.weekRange || data.meta.date || weekId;
          var breakingTitle = '本周无重磅新闻';
          if (data.breaking && data.breaking.length > 0) {
            breakingTitle = getText(data.breaking[0], 'title');
          }
          // 兼容旧格式：total 字段可能在 meta 中，也可能需要计算
          var total = data.meta.total;
          if (typeof total === 'undefined' || total === null) {
            total = (data.daily ? data.daily.length : 0) + (data.breaking ? data.breaking.length : 0);
          }
          weekList.push({
            weekStart: weekId,
            weekLabel: weekLabel,
            total: total,
            breakingTitle: breakingTitle
          });
        }
        pending--;
        if (pending === 0) {
          // 按时间倒序排列
          weekList.sort(function (a, b) {
            return b.weekStart.localeCompare(a.weekStart);
          });
          renderHistoryReview('historyTimeline', weekList);
        }
      });
    });
  }

  function renderNewsSection(news) {
    renderBreaking('featuredRow', news.breaking);
    renderDailyNews('newsList', news.daily, news.meta);
    renderSources('sourceList', news.sources);
    updateTimestamps(news.meta);
  }

  // 兼容旧格式（fallback）
  function renderNewsSectionLegacy(news) {
    renderBreaking('featuredRow', news.breaking);
    renderDailyNews('newsList', news.daily, news.meta);
    renderSources('sourceList', news.sources);
    updateTimestamps(news.meta);
  }

  function fetchData(url, callback) {
    // 加时间戳绕过 CDN 缓存
    var sep = url.indexOf('?') >= 0 ? '&' : '?';
    var nocacheUrl = url + sep + '_t=' + Date.now();
    fetch(nocacheUrl)
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
