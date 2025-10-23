# 🐙 Подключение Waifu Bot к GitHub репозиторию через GitHub Desktop

## 🎯 Обзор

Данная инструкция поможет вам создать GitHub репозиторий для вашего Waifu Bot и настроить его для работы с Render через GitHub Desktop.

## 📋 Требования

- ✅ GitHub аккаунт
- ✅ GitHub Desktop установлен
- ✅ Waifu Bot проект готов
- ✅ Базовые знания Git

## 🚀 Пошаговая настройка

### Шаг 1: Установка GitHub Desktop

#### 1.1 Скачивание и установка

1. **Перейдите на сайт GitHub Desktop:**
   - Откройте браузер
   - Перейдите по адресу: https://desktop.github.com/
   - Нажмите "Download for Windows"

2. **Установка:**
   - Запустите скачанный файл
   - Следуйте инструкциям установщика
   - Перезагрузите компьютер при необходимости

3. **Первый запуск:**
   - Запустите GitHub Desktop
   - Войдите в свой GitHub аккаунт
   - Настройте Git (если требуется)

### Шаг 2: Подготовка проекта

#### 2.1 Создание .gitignore файла

Создайте файл `.gitignore` в корне проекта:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/
env.bak/
venv.bak/

# Environment variables
.env
config.env

# Database
*.db
*.sqlite
*.sqlite3
waifu_bot.db

# Logs
*.log
logs/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.temp

# Bot specific
bot_data/
user_data/
```

#### 2.2 Создание README.md

Создайте файл `README.md` в корне проекта:

```markdown
# 🎭 Waifu Bot

Telegram бот для коллекционирования вайфу с системой гача, событий и WebApp.

## 🚀 Возможности

- 🎰 Система гача с различными редкостями
- 🎯 События для вайфу
- 📱 WebApp для просмотра карточек
- 💰 Система валют (монеты и гемы)
- 📊 Статистика и достижения

## 🛠️ Технологии

- Python 3.11+
- aiogram 3.x
- FastAPI
- SQLAlchemy
- SQLite/PostgreSQL
- Render (деплой)

## 📦 Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/ваш-username/waifu-bot.git
cd waifu-bot
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Настройте переменные окружения:
```bash
cp config.env.example config.env
# Отредактируйте config.env
```

4. Запустите бота:
```bash
python src/bot/main.py
```

## 🔧 Настройка

Создайте файл `config.env` с вашими настройками:

```env
BOT_TOKEN=ваш_токен_бота
DATABASE_URL=sqlite:///waifu_bot.db
```

## 📱 WebApp

WebApp доступен по адресу: https://ваш-домен.com

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

MIT License
```

### Шаг 3: Создание GitHub репозитория

#### 3.1 Через GitHub Desktop

1. **Откройте GitHub Desktop**
2. **Создайте новый репозиторий:**
   - Нажмите "File" → "New repository"
   - Или нажмите "Create a new repository on GitHub"

3. **Заполните форму:**
   - **Name:** `waifu-bot`
   - **Description:** `Telegram bot for waifu collection with gacha system`
   - **Local path:** Выберите папку с вашим проектом
   - **Initialize with README:** ✅ (если еще нет)
   - **Git ignore:** Python
   - **License:** MIT License

4. **Нажмите "Create repository"**

#### 3.2 Альтернативный способ через веб-интерфейс

1. **Перейдите на GitHub.com**
2. **Нажмите "New repository"**
3. **Заполните форму:**
   - Repository name: `waifu-bot`
   - Description: `Telegram bot for waifu collection with gacha system`
   - Visibility: Public/Private (на ваш выбор)
   - Initialize with README: ✅
   - Add .gitignore: Python
   - Add a license: MIT License

4. **Нажмите "Create repository"**

### Шаг 4: Подключение локального проекта к GitHub

#### 4.1 Если репозиторий уже создан на GitHub

1. **Откройте GitHub Desktop**
2. **Нажмите "Clone a repository from the Internet"**
3. **Введите URL репозитория:**
   - HTTPS: `https://github.com/ваш-username/waifu-bot.git`
   - Или найдите в списке "Your repositories"

