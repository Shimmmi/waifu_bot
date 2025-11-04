// Global state
let profileData = null;
let waifuList = [];
let currentView = 'profile';
let waifuSortBy = 'name'; // Default sort: name, rarity, level, power, race, profession, nationality
let showOnlyFavorites = false; // Filter toggle
let currentSkillCategory = 'account'; // Track active skill category

// Initialize WebApp
if (window.Telegram && window.Telegram.WebApp) {
    window.Telegram.WebApp.ready();
    window.Telegram.WebApp.expand();
}

// Load profile data on page load
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 WebApp loaded at:', new Date().toISOString());
    console.log('🔗 Current URL:', window.location.href);
    console.log('📱 User Agent:', navigator.userAgent);
    
    // Log URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    console.log('📋 URL Parameters:', Object.fromEntries(urlParams.entries()));
    
    await loadProfile();
});

// Reload profile when page becomes visible again (e.g., returning from waifu-card)
window.addEventListener('focus', async () => {
    const dataChanged = localStorage.getItem('waifu_data_changed');
    
    if (dataChanged === 'true') {
        console.log('🔄 Data changed, reloading...');
        localStorage.removeItem('waifu_data_changed');
        
        if (currentView === 'profile') {
            await loadProfile();
        } else if (currentView === 'waifus' || currentView === 'select-waifu') {
            // Reload waifu list
            const viewContent = document.getElementById('view-content');
            if (currentView === 'waifus') {
                await loadWaifuList(viewContent);
            } else if (currentView === 'select-waifu') {
                await loadSelectWaifu(viewContent);
            }
        }
    }
});

// Refresh current page
async function refreshCurrentPage() {
    const refreshBtn = document.getElementById('refresh-btn');
    if (!refreshBtn) return;
    
    // Add spinning animation
    refreshBtn.classList.add('spinning');
    
    try {
        if (currentView === 'profile') {
            await loadProfile();
        } else if (currentView === 'waifus') {
            const container = document.getElementById('view-content');
            await loadWaifuList(container);
        } else if (currentView === 'skills') {
            const container = document.getElementById('view-content');
            await loadSkills(container);
        } else if (currentView === 'upgrade') {
            const container = document.getElementById('view-content');
            await loadUpgradePage(container);
        } else if (currentView === 'clan') {
            const container = document.getElementById('view-content');
            await loadClanInfo(container);
        }
        
        // Show success animation
        refreshBtn.classList.remove('spinning');
        refreshBtn.style.transform = 'scale(1.2)';
        setTimeout(() => {
            refreshBtn.style.transform = '';
        }, 200);
    } catch (error) {
        console.error('Error refreshing page:', error);
        refreshBtn.classList.remove('spinning');
    }
}

// Navigation function
function navigateTo(view) {
    console.log(`🧭 Navigating to: ${view} (from: ${currentView})`);
    
    if (view === 'profile') {
        document.getElementById('profile-view').classList.remove('hidden');
        document.getElementById('other-views').classList.add('hidden');
        currentView = 'profile';
    } else {
        // Set currentView BEFORE loading content
        currentView = view;
        
        document.getElementById('profile-view').classList.add('hidden');
        document.getElementById('other-views').classList.remove('hidden');
        
        const viewTitle = document.getElementById('view-title');
        const viewContent = document.getElementById('view-content');
        
        const views = {
            'waifus': { title: '', content: 'loadWaifuList()' },
            'select-waifu': { title: '🎯 Выбрать активную вайфу', content: 'loadSelectWaifu()' },
            'shop': { title: '🏪 Магазин', content: 'loadShopItems()' },
            'clan': { title: '', content: 'loadClanInfo()' },
            'quests': { title: '📅 Ежедневные задания', content: 'loadQuests()' },
            'skills': { title: '', content: 'loadSkills()' },
            'settings': { title: '⚙️ Настройки профиля', content: 'loadSettings()' },
            'upgrade': { title: '⚡ Прокачка вайфу', content: 'loadUpgradePage()' }
        };
        
        if (views[view]) {
            viewTitle.textContent = views[view].title;
            
            // Hide/show back button based on view
            const backBtn = document.querySelector('#other-views .back-btn');
            if (backBtn) {
                // Hide back button for upgrade page (it already has one in the content)
                backBtn.style.display = view === 'upgrade' ? 'none' : 'block';
            }
            
            // Clear content first to prevent stale data
            viewContent.innerHTML = '<p class="loading">Загрузка...</p>';
            
            // Special handling for different views
            if (view === 'waifus') {
                loadWaifuList(viewContent);
            } else if (view === 'select-waifu') {
                loadSelectWaifu(viewContent);
            } else if (view === 'shop') {
                loadShopItems(viewContent);
            } else if (view === 'skills') {
                loadSkills(viewContent);
            } else if (view === 'quests') {
                loadQuests(viewContent);
            } else if (view === 'clan') {
                loadClanInfo(viewContent);
            } else if (view === 'settings') {
                loadSettings(viewContent);
            } else if (view === 'upgrade') {
                loadUpgradePage(viewContent);
            } else {
                viewContent.textContent = views[view].content;
            }
        }
    }
}

// Load waifu list (My Waifus - 1xN list with WebApp links)
async function loadWaifuList(container) {
    console.log('🎴 Loading My Waifus page');
    container.innerHTML = '<p class="loading">Загрузка...</p>';

    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch('/api/waifus?' + new URLSearchParams({ initData }));

        if (!response.ok) {
            throw new Error('Failed to fetch waifus');
        }

        waifuList = await response.json();
        console.log('🎴 Fetched waifus for My Waifus:', waifuList.length);

        if (waifuList.length === 0) {
            container.innerHTML = '<p style="padding: 20px; color: #666;">У вас пока нет вайфу</p>';
            return;
        }

        // Fetch skill effects to calculate summon costs
        summonCosts = await calculateSummonCosts();
        premiumCosts = await calculatePremiumSummonCosts();
        renderWaifuList(container);

    } catch (error) {
        console.error('Error loading waifu list:', error);
        container.innerHTML = '<p style="color: red; padding: 20px;">Ошибка загрузки</p>';
    }
}

// Global variable to store summon costs
let summonCosts = { single: 100, multi: 1000 };
let premiumCosts = { single: 100, multi: 1000 };

// Calculate summon costs with skill discounts
async function calculateSummonCosts() {
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch('/api/skills/effects?' + new URLSearchParams({ initData }));
        
        if (!response.ok) {
            return { single: 100, multi: 1000 };
        }
        
        const data = await response.json();
        const effects = data.effects || {};
        
        // Apply summon_discount
        const discount = effects.summon_discount || 0.0;
        const singleCost = Math.floor(100 * (1 - discount));
        const multiCost = Math.floor(1000 * (1 - discount));
        
        console.log(`💰 Summon costs calculated: ${singleCost} (${multiCost}) with ${discount*100}% discount`);
        return { single: singleCost, multi: multiCost };
        
    } catch (error) {
        console.error('Error calculating summon costs:', error);
        return { single: 100, multi: 1000 };
    }
}

// Calculate premium summon costs with skill discounts
async function calculatePremiumSummonCosts() {
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch('/api/skills/effects?' + new URLSearchParams({ initData }));
        
        if (!response.ok) {
            return { single: 100, multi: 1000 };
        }
        
        const data = await response.json();
        const effects = data.effects || {};
        
        // Apply summon_discount (same as regular summons)
        const discount = effects.summon_discount || 0.0;
        const singleCost = Math.floor(100 * (1 - discount));
        const multiCost = Math.floor(1000 * (1 - discount));
        
        console.log(`💎 Premium summon costs calculated: ${singleCost} (${multiCost}) with ${discount*100}% discount`);
        return { single: singleCost, multi: multiCost };
        
    } catch (error) {
        console.error('Error calculating premium summon costs:', error);
        return { single: 100, multi: 1000 };
    }
}

// Get rarity color for border/background
function getRarityColor(rarity) {
    const colors = {
        'Common': { border: '#d0d0d0', background: '#fafafa', glow: 'rgba(208, 208, 208, 0.3)' },
        'Uncommon': { border: '#4CAF50', background: '#f1f8f4', glow: 'rgba(76, 175, 80, 0.3)' },
        'Rare': { border: '#2196F3', background: '#e3f2fd', glow: 'rgba(33, 150, 243, 0.3)' },
        'Epic': { border: '#9C27B0', background: '#f3e5f5', glow: 'rgba(156, 39, 176, 0.3)' },
        'Legendary': { border: '#FF9800', background: '#fff3e0', glow: 'rgba(255, 152, 0, 0.5)' }
    };
    return colors[rarity] || colors['Common'];
}

// Render waifu list with current sort and filter settings
function renderWaifuList(container) {
    // Filter waifus
    let filteredWaifus = showOnlyFavorites 
        ? waifuList.filter(w => w.is_favorite) 
        : [...waifuList];

    // Sort waifus
    filteredWaifus.sort((a, b) => {
        switch (waifuSortBy) {
            case 'name':
                return a.name.localeCompare(b.name, 'ru');
            case 'rarity':
                const rarityOrder = { 'Common': 1, 'Uncommon': 2, 'Rare': 3, 'Epic': 4, 'Legendary': 5 };
                return (rarityOrder[b.rarity] || 0) - (rarityOrder[a.rarity] || 0);
            case 'level':
                return b.level - a.level;
            case 'power':
                return b.power - a.power;
            case 'race':
                return a.race.localeCompare(b.race, 'ru');
            case 'profession':
                return a.profession.localeCompare(b.profession, 'ru');
            case 'nationality':
                return a.nationality.localeCompare(b.nationality, 'ru');
            default:
                return 0;
        }
    });

    // Render toolbar + list
    container.innerHTML = `
        <!-- Toolbar Row 1 -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 8px; padding: 0 4px;">
            <button onclick="openSortModal()" style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; border: none; padding: 12px; border-radius: 12px; 
                font-size: 13px; font-weight: bold; cursor: pointer; display: flex; 
                align-items: center; justify-content: center; gap: 4px;
            ">
                🔄 Сортировка
            </button>
            <button onclick="toggleFavorites()" style="
                background: ${showOnlyFavorites ? '#4CAF50' : 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'}; 
                color: white; border: none; padding: 12px; border-radius: 12px; 
                font-size: 13px; font-weight: bold; cursor: pointer; display: flex; 
                align-items: center; justify-content: center; gap: 4px;
            ">
                ${showOnlyFavorites ? '✅ Избранные' : '❤️ Избранное'}
            </button>
        </div>
        
        <!-- Toolbar Row 2: Summon buttons (4 columns, compact) -->
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 4px; margin-bottom: 12px; padding: 0 4px;">
            <button onclick="summonWaifu(1)" style="
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                color: white; border: none; padding: 6px 4px; border-radius: 8px; 
                font-size: 9px; font-weight: bold; cursor: pointer; display: flex; 
                flex-direction: column; align-items: center; justify-content: center; gap: 2px;
            ">
                <div style="font-size: 10px;">✨</div>
                <div style="font-size: 8px; opacity: 0.95;">${summonCosts.single}💰</div>
            </button>
            <button onclick="summonWaifu(10)" style="
                background: linear-gradient(135deg, #FA8BFF 0%, #2BD2FF 90%, #2BFF88 100%); 
                color: white; border: none; padding: 6px 4px; border-radius: 8px; 
                font-size: 9px; font-weight: bold; cursor: pointer; display: flex; 
                flex-direction: column; align-items: center; justify-content: center; gap: 2px;
            ">
                <div style="font-size: 10px;">✨x10</div>
                <div style="font-size: 8px; opacity: 0.95;">${summonCosts.multi}💰</div>
            </button>
            <button onclick="summonPremiumWaifu(1)" style="
                background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); 
                color: white; border: none; padding: 6px 4px; border-radius: 8px; 
                font-size: 9px; font-weight: bold; cursor: pointer; display: flex; 
                flex-direction: column; align-items: center; justify-content: center; gap: 2px;
            ">
                <div style="font-size: 10px;">💎</div>
                <div style="font-size: 8px; opacity: 0.95;">${premiumCosts?.single || 100}💎</div>
            </button>
            <button onclick="summonPremiumWaifu(10)" style="
                background: linear-gradient(135deg, #FF6B6B 0%, #FFE66D 100%); 
                color: white; border: none; padding: 6px 4px; border-radius: 8px; 
                font-size: 9px; font-weight: bold; cursor: pointer; display: flex; 
                flex-direction: column; align-items: center; justify-content: center; gap: 2px;
            ">
                <div style="font-size: 10px;">💎x10</div>
                <div style="font-size: 8px; opacity: 0.95;">${premiumCosts?.multi || 1000}💎</div>
            </button>
        </div>
        
        <!-- Waifu List -->
        <div style="display: flex; flex-direction: column; gap: 12px;">
            ${filteredWaifus.length === 0 
                ? '<p style="padding: 20px; color: #666; text-align: center;">Нет вайфу для отображения</p>'
                : filteredWaifus.map(waifu => {
                    const rarityColors = getRarityColor(waifu.rarity);
                    return `
                    <div onclick="openWaifuDetail('${waifu.id}')" style="
                        background: ${rarityColors.background}; 
                        border-radius: 12px; padding: 16px; cursor: pointer; 
                        transition: all 0.2s; position: relative; display: flex; align-items: center;
                        border: 3px solid ${waifu.is_active ? '#4CAF50' : rarityColors.border};
                        box-shadow: 0 2px 8px ${rarityColors.glow};
                    " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px ${rarityColors.glow}'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px ${rarityColors.glow}'">
                        <div style="position: absolute; top: 8px; right: 8px; display: flex; gap: 4px; align-items: center;">
                            ${waifu.is_active ? '<div style="background: #4CAF50; color: white; padding: 4px 8px; border-radius: 12px; font-size: 10px;">✓ АКТИВНА</div>' : ''}
                            ${waifu.is_favorite ? '<div style="background: #f5576c; color: white; padding: 4px 6px; border-radius: 50%; font-size: 12px; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center;">❤️</div>' : ''}
                        </div>
                        <img src="${waifu.image_url}" alt="${waifu.name}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 8px; margin-right: 16px; border: 2px solid ${rarityColors.border};" onerror="this.src='data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20width=%2760%27%20height=%2760%27%3E%3Ctext%20x=%2750%25%27%20y=%2750%25%27%20font-size=%2712%27%20text-anchor=%27middle%27%20dy=%27.3em%27%3E🎭%3C/text%3E%3C/svg%3E'">
                        <div style="flex: 1;">
                            <div style="font-weight: bold; font-size: 16px; margin-bottom: 4px;">${waifu.name}</div>
                            <div style="font-size: 14px; color: #666; margin-bottom: 4px;">Уровень ${waifu.level} • 💪${waifu.power}</div>
                            <div style="font-size: 12px; color: #999;">${waifu.race} • ${waifu.profession} • ${getFlagEmoji(waifu.nationality)}</div>
                        </div>
                        <div style="color: #999; font-size: 20px;">→</div>
                    </div>
                `;}).join('')
            }
        </div>
    `;
}

