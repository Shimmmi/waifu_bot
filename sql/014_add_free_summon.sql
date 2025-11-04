-- Migration 014: Add free summon tracking
-- Adds last_free_summon timestamp to track daily free summon cooldown

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS last_free_summon TIMESTAMPTZ DEFAULT TIMESTAMPTZ '1970-01-01';

-- Set default value for existing users (allows immediate free summon)
UPDATE users 
SET last_free_summon = TIMESTAMPTZ '1970-01-01' 
WHERE last_free_summon IS NULL;

COMMENT ON COLUMN users.last_free_summon IS 'Timestamp of last free summon (1 per 24 hours)';
