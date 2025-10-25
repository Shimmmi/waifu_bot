-- SQL script to update all waifu images with DiceBear avatar URLs
-- Run this in your Neon SQL Editor: https://console.neon.tech/

-- Update each waifu with a random avatar
UPDATE waifu SET image_url = 'https://api.dicebear.com/7.x/adventurer/svg?seed=Bella' WHERE image_url IS NULL OR image_url = '' LIMIT 1;
UPDATE waifu SET image_url = 'https://api.dicebear.com/7.x/adventurer/svg?seed=Sophie' WHERE image_url IS NULL OR image_url = '' LIMIT 1;
UPDATE waifu SET image_url = 'https://api.dicebear.com/7.x/adventurer/svg?seed=Luna' WHERE image_url IS NULL OR image_url = '' LIMIT 1;
UPDATE waifu SET image_url = 'https://api.dicebear.com/7.x/adventurer/svg?seed=Mia' WHERE image_url IS NULL OR image_url = '' LIMIT 1;
UPDATE waifu SET image_url = 'https://api.dicebear.com/7.x/adventurer/svg?seed=Zoe' WHERE image_url IS NULL OR image_url = '' LIMIT 1;
UPDATE waifu SET image_url = 'https://api.dicebear.com/7.x/adventurer/svg?seed=Lily' WHERE image_url IS NULL OR image_url = '' LIMIT 1;
UPDATE waifu SET image_url = 'https://api.dicebear.com/7.x/adventurer/svg?seed=Chloe' WHERE image_url IS NULL OR image_url = '' LIMIT 1;
UPDATE waifu SET image_url = 'https://api.dicebear.com/7.x/adventurer/svg?seed=Emma' WHERE image_url IS NULL OR image_url = '' LIMIT 1;
UPDATE waifu SET image_url = 'https://api.dicebear.com/7.x/adventurer/svg?seed=Ava' WHERE image_url IS NULL OR image_url = '' LIMIT 1;
UPDATE waifu SET image_url = 'https://api.dicebear.com/7.x/adventurer/svg?seed=Aria' WHERE image_url IS NULL OR image_url = '' LIMIT 1;
UPDATE waifu SET image_url = 'https://api.dicebear.com/7.x/adventurer/svg?seed=Nora' WHERE image_url IS NULL OR image_url = '' LIMIT 1;
UPDATE waifu SET image_url = 'https://api.dicebear.com/7.x/adventurer/svg?seed=Ruby' WHERE image_url IS NULL OR image_url = '' LIMIT 1;
UPDATE waifu SET image_url = 'https://api.dicebear.com/7.x/adventurer/svg?seed=Jade' WHERE image_url IS NULL OR image_url = '' LIMIT 1;
UPDATE waifu SET image_url = 'https://api.dicebear.com/7.x/adventurer/svg?seed=Rose' WHERE image_url IS NULL OR image_url = '' LIMIT 1;
UPDATE waifu SET image_url = 'https://api.dicebear.com/7.x/adventurer/svg?seed=Iris' WHERE image_url IS NULL OR image_url = '' LIMIT 1;

-- Verify the update
SELECT id, name, image_url FROM waifu;