// Load select waifu page (3-column grid for active waifu selection)
async function loadSelectWaifu(container) {
    console.log('🎯 Loading select waifu page');
    container.innerHTML = '<p class="loading">Загрузка...</p>';

    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch('/api/waifus?' + new URLSearchParams({ initData }));

        if (!response.ok) {
            throw new Error('Failed to fetch waifus');
        }

        const selectWaifuList = await response.json();
        console.log('🎯 Fetched waifus for selection:', selectWaifuList.length);

        if (selectWaifuList.length === 0) {
            container.innerHTML = '<p style="padding: 20px; color: #666;">У вас пока нет вайфу</p>';
            return;
        }

        // Render waifu grid (3 columns for selection)
        container.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 16px;">
                ${selectWaifuList.map(waifu => `
                    <div onclick="selectWaifu('${waifu.id}')" style="background: white; border-radius: 12px; padding: 12px; cursor: pointer; transition: transform 0.2s; position: relative; ${waifu.is_active ? 'border: 3px solid #4CAF50;' : ''}">
                        ${waifu.is_active ? '<div style="position: absolute; top: 4px; right: 4px; background: #4CAF50; color: white; padding: 2px 6px; border-radius: 8px; font-size: 10px;">✓ АКТИВНА</div>' : ''}
                        <img src="${waifu.image_url}" alt="${waifu.name}" style="width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: 8px; margin-bottom: 8px;" onerror="this.src='data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20width=%27100%27%20height=%27100%27%3E%3Ctext%20x=%2750%25%27%20y=%2750%25%27%20font-size=%2712%27%20text-anchor=%27middle%27%20dy=%27.3em%27%3E🎭%3C/text%3E%3C/svg%3E'">
                        <div style="font-weight: bold; font-size: 14px; margin-bottom: 4px;">${waifu.name}</div>
                        <div style="font-size: 12px; color: #666;">Ур.${waifu.level} • 💪${waifu.power}</div>
                    </div>
                `).join('')}
            </div>
        `;

    } catch (error) {
        console.error('Error loading select waifu:', error);
        container.innerHTML = '<p style="color: red; padding: 20px;">Ошибка загрузки</p>';
    }
}

// Open quick select active waifu modal (like avatar selection) - from main profile page
async function openSelectActiveWaifuModal() {
    console.log('🔗 Opening select active waifu modal');
    
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch('/api/waifus?' + new URLSearchParams({ initData }));

        if (!response.ok) {
            throw new Error('Failed to fetch waifus');
        }

        const waifuList = await response.json();
        
        if (waifuList.length === 0) {
            if (window.Telegram?.WebApp?.showAlert) {
                window.Telegram.WebApp.showAlert('У вас пока нет вайфу');
            }
            return;
        }
        
        // Sort by power (descending)
        waifuList.sort((a, b) => {
            const powerA = calculatePower(a);
            const powerB = calculatePower(b);
            return powerB - powerA;
        });
        
        // Create modal
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            padding: 20px;
        `;
        
        modal.innerHTML = `
            <div style="background: white; border-radius: 20px; max-width: 600px; width: 100%; max-height: 80vh; overflow-y: auto; padding: 24px;">
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;">
                    ${waifuList.map(waifu => {
                        const power = calculatePower(waifu);
                        return `
                        <div onclick="selectActiveWaifuFromModal('${waifu.id}')" style="cursor: pointer; position: relative; border: ${waifu.is_active ? '3px solid #4CAF50' : '2px solid #e0e0e0'}; border-radius: 12px; padding: 8px; transition: transform 0.2s; display: flex; flex-direction: column;">
                            ${waifu.is_active ? '<div style="position: absolute; top: 4px; right: 4px; background: #4CAF50; color: white; padding: 2px 4px; border-radius: 6px; font-size: 10px; z-index: 1;">✓</div>' : ''}
                            <div style="width: 100%; height: 100px; overflow: hidden; border-radius: 8px; margin-bottom: 6px; flex-shrink: 0;">
                                <img src="${waifu.image_url}" alt="${waifu.name}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.src='data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20width=%27100%27%20height=%27100%27%3E%3Ctext%20x=%2750%25%27%20y=%2750%25%27%20font-size=%2712%27%20text-anchor=%27middle%27%20dy=%27.3em%27%3E🎭%3C/text%3E%3C/svg%3E'">
                            </div>
                            <div style="font-size: 11px; font-weight: bold; text-align: center; margin-bottom: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: #333;">${waifu.name}</div>
                            <div style="font-size: 9px; color: #666; text-align: center;">Ур.${waifu.level} • 💪${power}</div>
                        </div>
                        `;
                    }).join('')}
                </div>
                <button id="close-select-modal" style="margin-top: 16px; width: 100%; padding: 12px; background: #6c757d; color: white; border: none; border-radius: 12px; font-size: 14px; cursor: pointer;">
                    Отмена
                </button>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Close button
        modal.querySelector('#close-select-modal').addEventListener('click', () => {
            modal.remove();
        });
        
        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
    } catch (error) {
        console.error('Error opening select waifu modal:', error);
        if (window.Telegram?.WebApp?.showAlert) {
            window.Telegram.WebApp.showAlert('❌ Ошибка загрузки списка вайфу');
        }
    }
}

// Select waifu from modal and close it
async function selectActiveWaifuFromModal(waifuId) {
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch(`/api/waifu/${waifuId}/set-active?${new URLSearchParams({ initData })}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            // Close modal
            const modal = document.querySelector('div[style*="position: fixed"]');
            if (modal) {
                modal.remove();
            }
            
            // Reload profile immediately
            await loadProfile();
        } else {
            const errorData = await response.json();
            if (window.Telegram?.WebApp?.showAlert) {
                window.Telegram.WebApp.showAlert('❌ Ошибка: ' + (errorData.detail || 'Неизвестная ошибка'));
            }
        }
    } catch (error) {
        console.error('Error selecting waifu:', error);
        if (window.Telegram?.WebApp?.showAlert) {
            window.Telegram.WebApp.showAlert('❌ Ошибка: ' + error.message);
        }
    }
}

// Open sort modal
function openSortModal() {
    const sortOptions = [
        { value: 'name', label: '📝 По имени', icon: '📝' },
        { value: 'rarity', label: '💎 По редкости', icon: '💎' },
        { value: 'level', label: '⬆️ По уровню', icon: '⬆️' },
        { value: 'power', label: '💪 По силе', icon: '💪' },
        { value: 'race', label: '🧬 По расе', icon: '🧬' },
        { value: 'profession', label: '⚒️ По профессии', icon: '⚒️' },
        { value: 'nationality', label: '🌍 По национальности', icon: '🌍' }
    ];
    
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed; top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0,0,0,0.8); display: flex; align-items: center;
        justify-content: center; z-index: 10000; padding: 20px;
    `;
    
    modal.innerHTML = `
        <div style="background: white; border-radius: 20px; max-width: 400px; width: 100%; padding: 24px;">
            <div style="display: flex; flex-direction: column; gap: 8px;">
                ${sortOptions.map(opt => `
                    <button onclick="setSortBy('${opt.value}')" style="
                        background: ${waifuSortBy === opt.value ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : '#f0f0f0'};
                        color: ${waifuSortBy === opt.value ? 'white' : '#333'};
                        border: none; padding: 14px; border-radius: 12px; font-size: 14px;
                        font-weight: ${waifuSortBy === opt.value ? 'bold' : 'normal'};
                        cursor: pointer; text-align: left; transition: all 0.2s;
                    " onmouseover="if('${waifuSortBy}' !== '${opt.value}') this.style.background='#e0e0e0'"
                       onmouseout="if('${waifuSortBy}' !== '${opt.value}') this.style.background='#f0f0f0'">
                        ${opt.label}
                    </button>
                `).join('')}
            </div>
            <button onclick="closeSortModal()" style="
                background: #6c757d; color: white; border: none; padding: 12px;
                border-radius: 12px; font-size: 14px; font-weight: bold; cursor: pointer;
                width: 100%; margin-top: 16px;
            ">
                Закрыть
            </button>
        </div>
    `;
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
    
    document.body.appendChild(modal);
}

// Close sort modal
function closeSortModal() {
    const modal = document.querySelector('div[style*="position: fixed"]');
    if (modal) {
        modal.remove();
    }
}

// Set sort by
async function setSortBy(sortBy) {
    waifuSortBy = sortBy;
    closeSortModal();
    
    // Save preference to backend
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        await fetch('/api/profile/preferences?' + new URLSearchParams({ initData }), {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                waifu_sort_preference: sortBy
            })
        });
    } catch (error) {
        console.error('Error saving sort preference:', error);
    }
    
    // Re-render waifu list with new sort
    const viewContent = document.getElementById('view-content');
    if (viewContent && currentView === 'waifus') {
        renderWaifuList(viewContent);
    }
}

// Toggle favorites filter
function toggleFavorites() {
    showOnlyFavorites = !showOnlyFavorites;
    
    // Re-render waifu list with new filter
    const viewContent = document.getElementById('view-content');
    if (viewContent && currentView === 'waifus') {
        renderWaifuList(viewContent);
    }
}

// Open upgrade modal (placeholder)
function openUpgradeModal() {
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed; top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0,0,0,0.8); display: flex; align-items: center;
        justify-content: center; z-index: 10000; padding: 20px;
    `;
    
    modal.innerHTML = `
        <div style="background: white; border-radius: 20px; max-width: 400px; width: 100%; padding: 24px;">
            <div style="text-align: center; padding: 40px 20px; color: #666;">
                <div style="font-size: 48px; margin-bottom: 16px;">🚧</div>
                <p style="margin: 0; font-size: 16px;">Функция находится в разработке</p>
                <p style="margin: 8px 0 0 0; font-size: 14px; color: #999;">Скоро здесь появится система улучшения вайфу!</p>
            </div>
            <button onclick="closeUpgradeModal()" style="
                background: #6c757d; color: white; border: none; padding: 12px;
                border-radius: 12px; font-size: 14px; font-weight: bold; cursor: pointer;
                width: 100%; margin-top: 16px;
            ">
                Закрыть
            </button>
        </div>
    `;
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
    
    document.body.appendChild(modal);
}

// Close upgrade modal
function closeUpgradeModal() {
    const modal = document.querySelector('div[style*="position: fixed"]');
    if (modal) {
        modal.remove();
    }
}

// Summon waifu(s)
async function summonWaifu(count) {
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        
        const response = await fetch(`/api/summon?${new URLSearchParams({ initData })}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                count: count
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            if (window.Telegram?.WebApp?.showAlert) {
                window.Telegram.WebApp.showAlert('❌ Ошибка: ' + (errorData.detail || 'Неизвестная ошибка'));
            }
            return;
        }
        
        const data = await response.json();
        
        // Show summoned waifus in modal
        showSummonedWaifusModal(data.summoned, data.remaining_coins, null, false);
        
        // Reload waifu list
        const viewContent = document.getElementById('view-content');
        if (viewContent && currentView === 'waifus') {
            await loadWaifuList(viewContent);
        }
        
        // Reload profile to update coins
        if (profileData) {
            profileData.gold = data.remaining_coins;
            const coinsElement = document.querySelector('.currency-item:nth-child(1) .currency-value');
            if (coinsElement) {
                coinsElement.textContent = data.remaining_coins;
            }
        }
        
    } catch (error) {
        console.error('Error summoning waifu:', error);
        if (window.Telegram?.WebApp?.showAlert) {
            window.Telegram.WebApp.showAlert('❌ Ошибка: ' + error.message);
        }
    }
}

// Premium summon waifu(s) with gems
async function summonPremiumWaifu(count) {
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        
        const response = await fetch(`/api/summon-premium?${new URLSearchParams({ initData })}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                count: count
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            if (window.Telegram?.WebApp?.showAlert) {
                window.Telegram.WebApp.showAlert('❌ Ошибка: ' + (errorData.detail || 'Неизвестная ошибка'));
            }
            return;
        }
        
        const data = await response.json();
        
        // Show summoned waifus in modal (with gems info)
        showSummonedWaifusModal(data.summoned, data.remaining_coins, data.remaining_gems, true);
        
        // Reload waifu list
        const viewContent = document.getElementById('view-content');
        if (viewContent && currentView === 'waifus') {
            await loadWaifuList(viewContent);
        }
        
        // Reload profile to update gems
        if (profileData) {
            profileData.gems = data.remaining_gems;
            profileData.gold = data.remaining_coins;
            const gemsElement = document.querySelector('.currency-item:nth-child(2) .currency-value');
            const coinsElement = document.querySelector('.currency-item:nth-child(1) .currency-value');
            if (gemsElement) {
                gemsElement.textContent = data.remaining_gems;
            }
            if (coinsElement) {
                coinsElement.textContent = data.remaining_coins;
            }
        }
        
    } catch (error) {
        console.error('Error summoning premium waifu:', error);
        if (window.Telegram?.WebApp?.showAlert) {
            window.Telegram.WebApp.showAlert('❌ Ошибка: ' + error.message);
        }
    }
}

