-- Add is_active and is_favorite fields to waifu table
ALTER TABLE waifu 
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT FALSE NOT NULL,
ADD COLUMN IF NOT EXISTS is_favorite BOOLEAN DEFAULT FALSE NOT NULL;

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_waifu_owner_active ON waifu(owner_id, is_active);
CREATE INDEX IF NOT EXISTS idx_waifu_owner_favorite ON waifu(owner_id, is_favorite);
