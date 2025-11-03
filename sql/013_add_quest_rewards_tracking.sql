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