// Show summoned waifus modal
function showSummonedWaifusModal(waifus, remainingCoins, remainingGems = null, isPremium = false) {
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed; top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0,0,0,0.9); display: flex; align-items: center;
        justify-content: center; z-index: 10000; padding: 20px; overflow-y: auto;
    `;
    
    // Get rarity color helper
    const getRarityColorForSummon = (rarity) => {
        const colors = {
            'Common': '#d0d0d0',
            'Uncommon': '#4CAF50',
            'Rare': '#2196F3',
            'Epic': '#9C27B0',
            'Legendary': '#FF9800'
        };
        return colors[rarity] || '#d0d0d0';
    };
    
    // Rarity priority for sorting (higher = rarer)
    const rarityPriority = {
        'Legendary': 5,
        'Epic': 4,
        'Rare': 3,
        'Uncommon': 2,
        'Common': 1
    };
    
    // Sort by rarity (desc), then by power (desc)
    const sortedWaifus = [...waifus].sort((a, b) => {
        const rarityDiff = rarityPriority[b.rarity] - rarityPriority[a.rarity];
        if (rarityDiff !== 0) return rarityDiff;
        return b.power - a.power;
    });
    
    // Check if summoning 1 or 10
    const isSingle = waifus.length === 1;
    
    let contentHTML = '';
    
    if (isSingle) {
        // Single summon: just show the waifu large
        const waifu = sortedWaifus[0];
        contentHTML = `
            <div style="text-align: center;">
                <img src="${waifu.image_url}" alt="${waifu.name}" 
                    style="width: 100%; max-width: 300px; height: auto; aspect-ratio: 1 / 1; object-fit: cover; border-radius: 16px; border: 4px solid ${getRarityColorForSummon(waifu.rarity)}; box-shadow: 0 0 20px ${getRarityColorForSummon(waifu.rarity)}66; margin-bottom: 16px;"
                    onerror="this.src='data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20width=%27300%27%20height=%27300%27%3E%3Ctext%20x=%2750%25%27%20y=%2750%25%27%20font-size=%2748%27%20text-anchor=%27middle%27%20dy=%27.3em%27%3E🎭%3C/text%3E%3C/svg%3E'">
                <h3 style="margin: 0; font-size: 24px; color: ${getRarityColorForSummon(waifu.rarity)}; font-weight: bold;">
                    ${waifu.name}
                </h3>
            </div>
        `;
    } else {
        // 10 summons: best one large, rest in 3x3 grid
        const bestWaifu = sortedWaifus[0];
        const restWaifus = sortedWaifus.slice(1);
        
        contentHTML = `
            <div style="text-align: center; margin-bottom: 24px; padding-bottom: 24px; border-bottom: 2px solid #eee;">
                <div style="font-size: 20px; margin-bottom: 12px; color: #666; font-weight: bold;">Лучший призыв:</div>
                <img src="${bestWaifu.image_url}" alt="${bestWaifu.name}" 
                    style="width: 100%; max-width: 250px; height: auto; aspect-ratio: 1 / 1; object-fit: cover; border-radius: 16px; border: 4px solid ${getRarityColorForSummon(bestWaifu.rarity)}; box-shadow: 0 0 30px ${getRarityColorForSummon(bestWaifu.rarity)}99; margin-bottom: 12px;"
                    onerror="this.src='data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20width=%27250%27%20height=%27250%27%3E%3Ctext%20x=%2750%25%27%20y=%2750%25%27%20font-size=%2748%27%20text-anchor=%27middle%27%20dy=%27.3em%27%3E🎭%3C/text%3E%3C/svg%3E'">
                <h3 style="margin: 0; font-size: 22px; color: ${getRarityColorForSummon(bestWaifu.rarity)}; font-weight: bold;">
                    ${bestWaifu.name}
                </h3>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
                ${restWaifus.map(waifu => `
                    <div style="text-align: center;">
                        <img src="${waifu.image_url}" alt="${waifu.name}" 
                            style="width: 100%; aspect-ratio: 1 / 1; object-fit: cover; border-radius: 8px; border: 3px solid ${getRarityColorForSummon(waifu.rarity)}; box-shadow: 0 0 10px ${getRarityColorForSummon(waifu.rarity)}66; margin-bottom: 8px;"
                            onerror="this.src='data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20width=%27100%27%20height=%27100%27%3E%3Ctext%20x=%2750%25%27%20y=%2750%25%27%20font-size=%2724%27%20text-anchor=%27middle%27%20dy=%27.3em%27%3E🎭%3C/text%3E%3C/svg%3E'">
                        <div style="font-size: 12px; font-weight: bold; color: ${getRarityColorForSummon(waifu.rarity)}; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                            ${waifu.name}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    modal.innerHTML = `
        <div style="background: white; border-radius: 20px; max-width: 600px; width: 100%; max-height: 90vh; overflow-y: auto; padding: 24px; margin: auto;">
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="font-size: 48px; margin-bottom: 12px;">${isPremium ? '💎' : '✨'}</div>
                <h2 style="margin: 0 0 8px 0; font-size: 24px; color: #333;">${isPremium ? 'Премиум призыв завершен!' : 'Призыв завершен!'}</h2>
                <p style="margin: 0; color: #666; font-size: 14px;">Призвано вайфу: ${waifus.length}</p>
                ${!isPremium ? `<p style="margin: 8px 0 0 0; color: #FF9800; font-size: 16px; font-weight: bold;">Осталось монет: ${remainingCoins} 💰</p>` : ''}
                ${isPremium && remainingGems !== null ? `<p style="margin: 8px 0 0 0; color: #FFD700; font-size: 16px; font-weight: bold;">Осталось гемов: ${remainingGems} 💎</p>` : ''}
            </div>
            
            ${contentHTML}
            
            <button onclick="closeSummonModal()" style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; border: none; padding: 14px; border-radius: 12px; 
                font-size: 16px; font-weight: bold; cursor: pointer; width: 100%; margin-top: 24px;
            ">
                Отлично! 🎉
            </button>
        </div>
    `;
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
    
    document.body.appendChild(modal);
}

// Open upgrade modal
async function openUpgradeModal(targetWaifuId) {
    try {
        console.log('🔧 openUpgradeModal called with:', targetWaifuId, 'Type:', typeof targetWaifuId);
        const initData = window.Telegram?.WebApp?.initData || '';
        
        // Convert to string for comparison
        targetWaifuId = String(targetWaifuId);
        console.log('🔧 Converted to string:', targetWaifuId);
        
        // First, try to get waifu info from current waifus list
        let targetWaifu = null;
        
        // Try to get from all waifus (not just upgradeable)
        const allWaifusResponse = await fetch('/api/waifus?' + new URLSearchParams({ initData }));
        if (allWaifusResponse.ok) {
            const allWaifus = await allWaifusResponse.json();
            console.log('All waifus:', allWaifus.length, 'Looking for:', targetWaifuId);
            console.log('Sample IDs:', allWaifus.slice(0, 3).map(w => ({ id: w.id, type: typeof w.id })));
            targetWaifu = allWaifus.find(w => String(w.id) === String(targetWaifuId));
        }
        
        // If not found in all waifus, try to fetch directly by ID
        if (!targetWaifu) {
            console.log('Waifu not found in all waifus, trying direct fetch...');
            console.log('Target waifu ID:', targetWaifuId, 'Type:', typeof targetWaifuId);
            const directResponse = await fetch(`/api/waifu/${targetWaifuId}`);
            console.log('Direct fetch response status:', directResponse.status);
            if (directResponse.ok) {
                targetWaifu = await directResponse.json();
                console.log('Found waifu via direct fetch:', targetWaifu.name, 'ID:', targetWaifu.id);
            } else {
                const errorText = await directResponse.text();
                console.error('Direct fetch failed:', errorText);
            }
        }
        
        if (!targetWaifu) {
            console.error('Target waifu not found with ID:', targetWaifuId, 'Type:', typeof targetWaifuId);
            throw new Error('Вайфу не найдена');
        }
        
        // Calculate power for display
        if (!targetWaifu.power) {
            targetWaifu.power = calculatePower(targetWaifu);
        }
        
        // Check if waifu can be upgraded
        const maxLevels = {
            'Common': 30,
            'Uncommon': 35,
            'Rare': 40,
            'Epic': 45,
            'Legendary': 50
        };
        
        const maxLevel = maxLevels[targetWaifu.rarity] || 30;
        if (targetWaifu.level >= maxLevel) {
            if (window.Telegram?.WebApp?.showAlert) {
                window.Telegram.WebApp.showAlert(`Эта вайфу уже достигла максимального уровня (${maxLevel})`);
            }
            return;
        }
        
        // Get sacrifice candidates
        const candidatesResponse = await fetch(`/api/upgrade/sacrifice-candidates?target_waifu_id=${targetWaifuId}&${new URLSearchParams({ initData })}`);
        if (!candidatesResponse.ok) {
            const errorData = await candidatesResponse.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Failed to fetch sacrifice candidates');
        }
        
        const candidatesData = await candidatesResponse.json();
        const candidates = candidatesData.candidates || [];
        
        if (candidates.length === 0) {
            if (window.Telegram?.WebApp?.showAlert) {
                window.Telegram.WebApp.showAlert('Нет вайфу для жертвования');
            }
            return;
        }
        
        // Sort candidates by XP value (descending)
        candidates.sort((a, b) => b.xp_value - a.xp_value);
        
        // Create modal
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.9); display: flex; align-items: center;
            justify-content: center; z-index: 10000; padding: 20px; overflow-y: auto;
        `;
        
        const rarityColor = getRarityColor(targetWaifu.rarity);
        
        modal.innerHTML = `
            <div style="background: white; border-radius: 20px; max-width: 600px; width: 100%; max-height: 90vh; overflow-y: auto; padding: 24px; position: relative;">
                <!-- Close Button -->
                <button onclick="event.stopPropagation(); closeUpgradeModal()" style="
                    position: absolute; top: 16px; right: 16px; width: 32px; height: 32px;
                    background: #dc3545; color: white; border: none; border-radius: 50%;
                    font-size: 16px; font-weight: bold; cursor: pointer; display: flex;
                    align-items: center; justify-content: center; z-index: 10;
                ">×</button>
                
                <!-- Target Waifu Info -->
                <div style="text-align: center; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 2px solid #eee;">
                    <img src="${targetWaifu.image_url}" alt="${targetWaifu.name}" 
                        style="width: 120px; height: 120px; object-fit: cover; border-radius: 20px; border: 4px solid ${rarityColor}; box-shadow: 0 0 20px ${rarityColor}66, inset 0 0 0 2px ${rarityColor}; margin-bottom: 12px;"
                        onerror="this.src='data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20width=%27120%27%20height=%27120%27%3E%3Ctext%20x=%2750%25%27%20y=%2750%25%27%20font-size=%2736%27%20text-anchor=%27middle%27%20dy=%27.3em%27%3E🎭%3C/text%3E%3C/svg%3E'">
                    <h3 style="margin: 0; font-size: 18px; color: #333; font-weight: bold;">${targetWaifu.name}</h3>
                    <div style="font-size: 14px; color: #666; margin-top: 4px;">Уровень ${targetWaifu.level}/${maxLevel} • 💪${targetWaifu.power}</div>
                </div>
                
                <!-- Selection Summary -->
                <div id="selection-summary" style="background: #f8f9fa; border-radius: 12px; padding: 12px; margin-bottom: 20px; text-align: center;">
                    <div id="selected-info" style="font-size: 14px; color: #666; margin-bottom: 8px;">Выберите вайфу для получения опыта</div>
                    <button id="confirm-upgrade" onclick="confirmUpgrade('${targetWaifuId}')" style="
                        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); 
                        color: white; border: none; padding: 10px 20px; border-radius: 8px; 
                        font-size: 14px; font-weight: bold; cursor: pointer;
                        opacity: 0.5; pointer-events: none;
                    " disabled>
                        ⚡ Улучшить
                    </button>
                </div>
                
                <!-- Candidates Grid -->
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; max-height: 300px; overflow-y: auto;">
                    ${candidates.map(waifu => {
                        const candidateRarityColor = getRarityColor(waifu.rarity);
                        return `
                        <div class="candidate-card" data-waifu-id="${waifu.id}" data-xp-value="${waifu.xp_value}" style="
                            background: white; border: 3px solid ${candidateRarityColor}; border-radius: 12px; 
                            padding: 8px; cursor: pointer; transition: all 0.2s; text-align: center;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.1), 0 0 0 1px ${candidateRarityColor}33;
                        " onclick="toggleCandidate(this)">
                            <img src="${waifu.image_url}" alt="${waifu.name}" 
                                style="width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: 8px; margin-bottom: 6px; border: 2px solid ${candidateRarityColor}; box-shadow: inset 0 0 0 1px ${candidateRarityColor}66;"
                                onerror="this.src='data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20width=%27100%27%20height=%27100%27%3E%3Ctext%20x=%2750%25%27%20y=%2750%25%27%20font-size=%2712%27%20text-anchor=%27middle%27%20dy=%27.3em%27%3E🎭%3C/text%3E%3C/svg%3E'">
                            <div style="font-size: 11px; font-weight: bold; color: #333; margin-bottom: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${waifu.name}</div>
                            <div style="font-size: 10px; color: #666; margin-bottom: 2px;">Ур.${waifu.level}</div>
                            <div style="font-size: 10px; color: #28a745; font-weight: bold;">+${waifu.xp_value} XP</div>
                        </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
    } catch (error) {
        console.error('Error opening upgrade modal:', error);
        if (window.Telegram?.WebApp?.showAlert) {
            const errorMessage = typeof error === 'string' ? error : 
                                error?.message || 
                                JSON.stringify(error) || 
                                'Неизвестная ошибка';
            window.Telegram.WebApp.showAlert('❌ Ошибка: ' + errorMessage);
        }
    }
}

// Toggle candidate selection
function toggleCandidate(element) {
    const isSelected = element.classList.contains('selected');
    
    if (isSelected) {
        element.classList.remove('selected');
        element.style.background = 'white';
        element.style.transform = 'scale(1)';
    } else {
        element.classList.add('selected');
        element.style.background = 'linear-gradient(135deg, #FFD70022, #FFA50022)';
        element.style.transform = 'scale(1.05)';
    }
    
    updateSelectionSummary();
}

// Update selection summary
function updateSelectionSummary() {
    const selectedCards = document.querySelectorAll('.candidate-card.selected');
    const totalXP = Array.from(selectedCards).reduce((sum, card) => sum + parseInt(card.dataset.xpValue), 0);
    const count = selectedCards.length;
    
    const summaryDiv = document.getElementById('selected-info');
    const confirmBtn = document.getElementById('confirm-upgrade');
    
    if (count === 0) {
        summaryDiv.textContent = 'Выберите вайфу для получения опыта';
        confirmBtn.style.opacity = '0.5';
        confirmBtn.style.pointerEvents = 'none';
        confirmBtn.disabled = true;
    } else {
        summaryDiv.innerHTML = `Выбрано: ${count} вайфу • <strong>+${totalXP} XP</strong>`;
        confirmBtn.style.opacity = '1';
        confirmBtn.style.pointerEvents = 'auto';
        confirmBtn.disabled = false;
    }
}

// Confirm upgrade
async function confirmUpgrade(targetWaifuId) {
    try {
        const selectedCards = document.querySelectorAll('.candidate-card.selected');
        const sacrificeIds = Array.from(selectedCards).map(card => card.dataset.waifuId);
        
        if (sacrificeIds.length === 0) {
            if (window.Telegram?.WebApp?.showAlert) {
                window.Telegram.WebApp.showAlert('Выберите вайфу для жертвования');
            }
            return;
        }
        
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch('/api/upgrade/perform?' + new URLSearchParams({ initData }), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                target_waifu_id: targetWaifuId,
                sacrifice_waifu_ids: sacrificeIds
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to perform upgrade');
        }
        
        const result = await response.json();
        
        // Replace upgrade modal with results modal
        showUpgradeResultsModal(result, targetWaifuId);
        
        // Reload upgrade page
        const viewContent = document.getElementById('view-content');
        if (viewContent && currentView === 'upgrade') {
            await loadUpgradePage(viewContent);
        }
        
        // Reload waifus list if on waifus page
        if (currentView === 'waifus') {
            await loadWaifuList(viewContent);
        }
        
        // Reload profile to update active waifu if needed
        if (profileData) {
            await loadProfile();
        }
        
    } catch (error) {
        console.error('Error confirming upgrade:', error);
        if (window.Telegram?.WebApp?.showAlert) {
            window.Telegram.WebApp.showAlert('❌ Ошибка: ' + error.message);
        }
    }
}

// Close upgrade modal
function closeUpgradeModal() {
    const modals = document.querySelectorAll('div[style*="position: fixed"]');
    modals.forEach(modal => {
        if (modal.style.zIndex === '10000') {
            modal.remove();
        }
    });
}