4. **Выберите локальную папку** для клонирования
5. **Нажмите "Clone"**

#### 4.2 Если проект уже существует локально

1. **Откройте GitHub Desktop**
2. **Нажмите "Add an Existing Repository from your Hard Drive"**
3. **Выберите папку с вашим проектом**
4. **Нажмите "Add Repository"**
5. **Опубликуйте репозиторий:**
   - Нажмите "Publish repository"
   - Выберите видимость (Public/Private)
   - Нажмите "Publish Repository"

### Шаг 5: Первый коммит

#### 5.1 Добавление файлов

1. **В GitHub Desktop вы увидите список изменений**
2. **Проверьте файлы:**
   - ✅ Отметьте файлы для добавления
   - ❌ Убедитесь, что `.env` и другие конфиденциальные файлы не добавлены

3. **Добавьте commit message:**
   ```
   Initial commit: Add Waifu Bot with WebApp support
   ```

4. **Нажмите "Commit to main"**

#### 5.2 Отправка на GitHub

1. **Нажмите "Push origin"** (если репозиторий уже существует)
2. **Или "Publish repository"** (если это первый раз)

### Шаг 6: Настройка для Render

#### 6.1 Обновление render.yaml

Убедитесь, что файл `render.yaml` содержит правильные настройки:

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
    healthCheckPath: /health
```

#### 6.2 Создание файла для переменных окружения

Создайте файл `config.env.example`:

```env
# Telegram Bot
BOT_TOKEN=your_bot_token_here

# Database
DATABASE_URL=sqlite:///waifu_bot.db

# Redis (опционально)
REDIS_URL=redis://localhost:6379

# WebApp URL
WEBAPP_URL=https://your-domain.com
```

### Шаг 7: Подключение к Render

#### 7.1 Создание сервиса в Render

1. **Войдите в Render Dashboard**
2. **Нажмите "New +" → "Web Service"**
3. **Подключите GitHub репозиторий:**
   - Нажмите "Connect GitHub account"
   - Авторизуйтесь через GitHub
   - Выберите репозиторий `waifu-bot`

4. **Настройте сервис:**
   - **Name:** `waifu-bot-webapp`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python -m uvicorn src.bot.api_server:app --host 0.0.0.0 --port $PORT`

#### 7.2 Настройка переменных окружения

1. **В разделе "Environment Variables":**
   - Добавьте `DATABASE_URL`
   - Добавьте `BOT_TOKEN`
   - Добавьте `WEBAPP_URL`

2. **Нажмите "Create Web Service"**

### Шаг 8: Настройка домена

#### 8.1 Добавление кастомного домена

1. **В Render Dashboard перейдите в ваш сервис**
2. **Нажмите "Custom Domains"**
3. **Добавьте ваш домен:**
   - Введите домен (например, `bot.yourdomain.com`)
   - Нажмите "Add Domain"

4. **Настройте DNS:**
   - Добавьте CNAME запись в DNS настройках
   - Укажите на Render сервис

#### 8.2 Ожидание активации SSL

1. **Дождитесь активации SSL сертификата** (обычно 5-10 минут)
2. **Проверьте доступность:** `https://ваш-домен.com/health`

### Шаг 9: Обновление бота

#### 9.1 Обновление URL в коде

1. **Откройте файл `src/bot/handlers/menu.py`**
2. **Найдите строку с WebApp URL:**
   ```python
   web_app=WebAppInfo(url=f"https://ваш-домен.com/waifu-card/{waifu.id}?waifu_id={waifu.id}")
   ```

