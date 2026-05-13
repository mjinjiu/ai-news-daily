/**
 * AI前线 — 主应用逻辑 (app.js)
 * 职责：交互控制、事件委托、导航、广告初始化
 * 架构：纯事件驱动，所有动态内容交由 renderer.js 处理
 */

(function () {
  'use strict';

  // ==================== 1. 板块切换 ====================
  var navLinks = document.querySelectorAll('.nav-link');
  var sections = document.querySelectorAll('.main-section');

  function switchSection(targetId, skipScroll) {
    navLinks.forEach(function (link) {
      link.classList.toggle('active', link.dataset.section === targetId);
      link.setAttribute('aria-current', link.dataset.section === targetId ? 'page' : 'false');
    });

    sections.forEach(function (section) {
      section.classList.toggle('active', section.id === targetId + 'Section');
    });

    if (!skipScroll) {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // Update URL hash without triggering hashchange
    if (history.replaceState) {
      history.replaceState(null, null, '#' + targetId);
    }
  }

  // 导航点击
  document.querySelector('.nav-links').addEventListener('click', function (e) {
    var link = e.target.closest('.nav-link');
    if (!link) return;
    e.preventDefault();
    switchSection(link.dataset.section);
  });

  // Hash 变化
  window.addEventListener('hashchange', function () {
    var hash = window.location.hash.slice(1);
    if (hash) switchSection(hash);
  });

  // 页面加载检查 hash
  if (window.location.hash) {
    switchSection(window.location.hash.slice(1), true);
  }

  // ==================== 2. 语言切换（按钮已隐藏，逻辑保留备用） ====================
  var langToggle = document.getElementById('langToggle');
  if (langToggle) {
    langToggle.addEventListener('click', function () {
      I18N.toggle();
      try { localStorage.setItem('ai-frontline-lang', I18N.getLang()); } catch (e) { /* ignore */ }
    });

    // 初始化按钮文本
    function syncLangBtn() {
      langToggle.textContent = I18N.t('langBtn');
      langToggle.setAttribute('aria-pressed', I18N.getLang() === 'en' ? 'true' : 'false');
    }
    I18N.onChange(syncLangBtn);
    syncLangBtn();
  }

  // ==================== 3. 全局事件委托 — 新闻点击跳转 ====================
  document.addEventListener('click', function (e) {
    var clickable = e.target.closest('[data-source-url]');
    if (!clickable) return;
    if (e.target.closest('a')) return; // Let real links handle themselves

    var url = clickable.dataset.sourceUrl;
    if (!url) return;

    // Keyboard support: Enter key
    if (e.type === 'keydown' && e.key !== 'Enter') return;

    e.preventDefault();
    window.open(url, '_blank', 'noopener,noreferrer');
  });

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Enter') return;
    var el = document.activeElement;
    if (!el || !el.dataset.sourceUrl) return;
    e.preventDefault();
    window.open(el.dataset.sourceUrl, '_blank', 'noopener,noreferrer');
  });

  // ==================== 4. 广告位控制 ====================
  var adConfig = { top: false, sidebar: false, infeed: false, bottom: false };

  function initAds(config) {
    Object.assign(adConfig, config || {});
    var map = { top: 'adTop', sidebar: 'sidebarAd', infeed: 'adInfeed', bottom: 'adBottom' };
    Object.keys(map).forEach(function (key) {
      var el = document.getElementById(map[key]);
      if (!el) return;
      var placeholder = el.querySelector('.ad-placeholder');
      if (adConfig[key]) {
        el.classList.add('ad-active');
        if (placeholder) placeholder.style.display = 'none';
      } else {
        el.classList.remove('ad-active');
        if (placeholder) placeholder.style.display = '';
      }
    });
  }

  // Expose to global for manual override
  window.AIFrontline = { initAds: initAds };

  // ==================== 5. 渐入动画 (IntersectionObserver) ====================
  // CSS 默认 opacity:1；JS 在支持的情况下为元素添加 anim-initial 类触发动画
  var observer;
  function initAnimations() {
    var animElements = document.querySelectorAll('.anim-fade-up, .anim-scale-in');
    if (!animElements.length) return;

    // Add initial state class for JS-driven animation
    animElements.forEach(function (el) {
      el.classList.add('anim-initial');
    });

    if (!('IntersectionObserver' in window)) {
      // Fallback: show all immediately
      animElements.forEach(function (el) {
        el.classList.remove('anim-initial');
        el.classList.add('anim-visible');
      });
      return;
    }

    observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.remove('anim-initial');
          entry.target.classList.add('anim-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.05 });

    animElements.forEach(function (el) { observer.observe(el); });

    // 2s fallback: ensure all visible even if observer fails
    setTimeout(function () {
      animElements.forEach(function (el) {
        el.classList.remove('anim-initial');
        el.classList.add('anim-visible');
      });
    }, 2000);
  }

  // ==================== 6. 更新时间 ====================
  function updateTime() {
    var now = new Date();
    var lang = I18N.getLang();
    var timeStr;
    if (lang === 'zh') {
      timeStr = now.toLocaleString('zh-CN', {
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit'
      });
    } else {
      timeStr = now.toLocaleString('en-US', {
        year: 'numeric', month: 'short', day: '2-digit',
        hour: '2-digit', minute: '2-digit'
      });
    }
    var prefix = I18N.t('updatePrefix');
    document.querySelectorAll('.update-time').forEach(function (el) {
      el.textContent = prefix + timeStr;
    });
  }

  // ==================== 7. 深度解读分页（已废弃，保留空壳兼容旧代码） ====================
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-analysis-action]');
    if (!btn) return;
    // analysis section 已移除，此功能当前不生效
  });

  // ==================== 8. 所有数据渲染完成后初始化动画 ====================
  function onRenderComplete() {
    initAnimations();
    updateTime();
    setInterval(updateTime, 300000);
  }

  // ==================== 9. 初始化 ====================
  document.addEventListener('DOMContentLoaded', function () {
    Renderer.loadAll();
    // Wait a tick for DOM to update from renderer
    setTimeout(onRenderComplete, 100);
  });

  console.log('\u2705 AI前线 v4.2 loaded \u00b7 中文站专注版 \u00b7 https://mjinjiu.github.io/ai-news-daily/');
})();
