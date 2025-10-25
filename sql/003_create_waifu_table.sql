-- Create the main waifu table (for generated/pool waifus)
CREATE TABLE IF NOT EXISTS waifu (
    id TEXT PRIMARY KEY,
    card_number INTEGER UNIQUE NOT NULL,
    name TEXT NOT NULL,
    rarity TEXT NOT NULL,
    race TEXT NOT NULL,
    profession TEXT NOT NULL,
    nationality TEXT NOT NULL,
    image_url TEXT,
    owner_id BIGINT,
    level INTEGER NOT NULL DEFAULT 1,
    xp INTEGER NOT NULL DEFAULT 0,
    stats JSONB NOT NULL,
    dynamic JSONB NOT NULL,
    tags JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create events table
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    event_type TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    start_time TIMESTAMPTZ NOT NULL DEFAULT now(),
    end_time TIMESTAMPTZ,
    rewards JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create event_participations table
CREATE TABLE IF NOT EXISTS event_participations (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    waifu_id TEXT NOT NULL REFERENCES waifu(id),
    event_id INTEGER NOT NULL REFERENCES events(id),
    score DOUBLE PRECISION NOT NULL,
    rewards_received JSONB,
    participated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_waifu_owner_id ON waifu(owner_id);
CREATE INDEX IF NOT EXISTS idx_waifu_rarity ON waifu(rarity);
CREATE INDEX IF NOT EXISTS idx_waifu_card_number ON waifu(card_number);
CREATE INDEX IF NOT EXISTS idx_event_participations_user_id ON event_participations(user_id);
CREATE INDEX IF NOT EXISTS idx_event_participations_waifu_id ON event_participations(waifu_id);

