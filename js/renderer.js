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
  function getGithubDesc(item) {
    // 优先使用中文描述，fallback 到英文
    return item.description_zh || item.description || '';
  }

  function renderGithubFeatured(containerId, data) {
    var container = document.getElementById(containerId);
    if (!container || !data) return;
    // 适配数据结构：high_value 作为 featured
    var items = data.high_value || data.featured || [];
    if (items.length === 0) {
      container.innerHTML = '<div class="news-empty">暂无重磅项目</div>';
      return;
    }
    container.innerHTML = items.slice(0, 3).map(function (item) {
      var desc = getGithubDesc(item);
      return (
        '<article class="card featured anim-fade-up">' +
          '<div class="card-tag tag-breaking">🔥 Trending</div>' +
          '<h2>' + escapeHtml(item.name) + '</h2>' +
          '<p class="card-meta">' + escapeHtml(item.language || 'N/A') + ' · ⭐ +' + escapeHtml(item.stars_today || '0') + '</p>' +
          '<p class="card-summary">' + escapeHtml(desc) + '</p>' +
        '</article>'
      );
    }).join('');
  }

  function renderGithubList(containerId, data) {
    var container = document.getElementById(containerId);
    if (!container || !data) return;
    // 适配数据结构：all_projects 作为项目列表
    var items = data.all_projects || data.projects || [];
    var countEl = document.querySelector('.github-count');
    if (countEl) countEl.textContent = items.length + ' 个';
    if (items.length === 0) {
      container.innerHTML = '<div class="news-empty">暂无项目数据</div>';
      return;
    }
    container.innerHTML = items.map(function (item) {
      var desc = getGithubDesc(item);
      return (
        '<div class="news-item anim-fade-up">' +
          '<div class="news-bar tech"></div>' +
          '<div class="news-body">' +
            '<h3><a href="' + escapeHtml(item.url || '') + '" target="_blank" rel="noopener">' + escapeHtml(item.name) + '</a></h3>' +
            '<p class="news-excerpt">' + escapeHtml(desc) + '</p>' +
            '<div class="news-footer">' +
              '<span class="news-tag tag-tech">' + escapeHtml(item.language || 'N/A') + '</span>' +
              '<span class="news-source">⭐ +' + escapeHtml(item.stars_today || '0') + '</span>' +
              '<span class="news-date">score: ' + escapeHtml(item.score || '0') + '</span>' +
            '</div>' +
          '</div>' +
        '</div>'
      );
    }).join('');
  }

  function renderGithubLanguages(containerId, data) {
    var container = document.getElementById(containerId);
    if (!container || !data) return;
    // 从 all_projects 提取语言分布
    var items = data.all_projects || [];
    var langMap = {};
    items.forEach(function (item) {
      var lang = item.language || 'Unknown';
      if (!langMap[lang]) langMap[lang] = { count: 0, color: '#666' };
      langMap[lang].count++;
    });
    var languages = Object.keys(langMap).map(function (name) {
      return { name: name, count: langMap[name].count };
    }).sort(function (a, b) { return b.count - a.count; });

    if (languages.length === 0) {
      container.innerHTML = '<div class="news-empty">暂无语言数据</div>';
      return;
    }
    var total = languages.reduce(function (sum, l) { return sum + l.count; }, 0);
    container.innerHTML = languages.map(function (lang) {
      var pct = Math.round((lang.count / total) * 100);
      return (
        '<div class="lang-bar">' +
          '<span class="lang-name">● ' + escapeHtml(lang.name) + '</span>' +
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

  // ===== 主入口：加载所有数据（并行加载加速） =====
  function loadAll() {
    // 并行加载所有独立数据源
    Promise.all([
      // 1. AI新闻
      new Promise(function (resolve) {
        fetchData('data/news/current.json', function (news) {
          if (news) {
            renderNewsSection(news);
          } else {
            fetchData('data/news.json', function (legacy) {
              if (legacy) renderNewsSectionLegacy(legacy);
            });
          }
          resolve();
        });
      }),
      // 2. 历史回顾
      new Promise(function (resolve) {
        fetchData('data/news/index.json', function (index) {
          if (index && index.length > 0) {
            loadHistoryWeeksMeta(index);
          } else {
            renderHistoryReview('historyTimeline', null);
          }
          resolve();
        });
      }),
      // 3. GitHub趋势
      new Promise(function (resolve) {
        fetchData('data/github/current.json', function (data) {
          if (data) {
            renderGithubFeatured('githubFeatured', data);
            renderGithubList('githubList', data);
            renderGithubLanguages('githubLanguages', data);
            var githubDate = data.date || '';
            document.querySelectorAll('#githubSection .update-time').forEach(function (el) {
              el.textContent = (I18N.getLang() === 'zh' ? '更新于：' : 'Updated: ') + githubDate;
            });
          }
          resolve();
        });
      }),
      // 4. API趋势
      new Promise(function (resolve) {
        fetchData('data/api/current.json', function (data) {
          if (data) {
            renderApiFeatured('apiFeatured', data.featured);
            renderApiList('apiList', data.trends, data.meta);
            var apiDate = data.meta && data.meta.updatedAt ? data.meta.updatedAt.split('T')[0] : '';
            document.querySelectorAll('#apiSection .update-time').forEach(function (el) {
              el.textContent = (I18N.getLang() === 'zh' ? '更新于：' : 'Updated: ') + apiDate;
            });
          }
          resolve();
        });
      })
    ]).then(function () {
      console.log('🚀 所有数据加载完成');
      // 隐藏加载提示
      var loader = document.getElementById('pageLoader');
      if (loader) loader.style.display = 'none';
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
    var today = news.meta && news.meta.date ? news.meta.date : new Date().toISOString().split('T')[0];
    // 统一为 MM-DD 格式用于比较（breaking.date 是 "05-14" 格式）
    var todayShort = today.split('-').slice(1).join('-'); // "2026-05-14" → "05-14"
    var breaking = news.breaking || [];
    var daily = news.daily || [];

    // 分离当日重磅 vs 旧重磅
    var todayBreaking = [];
    var oldBreaking = [];
    breaking.forEach(function (item) {
      // 兼容两种日期格式："05-14" 和 "2026-05-14"
      var itemDate = item.date || '';
      var itemShort = itemDate.split('-').slice(-2).join('-'); // 取最后两位
      if (itemShort === todayShort) {
        todayBreaking.push(item);
      } else {
        oldBreaking.push(item);
      }
    });

    var featuredToShow = todayBreaking;
    var dailyToShow = daily;

    // 如果有当日重磅，旧重磅降级到 daily 列表（标记为重磅）
    if (todayBreaking.length > 0 && oldBreaking.length > 0) {
      oldBreaking.forEach(function (item) {
        item.category = 'breaking'; // 标记为重磅
      });
      dailyToShow = oldBreaking.concat(daily);
    }
    // 如果没有当日重磅，保留所有 breaking 作为 featured
    if (todayBreaking.length === 0) {
      featuredToShow = breaking;
    }

    renderBreaking('featuredRow', featuredToShow);
    renderDailyNews('newsList', dailyToShow, news.meta);
    renderSources('sourceList', news.sources);
    updateTimestamps(news.meta);
  }

  // 兼容旧格式（fallback）
  function renderNewsSectionLegacy(news) {
    renderNewsSection(news);
  }

  // ===== 缓存工具 =====
  var CACHE_PREFIX = 'ai_news_';
  var CACHE_TTL = 5 * 60 * 1000; // 5分钟缓存

  function getCache(key) {
    try {
      var item = localStorage.getItem(CACHE_PREFIX + key);
      if (!item) return null;
      var parsed = JSON.parse(item);
      if (Date.now() - parsed.time > CACHE_TTL) {
        localStorage.removeItem(CACHE_PREFIX + key);
        return null;
      }
      return parsed.data;
    } catch (e) { return null; }
  }

  function setCache(key, data) {
    try {
      localStorage.setItem(CACHE_PREFIX + key, JSON.stringify({
        time: Date.now(),
        data: data
      }));
    } catch (e) { /* 缓存满，忽略 */ }
  }

  function fetchData(url, callback) {
    // 尝试从缓存读取
    var cacheKey = url.replace(/\?.*$/, '').replace(/\//g, '_');
    var cached = getCache(cacheKey);
    if (cached) {
      // 先返回缓存，同时后台刷新
      callback(cached);
      // 后台静默刷新（不阻塞）
      fetch(url + (url.indexOf('?') >= 0 ? '&' : '?') + '_refresh=' + Date.now())
        .then(function (res) { return res.json(); })
        .then(function (data) { setCache(cacheKey, data); })
        .catch(function () {});
      return;
    }

    // 无缓存，正常请求
    var nocacheUrl = url + (url.indexOf('?') >= 0 ? '&' : '?') + '_t=' + Date.now();
    fetch(nocacheUrl)
      .then(function (res) { return res.json(); })
      .then(function (data) {
        setCache(cacheKey, data);
        callback(data);
      })
      .catch(function (err) {
        console.error('Failed to load ' + url + ':', err);
        callback(null);
      });
  }

  function prefetchData(url) {
    // 静默预加载，不回调
    var cacheKey = url.replace(/\?.*$/, '').replace(/\//g, '_');
    if (getCache(cacheKey)) return;
    fetch(url + (url.indexOf('?') >= 0 ? '&' : '?') + '_t=' + Date.now())
      .then(function (res) { return res.json(); })
      .then(function (data) { setCache(cacheKey, data); })
      .catch(function () {});
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
