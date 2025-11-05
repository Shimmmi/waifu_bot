-- Индексы для оптимизации частых запросов
-- Migration: 016_add_performance_indexes.sql

-- Индекс для поиска вайфу по владельцу и активности
CREATE INDEX IF NOT EXISTS idx_waifu_owner_active 
ON waifu(owner_id, is_active) 
WHERE is_active = TRUE;

-- Индекс для поиска участников клана
CREATE INDEX IF NOT EXISTS idx_clan_member_clan_user 
ON clan_members(clan_id, user_id);

-- Индекс для сообщений чата клана (сортировка по дате создания)
CREATE INDEX IF NOT EXISTS idx_clan_chat_clan_created 
ON clan_chat_messages(clan_id, created_at DESC) 
WHERE is_deleted = FALSE;

-- Индекс для событий клана
CREATE INDEX IF NOT EXISTS idx_clan_event_clan_status 
ON clan_events(clan_id, status, event_type);

-- Индекс для участия в событиях
CREATE INDEX IF NOT EXISTS idx_clan_event_participation_event_user 
ON clan_event_participations(event_id, user_id);

-- Индекс для активности рейдов
CREATE INDEX IF NOT EXISTS idx_clan_raid_activity_event_chat 
ON clan_raid_activity(event_id, chat_id, created_at DESC);

-- Индекс для XPLog по источнику
CREATE INDEX IF NOT EXISTS idx_xp_log_user_source 
ON xp_log(user_id, source, created_at DESC);

-- Индекс для пользователей по Telegram ID (часто используется для поиска)
CREATE INDEX IF NOT EXISTS idx_user_tg_id 
ON users(tg_id);

-- Индекс для навыков пользователя
CREATE INDEX IF NOT EXISTS idx_user_skill_level_user_skill 
ON user_skill_levels(user_id, skill_id);

-- Дополнительный индекс для поиска активной вайфу пользователя
CREATE INDEX IF NOT EXISTS idx_waifu_owner_id_active 
ON waifu(owner_id) 
WHERE is_active = TRUE;

-- Примечание: Индекс по power не создан, так как power - это вычисляемое поле
-- Сортировка по мощности выполняется на уровне приложения после расчета