// Show upgrade results modal
function showUpgradeResultsModal(result, targetWaifuId) {
    // Close current modal
    closeUpgradeModal();
    
    // Create results modal
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed; top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0,0,0,0.9); display: flex; align-items: center;
        justify-content: center; z-index: 10000; padding: 20px;
    `;
    
    const levelGained = result.new_level - result.old_level;
    const levelText = levelGained > 0 ? `+${levelGained}` : '0';
    
    // Stat names in Russian
    const statNamesRu = {
        'power': '💪 Сила',
        'charm': '✨ Обаяние',
        'luck': '🍀 Удача',
        'affection': '❤️ Привязанность',
        'intellect': '🧠 Интеллект',
        'speed': '⚡ Скорость'
    };
    
    // Build stat increases HTML
    let statIncreasesHTML = '';
    if (result.stat_increases && Object.keys(result.stat_increases).length > 0) {
        const statLines = [];
        for (const [statName, increaseAmount] of Object.entries(result.stat_increases)) {
            const statNameRu = statNamesRu[statName] || statName;
            const oldValue = result.old_stats[statName] || 0;
            const newValue = (result.old_stats[statName] || 0) + increaseAmount;
            statLines.push(`
                <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                    <span style="color: #666;">${statNameRu}:</span>
                    <span style="font-weight: bold; color: #28a745;">${oldValue} → ${newValue} (+${increaseAmount})</span>
                </div>
            `);
        }
        statIncreasesHTML = `
            <div style="border-top: 1px solid #dee2e6; padding-top: 12px; margin-top: 12px;">
                <div style="font-weight: bold; color: #333; margin-bottom: 8px; font-size: 14px;">📊 Улучшенные характеристики:</div>
                ${statLines.join('')}
            </div>
        `;
    }
    
    modal.innerHTML = `
        <div style="background: white; border-radius: 20px; max-width: 400px; width: 100%; padding: 24px; text-align: center;">
            <div style="font-size: 48px; margin-bottom: 16px;">⚡</div>
            <h3 style="margin: 0 0 16px 0; color: #333; font-size: 20px;">Улучшение завершено!</h3>
            
            <div style="background: #f8f9fa; border-radius: 12px; padding: 16px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="color: #666;">📈 Уровень:</span>
                    <span style="font-weight: bold; color: #28a745;">${result.old_level} → ${result.new_level}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="color: #666;">💫 Получено XP:</span>
                    <span style="font-weight: bold; color: #17a2b8;">+${result.xp_added}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: ${result.stat_increases && Object.keys(result.stat_increases).length > 0 ? '0' : '0'};">
                    <span style="color: #666;">🔥 Пожертвовано:</span>
                    <span style="font-weight: bold; color: #dc3545;">${result.sacrificed_count} вайфу</span>
                </div>
                ${statIncreasesHTML}
            </div>
            
            <button onclick="event.stopPropagation(); closeUpgradeModal()" style="
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
                color: white; border: none; padding: 14px; border-radius: 12px; 
                font-size: 16px; font-weight: bold; cursor: pointer; width: 100%;
            ">
                ✅ Готово
            </button>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Close on background click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// Close summon modal
function closeSummonModal() {
    const modal = document.querySelector('div[style*="position: fixed"]');
    if (modal) {
        modal.remove();
    }
}

// Toggle waifu favorite status (from detail modal)
async function toggleWaifuFavorite(waifuId) {
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch(`/api/waifu/${waifuId}/toggle-favorite?${new URLSearchParams({ initData })}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Update button appearance
            const btn = document.getElementById('favorite-toggle-btn');
            if (btn) {
                if (data.is_favorite) {
                    btn.style.background = '#f5576c';
                    btn.innerHTML = '❤️';
                } else {
                    btn.style.background = 'rgba(255,255,255,0.3)';
                    btn.innerHTML = '🤍';
                }
            }
            
            // Update waifuList for re-rendering
            const waifuIndex = waifuList.findIndex(w => w.id === waifuId);
            if (waifuIndex !== -1) {
                waifuList[waifuIndex].is_favorite = data.is_favorite;
            }
            
        } else {
            const errorData = await response.json();
            if (window.Telegram?.WebApp?.showAlert) {
                window.Telegram.WebApp.showAlert('❌ Ошибка: ' + (errorData.detail || 'Неизвестная ошибка'));
            }
        }
    } catch (error) {
        console.error('Error toggling favorite:', error);
        if (window.Telegram?.WebApp?.showAlert) {
            window.Telegram.WebApp.showAlert('❌ Ошибка: ' + error.message);
        }
    }
}

// Open waifu detail modal for viewing stats (from "My Waifus" list)
async function openWaifuDetail(waifuId) {
    console.log('🔗 Opening waifu detail modal for:', waifuId);
    
    try {
        // Fetch waifu data
        const response = await fetch(`/api/waifu/${waifuId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch waifu');
        }
        
        const waifu = await response.json();
        
        // Calculate XP progress using waifu XP formula
        // Formula: total XP for level N = 50 * N * (N - 1), XP for next level = level * 100
        const getTotalXPForLevel = (level) => {
            if (level <= 1) return 0;
            return 50 * level * (level - 1);
        };
        const xpForCurrentLevel = getTotalXPForLevel(waifu.level);
        const xpForNextLevel = waifu.level * 100; // XP needed to go from current level to next
        const xpInCurrentLevel = Math.max(0, waifu.xp - xpForCurrentLevel);
        const xpPercent = Math.min(100, Math.max(0, (xpInCurrentLevel / xpForNextLevel) * 100));
        
        // Get flag emoji
        const flagEmoji = getFlagEmoji(waifu.nationality);
        
        // Calculate total power using the same formula as backend
        const power = calculatePower(waifu);
        
        // Get rarity colors for modal background
        const rarityColors = getRarityColor(waifu.rarity);
        
        // Create modal
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            padding: 20px;
            overflow-y: auto;
        `;
        
        modal.innerHTML = `
            <div style="background: linear-gradient(135deg, ${rarityColors.border} 0%, ${rarityColors.border}88 100%); border-radius: 20px; max-width: 500px; width: 100%; max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px ${rarityColors.glow};">
                <!-- Header -->
                <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 20px 20px 0 0; backdrop-filter: blur(10px);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <h2 style="color: white; margin: 0; font-size: 24px; flex: 1;">${waifu.name}</h2>
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <button onclick="openUpgradeModal('${waifuId}')" style="
                                background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
                                border: none; color: white; padding: 6px 10px; border-radius: 8px;
                                font-size: 16px; font-weight: bold; cursor: pointer;
                                transition: all 0.2s; display: flex; align-items: center; justify-content: center;
                                width: 32px; height: 32px; min-width: 32px;
                            " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)" title="Улучшить">
                                ↑
                            </button>
                            <button id="favorite-toggle-btn" onclick="toggleWaifuFavorite('${waifuId}')" style="
                                background: ${waifu.is_favorite ? '#f5576c' : 'rgba(255,255,255,0.3)'};
                                border: none; color: white; width: 36px; height: 36px;
                                border-radius: 50%; font-size: 18px; cursor: pointer;
                                display: flex; align-items: center; justify-content: center;
                                transition: all 0.2s; padding: 0;
                            " onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'">
                                ${waifu.is_favorite ? '❤️' : '🤍'}
                            </button>
                            <span style="background: rgba(255,255,255,0.2); color: white; padding: 6px 12px; border-radius: 12px; font-size: 14px;">Ур.${waifu.level}</span>
                        </div>
                    </div>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                        <span style="background: rgba(255,255,255,0.2); color: white; padding: 4px 10px; border-radius: 8px; font-size: 12px;">${waifu.race}</span>
                        <span style="background: rgba(255,255,255,0.2); color: white; padding: 4px 10px; border-radius: 8px; font-size: 12px;">${flagEmoji} ${waifu.nationality}</span>
                        <span style="background: rgba(255,255,255,0.2); color: white; padding: 4px 10px; border-radius: 8px; font-size: 12px;">${waifu.profession}</span>
                        <span style="background: rgba(255,255,255,0.2); color: white; padding: 4px 10px; border-radius: 8px; font-size: 12px;">💪 ${power}</span>
                    </div>
                </div>
                
                <!-- Image -->
                <div style="padding: 20px;">
                    <img src="${waifu.image_url}" alt="${waifu.name}" style="width: 100%; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.3);" onerror="this.src='data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20width=%27300%27%20height=%27300%27%3E%3Ctext%20x=%2750%25%27%20y=%2750%25%27%20font-size=%2750%27%20text-anchor=%27middle%27%20dy=%27.3em%27%3E🎭%3C/text%3E%3C/svg%3E'">
                </div>
                
                <!-- Stats -->
                <div style="padding: 0 20px 20px;">
                    <div style="background: rgba(255,255,255,0.1); border-radius: 16px; padding: 16px; backdrop-filter: blur(10px);">
                        <!-- Main Stats -->
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 16px;">
                            <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 12px;">
                                <div style="color: rgba(255,255,255,0.9); font-size: 14px; white-space: nowrap;">💪 СИЛ • <span style="font-weight: bold; font-size: 16px;">${waifu.stats.power || 0}</span></div>
                            </div>
                            <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 12px;">
                                <div style="color: rgba(255,255,255,0.9); font-size: 14px; white-space: nowrap;">🍀 УДЧ • <span style="font-weight: bold; font-size: 16px;">${waifu.stats.luck || 0}</span></div>
                            </div>
                            <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 12px;">
                                <div style="color: rgba(255,255,255,0.9); font-size: 14px; white-space: nowrap;">🧠 ИНТ • <span style="font-weight: bold; font-size: 16px;">${waifu.stats.intellect || 0}</span></div>
                            </div>
                            <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 12px;">
                                <div style="color: rgba(255,255,255,0.9); font-size: 14px; white-space: nowrap;">✨ ОБА • <span style="font-weight: bold; font-size: 16px;">${waifu.stats.charm || 0}</span></div>
                            </div>
                            <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 12px;">
                                <div style="color: rgba(255,255,255,0.9); font-size: 14px; white-space: nowrap;">🎯 ЛОВ • <span style="font-weight: bold; font-size: 16px;">${waifu.dynamic.bond || 0}</span></div>
                            </div>
                            <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 12px;">
                                <div style="color: rgba(255,255,255,0.9); font-size: 14px; white-space: nowrap;">⚡ СКО • <span style="font-weight: bold; font-size: 16px;">${waifu.stats.speed || 0}</span></div>
                            </div>
                        </div>
                        
                        <!-- Dynamic Stats -->
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 16px;">
                            <div style="background: rgba(255,255,255,0.05); padding: 10px 8px; border-radius: 8px; text-align: center;">
                                <div style="color: rgba(255,255,255,0.9); font-size: 12px;">😊 Настроение • <span style="font-weight: bold;">${waifu.dynamic.mood || 0}</span></div>
                            </div>
                            <div style="background: rgba(255,255,255,0.05); padding: 10px 8px; border-radius: 8px; text-align: center;">
                                <div style="color: rgba(255,255,255,0.9); font-size: 12px;">❤️ Лояльность • <span style="font-weight: bold;">${waifu.dynamic.loyalty || 0}</span></div>
                            </div>
                            <div style="background: rgba(255,255,255,0.05); padding: 10px 8px; border-radius: 8px; text-align: center;">
                                <div style="color: rgba(255,255,255,0.9); font-size: 12px;">⚡ Энергия • <span style="font-weight: bold;">${waifu.dynamic.energy || 0}</span></div>
                            </div>
                        </div>
                        
                        <!-- XP Bar -->
                        <div style="margin-bottom: 16px;">
                            <div style="display: flex; justify-content: space-between; color: rgba(255,255,255,0.7); font-size: 12px; margin-bottom: 6px;">
                                <span>✨ Опыт</span>
                                <span>${xpInCurrentLevel} / ${xpForNextLevel} (${Math.round(xpPercent)}%)</span>
                            </div>
                            <div style="background: rgba(255,255,255,0.2); height: 8px; border-radius: 4px; overflow: hidden;">
                                <div style="background: linear-gradient(90deg, #4CAF50, #8BC34A); height: 100%; width: ${xpPercent}%; transition: width 0.3s;"></div>
                            </div>
                        </div>
                    </div>
                    
                    <button id="modal-close-btn" style="background: rgba(255,255,255,0.2); color: white; border: none; padding: 14px; border-radius: 12px; font-size: 14px; font-weight: bold; cursor: pointer; margin-top: 16px; width: 100%; transition: all 0.2s;">
                        ← Назад
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Add event listeners
        const closeBtn = modal.querySelector('#modal-close-btn');
        
        // Close modal
        closeBtn.addEventListener('click', () => {
            modal.remove();
        });
        
        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
    } catch (error) {
        console.error('Error opening waifu detail:', error);
        if (window.Telegram?.WebApp?.showAlert) {
            window.Telegram.WebApp.showAlert('❌ Ошибка загрузки данных вайфу');
        }
    }
}

// Helper function to get flag emoji
function getFlagEmoji(countryCode) {
    const flagMap = {
        'RU': '🇷🇺', 'US': '🇺🇸', 'JP': '🇯🇵', 'CN': '🇨🇳',
        'FR': '🇫🇷', 'DE': '🇩🇪', 'GB': '🇬🇧', 'IT': '🇮🇹',
        'ES': '🇪🇸', 'KR': '🇰🇷', 'BR': '🇧🇷', 'IN': '🇮🇳',
        'CA': '🇨🇦', 'Russian': '🇷🇺', 'American': '🇺🇸', 'Japanese': '🇯🇵',
        'Chinese': '🇨🇳', 'French': '🇫🇷', 'German': '🇩🇪', 'British': '🇬🇧',
        'Italian': '🇮🇹', 'Korean': '🇰🇷', 'Brazilian': '🇧🇷', 'Indian': '🇮🇳',
        'Canadian': '🇨🇦'
    };
    return flagMap[countryCode] || '🌎';
}

// Helper function to get profession emoji
function getProfessionEmoji(profession) {
    const professionMap = {
        'Warrior': '⚔️',
        'Mage': '🔮',
        'Assassin': '🗡️',
        'Knight': '🛡️',
        'Archer': '🏹',
        'Healer': '💚',
        'Merchant': '💰'
    };
    return professionMap[profession] || '👤';
}

// Open avatar selection (now opens file upload)
function openAvatarSelection() {
    // Create hidden file input
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'image/*';
    fileInput.style.display = 'none';
    fileInput.onchange = handleAvatarUpload;
    
    document.body.appendChild(fileInput);
    fileInput.click();
    document.body.removeChild(fileInput);
}

// Handle avatar upload
function handleAvatarUpload(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    
    // Check file type
    if (!file.type.startsWith('image/')) {
        window.Telegram?.WebApp?.showAlert?.('Пожалуйста, выберите изображение');
        return;
    }
    
    // Check file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
        window.Telegram?.WebApp?.showAlert?.('Файл слишком большой (макс. 5МБ)');
        return;
    }
    
    // Read file as base64
    const reader = new FileReader();
    reader.onload = async (e) => {
        const imageData = e.target.result;
        
        try {
            const initData = window.Telegram?.WebApp?.initData || '';
            const response = await fetch('/api/profile/upload-avatar?' + new URLSearchParams({ initData }), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image: imageData
                })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Ошибка загрузки');
            }
            
            const result = await response.json();
            
            window.Telegram?.WebApp?.showAlert?.('✅ Аватар загружен');
            
            // Reload profile to show new avatar
            await loadProfile();
            
        } catch (error) {
            console.error('Error uploading avatar:', error);
            window.Telegram?.WebApp?.showAlert?.('❌ ' + error.message);
        }
    };
    
    reader.onerror = () => {
        window.Telegram?.WebApp?.showAlert?.('Ошибка чтения файла');
    };
    
    reader.readAsDataURL(file);
}

