# 📱 Настройка WebApp для карточек вайфу

## 🎯 Обзор

Данная инструкция поможет вам настроить WebApp для отображения карточек вайфу в Telegram боте с использованием вашего домена на Render.

## 🏗️ Архитектура

```
Telegram Bot (Python) → WebApp (HTML/JS) → Render (ваш домен)
```

## 📋 Требования

- ✅ Домен подключен к Render
- ✅ Telegram бот работает
- ✅ Базовые знания HTML/CSS/JavaScript

## 🚀 Пошаговая настройка

### Шаг 1: Подготовка структуры проекта

Создайте следующую структуру файлов:

```
waifu_bot/
├── src/
│   └── bot/
│       └── handlers/
│           └── menu.py (уже есть)
├── webapp/
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   └── waifu-card.html
├── static/
│   ├── waifu-card.html
│   ├── waifu-card.css
│   └── waifu-card.js
└── requirements.txt
```

### Шаг 2: Создание WebApp файлов

#### 2.1 Создайте `webapp/index.html`

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Waifu Bot WebApp</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <h1>🎭 Waifu Bot</h1>
        <p>Добро пожаловать в WebApp!</p>
        
        <!-- Контейнер для карточки вайфу -->
        <div id="waifu-card-container">
            <p>Загрузка карточки вайфу...</p>
        </div>
        
        <div class="actions">
            <button id="close-btn" class="btn btn-secondary">Закрыть</button>
        </div>
    </div>
    
    <script src="script.js"></script>
</body>
</html>
```

#### 2.2 Создайте `webapp/style.css`

```css
/* Базовые стили */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--tg-theme-bg-color, #ffffff);
    color: var(--tg-theme-text-color, #000000);
    line-height: 1.6;
    padding: 20px;
}

