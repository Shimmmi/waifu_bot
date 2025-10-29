-- Проверка текущих значений характеристик вайфу
SELECT 
    rarity,
    COUNT(*) as count,
    ROUND(AVG((dynamic->>'bond')::int), 1) as avg_bond,
    ROUND(AVG((dynamic->>'loyalty')::int), 1) as avg_loyalty,
    MIN((dynamic->>'bond')::int) as min_bond,
    MAX((dynamic->>'bond')::int) as max_bond,
    MIN((dynamic->>'loyalty')::int) as min_loyalty,
    MAX((dynamic->>'loyalty')::int) as max_loyalty
FROM waifu 
WHERE dynamic IS NOT NULL
GROUP BY rarity
ORDER BY 
    CASE rarity 
        WHEN 'Common' THEN 1
        WHEN 'Uncommon' THEN 2
        WHEN 'Rare' THEN 3
        WHEN 'Epic' THEN 4
        WHEN 'Legendary' THEN 5
    END;

-- Проверяем, есть ли вайфу с bond = 0
SELECT COUNT(*) as zero_bond_count
FROM waifu 
WHERE (dynamic->>'bond')::int = 0 OR dynamic->>'bond' IS NULL;

-- Проверяем, есть ли вайфу с loyalty > 0
SELECT COUNT(*) as non_zero_loyalty_count
FROM waifu 
WHERE (dynamic->>'loyalty')::int > 0;
