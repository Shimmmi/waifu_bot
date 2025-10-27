// Global state
let currentState = 'profile';
let profileData = null;
let waifuList = [];
let activeWaifuId = null;

// Initialize WebApp
window.Telegram.WebApp.ready();
window.Telegram.WebApp.expand();

// Initialize on load
window.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const state = params.get('state') || 'profile';
    
    renderState(state);
});

// Handle browser history
window.addEventListener('popstate', (e) => {
    if (e.state) {
        renderState(e.state.state);
    }
});

// Navigation functions
function navigateToState(state, data = {}) {
    let url = `?state=${state}`;
    
    Object.entries(data).forEach(([key, value]) => {
        url += `&${key}=${value}`;
    });
    
    window.history.pushState({state, ...data}, '', url);
    renderState(state);
}

function renderState(state) {
    hideAllViews();
    
    switch(state) {
        case 'profile':
            renderProfile();
            break;
        case 'waifu-list':
            renderWaifuList();
            break;
    }
    
    currentState = state;
    showView(state);
}

function hideAllViews() {
    document.getElementById('profile-view').classList.add('hidden');
    document.getElementById('waifu-list-view').classList.add('hidden');
}

function showView(state) {
    const viewMap = {
        'profile': 'profile-view',
        'waifu-list': 'waifu-list-view'
    };
    
    const viewId = viewMap[state];
    if (viewId) {
        document.getElementById(viewId).classList.remove('hidden');
    }
}

// Render profile
async function renderProfile() {
    try {
        // Get initData from Telegram WebApp
        const initData = window.Telegram?.WebApp?.initData || '';
        
        // Load profile data with initData
        const response = await fetch('/api/profile?' + new URLSearchParams({ initData }));
        if (!response.ok) {
            throw new Error('Failed to fetch profile');
        }
        
        profileData = await response.json();
        activeWaifuId = profileData.active_waifu?.id || null;
        
        // Render profile info
        const profileInfo = document.getElementById('profile-info');
        profileInfo.innerHTML = `
            <p style="font-size: 14px; opacity: 0.7; margin-bottom: 8px;">@{profileData.username}</p>
            <p style="font-size: 16px; font-weight: bold;">💰 ${profileData.gold} золото</p>
            <p style="font-size: 16px; font-weight: bold;">⭐ Уровень ${profileData.level}</p>
        `.replace('{profileData.username}', profileData.username || 'Unknown');
        
        // Render active waifu
        const activeWaifuCard = document.getElementById('active-waifu-card');
        
        if (profileData.active_waifu) {
            const waifu = profileData.active_waifu;
            const stats = calculateStats(waifu.stats);
            const power = calculatePower(waifu);
            
            const dynamic = waifu.dynamic || {};
            
            activeWaifuCard.innerHTML = `
                <img src="${waifu.image_url}" alt="${waifu.name}" onerror="this.src='data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20width=%27200%27%20height=%27200%27%3E%3Ctext%20x=%2750%25%27%20y=%2750%25%27%20font-size=%2714%27%20text-anchor=%27middle%27%20dy=%27.3em%27%3E🎭%3C/text%3E%3C/svg%3E'">
                <div class="active-waifu-info">
                    <p style="font-size: 18px; font-weight: bold; margin-bottom: 8px;">${waifu.name}</p>
                    <p style="font-size: 14px; opacity: 0.7; margin-bottom: 12px;">Уровень ${waifu.level} • 💪${power}</p>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-label">⚔️ Сила</div>
                            <div class="stat-value">${stats.power}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">💖 Обаяние</div>
                            <div class="stat-value">${stats.charm}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">🍀 Удача</div>
                            <div class="stat-value">${stats.luck}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">💕 Привязанность</div>
                            <div class="stat-value">${stats.affection}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">🧠 Интеллект</div>
                            <div class="stat-value">${stats.intellect}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">⚡ Скорость</div>
                            <div class="stat-value">${stats.speed}</div>
                        </div>
                    </div>
                    <div class="stats-grid" style="grid-template-columns: repeat(3, 1fr); margin-top: 12px;">
                        <div class="stat-item">
                            <div class="stat-label">😊 Настроение</div>
                            <div class="stat-value">${dynamic.mood || 50}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">❤️ Лояльность</div>
                            <div class="stat-value">${dynamic.loyalty || 50}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">⚡ Энергия</div>
                            <div class="stat-value">${dynamic.energy || 100}</div>
                        </div>
                    </div>
                </div>
            `;
            
            // Add click handler to navigate to waifu list
            activeWaifuCard.onclick = () => navigateToState('waifu-list');
        } else {
            activeWaifuCard.innerHTML = `
                <p class="empty-state">Нет активной вайфу</p>
            `;
            activeWaifuCard.onclick = () => navigateToState('waifu-list');
        }
        
    } catch (error) {
        console.error('Error rendering profile:', error);
        document.getElementById('profile-info').innerHTML = `
            <p style="color: red;">Ошибка загрузки профиля</p>
        `;
    }
}

