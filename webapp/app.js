// Global state
let profileData = null;
let waifuList = [];
let currentView = 'profile';

// Initialize WebApp
if (window.Telegram && window.Telegram.WebApp) {
    window.Telegram.WebApp.ready();
    window.Telegram.WebApp.expand();
}

// Load profile data on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadProfile();
    
    // Set up level button
    document.getElementById('level-btn').addEventListener('click', () => {
        if (window.Telegram?.WebApp?.showAlert) {
            window.Telegram.WebApp.showAlert('Функция прокачки навыков будет добавлена в следующем обновлении!');
        }
    });
});

// Navigation function
function navigateTo(view) {
    if (view === 'profile') {
        document.getElementById('profile-view').classList.remove('hidden');
        document.getElementById('other-views').classList.add('hidden');
        currentView = 'profile';
    } else {
        document.getElementById('profile-view').classList.add('hidden');
        document.getElementById('other-views').classList.remove('hidden');
        
        const viewTitle = document.getElementById('view-title');
        const viewContent = document.getElementById('view-content');
        
        const views = {
            'waifus': { title: '🎴 Мои вайфу', content: 'Список всех вайфу игрока' },
            'shop': { title: '🏪 Магазин', content: 'Внутриигровой магазин' },
            'clan': { title: '🏰 Клан', content: 'Система кланов (в разработке)' },
            'quests': { title: '📅 Ежедневные задания', content: 'Активные миссии (в разработке)' },
            'skills': { title: '🧬 Прокачка навыков', content: 'Дерево навыков (в разработке)' },
            'settings': { title: '⚙️ Настройки профиля', content: 'Кастомизация профиля (в разработке)' }
        };
        
        if (views[view]) {
            viewTitle.textContent = views[view].title;
            viewContent.textContent = views[view].content;
        }
        
        currentView = view;
    }
}

// Load profile data
async function loadProfile() {
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        
        const response = await fetch('/api/profile?' + new URLSearchParams({ initData }));
        if (!response.ok) {
            throw new Error('Failed to fetch profile');
        }
        
        profileData = await response.json();
        
        // Update user info
        document.getElementById('user-name').textContent = '@' + (profileData.username || 'Unknown');
        document.getElementById('user-id').textContent = `ID: ${profileData.user_id || '...'}`;
        
        // Update currency
        document.getElementById('gold-value').textContent = profileData.gold || 0;
        document.getElementById('gem-value').textContent = profileData.gems || 0;
        document.getElementById('token-value').textContent = profileData.tokens || 0;
        
        // Update level and XP
        document.getElementById('player-level').textContent = profileData.level || 1;
        
        // Calculate XP progress (simplified)
        const currentXP = profileData.xp || 0;
        const nextLevelXP = 100 * Math.pow(profileData.level || 1, 1.1);
        const currentLevelXP = profileData.level > 1 ? 100 * Math.pow(profileData.level - 1, 1.1) : 0;
        const xpInLevel = currentXP - currentLevelXP;
        const xpNeeded = nextLevelXP - currentLevelXP;
        const xpPercent = Math.min(100, (xpInLevel / xpNeeded) * 100);
        
        document.getElementById('xp-fill').style.width = xpPercent + '%';
        document.getElementById('xp-current').textContent = Math.floor(xpInLevel);
        document.getElementById('xp-next').textContent = Math.floor(xpNeeded);
        
        // Load active waifu
        await loadActiveWaifu();
        
    } catch (error) {
        console.error('Error loading profile:', error);
        if (window.Telegram?.WebApp?.showAlert) {
            window.Telegram.WebApp.showAlert('Ошибка загрузки профиля');
        }
    }
}

// Load active waifu
async function loadActiveWaifu() {
    const activeWaifuCard = document.getElementById('active-waifu-card');
    
    if (!profileData.active_waifu) {
        activeWaifuCard.innerHTML = `
            <p style="padding: 20px; color: #666;">Нет активной вайфу</p>
            <button class="change-waifu-btn" onclick="navigateTo('waifus')">Выбрать вайфу</button>
        `;
        return;
    }
    
    const waifu = profileData.active_waifu;
    const power = calculatePower(waifu);
    
    activeWaifuCard.innerHTML = `
        <img src="${waifu.image_url}" alt="${waifu.name}" class="waifu-image" onerror="this.onerror=null; this.src='data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20width=%27100%27%20height=%27100%27%3E%3Ctext%20x=%2750%25%27%20y=%2750%25%27%20font-size=%2714%27%20text-anchor=%27middle%27%20dy=%27.3em%27%3E🎭%3C/text%3E%3C/svg%3E'">
        <div class="waifu-name">${waifu.name}</div>
        <div class="waifu-info">Уровень ${waifu.level} • 💪${power}</div>
        <button class="change-waifu-btn" onclick="navigateTo('waifus')">Сменить вайфу</button>
    `;
    
    // Make the card clickable to navigate to waifus
    activeWaifuCard.onclick = () => navigateTo('waifus');
}

// Calculate power
function calculatePower(waifu) {
    const stats = waifu.stats || {};
    const dynamic = waifu.dynamic || {};
    
    let power = 0;
    power += stats.power || 0;
    power += stats.intellect || 0;
    power += stats.charm || 0;
    power += stats.charisma || 0;
    power += stats.magic || 0;
    power += stats.speed || 0;
    
    // Add bonuses from level
    const levelBonus = Math.floor((waifu.level - 1) / 5);
    power += levelBonus * 5;
    
    // Add bonuses from mood and loyalty
    const mood = dynamic.mood || 50;
    const loyalty = dynamic.loyalty || 50;
    const dynamicBonus = Math.floor((mood + loyalty) / 50);
    power += dynamicBonus;
    
    return power;
}

// Close WebApp
function closeWebApp() {
    if (window.Telegram?.WebApp?.close) {
        window.Telegram.WebApp.close();
    }
}
