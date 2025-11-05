# 📋 Следующие шаги после клонирования проекта

## ✅ Что уже сделано
- ✅ Проект клонирован из GitHub в `/opt/waifu-bot`

## 🎯 Что делать дальше

### Шаг 1: Проверка Python и установка зависимостей

В терминале Cursor на сервере выполните:

```bash
# 1. Проверить версию Python
python3 --version
# Должно быть Python 3.11 или выше

# 2. Установить Python 3.11 (если нужно)
apt update
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# 3. Установить системные зависимости для PostgreSQL
apt install -y libpq-dev build-essential

# 4. Перейти в папку проекта
cd /opt/waifu-bot

# 5. Создать виртуальное окружение
python3.11 -m venv venv

# 6. Активировать виртуальное окружение
source venv/bin/activate

# 7. Обновить pip
pip install --upgrade pip

# 8. Установить зависимости проекта
pip install -r requirements.txt
```

### Шаг 2: Настройка переменных окружения

```bash
# 1. Создать файл .env
cd /opt/waifu-bot
nano .env
```

Добавьте в файл `.env`:

```env
# Telegram Bot Configuration
BOT_TOKEN=7401283035:AAGiaoJnrzqkuLQYYjNSTPLCReQVdH5oDe4

# Database Configuration
# Если используете PostgreSQL (нужно установить):
DATABASE_URL=postgresql://waifubot_user:YOUR_STRONG_PASSWORD@localhost:5432/waifu_bot
# Или если используете SQLite (для начала):
# DATABASE_URL=sqlite:///./waifu_bot.db

# Redis Configuration (опционально)
REDIS_URL=redis://localhost:6379/0

# WebApp Configuration
WEBAPP_URL=https://shimmirpgbot.ru

# Admin Configuration
ADMIN_ID=YOUR_TELEGRAM_ID

# Environment
ENV=production
```

**Сохранение в nano:** `Ctrl+O`, `Enter`, `Ctrl+X`

```bash
# 2. Установить права доступа
chmod 600 .env
```

### Шаг 3: Установка расширений в Cursor

После подключения к серверу через Remote SSH нужно установить расширения **на удаленном сервере**:

1. **Нажмите `Ctrl+Shift+X`** (или View → Extensions)

2. **Установите расширения:**
   - **Python** (Microsoft) - для работы с Python кодом
   - **Pylance** (Microsoft) - автодополнение для Python
   - **SQLTools** (mtxr) - если работаете с SQL

3. **Выберите Python интерпретатор:**
   - Нажмите `Ctrl+Shift+P`
   - Введите: `Python: Select Interpreter`
   - Выберите: `/opt/waifu-bot/venv/bin/python`

### Шаг 4: Проверка структуры проекта

```bash
cd /opt/waifu-bot
ls -la

# Должны быть видны:
# - src/
# - webapp/
# - requirements.txt
# - .env
# - venv/
# и другие файлы
```

### Шаг 5: (Опционально) Установка PostgreSQL и Redis

Если вы планируете использовать PostgreSQL вместо SQLite:

```bash
# Установка PostgreSQL
apt install -y postgresql postgresql-contrib

# Создание базы данных и пользователя
su - postgres
psql

# В PostgreSQL консоли:
CREATE DATABASE waifu_bot;
CREATE USER waifubot_user WITH PASSWORD 'YOUR_STRONG_PASSWORD';
ALTER ROLE waifubot_user SET client_encoding TO 'utf8';
GRANT ALL PRIVILEGES ON DATABASE waifu_bot TO waifubot_user;
\q
exit

# Установка Redis
apt install -y redis-server
systemctl start redis-server
systemctl enable redis-server
```

### Шаг 6: Тестовый запуск

```bash
cd /opt/waifu-bot
source venv/bin/activate

# Проверка импортов
python3 -c "from bot.config import get_settings; print('OK')"

# Тестовый запуск бота (если база данных настроена)
# python3 -m bot.main
```

---

## 🎯 Быстрая последовательность команд

Выполните все команды по порядку:

```bash
# 1. Проверка и установка Python
python3 --version
apt update
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip libpq-dev build-essential

# 2. Создание виртуального окружения
cd /opt/waifu-bot
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# 3. Установка зависимостей
pip install -r requirements.txt

# 4. Создание .env файла
nano .env
# (добавьте переменные окружения, см. выше)

# 5. Установка прав
chmod 600 .env

# 6. Проверка
ls -la
python3 -c "import sys; print(sys.version)"
```

---

## ✅ Чеклист

После выполнения всех шагов проверьте:

- [ ] Python 3.11 установлен
- [ ] Виртуальное окружение создано
- [ ] Зависимости установлены (`pip list`)
- [ ] Файл `.env` создан и заполнен
- [ ] Расширения Python установлены в Cursor
- [ ] Python интерпретатор выбран правильно
- [ ] Проект открыт в Cursor (`/opt/waifu-bot`)

---

## 🚀 После настройки

Когда всё будет готово, можно:
1. Настроить базу данных (PostgreSQL или SQLite)
2. Настроить systemd службы для автозапуска
3. Настроить Nginx для WebApp
4. Настроить SSL сертификат

**Начните с Шага 1!** Выполните команды по порядку.

