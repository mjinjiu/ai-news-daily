// AI前线 v3.1 — 双站点运营 · 板块切换 + 语言切换 + 站点跳转 + 广告位控制

(function() {
    // ========== 板块切换 ==========
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.section');

    function switchSection(targetId) {
        // 更新导航状态
        navLinks.forEach(l => {
            l.classList.remove('active');
            if (l.dataset.section === targetId) {
                l.classList.add('active');
            }
        });
        
        // 切换板块
        sections.forEach(s => s.classList.remove('active'));
        const targetSection = document.getElementById(targetId + 'Section');
        if (targetSection) {
            targetSection.classList.add('active');
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    }

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            switchSection(link.dataset.section);
        });
    });

    // 处理URL hash导航
    window.addEventListener('hashchange', () => {
        const hash = window.location.hash.slice(1);
        if (hash) switchSection(hash);
    });
    
    // 页面加载时检查hash
    if (window.location.hash) {
        const hash = window.location.hash.slice(1);
        switchSection(hash);
    }

    // ========== 语言切换（页面内） ==========
    let currentLang = 'zh';
    const langToggle = document.getElementById('langToggle');

    function toggleLanguage() {
        currentLang = currentLang === 'zh' ? 'en' : 'zh';
        
        // 切换所有带 data-zh / data-en 的元素（包括导航栏）
        document.querySelectorAll('[data-zh][data-en]').forEach(el => {
            const newText = el.getAttribute('data-' + currentLang);
            if (el.classList.contains('nav-link')) {
                // 导航链接需要保留emoji前缀
                const emoji = el.textContent.match(/^[^\w\s]+/);
                el.textContent = (emoji ? emoji[0] : '') + newText.replace(/^[^\w\s]+/, '');
            } else {
                el.textContent = newText;
            }
        });
        
        // 更新按钮文本和视觉状态
        langToggle.textContent = currentLang === 'zh' ? 'EN' : '中';
        langToggle.style.background = currentLang === 'en' ? 'var(--primary-soft)' : '';
        langToggle.style.color = currentLang === 'en' ? 'var(--primary)' : '';
        langToggle.style.borderColor = currentLang === 'en' ? 'var(--primary)' : '';
        
        // 更新页面标题
        document.title = currentLang === 'zh' 
            ? 'AI前线 - AI News & API Pricing'
            : 'AI Frontline - AI News & API Pricing';
    }

    langToggle.addEventListener('click', toggleLanguage);

    // ========== 新闻点击跳转 ==========
    document.querySelectorAll('.news-item[data-source-url]').forEach(item => {
        item.addEventListener('click', (e) => {
            if (e.target.closest('a')) return;
            const url = item.dataset.sourceUrl;
            if (url) window.open(url, '_blank', 'noopener,noreferrer');
        });
    });

    // 重磅卡片点击跳转
    document.querySelectorAll('.card.featured[data-source-url]').forEach(card => {
        card.addEventListener('click', (e) => {
            if (e.target.closest('a')) return;
            const url = card.dataset.sourceUrl;
            if (url) window.open(url, '_blank', 'noopener,noreferrer');
        });
    });

    // 本周回顾新闻点击跳转
    document.querySelectorAll('.day-list li[data-source-url]').forEach(li => {
        li.addEventListener('click', (e) => {
            if (e.target.closest('a')) return;
            const url = li.dataset.sourceUrl;
            if (url) window.open(url, '_blank', 'noopener,noreferrer');
        });
    });

    // ========== 广告位控制 ==========
    const adConfig = {
        top: false,
        sidebar: false,
        infeed: false,
        bottom: false
    };

    function initAds(config) {
        Object.assign(adConfig, config);
        
        if (adConfig.top) {
            document.getElementById('adTop').classList.add('ad-active');
            document.getElementById('adTop').querySelector('.ad-placeholder').style.display = 'none';
        }
        if (adConfig.sidebar) {
            document.getElementById('sidebarAd').classList.add('ad-active');
            document.getElementById('sidebarAd').querySelector('.ad-placeholder').style.display = 'none';
        }
        if (adConfig.infeed) {
            document.getElementById('adInfeed').classList.add('ad-active');
            document.getElementById('adInfeed').querySelector('.ad-placeholder').style.display = 'none';
        }
        if (adConfig.bottom) {
            document.getElementById('adBottom').classList.add('ad-active');
            document.getElementById('adBottom').querySelector('.ad-placeholder').style.display = 'none';
        }
    }

    window.AIFrontline = { initAds };

    // ========== 卡片渐入动画 ==========
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.05 });

    document.querySelectorAll('.card, .stat-item, .plan-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(12px)';
        el.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        observer.observe(el);
    });

    // Fallback: 确保所有卡片在2秒内显示
    setTimeout(() => {
        document.querySelectorAll('.card, .stat-item, .plan-card').forEach(el => {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        });
    }, 1500);

    // ========== 更新时间 ==========
    function updateTime() {
        const now = new Date();
        const timeStr = now.toLocaleString('zh-CN', {
            year: 'numeric', month: '2-digit', day: '2-digit',
            hour: '2-digit', minute: '2-digit'
        });
        const el = document.querySelector('.update-time');
        if (el) el.textContent = 'Updated: ' + timeStr;
    }
    updateTime();
    setInterval(updateTime, 300000);

    console.log('✅ AI前线 v3.1 已加载 · 中文版 · https://mjinjiu.github.io/ai-news-daily/');
})();
