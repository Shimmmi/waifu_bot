-- Migration: Reset loyalty to 0 and set dexterity (bond) based on rarity
-- Reset loyalty to 0 for all waifus
UPDATE waifu
SET dynamic = jsonb_set(
    COALESCE(dynamic, '{}'::jsonb),
    '{loyalty}',
    '0'
)
WHERE dynamic IS NOT NULL;

-- Set dexterity (bond) based on rarity
-- Common: 5-10
UPDATE waifu
SET dynamic = jsonb_set(
    COALESCE(dynamic, '{}'::jsonb),
    '{bond}',
    to_jsonb(FLOOR(RANDOM() * 6 + 5)::int)
)
WHERE rarity = 'Common';

-- Uncommon: 10-15
UPDATE waifu
SET dynamic = jsonb_set(
    COALESCE(dynamic, '{}'::jsonb),
    '{bond}',
    to_jsonb(FLOOR(RANDOM() * 6 + 10)::int)
)
WHERE rarity = 'Uncommon';

-- Rare: 15-20
UPDATE waifu
SET dynamic = jsonb_set(
    COALESCE(dynamic, '{}'::jsonb),
    '{bond}',
    to_jsonb(FLOOR(RANDOM() * 6 + 15)::int)
)
WHERE rarity = 'Rare';

-- Epic: 20-25
UPDATE waifu
SET dynamic = jsonb_set(
    COALESCE(dynamic, '{}'::jsonb),
    '{bond}',
    to_jsonb(FLOOR(RANDOM() * 6 + 20)::int)
)
WHERE rarity = 'Epic';

-- Legendary: 25-30
UPDATE waifu
SET dynamic = jsonb_set(
    COALESCE(dynamic, '{}'::jsonb),
    '{bond}',
    to_jsonb(FLOOR(RANDOM() * 6 + 25)::int)
)
WHERE rarity = 'Legendary';

