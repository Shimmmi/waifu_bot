-- Migration: Add tokens field to users table
-- Add tokens column for special currency (rare purchases)

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS tokens INTEGER NOT NULL DEFAULT 0;

-- Update existing users to have 0 tokens by default
UPDATE users 
SET tokens = 0 
WHERE tokens IS NULL;
