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
              'waifus': { title: '🎴 Мои вайфу', content: 'loadWaifuList()' },
              'shop': { title: '🏪 Магазин', content: 'loadShopItems()' },
              'clan': { title: '🏰 Клан', content: 'loadClanInfo()' },
              'quests': { title: '📅 Ежедневные задания', content: 'loadQuests()' },
              'skills': { title: '🧬 Прокачка навыков', content: 'loadSkillsTree()' },
              'settings': { title: '⚙️ Настройки профиля', content: 'loadSettings()' }
          };
          
          if (views[view]) {
              viewTitle.textContent = views[view].title;
              
              // Special handling for different views
              if (view === 'waifus') {
                  loadWaifuList(viewContent);
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
        
        currentView = view;
    }
}

// Load waifu list
async function loadWaifuList(container) {
    container.innerHTML = '<p class="loading">Загрузка...</p>';
    
    try {
        const initData = window.Telegram?.WebApp?.initData || '';
        const response = await fetch('/api/waifus?' + new URLSearchParams({ initData }));
        
        if (!response.ok) {
            throw new Error('Failed to fetch waifus');
        }
        
        waifuList = await response.json();
        
        if (waifuList.length === 0) {
            container.innerHTML = '<p style="padding: 20px; color: #666;">У вас пока нет вайфу</p>';
            return;
        }
        
        // Render waifu grid
        container.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-top: 16px;">
                ${waifuList.map(waifu => `
                    <div class="waifu-card" onclick="selectWaifu('${waifu.id}')" style="background: white; border-radius: 12px; padding: 12px; cursor: pointer; transition: transform 0.2s; ${waifu.is_active ? 'border: 3px solid #4CAF50;' : ''}">
                        ${waifu.is_active ? '<div style="position: absolute; top: 4px; right: 4px; background: #4CAF50; color: white; padding: 2px 6px; border-radius: 8px; font-size: 10px;">✓ АКТИВНА</div>' : ''}
                        <img src="${waifu.image_url}" alt="${waifu.name}" style="width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: 8px; margin-bottom: 8px;" onerror="this.src='data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20width=%27100%27%20height=%27100%27%3E%3Ctext%20x=%2750%25%27%20y=%2750%25%27%20font-size=%2712%27%20text-anchor=%27middle%27%20dy=%27.3em%27%3E🎭%3C/text%3E%3C/svg%3E'">
                        <div style="font-weight: bold; font-size: 14px; margin-bottom: 4px;">${waifu.name}</div>
                        <div style="font-size: 12px; color: #666;">Ур.${waifu.level} • 💪${waifu.power}</div>
                    </div>
                `).join('')}
            </div>
        `;
        
    } catch (error) {
        console.error('Error loading waifu list:', error);
        container.innerHTML = '<p style="color: red; padding: 20px;">Ошибка загрузки</p>';
    }
}

// Select waifu to make active
async function selectWaifu(waifuId) {
    try {
        const response = await fetch(`/api/waifu/${waifuId}/set-active`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error('Failed to set active waifu');
        }
        
        if (window.Telegram?.WebApp?.showAlert) {
            window.Telegram.WebApp.showAlert('✅ Вайфу установлена как активная!');
        }
        
        // Reload profile to update active waifu
        await loadProfile();
        
        // Return to profile
        navigateTo('profile');
        
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
