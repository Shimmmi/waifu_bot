-- Migration: Fix dexterity (bond) and loyalty values for existing waifus
-- This migration ensures all existing waifus have proper dexterity and loyalty values

-- First, ensure all waifus have dynamic field initialized
UPDATE waifu
SET dynamic = COALESCE(dynamic, '{}'::jsonb)
WHERE dynamic IS NULL;

-- Reset loyalty to 0 for all waifus (should be 0 for new waifus)
UPDATE waifu
SET dynamic = jsonb_set(
    COALESCE(dynamic, '{}'::jsonb),
    '{loyalty}',
    '0'
)
WHERE (dynamic->>'loyalty')::int != 0 OR dynamic->>'loyalty' IS NULL;

-- Set dexterity (bond) based on rarity for waifus that have bond = 0 or NULL
-- Common: 5-10
UPDATE waifu
SET dynamic = jsonb_set(
    COALESCE(dynamic, '{}'::jsonb),
    '{bond}',
    to_jsonb(FLOOR(RANDOM() * 6 + 5)::int)
)
WHERE rarity = 'Common' 
  AND ((dynamic->>'bond')::int = 0 OR dynamic->>'bond' IS NULL);

-- Uncommon: 10-15
UPDATE waifu
SET dynamic = jsonb_set(
    COALESCE(dynamic, '{}'::jsonb),
    '{bond}',
    to_jsonb(FLOOR(RANDOM() * 6 + 10)::int)
)
WHERE rarity = 'Uncommon' 
  AND ((dynamic->>'bond')::int = 0 OR dynamic->>'bond' IS NULL);

-- Rare: 15-20
UPDATE waifu
SET dynamic = jsonb_set(
    COALESCE(dynamic, '{}'::jsonb),
    '{bond}',
    to_jsonb(FLOOR(RANDOM() * 6 + 15)::int)
)
WHERE rarity = 'Rare' 
  AND ((dynamic->>'bond')::int = 0 OR dynamic->>'bond' IS NULL);

-- Epic: 20-25
UPDATE waifu
SET dynamic = jsonb_set(
    COALESCE(dynamic, '{}'::jsonb),
    '{bond}',
    to_jsonb(FLOOR(RANDOM() * 6 + 20)::int)
)
WHERE rarity = 'Epic' 
  AND ((dynamic->>'bond')::int = 0 OR dynamic->>'bond' IS NULL);

-- Legendary: 25-30
UPDATE waifu
SET dynamic = jsonb_set(
    COALESCE(dynamic, '{}'::jsonb),
    '{bond}',
    to_jsonb(FLOOR(RANDOM() * 6 + 25)::int)
)
WHERE rarity = 'Legendary' 
  AND ((dynamic->>'bond')::int = 0 OR dynamic->>'bond' IS NULL);
