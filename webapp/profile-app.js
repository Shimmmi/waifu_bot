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
            'waifus': { title: '🎴 Мои вайфу', content: 'loadWaifuList()' },
            'select-waifu': { title: '🎯 Выбрать активную вайфу', content: 'loadSelectWaifu()' },
            'shop': { title: '🏪 Магазин', content: 'loadShopItems()' },
            'clan': { title: '🏰 Клан', content: 'loadClanInfo()' },
            'quests': { title: '📅 Ежедневные задания', content: 'loadQuests()' },
            'skills': { title: '🧬 Прокачка навыков', content: 'loadSkillsTree()' },
            'settings': { title: '⚙️ Настройки профиля', content: 'loadSettings()' }
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
                loadSkillsTree(viewContent);
            } else if (view === 'quests') {
                loadQuests(viewContent);
            } else if (view === 'clan') {
                loadClanInfo(viewContent);
            } else if (view === 'settings') {
                loadSettings(viewContent);
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

        // Render waifu list (1 column, N rows)
        container.innerHTML = `
            <div style="display: flex; flex-direction: column; gap: 12px; margin-top: 16px;">
                ${waifuList.map(waifu => `
                    <div onclick="openWaifuDetail('${waifu.id}')" style="
                        background: white; border-radius: 12px; padding: 16px; cursor: pointer; 
                        transition: transform 0.2s; position: relative; display: flex; align-items: center;
                        ${waifu.is_active ? 'border: 3px solid #4CAF50;' : 'border: 1px solid #e0e0e0;'}
                    " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                        ${waifu.is_active ? '<div style="position: absolute; top: 8px; right: 8px; background: #4CAF50; color: white; padding: 4px 8px; border-radius: 12px; font-size: 10px;">✓ АКТИВНА</div>' : ''}
                        <img src="${waifu.image_url}" alt="${waifu.name}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 8px; margin-right: 16px;" onerror="this.src='data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20width=%2760%27%20height=%2760%27%3E%3Ctext%20x=%2750%25%27%20y=%2750%25%27%20font-size=%2712%27%20text-anchor=%27middle%27%20dy=%27.3em%27%3E🎭%3C/text%3E%3C/svg%3E'">
                        <div style="flex: 1;">
                            <div style="font-weight: bold; font-size: 16px; margin-bottom: 4px;">${waifu.name}</div>
                            <div style="font-size: 14px; color: #666; margin-bottom: 4px;">Уровень ${waifu.level} • 💪${waifu.power}</div>
                            <div style="font-size: 12px; color: #999;">${waifu.race} • ${waifu.profession}</div>
                        </div>
                        <div style="color: #999; font-size: 20px;">→</div>
                    </div>
                `).join('')}
            </div>
        `;

    } catch (error) {
        console.error('Error loading waifu list:', error);
        container.innerHTML = '<p style="color: red; padding: 20px;">Ошибка загрузки</p>';
    }
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
                <h2 style="margin: 0 0 20px 0; font-size: 20px; text-align: center;">🎯 Выбрать активную вайфу</h2>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;">
                    ${waifuList.map(waifu => `
                        <div onclick="selectActiveWaifuFromModal('${waifu.id}')" style="cursor: pointer; position: relative; border: ${waifu.is_active ? '3px solid #4CAF50' : '2px solid #e0e0e0'}; border-radius: 12px; padding: 8px; transition: transform 0.2s;">
                            ${waifu.is_active ? '<div style="position: absolute; top: 4px; right: 4px; background: #4CAF50; color: white; padding: 2px 4px; border-radius: 6px; font-size: 10px; z-index: 1;">✓</div>' : ''}
                            <img src="${waifu.image_url}" alt="${waifu.name}" style="width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: 8px; margin-bottom: 6px;" onerror="this.src='data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20width=%27100%27%20height=%27100%27%3E%3Ctext%20x=%2750%25%27%20y=%2750%25%27%20font-size=%2712%27%20text-anchor=%27middle%27%20dy=%27.3em%27%3E🎭%3C/text%3E%3C/svg%3E'">
                            <div style="font-size: 11px; font-weight: bold; text-align: center; margin-bottom: 2px;">${waifu.name}</div>
                            <div style="font-size: 9px; color: #666; text-align: center;">Ур.${waifu.level} • 💪${waifu.power}</div>
                        </div>
                    `).join('')}
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
            
            if (window.Telegram?.WebApp?.showAlert) {
                window.Telegram.WebApp.showAlert('✅ Вайфу установлена как активная!');
            }
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
        
        // Calculate total power
        const power = (waifu.stats.strength || 0) + 
                     (waifu.stats.luck || 0) + 
                     (waifu.stats.intelligence || 0) + 
                     (waifu.stats.charisma || 0) + 
                     (waifu.stats.bond || 0) + 
                     (waifu.stats.speed || 0);
        
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
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; max-width: 500px; width: 100%; max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">
                <!-- Header -->
                <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 20px 20px 0 0; backdrop-filter: blur(10px);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <h2 style="color: white; margin: 0; font-size: 24px;">${waifu.name}</h2>
                        <span style="background: rgba(255,255,255,0.2); color: white; padding: 6px 12px; border-radius: 12px; font-size: 14px;">Ур.${waifu.level}</span>
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
                                <div style="color: rgba(255,255,255,0.7); font-size: 12px; margin-bottom: 4px;">💪 Сила</div>
                                <div style="color: white; font-size: 18px; font-weight: bold;">${waifu.stats.strength || 0}</div>
                            </div>
                            <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 12px;">
                                <div style="color: rgba(255,255,255,0.7); font-size: 12px; margin-bottom: 4px;">🍀 Удача</div>
                                <div style="color: white; font-size: 18px; font-weight: bold;">${waifu.stats.luck || 0}</div>
                            </div>
                            <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 12px;">
                                <div style="color: rgba(255,255,255,0.7); font-size: 12px; margin-bottom: 4px;">🧠 Интеллект</div>
                                <div style="color: white; font-size: 18px; font-weight: bold;">${waifu.stats.intelligence || 0}</div>
                            </div>
                            <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 12px;">
                                <div style="color: rgba(255,255,255,0.7); font-size: 12px; margin-bottom: 4px;">✨ Обаяние</div>
                                <div style="color: white; font-size: 18px; font-weight: bold;">${waifu.stats.charisma || 0}</div>
                            </div>
                            <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 12px;">
                                <div style="color: rgba(255,255,255,0.7); font-size: 12px; margin-bottom: 4px;">💞 Привязанность</div>
                                <div style="color: white; font-size: 18px; font-weight: bold;">${waifu.stats.bond || 0}</div>
                            </div>
                            <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 12px;">
                                <div style="color: rgba(255,255,255,0.7); font-size: 12px; margin-bottom: 4px;">⚡ Скорость</div>
                                <div style="color: white; font-size: 18px; font-weight: bold;">${waifu.stats.speed || 0}</div>
                            </div>
                        </div>
                        
                        <!-- Dynamic Stats -->
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 16px;">
                            <div style="background: rgba(255,255,255,0.05); padding: 8px; border-radius: 8px; text-align: center;">
                                <div style="color: rgba(255,255,255,0.7); font-size: 11px;">😊 Настроение</div>
                                <div style="color: white; font-size: 14px; font-weight: bold;">${waifu.dynamic.mood || 0}</div>
                            </div>
                            <div style="background: rgba(255,255,255,0.05); padding: 8px; border-radius: 8px; text-align: center;">
                                <div style="color: rgba(255,255,255,0.7); font-size: 11px;">❤️ Лояльность</div>
                                <div style="color: white; font-size: 14px; font-weight: bold;">${waifu.dynamic.loyalty || 0}</div>
                            </div>
                            <div style="background: rgba(255,255,255,0.05); padding: 8px; border-radius: 8px; text-align: center;">
                                <div style="color: rgba(255,255,255,0.7); font-size: 11px;">⚡ Энергия</div>
                                <div style="color: white; font-size: 14px; font-weight: bold;">${waifu.dynamic.energy || 0}</div>
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
                    
                    <!-- Action Buttons -->
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 16px;">
                        <button id="modal-set-active-btn" style="background: ${waifu.is_active ? '#28a745' : '#6c757d'}; color: white; border: none; padding: 14px; border-radius: 12px; font-size: 14px; font-weight: bold; cursor: pointer; transition: all 0.2s;">
                            ${waifu.is_active ? '✅ Активна' : '⭐ Сделать активной'}
                        </button>
                        <button id="modal-toggle-favorite-btn" style="background: ${waifu.is_favorite ? '#28a745' : '#dc3545'}; color: white; border: none; padding: 14px; border-radius: 12px; font-size: 14px; font-weight: bold; cursor: pointer; transition: all 0.2s;">
                            ${waifu.is_favorite ? '💚 В избранном' : '❤️ В избранное'}
                        </button>
                    </div>
                    
                    <button id="modal-close-btn" style="background: rgba(255,255,255,0.2); color: white; border: none; padding: 14px; border-radius: 12px; font-size: 14px; font-weight: bold; cursor: pointer; margin-top: 12px; width: 100%; transition: all 0.2s;">
                        ← Назад
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Add event listeners
        const closeBtn = modal.querySelector('#modal-close-btn');
        const setActiveBtn = modal.querySelector('#modal-set-active-btn');
        const toggleFavoriteBtn = modal.querySelector('#modal-toggle-favorite-btn');
        
        // Close modal
        closeBtn.addEventListener('click', () => {
            modal.remove();
            // Reload current view
            if (currentView === 'profile') {
                loadProfile();
            } else if (currentView === 'waifus') {
                const viewContent = document.getElementById('view-content');
                loadWaifuList(viewContent);
            } else if (currentView === 'select-waifu') {
                const viewContent = document.getElementById('view-content');
                loadSelectWaifu(viewContent);
            }
        });
        
        // Set active
        setActiveBtn.addEventListener('click', async () => {
            try {
                const initData = window.Telegram?.WebApp?.initData || '';
                const response = await fetch(`/api/waifu/${waifuId}/set-active?${new URLSearchParams({ initData })}`, {
                    method: 'POST'
                });
                
                if (response.ok) {
                    setActiveBtn.style.background = '#28a745';
                    setActiveBtn.innerHTML = '✅ Активна';
                    
                    if (window.Telegram?.WebApp?.showAlert) {
                        window.Telegram.WebApp.showAlert('✅ Вайфу установлена как активная!');
                    }
                    
                    // Close modal and reload
                    setTimeout(() => {
                        modal.remove();
                        if (currentView === 'profile') {
                            loadProfile();
                        } else if (currentView === 'waifus') {
                            const viewContent = document.getElementById('view-content');
                            loadWaifuList(viewContent);
                        } else if (currentView === 'select-waifu') {
                            const viewContent = document.getElementById('view-content');
                            loadSelectWaifu(viewContent);
                        }
                    }, 500);
                } else {
                    const errorData = await response.json();
                    if (window.Telegram?.WebApp?.showAlert) {
                        window.Telegram.WebApp.showAlert('❌ Ошибка: ' + (errorData.detail || 'Неизвестная ошибка'));
                    }
                }
            } catch (error) {
                console.error('Error setting active:', error);
                if (window.Telegram?.WebApp?.showAlert) {
                    window.Telegram.WebApp.showAlert('❌ Ошибка: ' + error.message);
                }
            }
        });
        
        // Toggle favorite
        toggleFavoriteBtn.addEventListener('click', async () => {
            try {
                const initData = window.Telegram?.WebApp?.initData || '';
                const response = await fetch(`/api/waifu/${waifuId}/toggle-favorite?${new URLSearchParams({ initData })}`, {
                    method: 'POST'
                });
                
                if (response.ok) {
                    const data = await response.json();
                    if (data.is_favorite) {
                        toggleFavoriteBtn.style.background = '#28a745';
                        toggleFavoriteBtn.innerHTML = '💚 В избранном';
                    } else {
                        toggleFavoriteBtn.style.background = '#dc3545';
                        toggleFavoriteBtn.innerHTML = '❤️ В избранное';
                    }
                    
                    if (window.Telegram?.WebApp?.showAlert) {
                        window.Telegram.WebApp.showAlert('✅ ' + data.message);
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
        });
        
        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeBtn.click();
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
        'ES': '🇪🇸', 'KR': '🇰🇷', 'BR': '🇧🇷', 'IN': '🇮🇳'
    };
    return flagMap[countryCode] || countryCode;
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
        document.getElementById('token-value').textContent = profileData.tokens || 0;
        
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
            <button class="change-waifu-btn" onclick="openSelectActiveWaifuModal()">Выбрать вайфу</button>
        `;
        return;
    }
    
    const waifu = profileData.active_waifu;
    const power = calculatePower(waifu);
    
    activeWaifuCard.innerHTML = `
        <div onclick="openSelectActiveWaifuModal()" style="cursor: pointer;">
            <img src="${waifu.image_url}" alt="${waifu.name}" class="waifu-image" onerror="this.onerror=null; this.src='data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20width=%27100%27%20height=%27100%27%3E%3Ctext%20x=%2750%25%27%20y=%2750%25%27%20font-size=%2714%27%20text-anchor=%27middle%27%20dy=%27.3em%27%3E🎭%3C/text%3E%3C/svg%3E'">
            <div class="waifu-name">${waifu.name}</div>
            <div class="waifu-info">Уровень ${waifu.level} • 💪${power}</div>
            <button class="change-waifu-btn" onclick="event.stopPropagation(); openSelectActiveWaifuModal()">Сменить вайфу</button>
        </div>
    `;
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
