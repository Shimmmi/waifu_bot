-- Add user preferences field
-- Migration: 011_add_user_preferences.sql

-- Add waifu sort preference field
ALTER TABLE users ADD COLUMN IF NOT EXISTS waifu_sort_preference VARCHAR(20);

-- Set default value for existing users
UPDATE users SET waifu_sort_preference = 'name' WHERE waifu_sort_preference IS NULL;

-- Create index for faster queries (optional)
CREATE INDEX IF NOT EXISTS idx_users_sort_preference ON users(waifu_sort_preference) WHERE waifu_sort_preference IS NOT NULL;

