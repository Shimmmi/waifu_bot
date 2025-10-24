# 🔧 Исправление настроек в Render Dashboard

## 🎯 Проблема

Render все еще использует старый путь `src.bot.api_server:app` вместо `app:app`.

**Причина:** Настройки в Render Dashboard имеют приоритет над render.yaml.

## 🔧 Решение

### Вариант 1: Изменить настройки в Render Dashboard (Рекомендуется)

1. **Войдите в Render Dashboard**
   - Перейдите на https://dashboard.render.com

2. **Откройте ваш Web Service**
   - Найдите сервис `waifu-bot-webapp`
   - Нажмите на него

3. **Перейдите в Settings**
   - Нажмите на вкладку "Settings"

4. **Найдите "Build & Deploy"**
   - Прокрутите вниз до секции "Build & Deploy"

5. **Измените Start Command**
   - Найдите поле "Start Command"
   - Измените с `python -m uvicorn src.bot.api_server:app --host 0.0.0.0 --port $PORT`
   - На `python -m uvicorn app:app --host 0.0.0.0 --port $PORT`

6. **Сохраните изменения**
   - Нажмите "Save Changes"
   - Render автоматически пересоберет проект

### Вариант 2: Удалить настройки из Dashboard

1. **Войдите в Render Dashboard**
2. **Откройте ваш Web Service**
3. **Перейдите в Settings**
4. **Найдите "Build & Deploy"**
5. **Очистите поле "Start Command"**
   - Это заставит Render использовать настройки из render.yaml
6. **Сохраните изменения**

## 🚀 Пошаговая инструкция

### Шаг 1: Войдите в Render

1. Перейдите на https://dashboard.render.com
2. Войдите в свой аккаунт

### Шаг 2: Найдите ваш сервис

1. В списке сервисов найдите `waifu-bot-webapp`
2. Нажмите на него

### Шаг 3: Измените Start Command

1. Перейдите в "Settings"
2. Прокрутите до "Build & Deploy"
3. Найдите "Start Command"
4. Измените на:
   ```
   python -m uvicorn app:app --host 0.0.0.0 --port $PORT
   ```

### Шаг 4: Сохраните и подождите

1. Нажмите "Save Changes"
2. Подождите, пока Render пересоберет проект
3. Проверьте логи на ошибки

### Шаг 5: Тестирование

После успешного деплоя проверьте:

1. **API endpoint:**
   ```
   https://waifu-bot-webapp.onrender.com/api/waifu/wf_ddd65e42
   ```

2. **WebApp:**
   ```
   https://waifu-bot-webapp.onrender.com/waifu-card/wf_ddd65e42?waifu_id=wf_ddd65e42
   ```

## 🎯 Ожидаемые результаты

После изменения настроек:

### Логи должны показывать:
```
==> Running 'python -m uvicorn app:app --host 0.0.0.0 --port $PORT'
INFO:     Started server process [55]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:10000
```

### API endpoint должен возвращать:
```json
{
  "id": "wf_ddd65e42",
  "name": "Ava",
  "rarity": "Common",
  "race": "Demon",
  "profession": "Warrior",
  "level": 1,
  "xp": 158,
  "stats": {
    "power": 13,
    "charm": 6,
    "luck": 7,
    "affection": 8,
    "intellect": 8,
    "speed": 5
  },
  "dynamic": {
    "mood": 78,
    "loyalty": 60,
    "energy": 80
  }
}
```

### WebApp должен отображать:
- ✅ **Реальное имя** вайфу (Ava)
- ✅ **Правильную редкость** (Common)
- ✅ **Правильную расу** (Demon)
- ✅ **Реальные статы** (power: 13, charm: 6, etc.)

## 🔍 Отладка

### Если API все еще не работает:

1. **Проверьте Start Command в Dashboard:**
   - Убедитесь, что изменения сохранены
   - Проверьте, что используется `app:app`

2. **Проверьте логи сервера:**
   - Убедитесь, что логи показывают правильный путь
   - Проверьте на ошибки импорта

3. **Пересоберите проект вручную:**
   - В Render Dashboard нажмите "Manual Deploy"
   - Выберите "Clear build cache & deploy"

### Если WebApp не загружает данные:

1. **Проверьте JavaScript:**
   - Откройте Developer Tools в браузере
   - Проверьте ошибки в Console

2. **Проверьте Network:**
   - Убедитесь, что API запрос проходит успешно
   - Проверьте статус ответа (должен быть 200, а не 500)

## 📸 Скриншоты для помощи

### Где найти Start Command:

1. **Render Dashboard → Your Service → Settings**
2. **Прокрутите до "Build & Deploy"**
3. **Найдите "Start Command"**
4. **Измените значение**
5. **Нажмите "Save Changes"**

## 🎉 Готово!

После изменения настроек в Render Dashboard WebApp будет работать с реальными данными!

### Проверочный список:

- [ ] Вошли в Render Dashboard
- [ ] Открыли сервис waifu-bot-webapp
- [ ] Перешли в Settings
- [ ] Изменили Start Command на `python -m uvicorn app:app --host 0.0.0.0 --port $PORT`
- [ ] Сохранили изменения
- [ ] Проект пересобрался
- [ ] API endpoint работает (возвращает 200, а не 500)
- [ ] WebApp отображает реальные данные

## 🔄 Дальнейшие шаги

После успешного исправления:

1. **Протестируйте все вайфу**
2. **Убедитесь, что каждая кнопка** открывает свою вайфу
3. **Проверьте, что WebApp** работает на мобильных устройствах

Удачи с исправлением! 🎭✨
