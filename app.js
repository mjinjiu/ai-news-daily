// AI前线 - 网站交互脚本

// 更新时间显示
function updateTime() {
    const now = new Date();
    const timeString = now.toLocaleString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    const updateElement = document.querySelector('.update-time');
    if (updateElement) {
        updateElement.textContent = `最后更新：${timeString}`;
    }
}

// 新闻卡片动画
function animateCards() {
    const cards = document.querySelectorAll('.news-card');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, index * 100);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
}

// 搜索功能（可扩展）
function initSearch() {
    // 预留搜索功能接口
    console.log('搜索功能已准备就绪');
}

// 标签筛选功能
function filterByTag(tag) {
    const cards = document.querySelectorAll('.news-card');
    cards.forEach(card => {
        const cardTag = card.querySelector('.news-tag');
        if (tag === 'all' || cardTag.classList.contains(`tag-${tag}`)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', () => {
    updateTime();
    animateCards();
    initSearch();
    
    // 每5分钟更新时间
    setInterval(updateTime, 300000);
});

// 添加滚动效果
let lastScroll = 0;
window.addEventListener('scroll', () => {
    const header = document.querySelector('header');
    const currentScroll = window.pageYOffset;
    
    if (currentScroll > 100) {
        header.style.boxShadow = '0 4px 20px rgba(0,0,0,0.3)';
    } else {
        header.style.boxShadow = 'none';
    }
    
    lastScroll = currentScroll;
});
