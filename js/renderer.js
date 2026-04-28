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

  // ===== 8. 渲染深度解读 =====
  var analysisPage = 0;
  var analysisPerPage = 8;
  var analysisItems = [];

  function parseDate(d) {
    if (!d) return 0;
    var parts = d.split(/[-\/]/);
    if (parts.length === 2) {
      return new Date(2026, parseInt(parts[0]) - 1, parseInt(parts[1])).getTime();
    }
    if (parts.length >= 3) {
      return new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2])).getTime();
    }
    return 0;
  }

  function renderAnalysis(containerId, items) {
    analysisItems = items || [];
    // 按日期排序：新→旧
    analysisItems.sort(function (a, b) {
      return parseDate(b.date) - parseDate(a.date);
    });
    var container = document.getElementById(containerId);
    if (!container) return;
    updateAnalysisPage();
  }

  function updateAnalysisPage() {
    var container = document.getElementById('analysisFeatured');
    if (!container) return;

    var start = analysisPage * analysisPerPage;
    var pageItems = analysisItems.slice(start, start + analysisPerPage);
    var totalPages = Math.ceil(analysisItems.length / analysisPerPage) || 1;

    container.innerHTML = pageItems.map(function (item) {
      var points = (I18N.getLang() === 'zh' ? item.points_zh : item.points_en) || [];
      var debate = I18N.getLang() === 'zh' ? item.debate_zh : item.debate_en;
      var pointsHtml = points.map(function (p) {
        return (
          '<div class="point">' +
            '<span class="point-num">' + p.num + '</span>' +
            '<div class="point-content">' +
              '<strong>' + escapeHtml(p.title) + '</strong>' +
              '<p>' + escapeHtml(p.desc) + '</p>' +
            '</div>' +
          '</div>'
        );
      }).join('');

      var debateHtml = '';
      if (debate) {
        debateHtml = (
          '<div class="analysis-section debate">' +
            '<h3>' + I18N.t('debateTitle') + '</h3>' +
            '<div class="debate-grid">' +
              '<div class="debate-side pro">' +
                '<h4>' + I18N.t('proSide') + '</h4>' +
                '<ul>' + debate.pro.map(function (d) { return '<li>' + escapeHtml(d) + '</li>'; }).join('') + '</ul>' +
              '</div>' +
              '<div class="debate-side con">' +
                '<h4>' + I18N.t('conSide') + '</h4>' +
                '<ul>' + debate.con.map(function (d) { return '<li>' + escapeHtml(d) + '</li>'; }).join('') + '</ul>' +
              '</div>' +
            '</div>' +
          '</div>'
        );
      }

      var predictionHtml = '';
      if (item.prediction_zh || item.prediction_en) {
        predictionHtml = (
          '<div class="analysis-section prediction">' +
            '<h3>\ud83d\udd2e ' + I18N.t('predictionTitle') + '</h3>' +
            '<div class="prediction-box">' +
              '<p>' + escapeHtml(getText(item, 'prediction')) + '</p>' +
              '<p class="prediction-note">' + I18N.t('predictionNote') + '</p>' +
            '</div>' +
          '</div>'
        );
      }

      var tagsHtml = (item.tags || []).map(function (t) { return '<span class="tag">' + escapeHtml(t) + '</span>'; }).join('');

      return (
        '<article class="analysis-card featured anim-fade-up collapsed" data-id="' + item.id + '" data-index="' + (start + idx) + '">' +
          '<div class="analysis-header">' +
            '<span class="analysis-tag tag-breaking">' + item.grade + '\u7ea7\u00b7\u4ee3\u8868\u4f5c</span>' +
            '<span class="analysis-date">' + escapeHtml(item.date) + '</span>' +
          '</div>' +
          '<h2>' + escapeHtml(getText(item, 'title')) + '</h2>' +
          '<div class="analysis-summary">' +
            '<p>' + escapeHtml(getText(item, 'summary')) + '</p>' +
          '</div>' +
          '<div class="analysis-fold-hint">' +
            '<span class="fold-icon">▼</span>' +
            '<span class="fold-text">' + I18N.t('clickToExpand') + '</span>' +
          '</div>' +
          '<div class="analysis-body">' +
            '<div class="analysis-section">' +
              '<h3>\ud83d\udca1 ' + points.length + I18N.t('counterPoints') + '</h3>' +
              '<div class="analysis-points">' + pointsHtml + '</div>' +
            '</div>' +
            debateHtml +
            predictionHtml +
          '</div>' +
          '<div class="analysis-footer">' +
            '<div class="analysis-tags">' + tagsHtml + '</div>' +
            '<span class="analysis-source">' + I18N.t('sourceLabel') + '：' + escapeHtml(item.source) + '</span>' +
          '</div>' +
        '</article>'
      );
    }).join('');

    // Pagination
    var prevBtn = document.getElementById('analysisPrev');
    var nextBtn = document.getElementById('analysisNext');
    var pageNum = document.getElementById('analysisPageNum');
    if (prevBtn) prevBtn.disabled = analysisPage <= 0;
    if (nextBtn) nextBtn.disabled = analysisPage >= totalPages - 1;
    if (pageNum) pageNum.textContent = (analysisPage + 1) + ' / ' + totalPages;

    // 绑定折叠点击事件
    container.querySelectorAll('.analysis-card.collapsed').forEach(function(card) {
      card.addEventListener('click', function(e) {
        if (e.target.closest('a')) return;
        card.classList.toggle('collapsed');
        card.classList.toggle('expanded');
      });
    });
  }

  function nextAnalysisPage() {
    var totalPages = Math.ceil(analysisItems.length / analysisPerPage) || 1;
    if (analysisPage < totalPages - 1) {
      analysisPage++;
      updateAnalysisPage();
    }
  }

  function prevAnalysisPage() {
    if (analysisPage > 0) {
      analysisPage--;
      updateAnalysisPage();
    }
  }

  // ===== 9. 渲染API定价 =====
  function renderPricing(data) {
    if (!data) return;

    // International table
    var intlBody = document.getElementById('pricingIntlBody');
    if (intlBody && data.international) {
      intlBody.innerHTML = data.international.map(function (row) {
        return (
          '<tr class="tier-' + row.tier + '">' +
            '<td><strong>' + escapeHtml(row.model) + '</strong><br><span class="vendor">' + escapeHtml(row.vendor) + '</span></td>' +
            '<td>' + escapeHtml(row.input) + '</td>' +
            '<td>' + escapeHtml(row.output) + '</td>' +
            '<td>' + escapeHtml(row.context) + '</td>' +
            '<td><span class="badge ' + row.tier + '">' + escapeHtml(getText(row, 'badge')) + '</span></td>' +
          '</tr>'
        );
      }).join('');
    }

    // China table
    var cnBody = document.getElementById('pricingChinaBody');
    if (cnBody && data.china) {
      cnBody.innerHTML = data.china.map(function (row) {
        return (
          '<tr class="tier-' + row.tier + '">' +
            '<td><strong>' + escapeHtml(row.model) + '</strong><br><span class="vendor">' + escapeHtml(row.vendor) + '</span></td>' +
            '<td>' + escapeHtml(row.input) + '</td>' +
            '<td>' + escapeHtml(row.output) + '</td>' +
            '<td>' + escapeHtml(row.context) + '</td>' +
            '<td><span class="badge ' + row.tier + '">' + escapeHtml(getText(row, 'badge')) + '</span></td>' +
          '</tr>'
        );
      }).join('');
    }

    // Plan cards
    var plansContainer = document.getElementById('pricingPlans');
    if (plansContainer && data.plans) {
      plansContainer.innerHTML = data.plans.map(function (plan) {
        var cls = 'plan-card anim-fade-up';
        if (plan.highlight) cls += ' highlight';
        if (plan.isFree) cls += ' free';
        var feats = (I18N.getLang() === 'zh' ? plan.features_zh : plan.features_en) || [];
        return (
          '<div class="' + cls + '">' +
            '<div class="plan-name">' + escapeHtml(getText(plan, 'name')) + '</div>' +
            '<div class="plan-price">' + escapeHtml(getText(plan, 'price')) + '<span>' + escapeHtml(getText(plan, 'period')) + '</span></div>' +
            '<ul class="plan-features">' + feats.map(function (f) { return '<li>' + escapeHtml(f) + '</li>'; }).join('') + '</ul>' +
          '</div>'
        );
      }).join('');
    }
  }

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

    // Analysis data
    fetchData('data/analysis.json', function (analysis) {
      if (!analysis) return;
      renderAnalysis('analysisFeatured', analysis.items);
    });

    // Pricing data
    fetchData('data/pricing.json', function (pricing) {
      if (!pricing) return;
      renderPricing(pricing);
    });
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
    loadAll: loadAll,
    nextAnalysisPage: nextAnalysisPage,
    prevAnalysisPage: prevAnalysisPage,
    renderAnalysis: renderAnalysis,
    updateAnalysisPage: updateAnalysisPage
  };
})();
