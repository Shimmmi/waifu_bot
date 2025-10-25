-- Migration: Initialize dynamic stats for all waifus
-- This ensures all waifus have energy, mood, loyalty, and last_restore fields

-- Update existing waifus that don't have dynamic stats initialized
UPDATE waifu 
SET dynamic = jsonb_build_object(
    'energy', 100,
    'mood', 50,
    'loyalty', 50,
    'last_restore', now()::text
)
WHERE dynamic IS NULL 
   OR NOT (dynamic ? 'energy')
   OR NOT (dynamic ? 'mood')
   OR NOT (dynamic ? 'loyalty');

-- Add index for faster queries
CREATE INDEX IF NOT EXISTS idx_waifu_owner_id ON waifu(owner_id);
CREATE INDEX IF NOT EXISTS idx_waifu_dynamic ON waifu USING GIN (dynamic);