.container {
    max-width: 400px;
    margin: 0 auto;
    background: var(--tg-theme-secondary-bg-color, #f8f9fa);
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

h1 {
    text-align: center;
    margin-bottom: 20px;
    color: var(--tg-theme-text-color, #000000);
}

/* Карточка вайфу */
.waifu-card {
    background: var(--tg-theme-bg-color, #ffffff);
    border-radius: 12px;
    padding: 20px;
    margin: 20px 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.waifu-header {
    display: flex;
    align-items: center;
    margin-bottom: 15px;
}

.waifu-avatar {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    margin-right: 15px;
    color: white;
}

.waifu-info h2 {
    margin: 0;
    font-size: 18px;
    color: var(--tg-theme-text-color, #000000);
}

.waifu-rarity {
    font-size: 14px;
    margin-top: 4px;
}

.rarity-common { color: #6c757d; }
.rarity-uncommon { color: #28a745; }
.rarity-rare { color: #007bff; }
.rarity-epic { color: #6f42c1; }
.rarity-legendary { color: #fd7e14; }

.waifu-stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin: 15px 0;
}

.stat-item {
    display: flex;
    justify-content: space-between;
    padding: 8px 12px;
    background: var(--tg-theme-secondary-bg-color, #f8f9fa);
    border-radius: 6px;
    font-size: 14px;
}

.stat-label {
    color: var(--tg-theme-hint-color, #6c757d);
}

.stat-value {
    font-weight: 600;
    color: var(--tg-theme-text-color, #000000);
}

.waifu-details {
    margin-top: 15px;
}

.detail-row {
    display: flex;
    justify-content: space-between;
    padding: 6px 0;
    border-bottom: 1px solid var(--tg-theme-secondary-bg-color, #f8f9fa);
    font-size: 14px;
}

.detail-row:last-child {
    border-bottom: none;
}

.detail-label {
    color: var(--tg-theme-hint-color, #6c757d);
}

.detail-value {
    color: var(--tg-theme-text-color, #000000);
}

/* Кнопки */
.actions {
    display: flex;
    gap: 10px;
    margin-top: 20px;
}

.btn {
    flex: 1;
    padding: 12px 20px;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
}

.btn-primary {
    background: var(--tg-theme-button-color, #007bff);
    color: var(--tg-theme-button-text-color, #ffffff);
}

.btn-secondary {
    background: var(--tg-theme-secondary-bg-color, #f8f9fa);
    color: var(--tg-theme-text-color, #000000);
}

.btn:hover {
    opacity: 0.9;
    transform: translateY(-1px);
}

/* Анимации */
.loading {
    text-align: center;
    padding: 40px;
    color: var(--tg-theme-hint-color, #6c757d);
}

.fade-in {
    animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Адаптивность */
@media (max-width: 480px) {
    .container {
        margin: 10px;
        padding: 15px;
    }
    
    .waifu-stats {
        grid-template-columns: 1fr;
    }
}
```

#### 2.3 Создайте `webapp/script.js`

```javascript
// Инициализация Telegram WebApp
const tg = window.Telegram.WebApp;

// Инициализация WebApp
tg.ready();
tg.expand();

// Получение данных вайфу из URL параметров
function getWaifuId() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('waifu_id');
}

// Получение данных вайфу с сервера
async function fetchWaifuData(waifuId) {
    try {
        const response = await fetch(`/api/waifu/${waifuId}`);
        if (!response.ok) {
            throw new Error('Вайфу не найдена');
        }
        return await response.json();
    } catch (error) {
        console.error('Ошибка загрузки данных вайфу:', error);
        throw error;
    }
}

// Отображение карточки вайфу
function renderWaifuCard(waifu) {
    const container = document.getElementById('waifu-card-container');
    
    const cardHTML = `
        <div class="waifu-card fade-in">
            <div class="waifu-header">
                <div class="waifu-avatar">
                    ${getWaifuEmoji(waifu.race)}
                </div>
                <div class="waifu-info">
                    <h2>${waifu.name}</h2>
                    <div class="waifu-rarity rarity-${waifu.rarity.toLowerCase()}">
                        ${getRarityIcon(waifu.rarity)} ${waifu.rarity}
                    </div>
                </div>
            </div>
            
            <div class="waifu-stats">
                <div class="stat-item">
                    <span class="stat-label">💪 Сила</span>
                    <span class="stat-value">${waifu.stats.power}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">💖 Очарование</span>
                    <span class="stat-value">${waifu.stats.charm}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">🍀 Удача</span>
                    <span class="stat-value">${waifu.stats.luck}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">❤️ Привязанность</span>
                    <span class="stat-value">${waifu.stats.affection}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">🧠 Интеллект</span>
                    <span class="stat-value">${waifu.stats.intellect}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">⚡ Скорость</span>
                    <span class="stat-value">${waifu.stats.speed}</span>
                </div>
            </div>
            
            <div class="waifu-details">
                <div class="detail-row">
                    <span class="detail-label">🏷️ Раса</span>
                    <span class="detail-value">${waifu.race}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">💼 Профессия</span>
                    <span class="detail-value">${waifu.profession}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">🌍 Национальность</span>
                    <span class="detail-value">${waifu.nationality}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">⭐ Уровень</span>
                    <span class="detail-value">${waifu.level}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">✨ XP</span>
                    <span class="detail-value">${waifu.xp}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">💪 Общая мощь</span>
                    <span class="detail-value">${calculatePower(waifu)}</span>
                </div>
            </div>
            
            <div class="waifu-details" style="margin-top: 15px;">
                <div class="detail-row">
                    <span class="detail-label">😊 Настроение</span>
                    <span class="detail-value">${waifu.dynamic.mood}%</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">💝 Лояльность</span>
                    <span class="detail-value">${waifu.dynamic.loyalty}%</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">⚡ Энергия</span>
                    <span class="detail-value">${waifu.dynamic.energy}%</span>
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = cardHTML;
}

// Получение эмодзи для расы
function getWaifuEmoji(race) {
    const raceEmojis = {
        'Human': '👤',
        'Elf': '🧝',
        'Demon': '👹',
        'Angel': '👼',
        'Beastkin': '🐱',
        'Cyborg': '🤖',
        'Fairy': '🧚',
        'Vampire': '🧛',
        'Dragon': '🐲',
        'Spirit': '👻'
    };
    return raceEmojis[race] || '👤';
}

// Получение иконки редкости
function getRarityIcon(rarity) {
    const rarityIcons = {
        'Common': '⚪',
        'Uncommon': '🟢',
        'Rare': '🔵',
        'Epic': '🟣',
        'Legendary': '🟡'
    };
    return rarityIcons[rarity] || '⚪';
}

// Расчет общей мощи
function calculatePower(waifu) {
    const basePower = Object.values(waifu.stats).reduce((sum, stat) => sum + stat, 0);
    const moodBonus = waifu.dynamic.mood * 0.1;
    const loyaltyBonus = waifu.dynamic.loyalty * 0.05;
    const levelBonus = waifu.level * 2;
    return Math.round(basePower + moodBonus + loyaltyBonus + levelBonus);
}

// Обработка ошибок
function showError(message) {
    const container = document.getElementById('waifu-card-container');
    container.innerHTML = `
        <div class="waifu-card">
            <h2>❌ Ошибка</h2>
            <p>${message}</p>
        </div>
    `;
}

// Инициализация приложения
async function initApp() {
    try {
        const waifuId = getWaifuId();
        if (!waifuId) {
            throw new Error('ID вайфу не указан');
        }
        
        const waifu = await fetchWaifuData(waifuId);
        renderWaifuCard(waifu);
        
        // Настройка кнопки закрытия
        document.getElementById('close-btn').addEventListener('click', () => {
            tg.close();
        });
        
    } catch (error) {
        showError(error.message);
    }
}

// Запуск приложения
document.addEventListener('DOMContentLoaded', initApp);
```

### Шаг 3: Создание API endpoint

#### 3.1 Создайте `src/bot/api/waifu_api.py`

```python
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from bot.db import get_session
from bot.models import Waifu
from bot.services.waifu_generator import calculate_waifu_power

router = APIRouter()

@router.get("/api/waifu/{waifu_id}")
async def get_waifu_card(waifu_id: str, db: Session = Depends(get_session)) -> Dict[str, Any]:
    """Получение данных вайфу для WebApp"""
    try:
        # Получаем вайфу из базы данных
        waifu = db.query(Waifu).filter(Waifu.id == waifu_id).first()
        
        if not waifu:
            raise HTTPException(status_code=404, detail="Вайфу не найдена")
        
        # Формируем ответ
        waifu_data = {
            "id": waifu.id,
            "name": waifu.name,
            "rarity": waifu.rarity,
            "race": waifu.race,
            "profession": waifu.profession,
            "nationality": waifu.nationality,
            "level": waifu.level,
            "xp": waifu.xp,
            "stats": waifu.stats,
            "dynamic": waifu.dynamic,
            "tags": waifu.tags,
            "created_at": waifu.created_at.isoformat()
        }
        
        return waifu_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")
```

### Шаг 4: Настройка FastAPI сервера

#### 4.1 Создайте `src/bot/api_server.py`

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from bot.api.waifu_api import router as waifu_router

app = FastAPI(title="Waifu Bot API", version="1.0.0")

# Подключение API роутера
app.include_router(waifu_router)

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")

# Главная страница WebApp
@app.get("/")
async def read_root():
    return FileResponse("static/waifu-card.html")

# Страница карточки вайфу
@app.get("/waifu-card/{waifu_id}")
async def waifu_card_page(waifu_id: str):
    return FileResponse("static/waifu-card.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Шаг 5: Обновление requirements.txt

Добавьте в `requirements.txt`:

```txt
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
```

### Шаг 6: Настройка Render

#### 6.1 Создайте `render.yaml`

```yaml
services:
  - type: web
    name: waifu-bot-webapp
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python -m uvicorn src.bot.api_server:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: BOT_TOKEN
        sync: false
    healthCheckPath: /
```

#### 6.2 Настройка в Render Dashboard

1. **Подключите репозиторий:**
   - Войдите в Render Dashboard
   - Нажмите "New +" → "Web Service"
   - Подключите ваш GitHub репозиторий

2. **Настройте сервис:**
   - **Name:** `waifu-bot-webapp`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python -m uvicorn src.bot.api_server:app --host 0.0.0.0 --port $PORT`

3. **Настройте переменные окружения:**
   - `DATABASE_URL` - URL вашей базы данных
   - `BOT_TOKEN` - токен вашего бота

4. **Настройте домен:**
   - В разделе "Custom Domains" добавьте ваш домен
   - Настройте SSL сертификат

### Шаг 7: Обновление бота

#### 7.1 Обновите `src/bot/handlers/menu.py`

Замените URL в WebApp кнопках:

```python
# В функции handle_waifu_details_menu_callback
InlineKeyboardButton(
    text=f"🖼️ {waifu.name} - Ур.{waifu.level} {rarity_icon} 💪{power}",
    web_app=WebAppInfo(url=f"https://ваш-домен.com/waifu-card/{waifu.id}")
)
```

#### 7.2 Обновите `src/bot/main.py`

```python
import asyncio
from fastapi import FastAPI
import uvicorn
from multiprocessing import Process

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import get_settings
from bot.handlers.start import router as start_router
from bot.handlers.profile import router as profile_router
from bot.handlers.daily import router as daily_router
from bot.handlers.message_handler import router as message_router
from bot.handlers.menu import router as menu_router
from bot.handlers.waifu import router as waifu_router
from bot.handlers.debug import router as debug_router
from bot.handlers.webapp import router as webapp_router
from bot.api_server import app as api_app

async def run_bot():
    settings = get_settings()
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Include routers
    dp.include_router(start_router)
    dp.include_router(profile_router)
    dp.include_router(daily_router)
    dp.include_router(message_router)
    dp.include_router(menu_router)
    dp.include_router(waifu_router)
    dp.include_router(debug_router)
    dp.include_router(webapp_router)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

def run_api():
    uvicorn.run(api_app, host="0.0.0.0", port=8000)

async def main():
    # Запуск API сервера в отдельном процессе
    api_process = Process(target=run_api)
    api_process.start()
    
    # Запуск бота
    await run_bot()

if __name__ == "__main__":
    asyncio.run(main())
```

### Шаг 8: Тестирование

1. **Локальное тестирование:**
   ```bash
   python src/bot/api_server.py
   ```
   Откройте `http://localhost:8000/waifu-card/test-id`

2. **Тестирование на Render:**
   - Деплойте на Render
   - Проверьте доступность `https://ваш-домен.com/`
   - Протестируйте API: `https://ваш-домен.com/api/waifu/test-id`

3. **Тестирование в боте:**
   - Нажмите "ℹ️ Детальная информация"
   - Выберите вайфу
   - Проверьте открытие WebApp

## 🔧 Дополнительные настройки

### Настройка HTTPS

Render автоматически предоставляет SSL сертификаты для вашего домена.

### Оптимизация производительности

1. **Кэширование:**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=100)
   async def get_waifu_cached(waifu_id: str):
       # Кэшированное получение вайфу
   ```

2. **Сжатие статических файлов:**
   ```python
   from fastapi.middleware.gzip import GZipMiddleware
   
   app.add_middleware(GZipMiddleware, minimum_size=1000)
   ```

### Безопасность

1. **CORS настройки:**
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://web.telegram.org"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Валидация данных:**
   ```python
   from pydantic import BaseModel, validator
   
   class WaifuResponse(BaseModel):
       id: str
       name: str
       rarity: str
       # ... другие поля
       
       @validator('rarity')
       def validate_rarity(cls, v):
           if v not in ['Common', 'Uncommon', 'Rare', 'Epic', 'Legendary']:
               raise ValueError('Invalid rarity')
           return v
   ```

## 🐛 Отладка

### Логи

1. **Логи Render:**
   - Откройте Render Dashboard
   - Перейдите в раздел "Logs"
   - Просматривайте логи в реальном времени

2. **Логи бота:**
   ```python
   import logging
   
   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)
   ```

### Тестирование WebApp

1. **Проверка URL:**
   ```javascript
   console.log('Current URL:', window.location.href);
   console.log('Waifu ID:', getWaifuId());
   ```

2. **Проверка API:**
   ```bash
   curl https://ваш-домен.com/api/waifu/test-id
   ```

## 📱 Финальная настройка

После успешного деплоя обновите URL в боте:

```python
# В src/bot/handlers/menu.py
WEBAPP_URL = "https://ваш-домен.com"

# В функции handle_waifu_details_menu_callback
InlineKeyboardButton(
    text=f"🖼️ {waifu.name} - Ур.{waifu.level} {rarity_icon} 💪{power}",
    web_app=WebAppInfo(url=f"{WEBAPP_URL}/waifu-card/{waifu.id}")
)
```

## ✅ Проверочный список

- [ ] WebApp файлы созданы
- [ ] API endpoint работает
- [ ] Render сервис настроен
- [ ] Домен подключен
- [ ] SSL сертификат активен
- [ ] Бот обновлен с новыми URL
- [ ] Тестирование прошло успешно

## 🎉 Готово!

Теперь ваши пользователи смогут открывать красивые карточки вайфу в WebApp прямо из Telegram бота!