// Select waifu to make active
async function selectWaifu(waifuId) {
    console.log(`🎯 selectWaifu called for ${waifuId}, currentView: ${currentView}`);
    
    try {
        // Check if we're in the correct view (select-waifu)
        if (currentView !== 'select-waifu') {
            console.log('❌ Not in select-waifu view, ignoring click');
            return;
        }
        
        console.log('✅ In select-waifu view, proceeding with selection');
        
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch(`/api/waifu/${waifuId}/set-active?${new URLSearchParams({ initData })}`, {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error('Failed to set active waifu');
        }

        if (window.Telegram?.WebApp?.showAlert) {
            window.Telegram.WebApp.showAlert('✅ Вайфу установлена как активная!');
        }

        // Return to profile and reload it
        navigateTo('profile');
        
        // Reload profile to update active waifu
        await loadProfile();

    } catch (error) {
        console.error('Error setting active waifu:', error);
        if (window.Telegram?.WebApp?.showAlert) {
            window.Telegram.WebApp.showAlert('❌ Ошибка при установке активной вайфу');
        }
    }
}

// Load shop items
async function loadShopItems(container) {
    container.innerHTML = `
        <div style="text-align: center; padding: 60px 20px; color: #666;">
            <div style="font-size: 64px; margin-bottom: 16px;">🚧</div>
            <p style="margin: 0 0 8px 0; font-size: 18px; font-weight: bold;">Магазин временно не работает</p>
            <p style="margin: 0; font-size: 14px; color: #999;">Но скоро будет открыт!</p>
        </div>
    `;
}

// Purchase item
async function purchaseItem(itemId) {
    if (!window.Telegram?.WebApp?.showConfirm) {
        alert('Покупка пока не доступна');
        return;
    }
    
    try {
        const confirmed = await window.Telegram.WebApp.showConfirm('Подтвердите покупку');
        if (!confirmed) return;
        
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch('/api/shop/purchase?' + new URLSearchParams({ item_id: itemId, initData }), {
            method: 'POST'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to purchase item');
        }
        
        const result = await response.json();
        
        if (window.Telegram?.WebApp?.showAlert) {
            window.Telegram.WebApp.showAlert(result.message);
        }
        
        // Reload profile to update currency
        await loadProfile();
        
        // Reload shop to update prices if needed
        const viewContent = document.getElementById('view-content');
        if (currentView === 'shop') {
            loadShopItems(viewContent);
        }
        
    } catch (error) {
        console.error('Error purchasing item:', error);
        if (window.Telegram?.WebApp?.showAlert) {
            window.Telegram.WebApp.showAlert(`❌ Ошибка: ${error.message}`);
        }
    }
}

// Load quests
async function loadQuests(container) {
    container.innerHTML = '<p class="loading">Загрузка...</p>';
    
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch('/api/quests?' + new URLSearchParams({ initData }));
        
        if (!response.ok) {
            throw new Error('Failed to fetch quests');
        }
        
        const data = await response.json();
        const quests = data.quests || [];
        
        if (quests.length === 0) {
            container.innerHTML = '<p style="padding: 20px; color: #666;">Нет активных заданий</p>';
            return;
        }
        
        // Render quests
        container.innerHTML = `
            <div style="margin-top: 16px;">
                ${quests.map(quest => {
                    if (quest.claimed) {
                        return `
                            <div style="background: white; border-radius: 12px; padding: 16px; margin-bottom: 12px; border: 2px solid #4CAF50;">
                                <div style="display: flex; align-items: center; gap: 12px;">
                                    <div style="font-size: 32px;">${quest.icon}</div>
                                    <div style="flex: 1;">
                                        <div style="font-weight: bold; font-size: 16px; margin-bottom: 4px;">${quest.name}</div>
                                        <div style="font-size: 14px; color: #4CAF50; font-weight: bold;">✅ Задание выполнено, будет обновлено завтра</div>
                                    </div>
                                </div>
                            </div>
                        `;
                    } else if (quest.completed) {
                        return `
                            <div style="background: white; border-radius: 12px; padding: 16px; margin-bottom: 12px; border: 2px solid #4CAF50;">
                                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                                    <div style="font-size: 32px;">${quest.icon}</div>
                                    <div style="flex: 1;">
                                        <div style="font-weight: bold; font-size: 16px; margin-bottom: 4px;">${quest.name}</div>
                                        <div style="font-size: 12px; color: #666;">${quest.description}</div>
                                    </div>
                                </div>
                                <div style="background: #e0e0e0; border-radius: 8px; height: 8px; margin-bottom: 12px; overflow: hidden;">
                                    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); height: 100%; width: 100%; transition: width 0.3s;"></div>
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; font-size: 12px; color: #666;">
                                    <span>Прогресс: ${quest.progress}/${quest.target}</span>
                                    <span>🎁 ${quest.reward_gold} 💰 + ${quest.reward_xp} ⭐</span>
                                </div>
                                <button onclick="claimQuestReward('${quest.id}')" style="
                                    width: 100%; background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                                    color: white; border: none; padding: 12px; border-radius: 8px;
                                    font-size: 14px; font-weight: bold; cursor: pointer;
                                ">✅ Получить награду</button>
                            </div>
                        `;
                    } else {
                        return `
                            <div style="background: white; border-radius: 12px; padding: 16px; margin-bottom: 12px;">
                                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                                    <div style="font-size: 32px;">${quest.icon}</div>
                                    <div style="flex: 1;">
                                        <div style="font-weight: bold; font-size: 16px; margin-bottom: 4px;">${quest.name}</div>
                                        <div style="font-size: 12px; color: #666;">${quest.description}</div>
                                    </div>
                                </div>
                                <div style="background: #e0e0e0; border-radius: 8px; height: 8px; margin-bottom: 8px; overflow: hidden;">
                                    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); height: 100%; width: ${Math.min(100, (quest.progress / quest.target) * 100)}%; transition: width 0.3s;"></div>
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #666;">
                                    <span>Прогресс: ${quest.progress}/${quest.target}</span>
                                    <span>🎁 ${quest.reward_gold} 💰 + ${quest.reward_xp} ⭐</span>
                                </div>
                            </div>
                        `;
                    }
                }).join('')}
            </div>
        `;
        
    } catch (error) {
        console.error('Error loading quests:', error);
        container.innerHTML = '<p style="color: red; padding: 20px;">Ошибка загрузки</p>';
    }
}

// Claim quest reward
async function claimQuestReward(questId) {
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch(`/api/quests/claim?quest_id=${questId}&${new URLSearchParams({ initData })}`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            if (window.Telegram?.WebApp?.showAlert) {
                window.Telegram.WebApp.showAlert('❌ Ошибка: ' + (errorData.detail || 'Не удалось получить награду'));
            }
            return;
        }
        
        const result = await response.json();
        
        // Show success message
        if (window.Telegram?.WebApp?.showAlert) {
            window.Telegram.WebApp.showAlert('✅ ' + result.message);
        }
        
        // Reload quests
        const viewContent = document.getElementById('view-content');
        if (viewContent && currentView === 'quests') {
            await loadQuests(viewContent);
        }
        
        // Reload profile to update currency
        await loadProfile();
        
    } catch (error) {
        console.error('Error claiming quest reward:', error);
        if (window.Telegram?.WebApp?.showAlert) {
            window.Telegram.WebApp.showAlert('❌ Ошибка: Не удалось получить награду');
        }
    }
}

// Load clan info
async function loadClanInfo(container) {
    container.innerHTML = `
        <div style="padding: 20px; text-align: center;">
            <div style="background: white; border-radius: 12px; padding: 40px; margin-bottom: 20px;">
                <div style="font-size: 64px; margin-bottom: 16px;">🏰</div>
                <div style="font-weight: bold; font-size: 20px; margin-bottom: 8px;">Система кланов</div>
                <div style="color: #666; font-size: 14px;">Функция в разработке</div>
                <div style="color: #999; font-size: 12px; margin-top: 12px;">
                    Скоро вы сможете:<br>
                    • Создавать и вступать в кланы<br>
                    • Участвовать в клановых битвах<br>
                    • Получать бонусы от клана
                </div>
            </div>
        </div>
    `;
}

// Load upgrade page
async function loadUpgradePage(container) {
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch('/api/upgrade/waifus?' + new URLSearchParams({ initData }));
        
        if (!response.ok) {
            throw new Error('Failed to fetch upgradeable waifus');
        }
        
        const data = await response.json();
        const waifus = data.waifus || [];
        
        if (waifus.length === 0) {
            container.innerHTML = `
                <div style="padding: 20px; text-align: center;">
                    <div style="font-size: 48px; margin-bottom: 16px;">⚡</div>
                    <h3 style="margin: 0 0 8px 0; color: #333;">Нет вайфу для прокачки</h3>
                    <p style="margin: 0; color: #666;">Все вайфу достигли максимального уровня</p>
                </div>
            `;
            return;
        }
        
        // Sort by power (descending)
        waifus.sort((a, b) => b.power - a.power);
        
        container.innerHTML = `
            <div style="padding: 16px;">
                <div style="background: white; border-radius: 12px; padding: 16px; margin-bottom: 16px;">
                    <h3 style="margin: 0 0 8px 0; color: #333; font-size: 18px;">⚡ Прокачка вайфу</h3>
                    <p style="margin: 0; color: #666; font-size: 14px;">Выберите вайфу для улучшения. Жертвуйте других вайфу для получения опыта.</p>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;">
                    ${waifus.map(waifu => {
                        const rarityColor = getRarityColor(waifu.rarity);
                        const xpProgress = calculateXPProgress(waifu.xp, waifu.level);
                        
                        return `
                        <div style="
                            background: white; border-radius: 12px; padding: 12px; 
                            border: 2px solid ${rarityColor}; box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                            cursor: pointer; transition: transform 0.2s;
                        " onclick="console.log('🔧 Upgrade clicked for waifu:', '${waifu.id}', 'Type:', typeof '${waifu.id}'); openUpgradeModal('${waifu.id}')" onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">
                            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                                <img src="${waifu.image_url}" alt="${waifu.name}" 
                                    style="width: 40px; height: 40px; object-fit: cover; border-radius: 8px; border: 2px solid ${rarityColor};"
                                    onerror="this.src='data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20width=%2740%27%20height=%2740%27%3E%3Ctext%20x=%2750%25%27%20y=%2750%25%27%20font-size=%2712%27%20text-anchor=%27middle%27%20dy=%27.3em%27%3E🎭%3C/text%3E%3C/svg%3E'">
                                <div style="flex: 1; min-width: 0;">
                                    <div style="font-weight: bold; font-size: 14px; margin-bottom: 2px; color: ${rarityColor}; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${waifu.name}</div>
                                    <div style="font-size: 12px; color: #666;">Ур.${waifu.level}/${waifu.max_level} • 💪${waifu.power}</div>
                                </div>
                            </div>
                            
                            <!-- XP Progress Bar -->
                            <div style="margin-bottom: 8px;">
                                <div style="display: flex; justify-content: space-between; font-size: 10px; color: #666; margin-bottom: 4px;">
                                    <span>XP: ${waifu.xp}</span>
                                    <span>${xpProgress.current}/${xpProgress.next}</span>
                                </div>
                                <div style="background: #e0e0e0; border-radius: 4px; height: 6px; overflow: hidden;">
                                    <div style="background: linear-gradient(90deg, ${rarityColor}, ${rarityColor}88); height: 100%; width: ${xpProgress.percent}%; transition: width 0.3s;"></div>
                                </div>
                            </div>
                            
                            <div style="text-align: center;">
                                <button style="
                                    background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); 
                                    color: white; border: none; padding: 6px 12px; border-radius: 8px; 
                                    font-size: 12px; font-weight: bold; cursor: pointer; width: 100%;
                                ">
                                    ⚡ Улучшить
                                </button>
                            </div>
                        </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
        
    } catch (error) {
        console.error('Error loading upgrade page:', error);
        container.innerHTML = '<p style="color: red; padding: 20px;">Ошибка загрузки страницы прокачки</p>';
    }
}

// Calculate XP progress for display (waifu XP formula)
function calculateXPProgress(currentXP, currentLevel) {
    // Waifu XP formula: total XP for level N = 50 * N * (N - 1)
    // XP needed for next level = currentLevel * 100
    
    const getTotalXPForLevel = (level) => {
        if (level <= 1) return 0;
        return 50 * level * (level - 1);
    };
    
    // Calculate total XP needed for current level
    const xpNeededForCurrent = getTotalXPForLevel(currentLevel);
    
    // Calculate XP needed for next level (linear: level * 100)
    const xpForNextLevel = currentLevel > 0 ? currentLevel * 100 : 100;
    
    // XP in current level (how much XP above the threshold for current level)
    const xpInLevel = Math.max(0, currentXP - xpNeededForCurrent);
    
    const percent = Math.min(100, Math.max(0, (xpInLevel / xpForNextLevel) * 100));
    
    return {
        current: Math.floor(xpInLevel),
        next: Math.floor(xpForNextLevel),
        percent: percent
    };
}

// Load settings
async function loadSettings(container) {
    container.innerHTML = `
        <div style="padding: 20px;">
            <div style="background: white; border-radius: 12px; padding: 20px; margin-bottom: 12px;">
                <div style="font-weight: bold; font-size: 16px; margin-bottom: 12px;">🎨 Кастомизация профиля</div>
                <div style="color: #999; font-size: 14px; margin-bottom: 16px;">Функция в разработке</div>
                <button style="width: 100%; background: #e0e0e0; border: none; border-radius: 8px; padding: 12px; color: #666; font-weight: bold; cursor: not-allowed;" disabled>Изменить фон профиля</button>
            </div>
            
            <div style="background: white; border-radius: 12px; padding: 20px; margin-bottom: 12px;">
                <div style="font-weight: bold; font-size: 16px; margin-bottom: 12px;">🔔 Уведомления</div>
                <div style="color: #999; font-size: 14px; margin-bottom: 16px;">Функция в разработке</div>
                <button style="width: 100%; background: #e0e0e0; border: none; border-radius: 8px; padding: 12px; color: #666; font-weight: bold; cursor: not-allowed;" disabled>Настроить уведомления</button>
            </div>
            
            <div style="background: white; border-radius: 12px; padding: 20px;">
                <div style="font-weight: bold; font-size: 16px; margin-bottom: 12px;">🌐 Язык</div>
                <div style="color: #999; font-size: 14px; margin-bottom: 16px;">Функция в разработке</div>
                <button style="width: 100%; background: #e0e0e0; border: none; border-radius: 8px; padding: 12px; color: #666; font-weight: bold; cursor: not-allowed;" disabled>Изменить язык</button>
            </div>
        </div>
    `;
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
        
        // Update avatar - use uploaded image if available, otherwise use default
        const avatarElement = document.getElementById('user-avatar');
        if (profileData.avatar_image) {
            // Use uploaded avatar
            avatarElement.style.backgroundImage = `url(${profileData.avatar_image})`;
            avatarElement.style.backgroundSize = 'cover';
            avatarElement.style.backgroundPosition = 'center';
            avatarElement.textContent = '';
        } else {
            // Use default avatar based on user ID
            const avatarNum = ((profileData.user_id || 0) % 9) + 1;
            const avatarUrl = `https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/avatars/avatar_${avatarNum}.png`;
            avatarElement.style.backgroundImage = `url(${avatarUrl})`;
            avatarElement.style.backgroundSize = 'cover';
            avatarElement.style.backgroundPosition = 'center';
            avatarElement.textContent = '';
        }
        
        // Update currency
        document.getElementById('gold-value').textContent = profileData.gold || 0;
        document.getElementById('gem-value').textContent = profileData.gems || 0;
        document.getElementById('token-value').textContent = profileData.skill_points || 0;
        
        // Load user preferences
        if (profileData.waifu_sort_preference) {
            waifuSortBy = profileData.waifu_sort_preference;
        }
        
        // Update level and XP
        const currentLevel = profileData.level || 1;
        document.getElementById('player-level').textContent = currentLevel;
        
        // Calculate XP progress correctly using global XP formula
        const currentXP = profileData.xp || 0;
        
        // Global XP formula: arithmetic progression
        // Calculate total XP needed for current level
        let xpNeededForCurrent = 0;
        if (currentLevel > 1) {
            const n = currentLevel - 1;
            const a = 100;
            const d = 50;
            xpNeededForCurrent = n * (2 * a + (n - 1) * d) / 2;
        }
        
        // Calculate XP needed for next level
        const xpForNextLevel = currentLevel > 0 ? (100 + (currentLevel - 1) * 50) : 0;
        
        // XP in current level
        const xpInLevel = currentXP - xpNeededForCurrent;
        const xpNeeded = xpForNextLevel;
        
        const xpPercent = Math.min(100, Math.max(0, (xpInLevel / xpNeeded) * 100));
        
        document.getElementById('xp-fill').style.width = xpPercent + '%';
        document.getElementById('xp-current').textContent = Math.floor(xpInLevel);
        document.getElementById('xp-next').textContent = Math.floor(xpNeeded);
        
        // Load active waifu
        await loadActiveWaifu();
        
        // Load daily bonus status
        await loadDailyBonusStatus();
        
    } catch (error) {
        console.error('Error loading profile:', error);
        if (window.Telegram?.WebApp?.showAlert) {
            window.Telegram.WebApp.showAlert('Ошибка загрузки профиля');
        }
    }
}

