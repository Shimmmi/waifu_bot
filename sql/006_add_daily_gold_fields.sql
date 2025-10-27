-- Migration: Add daily gold tracking fields
-- Add daily_gold and last_gold_reset columns to users table

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS daily_gold INTEGER NOT NULL DEFAULT 0;

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS last_gold_reset TIMESTAMPTZ NOT NULL DEFAULT now();

-- Update existing users to have last_gold_reset set to now()
UPDATE users 
SET last_gold_reset = now() 
WHERE last_gold_reset IS NULL;
