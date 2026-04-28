/**
 * AI前线 — 国际化 (i18n) 模块
 * 支持中英双语切换，完整的翻译字典 + 动态插值
 */

const I18N = (function () {
  'use strict';

  let currentLang = 'zh';
  const listeners = [];

  const dict = {
    zh: {
      siteTitle: 'AI前线 - AI News & API Pricing',
      navLogo: 'AI前线',
      navNews: '\ud83d\udcf0 AI新闻',
      navAnalysis: '\ud83d\udd0d 深度解读',
      navPricing: '\ud83d\udcb0 API定价',
      langBtn: 'EN',
      adTopPlaceholder: '\ud83d\udce2 广告位：此处可挂载 Google AdSense / 百度联盟等广告',
      headlineTitle: '\u26a1 \u6bcf\u65e5AI\u524d\u7ebf',
      headlineSubtitle: '\u8ffd\u8e2a\u4eba\u5de5\u667a\u80fd\u6700\u65b0\u52a8\u6001\u4e0e\u884c\u4e1a\u8d8b\u52bf',
      updatePrefix: '\u66f4\u65b0\u4e8e\uff1a',
      sectionTodayNews: '\ud83d\udcf0 \u4eca\u65e5\u65b0\u95fb',
      sectionWeeklyReview: '\ud83d\udcc5 \u672c\u5468\u56de\u987e',
      sectionStats: '\ud83d\udcca \u4eca\u65e5AI\u5708\u901f\u89c8',
      sectionHot: '\ud83d\udd25 \u672c\u5468\u70ed\u699c',
      sectionTags: '\ud83c\udff7\ufe0f \u70ed\u95e8\u6807\u7b7e',
      sectionArchive: '\ud83d\udcc2 \u5386\u53f2\u5f52\u6863',
      sectionSources: '\ud83d\udce1 \u4fe1\u6e90',
      sectionIntl: '\ud83c\udf0d \u56fd\u9645\u7248',
      sectionIntlDesc: '\u4e13\u4e3a\u6d77\u5916\u8bfb\u8005\u6253\u9020\u7684\u82f1\u6587\u7248AI\u524d\u7ebf',
      visitIntl: '\ud83d\udc49 \u8bbf\u95ee AI Frontline \u2192',
      analysisTitle: '\ud83d\udd0d AI\u524d\u7ebf\u6df1\u5ea6\u89e3\u8bfb',
      analysisSubtitle: '\u4e0d\u6b62\u4e8e\u65b0\u95fb\uff0c\u66f4\u63d0\u4f9b\u884c\u4e1a\u6d1e\u5bdf\u4e0e\u8d8b\u52bf\u5224\u65ad',
      pricingTitle: '\ud83d\udcb0 \u4e3b\u6d41\u5927\u6a21\u578bAPI\u5b9a\u4ef7\u5bf9\u6bd4',
      pricingSubtitle: '\u6bcf\u767e\u4e07Token\u8ba1\u4ef7 \u00b7 \u6570\u636e\u622a\u81f32026\u5e744\u6708 \u00b7 \u4ec5\u4f9b\u53c2\u8003',
      intlModels: '\ud83c\udf0d \u56fd\u9645\u6a21\u578b International Models',
      chinaModels: '\ud83c\udde8\ud83c\uddf3 \u56fd\u4ea7\u6a21\u578b China Models (\u4eba\u6c11\u5e01 RMB)',
      planCompare: '\ud83c\udfab \u8ba2\u9605\u65b9\u6848\u5bf9\u6bd4',
      prevPage: '\u2190 \u4e0a\u4e00\u9875',
      nextPage: '\u4e0b\u4e00\u9875 \u2192',
      pagePrefix: '\u7b2c',
      pageSuffix: '\u9875',
      emptyNews: '\u6682\u65e0\u65b0\u95fb',
      expandBtn: '\u70b9\u51fb\u5c55\u5f00 \u2193',
      collapseBtn: '\u70b9\u51fb\u6536\u8d77 \u2191',
      counterPoints: '\u4e2a\u53cd\u76d1\u89c9\u89c2\u70b9',
      debateTitle: '\u4e89\u8bae\u7126\u70b9',
      proSide: '\u7acb\u8bba\u65b9',
      conSide: '\u53cd\u5bf9\u65b9',
      predictionTitle: '\u672a\u6765\u9884\u6d4b',
      predictionNote: '\u4ee5\u4e0a\u5206\u6790\u4ec5\u4ee3\u8868\u7f16\u8f91\u90e8\u89c2\u70b9\uff0c\u4e0d\u6784\u6210\u6295\u8d44\u5efa\u8bae',
      sourceLabel: '\u6765\u6e90',
      archiveEmpty: '\u6682\u65e0\u66f4\u65e9\u5f52\u6863\uff0c\u65b0\u6570\u636e\u5c06\u5728\u6bcf\u5468\u65e5\u81ea\u52a8\u5f52\u6863',
      footerCopyright: 'AI前线 © 2026 · AI Frontline · \u6bcf\u65e5\u66f4\u65b0',
      footerNote: '\u6570\u636e\u6765\u6e90\uff1a\u516c\u5f00\u7f51\u7edc\u8d44\u8baf\u6574\u7406 \u00b7 \u5e7f\u544a\u6536\u5165\u7528\u4e8e\u7ef4\u6301\u670d\u52a1\u5668\u8fd0\u8425',
      adInfeedPlaceholder: '\ud83d\udce2 \u4fe1\u606f\u6d41\u5e7f\u544a\u4f4d\uff08\u6587\u7ae0\u4e4b\u95f4\uff09',
      adSidebarPlaceholder: '\ud83d\udce2 \u4fa7\u8fb9\u5e7f\u544a\u4f4d\n300\u00d7600 / 300\u00d7250',
      adBottomPlaceholder: '\ud83d\udce2 \u5e95\u90e8\u5e7f\u544a\u4f4d \u00b7 728\u00d790 / 970\u00d790',
      categoryBreaking: '\u91cd\u78c5',
      categoryIndustry: '\u884c\u4e1a',
      categoryTech: '\u6280\u672f',
      categoryPolicy: '\u653f\u7b56',
      categoryFinance: '\u878d\u8d44',
      units: '\u6761',
      today: '\u4eca\u5929'
    },
    en: {
      siteTitle: 'AI Frontline - AI News & API Pricing',
      navLogo: 'AI Frontline',
      navNews: '\ud83d\udcf0 AI News',
      navAnalysis: '\ud83d\udd0d Deep Analysis',
      navPricing: '\ud83d\udcb0 API Pricing',
      langBtn: '\u4e2d',
      adTopPlaceholder: '\ud83d\udce2 Ad slot: Google AdSense / Baidu Union etc.',
      headlineTitle: '\u26a1 AI Frontline Daily',
      headlineSubtitle: 'Tracking the latest AI news and industry trends',
      updatePrefix: 'Updated: ',
      sectionTodayNews: '\ud83d\udcf0 Today\'s News',
      sectionWeeklyReview: '\ud83d\udcc5 Weekly Review',
      sectionStats: '\ud83d\udcca Today\'s AI Roundup',
      sectionHot: '\ud83d\udd25 Hot This Week',
      sectionTags: '\ud83c\udff7\ufe0f Hot Tags',
      sectionArchive: '\ud83d\udcc2 Archives',
      sectionSources: '\ud83d\udce1 Sources',
      sectionIntl: '\ud83c\udf0d International',
      sectionIntlDesc: 'English edition of AI Frontline for global readers',
      visitIntl: '\ud83d\udc49 Visit AI Frontline \u2192',
      analysisTitle: '\ud83d\udd0d AI Frontline Deep Analysis',
      analysisSubtitle: 'Beyond news: industry insights and trend judgment',
      pricingTitle: '\ud83d\udcb0 Mainstream LLM API Pricing Comparison',
      pricingSubtitle: 'Per million tokens \u00b7 Data as of Apr 2026 \u00b7 For reference only',
      intlModels: '\ud83c\udf0d International Models',
      chinaModels: '\ud83c\udde8\ud83c\uddf3 China Models (RMB)',
      planCompare: '\ud83c\udfab Subscription Plans',
      prevPage: '\u2190 Prev',
      nextPage: 'Next \u2192',
      pagePrefix: 'Page ',
      pageSuffix: '',
      emptyNews: 'No news yet',
      expandBtn: 'Expand \u2193',
      collapseBtn: 'Collapse \u2191',
      counterPoints: ' counter-intuitive insights',
      debateTitle: 'Debate',
      proSide: 'Pro',
      conSide: 'Con',
      predictionTitle: 'Prediction',
      predictionNote: 'Analysis represents editorial views only, not investment advice',
      sourceLabel: 'Source',
      archiveEmpty: 'No earlier archives. New data auto-archives every Sunday.',
      footerCopyright: 'AI Frontline © 2026 · Daily Updates',
      footerNote: 'Data sources: public web aggregation · Ad revenue supports server operations',
      adInfeedPlaceholder: '\ud83d\udce2 In-feed Ad Slot (between articles)',
      adSidebarPlaceholder: '\ud83d\udce2 Sidebar Ad\n300\u00d7600 / 300\u00d7250',
      adBottomPlaceholder: '\ud83d\udce2 Bottom Ad Slot \u00b7 728\u00d790 / 970\u00d790',
      categoryBreaking: 'Breaking',
      categoryIndustry: 'Industry',
      categoryTech: 'Tech',
      categoryPolicy: 'Policy',
      categoryFinance: 'Finance',
      units: ' items',
      today: 'Today'
    }
  };

  function t(key, interpolations) {
    let text = dict[currentLang][key] || dict.zh[key] || key;
    if (interpolations) {
      Object.keys(interpolations).forEach(function (k) {
        text = text.replace(new RegExp('{{' + k + '}}', 'g'), interpolations[k]);
      });
    }
    return text;
  }

  function getLang() { return currentLang; }

  function setLang(lang) {
    if (lang !== 'zh' && lang !== 'en') return;
    currentLang = lang;
    document.documentElement.lang = lang === 'zh' ? 'zh-CN' : 'en';
    notify();
  }

  function toggle() {
    setLang(currentLang === 'zh' ? 'en' : 'zh');
  }

  function onChange(fn) {
    listeners.push(fn);
  }

  function notify() {
    listeners.forEach(function (fn) { fn(currentLang); });
  }

  // Initialize from localStorage if available
  try {
    var saved = localStorage.getItem('ai-frontline-lang');
    if (saved === 'zh' || saved === 'en') currentLang = saved;
  } catch (e) { /* ignore */ }

  return {
    t: t,
    getLang: getLang,
    setLang: setLang,
    toggle: toggle,
    onChange: onChange
  };
})();
