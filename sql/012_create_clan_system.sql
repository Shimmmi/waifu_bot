-- Clan system tables
-- Migration: 012_create_clan_system.sql

-- Clans table
CREATE TABLE IF NOT EXISTS clans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    tag VARCHAR(10) UNIQUE NOT NULL,
    description TEXT,
    emblem_id INTEGER DEFAULT 1,
    type VARCHAR(20) DEFAULT 'open', -- 'open', 'invite', 'closed'
    leader_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    level INTEGER DEFAULT 1,
    experience BIGINT DEFAULT 0,
    total_power BIGINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    settings JSONB DEFAULT '{}'
);

-- Clan members table
CREATE TABLE IF NOT EXISTS clan_members (
    id SERIAL PRIMARY KEY,
    clan_id INTEGER REFERENCES clans(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'member', -- 'leader', 'officer', 'member'
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    donated_gold BIGINT DEFAULT 0,
    donated_skills INTEGER DEFAULT 0,
    UNIQUE(clan_id, user_id)
);

-- Clan events table
CREATE TABLE IF NOT EXISTS clan_events (
    id SERIAL PRIMARY KEY,
    clan_id INTEGER REFERENCES clans(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL, -- 'raid', 'war', 'quest', 'boss_challenge'
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ends_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'completed', 'cancelled'
    data JSONB DEFAULT '{}',
    rewards JSONB DEFAULT '{}'
);

-- Clan event participations table
CREATE TABLE IF NOT EXISTS clan_event_participations (
    id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES clan_events(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    score BIGINT DEFAULT 0,
    contribution JSONB DEFAULT '{}',
    UNIQUE(event_id, user_id)
);

-- Clan chat messages table
CREATE TABLE IF NOT EXISTS clan_chat_messages (
    id SERIAL PRIMARY KEY,
    clan_id INTEGER REFERENCES clans(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_clan_members_user_id ON clan_members(user_id);
CREATE INDEX IF NOT EXISTS idx_clan_members_clan_id ON clan_members(clan_id);
CREATE INDEX IF NOT EXISTS idx_clan_events_clan_id ON clan_events(clan_id);
CREATE INDEX IF NOT EXISTS idx_clan_events_status ON clan_events(status);
CREATE INDEX IF NOT EXISTS idx_clan_chat_clan_id ON clan_chat_messages(clan_id);
CREATE INDEX IF NOT EXISTS idx_clan_chat_created_at ON clan_chat_messages(created_at);

-- Add clan reference to users table (optional, for quick lookups)
ALTER TABLE users ADD COLUMN IF NOT EXISTS clan_id INTEGER REFERENCES clans(id) ON DELETE SET NULL;

