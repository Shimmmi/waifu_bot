-- Migration: Add quest rewards tracking
-- Add quest_rewards_claimed column to users table to track which quests have been claimed

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS quest_rewards_claimed JSONB DEFAULT '{}';

-- Initialize existing users
UPDATE users 
SET quest_rewards_claimed = '{}' 
WHERE quest_rewards_claimed IS NULL;
