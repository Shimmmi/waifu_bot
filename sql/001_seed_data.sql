-- Seed waifu templates for testing
INSERT INTO waifu_templates (code, name, rarity, artwork_url, base_stats, skills, tags) VALUES
('WF_001', 'Sakura', 'common', 'https://example.com/sakura.png', '{"hp": 100, "atk": 10, "def": 5, "spd": 3}', '{"skills": [{"id": "S1", "name": "Basic Attack", "desc": "Deals ATK damage"}]}', '["student", "cheerful"]'),
('WF_002', 'Yuki', 'common', 'https://example.com/yuki.png', '{"hp": 95, "atk": 12, "def": 4, "spd": 4}', '{"skills": [{"id": "S1", "name": "Ice Shard", "desc": "Deals ATK*1.2 damage"}]}', '["mage", "calm"]'),
('WF_003', 'Hana', 'uncommon', 'https://example.com/hana.png', '{"hp": 120, "atk": 15, "def": 8, "spd": 5}', '{"skills": [{"id": "S1", "name": "Flower Power", "desc": "Deals ATK*1.3 damage"}, {"id": "S2", "name": "Heal", "desc": "Restores 20 HP"}]}', '["healer", "gentle"]'),
('WF_004', 'Akane', 'rare', 'https://example.com/akane.png', '{"hp": 150, "atk": 25, "def": 10, "spd": 7}', '{"skills": [{"id": "S1", "name": "Fire Slash", "desc": "Deals ATK*1.5 damage"}, {"id": "S2", "name": "Flame Shield", "desc": "Reduces damage by 25% for 2 turns"}]}', '["warrior", "fiery"]'),
('WF_005', 'Luna', 'epic', 'https://example.com/luna.png', '{"hp": 200, "atk": 35, "def": 15, "spd": 10}', '{"skills": [{"id": "S1", "name": "Moon Beam", "desc": "Deals ATK*2.0 damage"}, {"id": "S2", "name": "Lunar Blessing", "desc": "Increases all stats by 20% for 3 turns"}]}', '["priestess", "mystical"]'),
('WF_006', 'Aria', 'legendary', 'https://example.com/aria.png', '{"hp": 300, "atk": 50, "def": 25, "spd": 15}', '{"skills": [{"id": "S1", "name": "Divine Strike", "desc": "Deals ATK*2.5 damage"}, {"id": "S2", "name": "Celestial Protection", "desc": "Makes user invulnerable for 1 turn"}, {"id": "S3", "name": "Heavenly Light", "desc": "Full party heal + buff"}]}', '["goddess", "divine"]')
ON CONFLICT (code) DO NOTHING;

