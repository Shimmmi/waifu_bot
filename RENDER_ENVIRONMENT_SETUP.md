# 🔧 Настройка переменных окружения в Render

## 🎯 Проблема

API endpoint возвращает `{"detail":"Database not configured"}` вместо данных вайфу.

## 🔧 Решение

### 1. Настройка переменных окружения в Render

В Render Dashboard вам нужно настроить следующие переменные:

#### **Обязательные переменные:**
```
DATABASE_URL=postgresql://username:password@host:port/database
BOT_TOKEN=7401283035:AAGiaoJnrzqkuLQYYjNSTPLCReQVdH5oDe4
WEBAPP_URL=https://shimmirpgbot.ru
```

#### **Дополнительные переменные:**
```
REDIS_URL=redis://username:password@host:port
ENV=production
```

### 2. Получение DATABASE_URL из Neon

1. **Войдите в Neon Dashboard**
2. **Перейдите в ваш проект**
3. **Нажмите "Connection Details"**
4. **Скопируйте Connection String**
5. **Добавьте в Render как переменную `DATABASE_URL`**

### 3. Получение REDIS_URL из Redis Cloud

1. **Войдите в Redis Cloud Dashboard**
2. **Перейдите в ваш database**
3. **Нажмите "Connect"**
4. **Скопируйте Connection String**
5. **Добавьте в Render как переменную `REDIS_URL`**

### 4. Настройка в Render Dashboard

1. **Войдите в Render Dashboard**
2. **Перейдите в ваш Web Service**
3. **Нажмите "Environment"**
4. **Добавьте переменные:**
   - `DATABASE_URL` - Connection String из Neon
   - `BOT_TOKEN` - 7401283035:AAGiaoJnrzqkuLQYYjNSTPLCReQVdH5oDe4
   - `WEBAPP_URL` - https://shimmirpgbot.ru
   - `REDIS_URL` - Connection String из Redis Cloud
5. **Нажмите "Save Changes"**
6. **Пересоберите проект**

### 5. Проверка подключения

После настройки переменных окружения:

1. **Пересоберите проект в Render**
2. **Проверьте логи** на ошибки подключения
3. **Протестируйте API endpoint**

## 🚀 Пошаговая настройка

### Шаг 1: Настройка Neon

1. **Войдите в Neon Dashboard**
2. **Перейдите в ваш проект**
3. **Нажмите "Connection Details"**
4. **Скопируйте Connection String**
5. **Добавьте в Render как `DATABASE_URL`**

### Шаг 2: Настройка Redis

1. **Войдите в Redis Cloud Dashboard**
2. **Перейдите в ваш database**
3. **Нажмите "Connect"**
4. **Скопируйте Connection String**
5. **Добавьте в Render как `REDIS_URL`**

### Шаг 3: Обновление Render

1. **В Render Dashboard перейдите в ваш сервис**
2. **Перейдите в "Environment"**
3. **Добавьте переменные:**
   - `DATABASE_URL`
   - `BOT_TOKEN`
   - `WEBAPP_URL`
   - `REDIS_URL`
4. **Нажмите "Save Changes"**
5. **Пересоберите проект**

### Шаг 4: Тестирование

После настройки проверьте:

1. **API endpoint:**
   ```
   https://waifu-bot-webapp.onrender.com/api/waifu/wf_ddd65e42
   ```

2. **WebApp:**
   ```
   https://waifu-bot-webapp.onrender.com/waifu-card/wf_ddd65e42?waifu_id=wf_ddd65e42
   ```

## 🎯 Ожидаемые результаты

После настройки:

- ✅ **API endpoint возвращает** реальные данные вайфу
- ✅ **WebApp отображает** конкретную вайфу
- ✅ **Каждая кнопка** открывает свою вайфу
- ✅ **WebApp работает** с реальными данными

## 🔍 Отладка

### Если API все еще не работает:

1. **Проверьте переменные окружения** в Render
2. **Проверьте логи сервера** на ошибки
3. **Убедитесь, что Connection String правильный**

### Если WebApp не загружает данные:

1. **Проверьте JavaScript** в браузере
2. **Проверьте Network tab** для API запросов
3. **Убедитесь, что API endpoint работает**

## 🎉 Готово!

После настройки переменных окружения WebApp будет работать с реальными данными!

### Проверочный список:

- [ ] DATABASE_URL настроен в Render
- [ ] BOT_TOKEN настроен в Render
- [ ] WEBAPP_URL настроен в Render
- [ ] REDIS_URL настроен в Render
- [ ] Проект пересобран в Render
- [ ] API endpoint работает
- [ ] WebApp отображает реальные данные

Удачи с настройкой! 🎭✨
