-- Migration: Add user_skills field to users table
-- Add user_skills column for passive skill upgrades

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS user_skills JSONB NOT NULL DEFAULT '{}';

-- Update existing users to have empty skills
UPDATE users 
SET user_skills = '{}' 
WHERE user_skills IS NULL;
