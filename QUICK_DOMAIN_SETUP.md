# 🚀 Быстрая настройка домена shimmirpgbot.ru для Render

## 📋 Что нужно сделать

### 1. Настройка DNS в reg.ru ✅

1. **Войдите в панель управления reg.ru**
2. **Перейдите к управлению доменом `shimmirpgbot.ru`**
3. **Добавьте DNS записи:**

#### CNAME запись:
- **Тип:** CNAME
- **Имя:** `www`
- **Значение:** `waifu-bot-webapp.onrender.com`

#### A запись для корневого домена:
- **Тип:** A
- **Имя:** `@` (или оставьте пустым)
- **Значение:** `76.76.19.61`

### 2. Настройка Render ✅

1. **В Render Dashboard создайте Web Service:**
   - Name: `waifu-bot-webapp`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python -m uvicorn src.bot.api_server:app --host 0.0.0.0 --port $PORT`

2. **Добавьте переменные окружения:**
   - `DATABASE_URL`
   - `BOT_TOKEN`
   - `WEBAPP_URL` = `https://shimmirpgbot.ru`

3. **Добавьте кастомные домены:**
   - `shimmirpgbot.ru`
   - `www.shimmirpgbot.ru`

### 3. Обновление бота ✅

URL уже обновлен в коде:
```python
web_app=WebAppInfo(url=f"https://shimmirpgbot.ru/waifu-card/{waifu.id}?waifu_id={waifu.id}")
```

### 4. Тестирование ✅

1. **Проверьте доступность:**
   - https://shimmirpgbot.ru/health
   - https://www.shimmirpgbot.ru/health

2. **Протестируйте WebApp в боте**

## 🎯 Готово!

Теперь ваш бот доступен по адресу:
- **Основной домен:** https://shimmirpgbot.ru
- **WWW поддомен:** https://www.shimmirpgbot.ru

## 📞 Если что-то не работает

1. **Проверьте DNS записи в reg.ru**
2. **Убедитесь, что домен добавлен в Render**
3. **Дождитесь активации SSL сертификатов (5-10 минут)**
4. **Проверьте логи в Render Dashboard**
