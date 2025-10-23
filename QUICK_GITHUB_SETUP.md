# 🚀 Быстрая настройка GitHub для Waifu Bot

## 📋 Что нужно сделать

### 1. Установка GitHub Desktop ✅

1. **Скачайте GitHub Desktop:**
   - Перейдите на https://desktop.github.com/
   - Скачайте и установите приложение
   - Войдите в свой GitHub аккаунт

### 2. Создание репозитория

#### Вариант A: Через GitHub Desktop (рекомендуется)

1. **Откройте GitHub Desktop**
2. **Нажмите "Create a new repository on GitHub"**
3. **Заполните форму:**
   - Name: `waifu-bot`
   - Description: `Telegram bot for waifu collection with gacha system`
   - Local path: Выберите папку с проектом
   - Initialize with README: ✅
   - Git ignore: Python
   - License: MIT License
4. **Нажмите "Create repository"**

#### Вариант B: Через веб-интерфейс

1. **Перейдите на GitHub.com**
2. **Нажмите "New repository"**
3. **Заполните форму аналогично варианту A**
4. **Нажмите "Create repository"**
5. **Клонируйте репозиторий в GitHub Desktop**

### 3. Подключение проекта

1. **Если проект уже существует локально:**
   - В GitHub Desktop нажмите "Add an Existing Repository"
   - Выберите папку с проектом
   - Нажмите "Publish repository"

2. **Если репозиторий уже создан на GitHub:**
   - В GitHub Desktop нажмите "Clone a repository"
   - Выберите ваш репозиторий
   - Выберите локальную папку
   - Нажмите "Clone"

### 4. Первый коммит

1. **Проверьте файлы в GitHub Desktop**
2. **Убедитесь, что .env файлы не добавлены**
3. **Добавьте commit message:**
   ```
   Initial commit: Add Waifu Bot with WebApp support
   ```
4. **Нажмите "Commit to main"**
5. **Нажмите "Push origin"**

### 5. Настройка Render

1. **Войдите в Render Dashboard**
2. **Создайте новый Web Service:**
   - Connect GitHub repository
   - Выберите `waifu-bot`
   - Name: `waifu-bot-webapp`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python -m uvicorn src.bot.api_server:app --host 0.0.0.0 --port $PORT`

3. **Настройте переменные окружения:**
   - `DATABASE_URL`
   - `BOT_TOKEN`
   - `WEBAPP_URL`

4. **Добавьте ваш домен**
5. **Дождитесь активации SSL**

### 6. Обновление бота

1. **Откройте `src/bot/handlers/menu.py`**
2. **Замените URL на ваш реальный домен:**
   ```python
   web_app=WebAppInfo(url=f"https://ваш-реальный-домен.com/waifu-card/{waifu.id}?waifu_id={waifu.id}")
   ```
3. **Сделайте коммит и пуш изменений**

## 🎯 Готово!

Теперь ваш бот подключен к GitHub и готов для деплоя на Render!

## 📞 Если что-то не работает

1. **Проверьте авторизацию в GitHub Desktop**
2. **Убедитесь, что репозиторий создан правильно**
3. **Проверьте настройки Render**
4. **Убедитесь, что домен настроен и SSL активен**
