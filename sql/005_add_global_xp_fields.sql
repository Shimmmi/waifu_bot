-- Add global XP system fields to users table
ALTER TABLE users
ADD COLUMN IF NOT EXISTS account_level INTEGER DEFAULT 1 NOT NULL,
ADD COLUMN IF NOT EXISTS global_xp INTEGER DEFAULT 0 NOT NULL,
ADD COLUMN IF NOT EXISTS skill_points INTEGER DEFAULT 0 NOT NULL,
ADD COLUMN IF NOT EXISTS last_global_xp TIMESTAMPTZ DEFAULT now() NOT NULL;

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_users_account_level ON users(account_level);
CREATE INDEX IF NOT EXISTS idx_users_global_xp ON users(global_xp);
