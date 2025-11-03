# Применение миграции quest_rewards_claimed

## Проблема
После добавления функционала отслеживания наград за задания, в базе данных отсутствует колонка `quest_rewards_claimed`, что может приводить к ошибкам при загрузке профиля.

## Решение

### Вариант 1: Через Neon Console (Рекомендуется)

1. Откройте ваш проект в Neon Console: https://console.neon.tech
2. Выберите ваш проект и откройте SQL Editor
3. Скопируйте содержимое файла `sql/013_add_quest_rewards_tracking.sql`
4. Вставьте SQL запрос в редактор
5. Нажмите "Run" для выполнения

### Вариант 2: Через psql

Если у вас есть доступ через командную строку:

```bash
psql "your-connection-string" -f sql/013_add_quest_rewards_tracking.sql
```

## SQL для миграции

```sql
-- Migration: Add quest rewards tracking
-- Add quest_rewards_claimed column to users table to track which quests have been claimed

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'quest_rewards_claimed'
    ) THEN
        ALTER TABLE users ADD COLUMN quest_rewards_claimed JSONB DEFAULT '{}';
    END IF;
END $$;

-- Initialize existing users with empty dict if NULL
UPDATE users 
SET quest_rewards_claimed = '{}'::jsonb
WHERE quest_rewards_claimed IS NULL;
```

## Проверка успешности миграции

После применения миграции проверьте, что колонка создана:

```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users' AND column_name = 'quest_rewards_claimed';
```

Должен вернуться результат:
```
column_name              | data_type
quest_rewards_claimed    | jsonb
```

## После применения миграции

1. Перезапустите бота на Render
2. Проверьте работу WebApp и команд бота

## Если проблема осталась

Если после применения миграции проблема сохраняется:
1. Проверьте логи Render на наличие ошибок базы данных
2. Убедитесь, что миграция была применена успешно
3. Проверьте, что поле `quest_rewards_claimed` существует в таблице `users`
