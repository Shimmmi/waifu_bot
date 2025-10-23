-- users
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  tg_id BIGINT UNIQUE NOT NULL,
  username TEXT,
  display_name TEXT,
  coins BIGINT DEFAULT 0,
  gems BIGINT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now(),
  last_daily TIMESTAMPTZ DEFAULT '1970-01-01',
  daily_streak INT DEFAULT 0,
  pity_counter INT DEFAULT 0,
  daily_xp INT DEFAULT 0,
  last_xp_reset TIMESTAMPTZ DEFAULT now()
);

-- waifu_templates
CREATE TABLE IF NOT EXISTS waifu_templates (
  template_id SERIAL PRIMARY KEY,
  code TEXT UNIQUE,
  name TEXT,
  rarity TEXT,
  artwork_url TEXT,
  base_stats JSONB,
  skills JSONB,
  tags TEXT[],
  created_at TIMESTAMPTZ DEFAULT now()
);

-- waifus (instances)
CREATE TABLE IF NOT EXISTS waifus (
  id BIGSERIAL PRIMARY KEY,
  owner_id INT REFERENCES users(id) ON DELETE CASCADE,
  template_id INT REFERENCES waifu_templates(template_id),
  nickname TEXT,
  level INT DEFAULT 1,
  xp BIGINT DEFAULT 0,
  affection INT DEFAULT 0,
  skin_id INT DEFAULT NULL,
  is_active BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT now(),
  last_xp_at TIMESTAMPTZ DEFAULT '1970-01-01'
);

-- xp logs
CREATE TABLE IF NOT EXISTS xp_logs (
  id BIGSERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id),
  waifu_id BIGINT REFERENCES waifus(id),
  source TEXT,
  amount INT,
  meta JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- pull history
CREATE TABLE IF NOT EXISTS pull_history (
  id BIGSERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id),
  type TEXT,
  cost JSONB,
  result JSONB,
  pity_counter INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- transactions
CREATE TABLE IF NOT EXISTS transactions (
  id BIGSERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id),
  kind TEXT,
  amount BIGINT,
  currency TEXT,
  reason TEXT,
  meta JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- indexes
CREATE INDEX IF NOT EXISTS idx_users_tg_id ON users(tg_id);
CREATE INDEX IF NOT EXISTS idx_waifus_owner_id ON waifus(owner_id);
CREATE INDEX IF NOT EXISTS idx_xp_logs_user_id ON xp_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_pull_history_user_id ON pull_history(user_id);


