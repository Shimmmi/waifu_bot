// Global state
let profileData = null;
let waifuList = [];
let currentView = 'profile';
let waifuSortBy = 'name'; // Default sort: name, rarity, level, power, race, profession, nationality
let showOnlyFavorites = false; // Filter toggle

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
            'clan': { title: '🏰 Клан', content: 'loadClanInfo()' },
            'quests': { title: '📅 Ежедневные задания', content: 'loadQuests()' },
            'skills': { title: '', content: 'loadSkills()' },
            'settings': { title: '⚙️ Настройки профиля', content: 'loadSettings()' },
            'upgrade': { title: '⚡ Прокачка вайфу', content: 'loadUpgradePage()' }
        };
        
        if (views[view]) {
            viewTitle.textContent = views[view].title;
            
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

        renderWaifuList(container);

    } catch (error) {
        console.error('Error loading waifu list:', error);
        container.innerHTML = '<p style="color: red; padding: 20px;">Ошибка загрузки</p>';
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
        
        <!-- Toolbar Row 2: Summon buttons -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 16px; padding: 0 4px;">
            <button onclick="summonWaifu(1)" style="
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                color: white; border: none; padding: 12px 8px; border-radius: 12px; 
                font-size: 13px; font-weight: bold; cursor: pointer; display: flex; 
                flex-direction: column; align-items: center; justify-content: center; gap: 4px;
            ">
                <div style="font-size: 14px;">✨ Призыв</div>
                <div style="font-size: 12px; opacity: 0.9;">(100💰)</div>
            </button>
            <button onclick="summonWaifu(10)" style="
                background: linear-gradient(135deg, #FA8BFF 0%, #2BD2FF 90%, #2BFF88 100%); 
                color: white; border: none; padding: 12px 8px; border-radius: 12px; 
                font-size: 13px; font-weight: bold; cursor: pointer; display: flex; 
                flex-direction: column; align-items: center; justify-content: center; gap: 4px;
            ">
                <div style="font-size: 14px;">✨ Призыв x10</div>
                <div style="font-size: 12px; opacity: 0.9;">(1000💰)</div>
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
        showSummonedWaifusModal(data.summoned, data.remaining_coins);
        
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

// Show summoned waifus modal
function showSummonedWaifusModal(waifus, remainingCoins) {
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
                <div style="font-size: 48px; margin-bottom: 12px;">✨</div>
                <h2 style="margin: 0 0 8px 0; font-size: 24px; color: #333;">Призыв завершен!</h2>
                <p style="margin: 0; color: #666; font-size: 14px;">Призвано вайфу: ${waifus.length}</p>
                <p style="margin: 8px 0 0 0; color: #FF9800; font-size: 16px; font-weight: bold;">Осталось монет: ${remainingCoins} 💰</p>
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
    const modal = document.querySelector('div[style*="position: fixed"]');
    if (modal) {
        modal.remove();
    }
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
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #666;">🔥 Пожертвовано:</span>
                    <span style="font-weight: bold; color: #dc3545;">${result.sacrificed_count} вайфу</span>
                </div>
            </div>
            
            <button onclick="closeUpgradeModal()" style="
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
        
        // Calculate XP progress
        const xpForNextLevel = Math.floor(100 * Math.pow(waifu.level + 1, 1.1));
        const xpInCurrentLevel = waifu.xp;
        const xpPercent = Math.min((xpInCurrentLevel / xpForNextLevel) * 100, 100);
        
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
                                border: none; color: white; padding: 8px 12px; border-radius: 8px;
                                font-size: 12px; font-weight: bold; cursor: pointer;
                                transition: all 0.2s; display: flex; align-items: center; gap: 4px;
                            " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                                ⚡ Улучшить
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
                                <div style="color: rgba(255,255,255,0.9); font-size: 14px;">💪 Сила • <span style="font-weight: bold; font-size: 16px;">${waifu.stats.power || 0}</span></div>
                            </div>
                            <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 12px;">
                                <div style="color: rgba(255,255,255,0.9); font-size: 14px;">🍀 Удача • <span style="font-weight: bold; font-size: 16px;">${waifu.stats.luck || 0}</span></div>
                            </div>
                            <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 12px;">
                                <div style="color: rgba(255,255,255,0.9); font-size: 14px;">🧠 Интеллект • <span style="font-weight: bold; font-size: 16px;">${waifu.stats.intellect || 0}</span></div>
                            </div>
                            <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 12px;">
                                <div style="color: rgba(255,255,255,0.9); font-size: 14px;">✨ Обаяние • <span style="font-weight: bold; font-size: 16px;">${waifu.stats.charm || 0}</span></div>
                            </div>
                            <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 12px;">
                                <div style="color: rgba(255,255,255,0.9); font-size: 14px;">🎯 Ловкость • <span style="font-weight: bold; font-size: 16px;">${waifu.dynamic.bond || 0}</span></div>
                            </div>
                            <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 12px;">
                                <div style="color: rgba(255,255,255,0.9); font-size: 14px;">⚡ Скорость • <span style="font-weight: bold; font-size: 16px;">${waifu.stats.speed || 0}</span></div>
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

// Open avatar selection
async function openAvatarSelection() {
    try {
        const response = await fetch('/api/avatars');
        if (!response.ok) {
            throw new Error('Failed to fetch avatars');
        }
        
        const data = await response.json();
        const avatars = data.avatars;
        
        // Create avatar selection modal
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
            background: rgba(0,0,0,0.8); z-index: 1000; display: flex; 
            align-items: center; justify-content: center;
        `;
        
        modal.innerHTML = `
            <div style="background: white; border-radius: 12px; padding: 20px; max-width: 90%; max-height: 80%; overflow-y: auto;">
                <h3 style="margin: 0 0 16px 0; text-align: center;">Выберите аватар</h3>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px;">
                    ${avatars.map(avatar => `
                        <div onclick="selectAvatar('${avatar.id}')" style="
                            cursor: pointer; text-align: center; padding: 8px; 
                            border-radius: 8px; border: 2px solid transparent;
                            transition: all 0.2s;
                        " onmouseover="this.style.borderColor='#4CAF50'" onmouseout="this.style.borderColor='transparent'">
                            <img src="${avatar.url}" alt="${avatar.name}" style="width: 60px; height: 60px; border-radius: 50%; object-fit: cover;" 
                                 onerror="this.src='data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20width=%2760%27%20height=%2760%27%3E%3Ctext%20x=%2750%25%27%20y=%2750%25%27%20font-size=%2712%27%20text-anchor=%27middle%27%20dy=%27.3em%27%3E👤%3C/text%3E%3C/svg%3E'">
                            <div style="font-size: 12px; margin-top: 4px;">${avatar.name}</div>
                        </div>
                    `).join('')}
                </div>
                <button onclick="closeAvatarModal()" style="
                    width: 100%; padding: 8px; background: #f44336; color: white; 
                    border: none; border-radius: 6px; cursor: pointer;
                ">Отмена</button>
            </div>
        `;
        
        document.body.appendChild(modal);
        
    } catch (error) {
        console.error('Error loading avatars:', error);
        if (window.Telegram?.WebApp?.showAlert) {
            window.Telegram.WebApp.showAlert('Ошибка загрузки аватаров');
        }
    }
}

// Select avatar
async function selectAvatar(avatarId) {
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch(`/api/avatar/select?avatar_id=${avatarId}&${new URLSearchParams({ initData })}`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error('Failed to select avatar');
        }
        
        const result = await response.json();
        
        if (window.Telegram?.WebApp?.showAlert) {
            window.Telegram.WebApp.showAlert(result.message);
        }
        
        closeAvatarModal();
        
        // Reload profile to show new avatar
        await loadProfile();
        
    } catch (error) {
        console.error('Error selecting avatar:', error);
        if (window.Telegram?.WebApp?.showAlert) {
            window.Telegram.WebApp.showAlert('Ошибка выбора аватара');
        }
    }
}

// Close avatar modal
function closeAvatarModal() {
    const modal = document.querySelector('div[style*="position: fixed"]');
    if (modal) {
        modal.remove();
    }
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
    container.innerHTML = '<p class="loading">Загрузка...</p>';
    
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch('/api/shop?' + new URLSearchParams({ initData }));
        
        if (!response.ok) {
            throw new Error('Failed to fetch shop items');
        }
        
        const data = await response.json();
        const items = data.items || [];
        
        if (items.length === 0) {
            container.innerHTML = '<p style="padding: 20px; color: #666;">В магазине пока нет товаров</p>';
            return;
        }
        
        // Render shop items
        container.innerHTML = `
            <div style="display: flex; flex-direction: column; gap: 12px; margin-top: 16px;">
                ${items.map(item => `
                    <div style="background: white; border-radius: 12px; padding: 16px;">
                        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                            <div style="font-size: 32px;">${item.emoji}</div>
                            <div style="flex: 1;">
                                <div style="font-weight: bold; font-size: 16px; margin-bottom: 4px;">${item.name}</div>
                                <div style="font-size: 12px; color: #666;">${item.description}</div>
                            </div>
                        </div>
                        <button 
                            onclick="purchaseItem('${item.id}')" 
                            style="width: 100%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; padding: 12px; font-weight: bold; cursor: pointer; font-size: 14px;">
                            Купить за ${item.price} ${item.currency === 'gold' ? '💰' : item.currency === 'gems' ? '💎' : '🔮'}
                        </button>
                    </div>
                `).join('')}
            </div>
        `;
        
    } catch (error) {
        console.error('Error loading shop items:', error);
        container.innerHTML = '<p style="color: red; padding: 20px;">Ошибка загрузки</p>';
    }
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

// Load skills tree
async function loadSkillsTree(container) {
    container.innerHTML = '<p class="loading">Загрузка...</p>';
    
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch('/api/skills?' + new URLSearchParams({ initData }));
        
        if (!response.ok) {
            throw new Error('Failed to fetch skills');
        }
        
        const data = await response.json();
        
        // Render skills tree
        let html = `
            <div style="margin-top: 16px;">
                <div style="background: white; border-radius: 12px; padding: 16px; margin-bottom: 16px; text-align: center;">
                    <div style="font-weight: bold; font-size: 18px; margin-bottom: 4px;">⭐ Очков навыков: ${data.skill_points}</div>
                    <div style="font-size: 12px; color: #666;">Получайте очки за повышение уровня</div>
                </div>
        `;
        
        // Render each category
        for (const [category, skills] of Object.entries(data.skills)) {
            const categoryNames = {
                'combat': '⚔️ Боевые',
                'economy': '💰 Экономика',
                'waifu': '👥 Вайфу'
            };
            
            html += `<div style="margin-bottom: 20px;">`;
            html += `<h3 style="font-size: 16px; margin-bottom: 12px; color: white;">${categoryNames[category] || category}</h3>`;
            
            skills.forEach(skill => {
                const currentLevel = data.user_skills[skill.id] || 0;
                const canUpgrade = data.skill_points > 0 && currentLevel < skill.max_level;
                
                html += `
                    <div style="background: white; border-radius: 12px; padding: 12px; margin-bottom: 8px;">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div style="font-size: 32px;">${skill.icon}</div>
                            <div style="flex: 1;">
                                <div style="font-weight: bold; font-size: 14px; margin-bottom: 4px;">${skill.name}</div>
                                <div style="font-size: 11px; color: #666; margin-bottom: 4px;">${skill.description}</div>
                                <div style="font-size: 12px; color: #999;">Уровень: ${currentLevel}/${skill.max_level}</div>
                            </div>
                            <button 
                                onclick="upgradeSkill('${skill.id}')"
                                ${!canUpgrade ? 'disabled' : ''}
                                style="
                                    background: ${canUpgrade ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : '#ccc'}; 
                                    color: white; 
                                    border: none; 
                                    border-radius: 8px; 
                                    padding: 8px 16px; 
                                    font-weight: bold; 
                                    cursor: ${canUpgrade ? 'pointer' : 'not-allowed'}; 
                                    font-size: 12px;
                                    opacity: ${canUpgrade ? '1' : '0.6'};
                                ">
                                +1
                            </button>
                        </div>
                    </div>
                `;
            });
            
            html += `</div>`;
        }
        
        html += `</div>`;
        
        container.innerHTML = html;
        
    } catch (error) {
        console.error('Error loading skills tree:', error);
        container.innerHTML = '<p style="color: red; padding: 20px;">Ошибка загрузки</p>';
    }
}

// Upgrade skill
async function upgradeSkill(skillId) {
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch(`/api/skills/upgrade?skill_id=${skillId}&${new URLSearchParams({ initData })}`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to upgrade skill');
        }
        
        const result = await response.json();
        
        if (window.Telegram?.WebApp?.showAlert) {
            window.Telegram.WebApp.showAlert(result.message);
        }
        
        // Reload skills tree
        const viewContent = document.getElementById('view-content');
        if (currentView === 'skills') {
            loadSkillsTree(viewContent);
        }
        
    } catch (error) {
        console.error('Error upgrading skill:', error);
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
                ${quests.map(quest => `
                    <div style="background: white; border-radius: 12px; padding: 16px; margin-bottom: 12px; ${quest.completed ? 'border: 2px solid #4CAF50;' : ''}">
                        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                            <div style="font-size: 32px;">${quest.icon}</div>
                            <div style="flex: 1;">
                                <div style="font-weight: bold; font-size: 16px; margin-bottom: 4px;">${quest.name}</div>
                                <div style="font-size: 12px; color: #666;">${quest.description}</div>
                            </div>
                            ${quest.completed ? '<div style="font-size: 24px;">✅</div>' : ''}
                        </div>
                        <div style="background: #e0e0e0; border-radius: 8px; height: 8px; margin-bottom: 8px; overflow: hidden;">
                            <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); height: 100%; width: ${Math.min(100, (quest.progress / quest.target) * 100)}%; transition: width 0.3s;"></div>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #666;">
                            <span>Прогресс: ${quest.progress}/${quest.target}</span>
                            <span>🎁 ${quest.reward_gold} 💰 + ${quest.reward_xp} ⭐</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
    } catch (error) {
        console.error('Error loading quests:', error);
        container.innerHTML = '<p style="color: red; padding: 20px;">Ошибка загрузки</p>';
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

// Calculate XP progress for display
function calculateXPProgress(currentXP, currentLevel) {
    // Calculate XP needed for current level
    let xpNeededForCurrent = 0;
    for (let i = 1; i < currentLevel; i++) {
        xpNeededForCurrent += Math.floor(100 * Math.pow(i, 1.1));
    }
    
    // Calculate XP needed for next level
    const xpForNextLevel = Math.floor(100 * Math.pow(currentLevel, 1.1));
    
    // XP in current level
    const xpInLevel = currentXP - xpNeededForCurrent;
    const xpNeeded = xpForNextLevel;
    
    const percent = Math.min(100, (xpInLevel / xpNeeded) * 100);
    
    return {
        current: Math.floor(xpInLevel),
        next: Math.floor(xpNeeded),
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
        
        // Update avatar (use user's selected avatar or default)
        const avatarNum = profileData.avatar || 1;
        const avatarUrl = `https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/avatars/avatar_${avatarNum}.png`;
        const avatarElement = document.getElementById('user-avatar');
        avatarElement.style.backgroundImage = `url(${avatarUrl})`;
        avatarElement.style.backgroundSize = 'cover';
        avatarElement.style.backgroundPosition = 'center';
        avatarElement.textContent = '';
        
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
        
        // Calculate XP progress correctly
        const currentXP = profileData.xp || 0;
        
        // Calculate XP needed for current level
        let xpNeededForCurrent = 0;
        for (let i = 1; i < currentLevel; i++) {
            xpNeededForCurrent += Math.floor(100 * Math.pow(i, 1.1));
        }
        
        // Calculate XP needed for next level
        const xpForNextLevel = Math.floor(100 * Math.pow(currentLevel, 1.1));
        
        // XP in current level
        const xpInLevel = currentXP - xpNeededForCurrent;
        const xpNeeded = xpForNextLevel;
        
        const xpPercent = Math.min(100, (xpInLevel / xpNeeded) * 100);
        
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
                <button onclick="loadSkills(document.getElementById('other-views'))" style="
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
    const { skills_tree, category_progress } = data;
    
    container.innerHTML = `
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 20px; border-radius: 16px; margin-bottom: 20px; text-align: center;">
            <h2 style="margin: 0 0 8px 0; font-size: 24px;">🧬 Прокачка</h2>
            <div style="font-size: 14px; opacity: 0.9;">
                Очки навыков: <span style="font-weight: bold;">${skillsData.skill_points || 0}</span>
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
            ${renderSkillCategory('account', skills_tree.account)}
        </div>
    `;
    
    // Set active tab
    document.getElementById('tab-account').style.opacity = '1';
    document.getElementById('tab-passive').style.opacity = '0.7';
    document.getElementById('tab-training').style.opacity = '0.7';
}

// Show skill category
function showSkillCategory(category) {
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
            <div style="display: flex; align-items: center; margin-bottom: 12px;">
                <div style="font-size: 24px; margin-right: 12px;">${skill.icon}</div>
                <div style="flex: 1;">
                    <h3 style="margin: 0 0 4px 0; font-size: 16px; color: #333;">${skill.name}</h3>
                    <div style="font-size: 12px; color: #666;">${skill.description}</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 14px; font-weight: bold; color: #333;">
                        ${skill.current_level}/${skill.max_level}
                    </div>
                    ${isLocked ? '<div style="font-size: 10px; color: #999;">Заблокирован</div>' : ''}
                </div>
            </div>
            
            <!-- Progress Bar -->
            <div style="background: #f0f0f0; border-radius: 8px; height: 6px; margin-bottom: 12px;">
                <div style="
                    background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                    height: 100%; border-radius: 8px; width: ${(skill.current_level / skill.max_level) * 100}%;
                    transition: width 0.3s;
                "></div>
            </div>
            
            <!-- Effects -->
            ${skill.current_level > 0 ? `
                <div style="background: #f8f9fa; border-radius: 8px; padding: 8px; margin-bottom: 12px;">
                    <div style="font-size: 12px; color: #666; margin-bottom: 4px;">Текущие эффекты:</div>
                    ${Object.entries(skill.effects[skill.current_level] || {}).map(([key, value]) => 
                        `<div style="font-size: 11px; color: #333;">${key}: +${(value * 100).toFixed(0)}%</div>`
                    ).join('')}
                </div>
            ` : ''}
            
            <!-- Upgrade Button -->
            ${canUpgrade ? `
                <button onclick="upgradeSkill('${skill.skill_id}')" style="
                    background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                    color: white; border: none; padding: 10px 16px; border-radius: 8px;
                    font-size: 14px; font-weight: bold; cursor: pointer; width: 100%;
                    transition: all 0.2s;
                " onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">
                    ⚡ Улучшить (${skill.next_level_cost} очков)
                </button>
            ` : isMaxLevel ? `
                <div style="
                    background: #e8f5e8; color: #4CAF50; padding: 10px 16px; border-radius: 8px;
                    text-align: center; font-size: 14px; font-weight: bold;
                ">
                    ✅ Максимальный уровень
                </div>
            ` : isLocked ? `
                <div style="
                    background: #f5f5f5; color: #999; padding: 10px 16px; border-radius: 8px;
                    text-align: center; font-size: 14px;
                ">
                    🔒 Требуется ${skill.unlock_requirement} очков в категории
                </div>
            ` : `
                <div style="
                    background: #f5f5f5; color: #999; padding: 10px 16px; border-radius: 8px;
                    text-align: center; font-size: 14px;
                ">
                    Недостаточно очков навыков
                </div>
            `}
        </div>
    `;
}

// Upgrade skill
async function upgradeSkill(skillId) {
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch('/api/skills/upgrade', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                skill_id: skillId,
                initData: initData
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to upgrade skill');
        }
        
        const result = await response.json();
        
        // Show success message
        if (window.Telegram?.WebApp?.showAlert) {
            window.Telegram.WebApp.showAlert(`✅ Навык улучшен до уровня ${result.new_level}!`);
        }
        
        // Reload skills page
        loadSkills(document.getElementById('other-views'));
        
    } catch (error) {
        console.error('Error upgrading skill:', error);
        if (window.Telegram?.WebApp?.showAlert) {
            window.Telegram.WebApp.showAlert('❌ Ошибка: ' + error.message);
        }
    }
}