// Load daily bonus status
async function loadDailyBonusStatus() {
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch('/api/daily-bonus-status?' + new URLSearchParams({ initData }));
        
        if (!response.ok) {
            console.error('Failed to fetch daily bonus status');
            return;
        }
        
        const bonusData = await response.json();
        const dailyBonusButton = document.getElementById('daily-bonus-button');
        
        if (!dailyBonusButton) {
            console.error('Daily bonus button not found');
            return;
        }
        
        if (bonusData.can_claim) {
            // Show button - can claim
            dailyBonusButton.style.display = 'flex';
            dailyBonusButton.innerHTML = `
                <div style="font-size: 24px; margin-bottom: 4px;">🎁</div>
                <div style="font-size: 12px; font-weight: bold;">Ежедневный бонус</div>
                <div style="font-size: 10px; opacity: 0.8;">+100💰</div>
            `;
            dailyBonusButton.onclick = claimDailyBonus;
        } else {
            // Hide button - on cooldown
            dailyBonusButton.style.display = 'none';
        }
        
    } catch (error) {
        console.error('Error loading daily bonus status:', error);
    }
}

// Claim daily bonus
async function claimDailyBonus() {
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch('/api/daily-bonus?' + new URLSearchParams({ initData }), {
            method: 'POST'
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to claim daily bonus');
        }
        
        const result = await response.json();
        
        // Show success message
        if (window.Telegram?.WebApp?.showAlert) {
            window.Telegram.WebApp.showAlert(`🎁 Ежедневный бонус получен!\n\n💰 +100 монет\n🔥 Серия: ${result.streak} дней\n💵 Баланс: ${result.new_balance} монет`);
        }
        
        // Reload profile to update coins
        await loadProfile();
        
    } catch (error) {
        console.error('Error claiming daily bonus:', error);
        if (window.Telegram?.WebApp?.showAlert) {
            window.Telegram.WebApp.showAlert('❌ Ошибка: ' + error.message);
        }
    }
}

// Load active waifu
async function loadActiveWaifu() {
    const activeWaifuCard = document.getElementById('active-waifu-card');
    
    if (!profileData.active_waifu) {
        // Reset background to white when no active waifu
        activeWaifuCard.style.background = 'white';
        activeWaifuCard.innerHTML = `
            <div onclick="openSelectActiveWaifuModal()" style="cursor: pointer; padding: 20px; text-align: center;">
                <p style="color: #666; margin-bottom: 12px;">Нет активной вайфу</p>
                <p style="color: #999; font-size: 14px;">Нажмите для выбора</p>
            </div>
        `;
        return;
    }
    
    const waifu = profileData.active_waifu;
    const power = calculatePower(waifu);
    const professionEmoji = getProfessionEmoji(waifu.profession);
    const flagEmoji = getFlagEmoji(waifu.nationality);
    const rarityColors = getRarityColor(waifu.rarity);
    
    // Set background color on the card itself
    activeWaifuCard.style.background = rarityColors.background;
    
    activeWaifuCard.innerHTML = `
        <div onclick="openSelectActiveWaifuModal()" style="cursor: pointer;">
            <img src="${waifu.image_url}" alt="${waifu.name}" class="waifu-image" onerror="this.onerror=null; this.src='data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20width=%27100%27%20height=%27100%27%3E%3Ctext%20x=%2750%25%27%20y=%2750%25%27%20font-size=%2714%27%20text-anchor=%27middle%27%20dy=%27.3em%27%3E🎭%3C/text%3E%3C/svg%3E'">
            <div class="waifu-name">${waifu.name}</div>
            <div class="waifu-info">Уровень ${waifu.level} • 💪${power} • ${professionEmoji} ${flagEmoji}</div>
        </div>
    `;
}

// Calculate power (must match backend: src/bot/services/waifu_generator.py::calculate_waifu_power)
function calculatePower(waifu) {
    const stats = waifu.stats || {};
    const dynamic = waifu.dynamic || {};
    
    // Base power from all stats
    let basePower = 0;
    basePower += stats.power || 0;
    basePower += stats.charm || 0;
    basePower += stats.luck || 0;
    basePower += stats.affection || 0;
    basePower += stats.intellect || 0;
    basePower += stats.speed || 0;
    
    // Bonuses from dynamic characteristics
    const mood = dynamic.mood || 50;
    const loyalty = dynamic.loyalty || 50;
    const moodBonus = mood * 0.1;
    const loyaltyBonus = loyalty * 0.05;
    
    // Level bonus
    const level = waifu.level || 1;
    const levelBonus = level * 2;
    
    const totalPower = basePower + moodBonus + loyaltyBonus + levelBonus;
    return Math.floor(totalPower);
}

// Close WebApp
function closeWebApp() {
    if (window.Telegram?.WebApp?.close) {
        window.Telegram.WebApp.close();
    }
}

// ==================== SKILLS SYSTEM ====================

let skillsData = null;
let skillsTree = null;

// Clan system state
let clanData = null;

// Load clan page
async function loadClanInfo(container) {
    console.log('🏰 Loading clan page');
    container.innerHTML = '<p class="loading">Загрузка информации о клане...</p>';
    
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch('/api/clans/my-clan?' + new URLSearchParams({ initData }));
        
        if (!response.ok) {
            throw new Error('Failed to fetch clan info');
        }
        
        const data = await response.json();
        clanData = data.clan;
        
        if (!clanData) {
            // User is not in a clan - show search/create UI
            renderNoClanView(container);
        } else {
            // User is in a clan - show clan info
            renderClanView(container, clanData);
        }
        
    } catch (error) {
        console.error('Error loading clan:', error);
        container.innerHTML = `
            <div style="text-align: center; padding: 20px;">
                <p style="color: #f5576c; margin-bottom: 8px; font-weight: bold;">Ошибка загрузки клана</p>
                <p style="color: #999; margin-bottom: 16px; font-size: 12px;">${error.message}</p>
                <button onclick="loadClanInfo(document.getElementById('other-views'))" style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; border: none; padding: 12px 24px; border-radius: 8px;
                    font-size: 14px; cursor: pointer;
                ">Повторить</button>
            </div>
        `;
    }
}

// Render no clan view
function renderNoClanView(container) {
    container.innerHTML = `
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 20px; border-radius: 16px; margin-bottom: 20px; text-align: center;">
            <h2 style="margin: 0 0 8px 0; font-size: 24px;">🏰 Клан</h2>
            <div style="font-size: 14px; opacity: 0.9;">Присоединяйтесь к кланам или создайте свой!</div>
        </div>
        
        <button onclick="openCreateClanModal()" style="
            width: 100%; background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white; border: none; padding: 16px; border-radius: 12px;
            font-size: 16px; font-weight: bold; cursor: pointer;
            margin-bottom: 16px; box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
        ">
            ➕ Создать клан
        </button>
        
        <button onclick="openSearchClansModal()" style="
            width: 100%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; border: none; padding: 16px; border-radius: 12px;
            font-size: 16px; font-weight: bold; cursor: pointer;
            margin-bottom: 16px;
        ">
            🔍 Найти клан
        </button>
    `;
}

// Render clan view
function renderClanView(container, clan) {
    container.innerHTML = `
        <!-- Back button -->
        <button onclick="navigateTo('profile')" style="
            background: rgba(255, 255, 255, 0.2);
            border: none;
            border-radius: 12px;
            padding: 12px 20px;
            color: white;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-bottom: 16px;
            width: 100%;
        ">
            ← Назад
        </button>
        
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 16px; border-radius: 16px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                ${clan.my_role === 'leader' ? `
                    <input type="file" id="clan-image-upload" accept="image/*" style="display: none;" onchange="handleClanImageUpload(event)">
                    <label for="clan-image-upload" style="
                        width: 48px; height: 48px; border-radius: 8px; 
                        background: rgba(255,255,255,0.2); cursor: pointer;
                        display: flex; align-items: center; justify-content: center;
                        font-size: 24px; border: 2px dashed rgba(255,255,255,0.5);
                        background-size: cover; background-position: center;
                        ${clan.image ? `background-image: url('${clan.image}');` : ''}
                    ">${clan.image ? '' : '📷'}</label>
                ` : `
                    <div style="width: 48px; height: 48px; border-radius: 8px; 
                                background: rgba(255,255,255,0.2); 
                                display: flex; align-items: center; justify-content: center;
                                font-size: 24px;
                                background-size: cover; background-position: center;
                                ${clan.image ? `background-image: url('${clan.image}');` : ''}
                    ">${clan.image ? '' : '🏰'}</div>
                `}
                <div style="flex: 1;">
                    <h2 style="margin: 0; font-size: 20px;">${clan.name}</h2>
                    <div style="font-size: 14px; opacity: 0.9;">#${clan.tag}</div>
                </div>
            </div>
        </div>
        
        <!-- Stats -->
        <div style="background: white; padding: 16px; border-radius: 12px; margin-bottom: 16px;">
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; text-align: center;">
                <div>
                    <div style="font-size: 12px; color: #666; margin-bottom: 4px;">Уровень</div>
                    <div style="font-size: 20px; font-weight: bold; color: #667eea;">${clan.level}</div>
                </div>
                <div>
                    <div style="font-size: 12px; color: #666; margin-bottom: 4px;">Сила</div>
                    <div style="font-size: 20px; font-weight: bold; color: #667eea;">${clan.total_power.toLocaleString()}</div>
                </div>
                <div>
                    <div style="font-size: 12px; color: #666; margin-bottom: 4px;">Участников</div>
                    <div style="font-size: 20px; font-weight: bold; color: #667eea;">${clan.members.length}</div>
                </div>
            </div>
        </div>
        
        <!-- Active Raid -->
        <div id="active-raid-section"></div>
        
        <!-- Members Link -->
        <div style="background: white; padding: 16px; border-radius: 12px; margin-bottom: 16px;">
            <button onclick="openClanMembersModal()" style="
                width: 100%; background: none; border: none; padding: 0;
                text-align: left; cursor: pointer;
            ">
                <h3 style="margin: 0; font-size: 18px; color: #333; display: flex; align-items: center; justify-content: space-between;">
                    <span>👥 Участники</span>
                    <span style="font-size: 14px; color: #666; font-weight: normal;">${clan.members.length} →</span>
                </h3>
            </button>
        </div>
        
        <!-- Chat -->
        <div style="background: white; padding: 16px; border-radius: 12px; margin-bottom: 16px;">
            <h3 style="margin: 0 0 12px 0; font-size: 18px; color: #333;">💬 Чат клана</h3>
            <div id="clan-chat-messages" style="max-height: 200px; overflow-y: auto; margin-bottom: 12px;">
                ${renderClanChat(clan.messages)}
            </div>
            <div style="display: flex; gap: 8px;">
                <input type="text" id="clan-chat-input" placeholder="Введите сообщение..." style="
                    flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 8px;
                    font-size: 14px;
                " onkeypress="if(event.key==='Enter') sendClanMessage()">
                <button onclick="sendClanMessage()" style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; border: none; padding: 10px; border-radius: 8px;
                    font-size: 20px; cursor: pointer; width: 40px; height: 40px; display: flex;
                    align-items: center; justify-content: center;
                ">➤</button>
            </div>
        </div>
        
        <!-- Footer Buttons -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 16px;">
            <button onclick="openClanSkillsModal()" style="
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white; border: none; padding: 12px; border-radius: 12px;
                font-size: 14px; font-weight: bold; cursor: pointer;
            ">
                🧬 Навыки клана
            </button>
            <button onclick="openClanSettingsModal()" style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; border: none; padding: 12px; border-radius: 12px;
                font-size: 14px; font-weight: bold; cursor: pointer;
            ">
                ⚙️ Настройки
            </button>
        </div>
    `;
    
    // Load active raid
    loadActiveRaid(clan.my_role);
}

// Render clan members
function renderClanMembers(members) {
    const roleEmojis = {
        'leader': '👑',
        'officer': '⭐',
        'member': '👤'
    };
    
    return members.map(m => `
        <div style="display: flex; align-items: center; padding: 8px; border-bottom: 1px solid #f0f0f0;">
            <div style="font-size: 24px; margin-right: 8px;">${roleEmojis[m.role]}</div>
            <div style="flex: 1;">
                <div style="font-weight: bold; font-size: 14px; color: #333;">@${m.username}</div>
                <div style="font-size: 12px; color: #666;">В клане с ${new Date(m.joined_at).toLocaleDateString('ru-RU')}</div>
            </div>
        </div>
    `).join('');
}

// Render clan chat
function renderClanChat(messages) {
    if (!messages || messages.length === 0) {
        return '<div style="text-align: center; color: #999; padding: 20px;">Нет сообщений</div>';
    }
    
    return messages.map(m => `
        <div style="margin-bottom: 8px;">
            <div style="font-size: 12px; color: #666; margin-bottom: 2px;">
                <strong>@${m.username}</strong> • ${new Date(m.created_at).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}
            </div>
            <div style="background: #f5f5f5; padding: 8px; border-radius: 8px; font-size: 14px; color: #333;">
                ${m.message}
            </div>
        </div>
    `).join('');
}

