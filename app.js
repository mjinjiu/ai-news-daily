// AI前线 v2.0 — 板块切换 + 语言切换 + 广告位控制

(function() {
    // ========== 板块切换 ==========
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.section');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = link.dataset.section;
            
            // 更新导航状态
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            // 切换板块
            sections.forEach(s => s.classList.remove('active'));
            document.getElementById(target + 'Section').classList.add('active');
            
            // 滚动到顶部
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    });

    // ========== 语言切换 ==========
    let currentLang = 'zh';
    const langToggle = document.getElementById('langToggle');

    function toggleLanguage() {
        currentLang = currentLang === 'zh' ? 'en' : 'zh';
        
        // 切换所有带 data-zh / data-en 的元素
        document.querySelectorAll('[data-zh][data-en]').forEach(el => {
            el.textContent = el.getAttribute('data-' + currentLang);
        });
        
        // 更新按钮文本
        langToggle.textContent = currentLang === 'zh' ? 'EN/中' : '中/EN';
        
        // 更新页面标题
        document.title = currentLang === 'zh' 
            ? 'AI前线 - AI News & API Pricing'
            : 'AI Frontline - AI News & API Pricing';
    }

    langToggle.addEventListener('click', toggleLanguage);

    // ========== 广告位控制 ==========
    // 预留：根据用户配置显示/隐藏广告位
    const adConfig = {
        top: false,      // 顶部横幅
        sidebar: false,  // 侧边栏
        infeed: false,   // 信息流
        bottom: false    // 底部
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

    // 将广告初始化函数暴露到全局，供后续配置调用
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

    // Fallback: 确保所有卡片在2秒内显示（IntersectionObserver未触发时）
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
    setInterval(updateTime, 300000); // 每5分钟更新

    console.log('✅ AI前线 v2.0 已加载 · AI Frontline initialized');
})();
