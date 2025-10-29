-- Create skills system tables
-- Migration: 010_create_skills_system.sql

-- Table for storing user skill points and progress
CREATE TABLE IF NOT EXISTS user_skills (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    skill_points INTEGER NOT NULL DEFAULT 0,
    total_earned_points INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Table for skill definitions
CREATE TABLE IF NOT EXISTS skills (
    id SERIAL PRIMARY KEY,
    skill_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(20) NOT NULL, -- 'account', 'passive', 'training'
    max_level INTEGER NOT NULL DEFAULT 5,
    base_cost INTEGER NOT NULL DEFAULT 1,
    cost_increase INTEGER NOT NULL DEFAULT 1,
    unlock_requirement INTEGER NOT NULL DEFAULT 0, -- Points needed in category to unlock
    effects JSONB NOT NULL DEFAULT '{}', -- Skill effects per level
    icon VARCHAR(20) NOT NULL DEFAULT '⭐',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for user skill levels
CREATE TABLE IF NOT EXISTS user_skill_levels (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    skill_id VARCHAR(50) NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    level INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, skill_id)
);

-- Table for tracking skill point earnings from chat activity
CREATE TABLE IF NOT EXISTS skill_point_earnings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    points_earned INTEGER NOT NULL,
    source VARCHAR(50) NOT NULL, -- 'chat_message', 'daily_bonus', 'special_event'
    source_details JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert skill definitions
INSERT INTO skills (skill_id, name, description, category, max_level, base_cost, cost_increase, unlock_requirement, effects, icon) VALUES
-- ACCOUNT SKILLS
('gold_mine', 'Золотая жила', 'Увеличивает золото за сообщения в чатах', 'account', 5, 1, 1, 0, '{"1": {"gold_bonus": 0.1}, "2": {"gold_bonus": 0.15}, "3": {"gold_bonus": 0.2}, "4": {"gold_bonus": 0.25}, "5": {"gold_bonus": 0.3}}', '💰'),
('investor', 'Инвестор', 'Увеличивает золото от ежедневного бонуса', 'account', 3, 2, 1, 2, '{"1": {"daily_gold_bonus": 0.05}, "2": {"daily_gold_bonus": 0.1}, "3": {"daily_gold_bonus": 0.15}}', '📈'),
('bargain_hunter', 'Скупщик', 'Скидка на призыв вайфу', 'account', 2, 3, 2, 5, '{"1": {"summon_discount": 0.05}, "2": {"summon_discount": 0.1}}', '🛒'),
('banker', 'Банкир', 'Бонус золота за каждую вайфу в коллекции', 'account', 1, 5, 0, 8, '{"1": {"collection_gold_bonus": 0.01, "max_collection_bonus": 0.5}}', '🏦'),
('experienced_player', 'Опытный игрок', 'Увеличивает опыт за сообщения', 'account', 5, 1, 1, 3, '{"1": {"xp_bonus": 0.2}, "2": {"xp_bonus": 0.4}, "3": {"xp_bonus": 0.6}, "4": {"xp_bonus": 0.8}, "5": {"xp_bonus": 1.0}}', '⚡'),
('wise_mentor', 'Мудрец', 'Увеличивает опыт от ежедневного бонуса', 'account', 3, 2, 1, 6, '{"1": {"daily_xp_bonus": 0.1}, "2": {"daily_xp_bonus": 0.2}, "3": {"daily_xp_bonus": 0.3}}', '🧙'),
('teacher', 'Наставник', 'Бонус опыта за вайфу выше 20 уровня', 'account', 1, 4, 0, 10, '{"1": {"high_level_xp_bonus": 0.05, "max_high_level_bonus": 1.0}}', '👨‍🏫'),
('lucky_novice', 'Удача новичка', 'Увеличивает шанс редкой вайфу при призыве', 'account', 5, 2, 1, 4, '{"1": {"rare_chance": 0.02}, "2": {"rare_chance": 0.04}, "3": {"rare_chance": 0.06}, "4": {"rare_chance": 0.08}, "5": {"rare_chance": 0.1}}', '🍀'),
('summon_mage', 'Маг призыва', 'Увеличивает шанс эпической вайфу при призыве', 'account', 3, 3, 2, 7, '{"1": {"epic_chance": 0.01}, "2": {"epic_chance": 0.02}, "3": {"epic_chance": 0.03}}', '🔮'),
('legend_seeker', 'Легенда', 'Увеличивает шанс легендарной вайфу при призыве', 'account', 2, 5, 3, 12, '{"1": {"legendary_chance": 0.005}, "2": {"legendary_chance": 0.01}}', '👑'),

-- PASSIVE WAIFU SKILLS
('loyalty', 'Верность', 'Увеличивает бонус к силе от лояльности', 'passive', 5, 1, 1, 0, '{"1": {"loyalty_power_bonus": 0.2}, "2": {"loyalty_power_bonus": 0.4}, "3": {"loyalty_power_bonus": 0.6}, "4": {"loyalty_power_bonus": 0.8}, "5": {"loyalty_power_bonus": 1.0}}', '❤️'),
('joy', 'Радость', 'Увеличивает бонус к силе от настроения', 'passive', 5, 1, 1, 2, '{"1": {"mood_power_bonus": 0.15}, "2": {"mood_power_bonus": 0.3}, "3": {"mood_power_bonus": 0.45}, "4": {"mood_power_bonus": 0.6}, "5": {"mood_power_bonus": 0.75}}', '😊'),
('trust', 'Доверие', 'Увеличивает скорость роста лояльности', 'passive', 3, 2, 1, 5, '{"1": {"loyalty_growth": 0.1}, "2": {"loyalty_growth": 0.2}, "3": {"loyalty_growth": 0.3}}', '🤝'),
('optimism', 'Оптимизм', 'Увеличивает скорость восстановления настроения', 'passive', 3, 2, 1, 8, '{"1": {"mood_recovery": 0.05}, "2": {"mood_recovery": 0.1}, "3": {"mood_recovery": 0.15}}', '☀️'),
('battery', 'Батарейка', 'Увеличивает максимальную энергию всех вайфу', 'passive', 5, 2, 1, 3, '{"1": {"max_energy": 20}, "2": {"max_energy": 40}, "3": {"max_energy": 60}, "4": {"max_energy": 80}, "5": {"max_energy": 100}}', '🔋'),
('regeneration', 'Регенерация', 'Увеличивает скорость восстановления энергии', 'passive', 3, 2, 1, 6, '{"1": {"energy_recovery": 0.1}, "2": {"energy_recovery": 0.2}, "3": {"energy_recovery": 0.3}}', '🔄'),
('endurance', 'Неутомимость', 'Уменьшает расход энергии на действия', 'passive', 3, 3, 1, 9, '{"1": {"energy_cost_reduction": 0.2}, "2": {"energy_cost_reduction": 0.4}, "3": {"energy_cost_reduction": 0.6}}', '💪'),
('mentor', 'Ментор', 'Увеличивает опыт для вайфу при улучшении', 'passive', 5, 2, 1, 4, '{"1": {"upgrade_xp_bonus": 0.25}, "2": {"upgrade_xp_bonus": 0.5}, "3": {"upgrade_xp_bonus": 0.75}, "4": {"upgrade_xp_bonus": 1.0}, "5": {"upgrade_xp_bonus": 1.25}}', '👨‍🏫'),
('golden_hand', 'Золотая рука', 'Увеличивает золото от вайфу за действия', 'passive', 3, 2, 1, 7, '{"1": {"waifu_gold_bonus": 0.1}, "2": {"waifu_gold_bonus": 0.2}, "3": {"waifu_gold_bonus": 0.3}}', '🤲'),
('synergy', 'Синергия', 'Увеличивает силу за каждую вайфу в избранном', 'passive', 1, 4, 0, 10, '{"1": {"favorite_power_bonus": 0.05, "max_favorite_bonus": 0.5}}', '🔗'),

-- TRAINING WAIFU SKILLS
('spiritual_strength', 'Сила духа', 'Увеличивает силу всех вайфу', 'training', 5, 2, 1, 0, '{"1": {"power_bonus": 0.1}, "2": {"power_bonus": 0.2}, "3": {"power_bonus": 0.3}, "4": {"power_bonus": 0.4}, "5": {"power_bonus": 0.5}}', '💪'),
('mental_acuity', 'Острота ума', 'Увеличивает интеллект всех вайфу', 'training', 5, 2, 1, 3, '{"1": {"intellect_bonus": 0.1}, "2": {"intellect_bonus": 0.2}, "3": {"intellect_bonus": 0.3}, "4": {"intellect_bonus": 0.4}, "5": {"intellect_bonus": 0.5}}', '🧠'),
('magnetism', 'Магнетизм', 'Увеличивает обаяние всех вайфу', 'training', 5, 2, 1, 6, '{"1": {"charm_bonus": 0.1}, "2": {"charm_bonus": 0.2}, "3": {"charm_bonus": 0.3}, "4": {"charm_bonus": 0.4}, "5": {"charm_bonus": 0.5}}', '✨'),
('agility', 'Ловкость', 'Увеличивает ловкость всех вайфу', 'training', 5, 2, 1, 9, '{"1": {"dexterity_bonus": 0.1}, "2": {"dexterity_bonus": 0.2}, "3": {"dexterity_bonus": 0.3}, "4": {"dexterity_bonus": 0.4}, "5": {"dexterity_bonus": 0.5}}', '🎯'),
('fortune', 'Фортуна', 'Увеличивает удачу всех вайфу', 'training', 3, 3, 1, 12, '{"1": {"luck_bonus": 0.15}, "2": {"luck_bonus": 0.3}, "3": {"luck_bonus": 0.45}}', '🍀'),
('speed', 'Скорость', 'Увеличивает скорость всех вайфу', 'training', 3, 3, 1, 15, '{"1": {"speed_bonus": 0.15}, "2": {"speed_bonus": 0.3}, "3": {"speed_bonus": 0.45}}', '⚡'),
('stamina', 'Выносливость', 'Увеличивает максимальное здоровье всех вайфу', 'training', 3, 3, 1, 18, '{"1": {"health_bonus": 0.2}, "2": {"health_bonus": 0.4}, "3": {"health_bonus": 0.6}}', '❤️‍🩹'),
('elite', 'Элита', 'Увеличивает силу редких и выше вайфу', 'training', 2, 4, 2, 21, '{"1": {"rare_power_bonus": 0.25}, "2": {"rare_power_bonus": 0.5}}', '👑'),
('legend', 'Легенда', 'Увеличивает силу эпических и легендарных вайфу', 'training', 2, 5, 3, 25, '{"1": {"epic_power_bonus": 0.5}, "2": {"epic_power_bonus": 1.0}}', '🌟'),
('harmony', 'Гармония', 'Увеличивает все характеристики за каждую редкость в коллекции', 'training', 1, 6, 0, 30, '{"1": {"rarity_bonus": 0.05, "max_rarity_bonus": 0.25}}', '🎵');

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_skills_user_id ON user_skills(user_id);
CREATE INDEX IF NOT EXISTS idx_user_skill_levels_user_id ON user_skill_levels(user_id);
CREATE INDEX IF NOT EXISTS idx_user_skill_levels_skill_id ON user_skill_levels(skill_id);
CREATE INDEX IF NOT EXISTS idx_skill_point_earnings_user_id ON skill_point_earnings(user_id);
CREATE INDEX IF NOT EXISTS idx_skill_point_earnings_created_at ON skill_point_earnings(created_at);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_user_skills_updated_at BEFORE UPDATE ON user_skills FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_skill_levels_updated_at BEFORE UPDATE ON user_skill_levels FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