// Open create clan modal
function openCreateClanModal() {
    const modal = document.createElement('div');
    modal.id = 'create-clan-modal';
    modal.style.cssText = `
        position: fixed; top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0,0,0,0.8); display: flex; align-items: center;
        justify-content: center; z-index: 10000;
    `;
    
    modal.innerHTML = `
        <div style="background: white; padding: 24px; border-radius: 16px; width: 90%; max-width: 400px;">
            <h3 style="margin: 0 0 16px 0;">Создать клан</h3>
            
            <div style="margin-bottom: 12px;">
                <label style="display: block; margin-bottom: 4px; font-size: 12px; color: #666;">Название</label>
                <input type="text" id="clan-name-input" placeholder="Введите название..." style="
                    width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px;
                    font-size: 14px; box-sizing: border-box;
                ">
            </div>
            
            <div style="margin-bottom: 12px;">
                <label style="display: block; margin-bottom: 4px; font-size: 12px; color: #666;">Тег</label>
                <input type="text" id="clan-tag-input" placeholder="TAG" maxlength="10" style="
                    width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px;
                    font-size: 14px; box-sizing: border-box; text-transform: uppercase;
                ">
            </div>
            
            <div style="margin-bottom: 16px;">
                <label style="display: block; margin-bottom: 4px; font-size: 12px; color: #666;">Описание</label>
                <textarea id="clan-desc-input" placeholder="Описание клана..." rows="3" style="
                    width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px;
                    font-size: 14px; box-sizing: border-box; resize: vertical;
                "></textarea>
            </div>
            
            <div style="margin-bottom: 16px;">
                <label style="display: block; margin-bottom: 4px; font-size: 12px; color: #666;">Тип клана</label>
                <select id="clan-type-input" style="
                    width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px;
                    font-size: 14px;
                ">
                    <option value="open">Открытый (любой может присоединиться)</option>
                    <option value="invite">По приглашению</option>
                    <option value="closed">Закрытый</option>
                </select>
            </div>
            
            <div style="display: flex; gap: 8px;">
                <button onclick="createClan()" style="
                    flex: 1; background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                    color: white; border: none; padding: 12px; border-radius: 8px;
                    font-size: 14px; font-weight: bold; cursor: pointer;
                ">Создать</button>
                <button onclick="closeCreateClanModal()" style="
                    background: #e0e0e0; border: none; padding: 12px 16px;
                    border-radius: 8px; font-size: 14px; cursor: pointer;
                ">Отмена</button>
            </div>
            
            <div style="margin-top: 12px; font-size: 12px; color: #666; text-align: center;">
                Стоимость: 1000 золота
            </div>
        </div>
    `;
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
    
    document.body.appendChild(modal);
}

// Close create clan modal
function closeCreateClanModal() {
    const modal = document.getElementById('create-clan-modal');
    if (modal) {
        modal.remove();
    }
}

// Create clan
async function createClan() {
    try {
        const name = document.getElementById('clan-name-input').value.trim();
        const tag = document.getElementById('clan-tag-input').value.trim().toUpperCase();
        const description = document.getElementById('clan-desc-input').value.trim();
        const type = document.getElementById('clan-type-input').value;
        
        if (!name || name.length < 3) {
            window.Telegram?.WebApp?.showAlert?.('Название должно быть не менее 3 символов');
            return;
        }
        
        if (!tag || tag.length < 2) {
            window.Telegram?.WebApp?.showAlert?.('Тег должен быть не менее 2 символов');
            return;
        }
        
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch('/api/clans/create?' + new URLSearchParams({ initData }), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, tag, description, type })
        });
        
        if (!response.ok) {
            const error = await response.json();
            window.Telegram?.WebApp?.showAlert?.(error.detail || 'Ошибка создания клана');
            return;
        }
        
        const result = await response.json();
        window.Telegram?.WebApp?.showAlert?.('Клан создан!');
        
        // Close modal and reload
        closeCreateClanModal();
        loadClanInfo(document.getElementById('other-views'));
        loadProfile();
        
    } catch (error) {
        console.error('Error creating clan:', error);
        window.Telegram?.WebApp?.showAlert?.('Ошибка создания клана');
    }
}

// Search clans modal
function openSearchClansModal() {
    const modal = document.createElement('div');
    modal.id = 'search-clans-modal';
    modal.style.cssText = `
        position: fixed; top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0,0,0,0.8); display: flex; align-items: center;
        justify-content: center; z-index: 10000;
    `;
    
    modal.innerHTML = `
        <div style="background: white; padding: 24px; border-radius: 16px; width: 90%; max-width: 500px; max-height: 80vh; overflow-y: auto;">
            <h3 style="margin: 0 0 16px 0;">🔍 Найти клан</h3>
            
            <div style="margin-bottom: 16px;">
                <input type="text" id="clan-search-input" placeholder="Название или тег..." style="
                    width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px;
                    font-size: 14px; box-sizing: border-box;
                " onkeyup="if(event.key==='Enter') searchClans()">
            </div>
            
            <div style="margin-bottom: 16px;">
                <select id="clan-type-filter" style="
                    width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px;
                    font-size: 14px;
                ">
                    <option value="">Все типы</option>
                    <option value="open">Открытые</option>
                    <option value="invite">По приглашению</option>
                    <option value="closed">Закрытые</option>
                </select>
            </div>
            
            <button onclick="searchClans()" style="
                width: 100%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; border: none; padding: 12px; border-radius: 8px;
                font-size: 14px; font-weight: bold; cursor: pointer;
                margin-bottom: 16px;
            ">🔍 Найти</button>
            
            <div id="search-results"></div>
            
            <button onclick="closeSearchClansModal()" style="
                width: 100%; background: #e0e0e0; border: none; padding: 12px;
                border-radius: 8px; font-size: 14px; cursor: pointer;
            ">Закрыть</button>
        </div>
    `;
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
    
    document.body.appendChild(modal);
}

// Close search clans modal
function closeSearchClansModal() {
    const modal = document.getElementById('search-clans-modal');
    if (modal) {
        modal.remove();
    }
}

// Search clans
async function searchClans() {
    const query = document.getElementById('clan-search-input').value.trim();
    const type = document.getElementById('clan-type-filter').value;
    const resultsDiv = document.getElementById('search-results');
    
    resultsDiv.innerHTML = '<p style="text-align: center; color: #999; padding: 20px;">Загрузка...</p>';
    
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        const params = new URLSearchParams({ initData });
        if (query) params.append('q', query);
        if (type) params.append('type', type);
        
        const response = await fetch(`/api/clans/search?${params}`);
        
        if (!response.ok) {
            resultsDiv.innerHTML = '<p style="text-align: center; color: #f5576c; padding: 20px;">Ошибка поиска</p>';
            return;
        }
        
        const data = await response.json();
        
        if (data.clans.length === 0) {
            resultsDiv.innerHTML = '<p style="text-align: center; color: #999; padding: 20px;">Кланы не найдены</p>';
            return;
        }
        
        resultsDiv.innerHTML = data.clans.map(clan => `
            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 12px; margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div>
                        <div style="font-weight: bold; font-size: 16px;">${clan.name}</div>
                        <div style="font-size: 12px; color: #666;">#${clan.tag}</div>
                    </div>
                    <button onclick="joinClanNow(${clan.id})" style="
                        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                        color: white; border: none; padding: 8px 16px;
                        border-radius: 8px; font-size: 12px; cursor: pointer;
                    ">Вступить</button>
                </div>
                ${clan.description ? `<div style="font-size: 12px; color: #666; margin-bottom: 8px;">${clan.description}</div>` : ''}
                <div style="display: flex; gap: 16px; font-size: 12px; color: #666;">
                    <span>👥 ${clan.members_count}/${50 + clan.level * 5}</span>
                    <span>💪 ${clan.total_power.toLocaleString()}</span>
                    <span>⭐ Ур. ${clan.level}</span>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error searching clans:', error);
        resultsDiv.innerHTML = '<p style="text-align: center; color: #f5576c; padding: 20px;">Ошибка поиска</p>';
    }
}

// Join clan from search
async function joinClanNow(clanId) {
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch('/api/clans/join?' + new URLSearchParams({ initData }), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ clan_id: clanId })
        });
        
        if (!response.ok) {
            const error = await response.json();
            window.Telegram?.WebApp?.showAlert?.(error.detail || 'Ошибка вступления');
            return;
        }
        
        window.Telegram?.WebApp?.showAlert?.('Вы присоединились к клану!');
        document.querySelector('div[style*="position: fixed"]').remove();
        loadClanInfo(document.getElementById('other-views'));
        loadProfile();
        
    } catch (error) {
        console.error('Error joining clan:', error);
        window.Telegram?.WebApp?.showAlert?.('Ошибка вступления');
    }
}

// Send clan message
async function sendClanMessage() {
    const input = document.getElementById('clan-chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch('/api/clans/chat/send?' + new URLSearchParams({ initData }), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        
        if (!response.ok) {
            const error = await response.json();
            window.Telegram?.WebApp?.showAlert?.(error.detail || 'Ошибка отправки сообщения');
            return;
        }
        
        input.value = '';
        // Reload just the chat instead of entire page
        await reloadClanChat();
        
    } catch (error) {
        console.error('Error sending message:', error);
        window.Telegram?.WebApp?.showAlert?.('Ошибка отправки сообщения');
    }
}

// Reload clan chat messages
async function reloadClanChat() {
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch('/api/clans/my-clan?' + new URLSearchParams({ initData }));
        
        if (!response.ok) {
            throw new Error('Failed to fetch clan info');
        }
        
        const data = await response.json();
        const clan = data.clan;
        
        if (clan && clan.messages) {
            const chatContainer = document.getElementById('clan-chat-messages');
            if (chatContainer) {
                chatContainer.innerHTML = renderClanChat(clan.messages);
                // Scroll to bottom to show latest message
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        }
    } catch (error) {
        console.error('Error reloading clan chat:', error);
    }
}

// Leave clan
async function leaveClan() {
    const confirmed = await window.Telegram?.WebApp?.showConfirm?.('Вы действительно хотите покинуть клан?');
    if (!confirmed) return;
    
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch('/api/clans/leave?' + new URLSearchParams({ initData }), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (!response.ok) {
            const error = await response.json();
            window.Telegram?.WebApp?.showAlert?.(error.detail || 'Ошибка');
            return;
        }
        
        window.Telegram?.WebApp?.showAlert?.('Вы покинули клан');
        loadClanInfo(document.getElementById('other-views'));
        loadProfile();
        
    } catch (error) {
        console.error('Error leaving clan:', error);
        window.Telegram?.WebApp?.showAlert?.('Ошибка');
    }
}

// Open clan members modal
function openClanMembersModal() {
    // Fetch current clan info to get members
    (async () => {
        try {
            const initData = window.Telegram?.WebApp?.initData || '';
            const response = await fetch('/api/clans/my-clan?' + new URLSearchParams({ initData }));
            
            if (!response.ok) {
                throw new Error('Failed to fetch clan info');
            }
            
            const data = await response.json();
            const clan = data.clan;
            
            const modal = document.createElement('div');
            modal.style.cssText = `
                position: fixed; top: 0; left: 0; right: 0; bottom: 0;
                background: rgba(0,0,0,0.8); display: flex; align-items: center;
                justify-content: center; z-index: 10000; padding: 20px;
            `;
            
            modal.innerHTML = `
                <div style="background: white; border-radius: 20px; max-width: 500px; width: 100%; max-height: 80vh; overflow-y: auto; padding: 24px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h3 style="margin: 0; font-size: 20px; color: #333;">👥 Участники клана</h3>
                        <button onclick="closeClanMembersModal()" style="
                            background: #dc3545; color: white; border: none; border-radius: 50%;
                            width: 32px; height: 32px; font-size: 18px; font-weight: bold;
                            cursor: pointer; display: flex; align-items: center; justify-content: center;
                        ">×</button>
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 12px;">
                        ${renderClanMembers(clan.members)}
                    </div>
                </div>
            `;
            
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.remove();
                }
            });
            
            document.body.appendChild(modal);
        } catch (error) {
            console.error('Error loading clan members:', error);
            window.Telegram?.WebApp?.showAlert?.('Ошибка загрузки участников');
        }
    })();
}

// Close clan members modal
function closeClanMembersModal() {
    const modal = document.querySelector('div[style*="position: fixed"]');
    if (modal) {
        modal.remove();
    }
}

// Open clan skills modal
function openClanSkillsModal() {
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed; top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0,0,0,0.8); display: flex; align-items: center;
        justify-content: center; z-index: 10000; padding: 20px;
    `;
    
    modal.innerHTML = `
        <div style="background: white; border-radius: 20px; max-width: 400px; width: 100%; padding: 24px; text-align: center;">
            <button onclick="closeClanSkillsModal()" style="
                position: absolute; top: 16px; right: 16px; width: 32px; height: 32px;
                background: #dc3545; color: white; border: none; border-radius: 50%;
                font-size: 16px; font-weight: bold; cursor: pointer;
            ">×</button>
            <div style="font-size: 64px; margin-bottom: 16px;">🚧</div>
            <h3 style="margin: 0 0 8px 0; font-size: 20px; color: #333;">В разработке</h3>
            <p style="margin: 0; font-size: 14px; color: #666;">Навыки клана появятся в будущих обновлениях</p>
        </div>
    `;
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
    
    document.body.appendChild(modal);
}

// Close clan skills modal
function closeClanSkillsModal() {
    const modal = document.querySelector('div[style*="position: fixed"]');
    if (modal) {
        modal.remove();
    }
}

// Open clan settings modal
async function openClanSettingsModal() {
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch('/api/clans/my-clan?' + new URLSearchParams({ initData }));
        
        if (!response.ok) {
            throw new Error('Failed to fetch clan info');
        }
        
        const data = await response.json();
        const clan = data.clan;
        
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.8); display: flex; align-items: center;
            justify-content: center; z-index: 10000; padding: 20px;
        `;
        
        modal.innerHTML = `
            <div style="background: white; border-radius: 20px; max-width: 400px; width: 100%; padding: 24px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h3 style="margin: 0; font-size: 20px; color: #333;">⚙️ Настройки клана</h3>
                    <button onclick="closeClanSettingsModal()" style="
                        background: #dc3545; color: white; border: none; border-radius: 50%;
                        width: 32px; height: 32px; font-size: 18px; font-weight: bold;
                        cursor: pointer; display: flex; align-items: center; justify-content: center;
                    ">×</button>
                </div>
                <div style="display: flex; flex-direction: column; gap: 12px;">
                    <div style="background: #f8f9fa; padding: 16px; border-radius: 12px; text-align: center;">
                        <div style="font-size: 12px; color: #666; margin-bottom: 4px;">Уровень клана</div>
                        <div style="font-size: 24px; font-weight: bold; color: #667eea;">${clan.level}</div>
                    </div>
                    <div style="background: #f8f9fa; padding: 16px; border-radius: 12px; text-align: center;">
                        <div style="font-size: 12px; color: #666; margin-bottom: 4px;">Общая сила</div>
                        <div style="font-size: 20px; font-weight: bold; color: #667eea;">${clan.total_power.toLocaleString()}</div>
                    </div>
                    ${clan.my_role === 'leader' ? `
                        <div style="padding-top: 12px; border-top: 2px solid #eee;">
                            <p style="font-size: 14px; color: #666; margin: 0 0 8px 0;">Действия</p>
                            <button onclick="leaveClan()" style="
                                width: 100%; background: #ff4444;
                                color: white; border: none; padding: 12px; border-radius: 12px;
                                font-size: 14px; font-weight: bold; cursor: pointer; margin-top: 8px;
                            ">
                                🚪 Покинуть клан
                            </button>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
        document.body.appendChild(modal);
    } catch (error) {
        console.error('Error loading clan settings:', error);
        window.Telegram?.WebApp?.showAlert?.('Ошибка загрузки настроек');
    }
}

// Close clan settings modal
function closeClanSettingsModal() {
    const modal = document.querySelector('div[style*="position: fixed"]');
    if (modal) {
        modal.remove();
    }
}

// Handle clan image upload
function handleClanImageUpload(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    
    // Check file type
    if (!file.type.startsWith('image/')) {
        window.Telegram?.WebApp?.showAlert?.('Пожалуйста, выберите изображение');
        return;
    }
    
    // Check file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
        window.Telegram?.WebApp?.showAlert?.('Файл слишком большой (макс. 5МБ)');
        return;
    }
    
    // Read file as base64
    const reader = new FileReader();
    reader.onload = async (e) => {
        const imageData = e.target.result;
        
        try {
            const initData = window.Telegram?.WebApp?.initData || '';
            const response = await fetch('/api/clans/upload-image?' + new URLSearchParams({ initData }), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image: imageData
                })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Ошибка загрузки');
            }
            
            const result = await response.json();
            
            window.Telegram?.WebApp?.showAlert?.('✅ Изображение загружено');
            
            // Reload clan page
            loadClanInfo(document.getElementById('view-content'));
            
        } catch (error) {
            console.error('Error uploading image:', error);
            window.Telegram?.WebApp?.showAlert?.('❌ ' + error.message);
        }
    };
    
    reader.onerror = () => {
        window.Telegram?.WebApp?.showAlert?.('Ошибка чтения файла');
    };
    
    reader.readAsDataURL(file);
}

// Load active raid
async function loadActiveRaid(myRole) {
    const section = document.getElementById('active-raid-section');
    if (!section) return;
    
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch('/api/clans/events?' + new URLSearchParams({ initData }));
        
        if (!response.ok) {
            section.innerHTML = '';
            return;
        }
        
        const data = await response.json();
        const activeRaids = data.active.filter(e => e.type === 'raid');
        
        if (activeRaids.length === 0) {
            // No active raid - show start button for leaders/officers
            if (myRole === 'leader' || myRole === 'officer') {
                section.innerHTML = `
                    <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%); 
                                color: white; padding: 16px; border-radius: 12px; margin-bottom: 16px; text-align: center;">
                        <h3 style="margin: 0 0 8px 0; font-size: 18px;">🐉 Clan Raid</h3>
                        <p style="margin: 0 0 12px 0; font-size: 14px; opacity: 0.9;">Начните новый рейд!</p>
                        <button onclick="startRaid()" style="
                            background: white; color: #ff6b6b; border: none; padding: 10px 20px;
                            border-radius: 8px; font-size: 14px; font-weight: bold; cursor: pointer;
                        ">Запустить рейд</button>
                    </div>
                `;
            } else {
                section.innerHTML = '';
            }
        } else {
            // Active raid
            const raid = activeRaids[0];
            const boss_hp = raid.data.boss_hp || 0;
            const boss_max_hp = raid.data.boss_max_hp || 1;
            const hp_percent = Math.round((boss_hp / boss_max_hp) * 100);
            
            section.innerHTML = `
                <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%); 
                            color: white; padding: 16px; border-radius: 12px; margin-bottom: 16px;">
                    <h3 style="margin: 0 0 12px 0; font-size: 18px;">🐉 ${raid.data.boss_name || 'Clan Raid'}</h3>
                    <div style="margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 12px;">
                            <span>HP Босса</span>
                            <span>${hp_percent}%</span>
                        </div>
                        <div style="background: rgba(255,255,255,0.3); border-radius: 8px; height: 24px; overflow: hidden;">
                            <div style="background: white; height: 100%; width: ${hp_percent}%; transition: width 0.3s;"></div>
                        </div>
                    </div>
                    <button onclick="attackRaidBoss()" style="
                        width: 100%; background: white; color: #ff6b6b; border: none;
                        padding: 12px; border-radius: 8px; font-size: 14px; font-weight: bold;
                        cursor: pointer;
                    ">⚔️ Атаковать</button>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading raid:', error);
        section.innerHTML = '';
    }
}

