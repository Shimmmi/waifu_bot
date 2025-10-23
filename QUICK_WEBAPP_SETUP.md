# 🚀 Быстрая настройка WebApp для Waifu Bot

## 📋 Что нужно сделать

### 1. Подготовка файлов ✅
Все необходимые файлы уже созданы:
- `webapp/waifu-card.html` - WebApp страница
- `src/bot/api_server.py` - API сервер
- `render.yaml` - конфигурация Render
- `run_api_server.py` - скрипт запуска
- `test_webapp.py` - скрипт тестирования

### 2. Локальное тестирование

```bash
# Запуск API сервера
python run_api_server.py

# В другом терминале - тестирование
python test_webapp.py
```

### 3. Настройка Render

1. **Войдите в Render Dashboard**
2. **Создайте новый Web Service:**
   - Connect your repository
   - Name: `waifu-bot-webapp`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python -m uvicorn src.bot.api_server:app --host 0.0.0.0 --port $PORT`

3. **Настройте переменные окружения:**
   - `DATABASE_URL` - ваш URL базы данных
   - `BOT_TOKEN` - токен вашего бота

4. **Добавьте ваш домен:**
   - Custom Domains → Add Domain
   - Введите ваш домен
   - Дождитесь активации SSL

### 4. Обновление бота

Замените `https://ваш-домен.com` на ваш реальный домен в файле `src/bot/handlers/menu.py`:

```python
# Строка 898
web_app=WebAppInfo(url=f"https://ВАШ-РЕАЛЬНЫЙ-ДОМЕН.com/waifu-card/{waifu.id}?waifu_id={waifu.id}")
```

### 5. Тестирование

1. **Проверьте доступность:**
   - `https://ваш-домен.com/health`
   - `https://ваш-домен.com/`

2. **Протестируйте в боте:**
   - Откройте "📋 Мои вайфу"
   - Нажмите "ℹ️ Детальная информация"
   - Выберите вайфу
   - Проверьте открытие WebApp

## 🎯 Готово!

Теперь ваши пользователи смогут открывать красивые карточки вайфу в WebApp прямо из Telegram бота!

## 📞 Если что-то не работает

1. **Проверьте логи Render** в Dashboard
2. **Убедитесь, что домен настроен** и SSL активен
3. **Проверьте переменные окружения** в Render
4. **Протестируйте API локально** с помощью `test_webapp.py`