3. **Замените на ваш реальный домен:**
   ```python
   web_app=WebAppInfo(url=f"https://bot.yourdomain.com/waifu-card/{waifu.id}?waifu_id={waifu.id}")
   ```

#### 9.2 Коммит и пуш изменений

1. **В GitHub Desktop:**
   - Проверьте изменения
   - Добавьте commit message: `Update WebApp URL with custom domain`
   - Нажмите "Commit to main"
   - Нажмите "Push origin"

2. **Render автоматически обновится** (если настроен auto-deploy)

### Шаг 10: Тестирование

#### 10.1 Тестирование API

1. **Проверьте health check:**
   ```bash
   curl https://ваш-домен.com/health
   ```

2. **Проверьте WebApp:**
   - Откройте `https://ваш-домен.com/` в браузере
   - Убедитесь, что страница загружается

#### 10.2 Тестирование в боте

1. **Запустите бота локально:**
   ```bash
   python src/bot/main.py
   ```

2. **Протестируйте WebApp:**
   - Откройте "📋 Мои вайфу"
   - Нажмите "ℹ️ Детальная информация"
   - Выберите вайфу
   - Проверьте открытие WebApp

## 🔧 Дополнительные настройки

### Настройка автоматического деплоя

1. **В Render Dashboard:**
   - Перейдите в настройки сервиса
   - Включите "Auto-Deploy" для main ветки

2. **Теперь каждый push в main** будет автоматически деплоить изменения

### Настройка веток

1. **Создание feature ветки:**
   ```bash
   # В GitHub Desktop
   Current branch: main → Create new branch
   Name: feature/new-feature
   ```

2. **Работа с ветками:**
   - Вносите изменения в feature ветку
   - Коммитьте изменения
   - Создавайте Pull Request на GitHub

### Настройка .gitignore

Дополните `.gitignore` при необходимости:

```gitignore
# Bot logs
bot.log
error.log

# Database backups
*.backup
*.bak

# Configuration files
config.local.env
secrets.env

# Temporary files
temp/
tmp/
```

## 🐛 Решение проблем

### Проблема: "Repository not found"

**Решение:**
1. Проверьте правильность URL репозитория
2. Убедитесь, что у вас есть доступ к репозиторию
3. Проверьте авторизацию в GitHub Desktop

### Проблема: "Authentication failed"

**Решение:**
1. Выйдите из GitHub Desktop
2. Войдите заново с правильными учетными данными
3. Проверьте настройки Git в GitHub Desktop

### Проблема: "Push failed"

**Решение:**
1. Проверьте интернет-соединение
2. Убедитесь, что у вас есть права на push в репозиторий
3. Попробуйте сделать pull перед push

### Проблема: "Render deployment failed"

**Решение:**
1. Проверьте логи в Render Dashboard
2. Убедитесь, что все зависимости в requirements.txt
3. Проверьте переменные окружения
4. Проверьте правильность start command

## 📱 Мобильное приложение GitHub

### GitHub Mobile

1. **Скачайте GitHub Mobile** из App Store/Google Play
2. **Авторизуйтесь** в своем аккаунте
3. **Просматривайте репозиторий** на мобильном устройстве
4. **Отслеживайте изменения** и issues

## 🎉 Готово!

Теперь ваш Waifu Bot подключен к GitHub и готов для деплоя на Render!

### Проверочный список:

- [ ] GitHub Desktop установлен и настроен
- [ ] Репозиторий создан на GitHub
- [ ] Локальный проект подключен к GitHub
- [ ] Первый коммит выполнен
- [ ] Render сервис настроен
- [ ] Домен подключен
- [ ] WebApp URL обновлен
- [ ] Тестирование прошло успешно

## 📞 Поддержка

При возникновении проблем:

1. **Проверьте документацию GitHub Desktop**
2. **Обратитесь к GitHub Support**
3. **Проверьте логи Render**
4. **Убедитесь в правильности настроек**

Удачи с вашим Waifu Bot! 🎭✨