// Attack raid boss
async function attackRaidBoss() {
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch('/api/clans/raid/attack?' + new URLSearchParams({ initData }), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (!response.ok) {
            const error = await response.json();
            window.Telegram?.WebApp?.showAlert?.(error.detail || 'Ошибка атаки');
            return;
        }
        
        const result = await response.json();
        
        if (result.boss_defeated) {
            window.Telegram?.WebApp?.showAlert?.(`🎉 Босс повержен! Урон: ${result.damage.toLocaleString()}`);
        } else {
            window.Telegram?.WebApp?.showAlert?.(`⚔️ Урон: ${result.damage.toLocaleString()}`);
        }
        
        loadActiveRaid(clanData.my_role);
        loadProfile();
        
    } catch (error) {
        console.error('Error attacking raid:', error);
        window.Telegram?.WebApp?.showAlert?.('Ошибка атаки');
    }
}

// Start raid
async function startRaid() {
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch('/api/clans/raid/start?' + new URLSearchParams({ initData }), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (!response.ok) {
            const error = await response.json();
            window.Telegram?.WebApp?.showAlert?.(error.detail || 'Ошибка запуска рейда');
            return;
        }
        
        window.Telegram?.WebApp?.showAlert?.('Рейд запущен!');
        loadActiveRaid(clanData.my_role);
        
    } catch (error) {
        console.error('Error starting raid:', error);
        window.Telegram?.WebApp?.showAlert?.('Ошибка запуска рейда');
    }
}

// Load skills page
async function loadSkills(container) {
    console.log('🧬 Loading skills page');
    container.innerHTML = '<p class="loading">Загрузка навыков...</p>';
    
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch('/api/skills/tree?' + new URLSearchParams({ initData }));
        
        if (!response.ok) {
            throw new Error('Failed to fetch skills');
        }
        
        const data = await response.json();
        skillsData = data;
        skillsTree = data.skills_tree;
        
        renderSkillsPage(container, data);
        
    } catch (error) {
        console.error('Error loading skills:', error);
        
        // Try to get error message from response
        let errorMessage = 'Неизвестная ошибка';
        if (error.message) {
            errorMessage = error.message;
        }
        
        container.innerHTML = `
            <div style="text-align: center; padding: 20px;">
                <p style="color: #f5576c; margin-bottom: 8px; font-weight: bold;">Ошибка загрузки навыков</p>
                <p style="color: #999; margin-bottom: 16px; font-size: 12px;">${errorMessage}</p>
                <button onclick="loadSkills(document.getElementById('view-content'))" style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; border: none; padding: 12px 24px; border-radius: 8px;
                    font-size: 14px; cursor: pointer;
                ">Повторить</button>
            </div>
        `;
    }
}

// Render skills page
function renderSkillsPage(container, data) {
    const { skills_tree, category_progress, skill_points } = data;
    
    container.innerHTML = `
        <!-- Back button -->
        <button onclick="navigateTo('profile')" class="back-btn" style="
            background: rgba(255, 255, 255, 0.2);
            border: none;
            border-radius: 12px;
            padding: 12px 20px;
            color: white;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-bottom: 16px;
            width: 100%;
        ">
            ← Назад
        </button>
        
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 20px; border-radius: 16px; margin-bottom: 20px; text-align: center;">
            <h2 style="margin: 0 0 8px 0; font-size: 24px;">🧬 Прокачка</h2>
            <div style="font-size: 14px; opacity: 0.9;">
                Очки навыков: <span style="font-weight: bold;">${skill_points || 0}</span>
            </div>
        </div>
        
        <!-- Category Tabs -->
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 20px;">
            <button onclick="showSkillCategory('account')" id="tab-account" style="
                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                color: white; border: none; padding: 12px; border-radius: 12px;
                font-size: 14px; font-weight: bold; cursor: pointer;
                box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
            ">
                📊 Аккаунт<br><small>${category_progress.account || 0} очков</small>
            </button>
            <button onclick="showSkillCategory('passive')" id="tab-passive" style="
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white; border: none; padding: 12px; border-radius: 12px;
                font-size: 14px; font-weight: bold; cursor: pointer;
                box-shadow: 0 4px 12px rgba(240, 147, 251, 0.3);
            ">
                🎭 Пассивные<br><small>${category_progress.passive || 0} очков</small>
            </button>
            <button onclick="showSkillCategory('training')" id="tab-training" style="
                background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
                color: white; border: none; padding: 12px; border-radius: 12px;
                font-size: 14px; font-weight: bold; cursor: pointer;
                box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
            ">
                🏋️ Тренировки<br><small>${category_progress.training || 0} очков</small>
            </button>
        </div>
        
        <!-- Skills Content -->
        <div id="skills-content">
            ${renderSkillCategory(currentSkillCategory, skills_tree[currentSkillCategory] || skills_tree.account)}
        </div>
    `;
    
    // Set active tab based on current category
    document.getElementById(`tab-${currentSkillCategory}`).style.opacity = '1';
    ['account', 'passive', 'training'].filter(cat => cat !== currentSkillCategory).forEach(cat => {
        const tab = document.getElementById(`tab-${cat}`);
        if (tab) tab.style.opacity = '0.7';
    });
}

// Show skill category
function showSkillCategory(category) {
    // Update global state
    currentSkillCategory = category;
    
    // Update tab styles
    document.querySelectorAll('[id^="tab-"]').forEach(tab => {
        tab.style.opacity = '0.7';
    });
    document.getElementById(`tab-${category}`).style.opacity = '1';
    
    // Update content
    const content = document.getElementById('skills-content');
    content.innerHTML = renderSkillCategory(category, skillsTree[category]);
}

// Render skill category
function renderSkillCategory(category, skills) {
    if (!skills || skills.length === 0) {
        return '<p style="text-align: center; color: #666; padding: 20px;">Навыки не найдены</p>';
    }
    
    return `
        <div style="display: grid; gap: 12px;">
            ${skills.map(skill => renderSkillCard(skill)).join('')}
        </div>
    `;
}

// Render skill card
function renderSkillCard(skill) {
    const isMaxLevel = skill.current_level >= skill.max_level;
    const canUpgrade = skill.can_upgrade && skill.is_unlocked;
    const isLocked = !skill.is_unlocked;
    
    let cardStyle = `
        background: white; border-radius: 16px; padding: 16px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); transition: all 0.2s;
        border: 2px solid ${isLocked ? '#ddd' : canUpgrade ? '#4CAF50' : '#ccc'};
    `;
    
    if (isLocked) {
        cardStyle += 'opacity: 0.6;';
    }
    
    return `
        <div style="${cardStyle}" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="font-size: 32px;">${skill.icon}</div>
                <div style="flex: 1;">
                    <h3 style="margin: 0 0 4px 0; font-size: 16px; color: #333;">${skill.name}</h3>
                    <div style="font-size: 12px; color: #666;">${skill.description}</div>
                </div>
                <div style="text-align: right;">
                    ${canUpgrade ? `
                        <button onclick="upgradeSkill('${skill.skill_id}')" style="
                            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                            color: white; border: none; padding: 8px 16px; border-radius: 8px;
                            font-size: 13px; font-weight: bold; cursor: pointer;
                            transition: all 0.2s; min-width: 70px;
                        " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                            ${skill.current_level}/${skill.max_level}
                        </button>
                    ` : isMaxLevel ? `
                        <div style="
                            background: #e8f5e8; color: #4CAF50; padding: 8px 16px; border-radius: 8px;
                            text-align: center; font-size: 13px; font-weight: bold; min-width: 70px;
                        ">
                            МАХ
                        </div>
                    ` : `<div style="font-size: 14px; font-weight: bold; color: #333;">${skill.current_level}/${skill.max_level}</div>`}
                    ${isLocked ? '<div style="font-size: 10px; color: #999;">Заблокирован</div>' : ''}
                </div>
            </div>
            
            <!-- Progress Bar -->
            <div style="background: #f0f0f0; border-radius: 8px; height: 6px; margin-top: 12px;">
                <div style="
                    background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                    height: 100%; border-radius: 8px; width: ${(skill.current_level / skill.max_level) * 100}%;
                    transition: width 0.3s;
                "></div>
            </div>
            
            <!-- Click to view details -->
            ${skill.current_level > 0 || isLocked || !canUpgrade ? `
                <div style="margin-top: 8px; text-align: center;">
                    <button onclick="openSkillDetailModalBySkillId('${skill.skill_id}')" style="
                        background: transparent; color: #667eea; border: 1px solid #667eea;
                        padding: 6px 12px; border-radius: 6px; font-size: 12px; cursor: pointer;
                        transition: all 0.2s;
                    " onmouseover="this.style.background='#667eea'; this.style.color='white'" 
                       onmouseout="this.style.background='transparent'; this.style.color='#667eea'">
                        📋 Детали
                    </button>
                </div>
            ` : ''}
        </div>
    `;
}

// Open skill detail modal
function openSkillDetailModal(skill) {
    const isMaxLevel = skill.current_level >= skill.max_level;
    const canUpgrade = skill.can_upgrade && skill.is_unlocked;
    const isLocked = !skill.is_unlocked;
    
    let modalContent = `
        <div style="
            position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.7);
            z-index: 10000; display: flex; align-items: center; justify-content: center;
            padding: 20px;
        " onclick="closeSkillDetailModal()" id="skill-detail-modal">
            <div style="
                background: white; border-radius: 20px; padding: 24px; max-width: 400px; width: 100%;
                max-height: 80vh; overflow-y: auto; box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            " onclick="event.stopPropagation()">
                <div style="text-align: center; margin-bottom: 20px;">
                    <div style="font-size: 48px; margin-bottom: 8px;">${skill.icon}</div>
                    <h2 style="margin: 0 0 8px 0; font-size: 20px; color: #333;">${skill.name}</h2>
                    <p style="margin: 0; font-size: 14px; color: #666;">${skill.description}</p>
                </div>
                
                <div style="text-align: center; margin-bottom: 16px;">
                    <span style="font-size: 18px; font-weight: bold; color: #333;">
                        ${skill.current_level}/${skill.max_level}
                    </span>
                </div>
                
                <!-- Effects -->
                ${skill.current_level > 0 ? `
                    <div style="background: #f8f9fa; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                        <div style="font-size: 14px; color: #666; margin-bottom: 8px; font-weight: bold;">Текущие эффекты:</div>
                        ${Object.entries(skill.effects[skill.current_level] || {}).map(([key, value]) => 
                            `<div style="font-size: 13px; color: #333; margin-bottom: 4px;">${key}: +${(value * 100).toFixed(0)}%</div>`
                        ).join('')}
                    </div>
                ` : ''}
                
                <!-- Locked info -->
                ${isLocked ? `
                    <div style="background: #fff3cd; border-radius: 8px; padding: 12px; margin-bottom: 16px; text-align: center;">
                        <div style="font-size: 13px; color: #856404;">🔒 Требуется ${skill.unlock_requirement} очков в категории</div>
                    </div>
                ` : ''}
                
                <button onclick="closeSkillDetailModal()" style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; border: none; padding: 12px 24px; border-radius: 8px;
                    font-size: 14px; font-weight: bold; cursor: pointer; width: 100%;
                ">
                    Закрыть
                </button>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalContent);
}

function closeSkillDetailModal() {
    const modal = document.getElementById('skill-detail-modal');
    if (modal) {
        modal.remove();
    }
}

function openSkillDetailModalBySkillId(skillId) {
    // Find the skill in the current skillsTree
    let foundSkill = null;
    for (const category in skillsTree) {
        const skill = skillsTree[category].find(s => s.skill_id === skillId);
        if (skill) {
            foundSkill = skill;
            break;
        }
    }
    
    if (foundSkill) {
        openSkillDetailModal(foundSkill);
    }
}

// Upgrade skill
async function upgradeSkill(skillId) {
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch('/api/skills/upgrade?' + new URLSearchParams({ initData }), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                skill_id: skillId
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to upgrade skill');
        }
        
        const result = await response.json();
        
        // Reload skills page with current category preserved
        loadSkills(document.getElementById('view-content'));
        
    } catch (error) {
        console.error('Error upgrading skill:', error);
        if (window.Telegram?.WebApp?.showAlert) {
            window.Telegram.WebApp.showAlert('❌ Ошибка: ' + error.message);
        }
    }
}
