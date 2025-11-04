-- Clan raid activity tracking table
-- Migration: 015_add_clan_raid_activity.sql

CREATE TABLE IF NOT EXISTS clan_raid_activity (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES clan_events(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chat_id BIGINT NOT NULL,  -- Telegram chat ID
    message_type VARCHAR(20) NOT NULL,  -- 'text', 'sticker', 'photo', 'video', 'voice', 'link', 'document', 'animation'
    damage_dealt INTEGER NOT NULL DEFAULT 0,  -- Урон от этого действия
    message_id BIGINT,  -- Telegram message ID (для отслеживания)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(event_id, user_id, message_id)  -- Одно сообщение = один урон
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_raid_activity_event_id ON clan_raid_activity(event_id);
CREATE INDEX IF NOT EXISTS idx_raid_activity_user_id ON clan_raid_activity(user_id);
CREATE INDEX IF NOT EXISTS idx_raid_activity_chat_id ON clan_raid_activity(chat_id);
CREATE INDEX IF NOT EXISTS idx_raid_activity_created_at ON clan_raid_activity(created_at);