// Render waifu list
async function renderWaifuList() {
    const waifuGrid = document.getElementById('waifu-grid');
    waifuGrid.innerHTML = '<p class="loading">Загрузка...</p>';
    
    try {
        // Load waifu list
        // Get initData from Telegram WebApp
        const initData = window.Telegram?.WebApp?.initData || '';
        
        const response = await fetch('/api/waifus?' + new URLSearchParams({ initData }));
        if (!response.ok) {
            throw new Error('Failed to fetch waifus');
        }
        
        waifuList = await response.json();
        
        if (waifuList.length === 0) {
            waifuGrid.innerHTML = '<p class="empty-state">У вас пока нет вайфу</p>';
            return;
        }
        
        // Render grid
        waifuGrid.innerHTML = '';
        waifuList.forEach(waifu => {
            const isActive = waifu.id === activeWaifuId;
            const power = calculatePower(waifu);
            
            const card = document.createElement('div');
            card.className = `waifu-card ${isActive ? 'active' : ''}`;
            card.innerHTML = `
                ${isActive ? '<div class="active-badge">✓ АКТИВНАЯ</div>' : ''}
                <img src="${waifu.image_url}" alt="${waifu.name}" onerror="this.src='data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20width=%27100%27%20height=%27100%27%3E%3Ctext%20x=%2750%25%27%20y=%2750%25%27%20font-size=%2712%27%20text-anchor=%27middle%27%20dy=%27.3em%27%3E🎭%3C/text%3E%3C/svg%3E'">
                <div class="waifu-card-info">
                    <div class="waifu-card-name">${waifu.name}</div>
                    <div class="waifu-card-level">Ур.${waifu.level} • 💪${power}</div>
                </div>
            `;
            
            card.onclick = () => setActiveWaifu(waifu.id);
            waifuGrid.appendChild(card);
        });
        
    } catch (error) {
        console.error('Error rendering waifu list:', error);
        waifuGrid.innerHTML = '<p class="empty-state" style="color: red;">Ошибка загрузки</p>';
    }
}

// Set active waifu
async function setActiveWaifu(waifuId) {
    try {
        const response = await fetch(`/api/waifu/${waifuId}/set-active`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error('Failed to set active waifu');
        }
        
        // Update active waifu ID
        activeWaifuId = waifuId;
        
        // Show feedback
        window.Telegram.WebApp.showAlert('✅ Вайфу установлена как активная!');
        
        // Return to profile and refresh
        navigateToState('profile');
        await renderProfile();
        
    } catch (error) {
        console.error('Error setting active waifu:', error);
        window.Telegram.WebApp.showAlert('❌ Ошибка при установке активной вайфу');
    }
}

// Helper functions
function calculateStats(stats) {
    return {
        power: stats.power || 0,
        intellect: stats.intellect || 0,
        charm: stats.charm || 0,
        luck: stats.luck || 0,
        affection: stats.affection || 0,
        speed: stats.speed || 0
    };
}

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
    window.Telegram.WebApp.close();
}
