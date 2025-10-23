# Таблицы данных для генерации вайфу

RACES = [
    "Human", "Elf", "Demon", "Angel", "Beastkin", 
    "Cyborg", "Fairy", "Vampire", "Dragon", "Spirit"
]

PROFESSIONS = [
    "Idol", "Baker", "Warrior", "Mage", "Scholar", 
    "Assassin", "Artist", "Nurse", "Chef", "Dancer",
    "Singer", "Teacher", "Engineer", "Doctor", "Knight"
]

NATIONALITIES = [
    "JP", "RU", "US", "KR", "CN", "EU", "IN", "BR", "CA", "AU"
]

RARITIES = {
    "Common": 1, 
    "Uncommon": 2, 
    "Rare": 3, 
    "Epic": 4, 
    "Legendary": 5
}

# Распределение характеристик по редкости
STATS_DISTRIBUTION = {
    "Common": {
        "power": (5, 15), 
        "charm": (5, 10), 
        "luck": (5, 10), 
        "affection": (5, 10),
        "intellect": (5, 10),
        "speed": (5, 10)
    },
    "Uncommon": {
        "power": (10, 20), 
        "charm": (10, 15), 
        "luck": (10, 15), 
        "affection": (10, 15),
        "intellect": (10, 15),
        "speed": (10, 15)
    },
    "Rare": {
        "power": (15, 25), 
        "charm": (15, 25), 
        "luck": (15, 20), 
        "affection": (15, 20),
        "intellect": (15, 20),
        "speed": (15, 20)
    },
    "Epic": {
        "power": (20, 35), 
        "charm": (20, 35), 
        "luck": (20, 30), 
        "affection": (20, 30),
        "intellect": (20, 30),
        "speed": (20, 30)
    },
    "Legendary": {
        "power": (30, 45), 
        "charm": (30, 45), 
        "luck": (30, 40), 
        "affection": (30, 40),
        "intellect": (30, 40),
        "speed": (30, 40)
    }
}

# События и их требования
EVENTS = {
    "dance": {
        "base_stats": ["charm", "speed", "luck"], 
        "profession_bonus": "Dancer",
        "name": "Танцевальный конкурс",
        "description": "Покажи свои танцевальные навыки!"
    },
    "hunt": {
        "base_stats": ["power", "speed", "luck"], 
        "profession_bonus": "Warrior",
        "name": "Охота на монстров",
        "description": "Сражайся с опасными существами!"
    },
    "quiz": {
        "base_stats": ["intellect", "charm", "luck"], 
        "profession_bonus": "Scholar",
        "name": "Интеллектуальная викторина",
        "description": "Проверь свои знания!"
    },
    "cooking": {
        "base_stats": ["intellect", "charm", "luck"], 
        "profession_bonus": "Chef",
        "name": "Кулинарный конкурс",
        "description": "Приготовь самое вкусное блюдо!"
    },
    "singing": {
        "base_stats": ["charm", "intellect", "luck"], 
        "profession_bonus": "Singer",
        "name": "Вокальный конкурс",
        "description": "Покажи свой голос!"
    }
}

# Имена для генерации
NAMES_BY_NATIONALITY = {
    "JP": ["Sakura", "Yuki", "Hana", "Akane", "Luna", "Aria", "Miku", "Rei", "Asuka", "Mai"],
    "RU": ["Anastasia", "Katya", "Svetlana", "Natasha", "Irina", "Olga", "Maria", "Elena", "Anna", "Daria"],
    "US": ["Emma", "Olivia", "Sophia", "Isabella", "Ava", "Mia", "Charlotte", "Amelia", "Harper", "Evelyn"],
    "KR": ["Ji-eun", "Min-jung", "So-young", "Hye-jin", "Eun-jung", "Ji-hye", "Seo-yeon", "Min-ji", "Ji-woo", "Hae-in"],
    "CN": ["Mei", "Ling", "Xia", "Wei", "Jing", "Li", "Fang", "Hui", "Lan", "Yan"],
    "EU": ["Sophie", "Marie", "Claire", "Emma", "Anna", "Lisa", "Sarah", "Julia", "Nina", "Elena"],
    "IN": ["Priya", "Kavya", "Ananya", "Shreya", "Isha", "Riya", "Aanya", "Sneha", "Pooja", "Divya"],
    "BR": ["Ana", "Maria", "Julia", "Fernanda", "Camila", "Beatriz", "Larissa", "Gabriela", "Isabella", "Leticia"],
    "CA": ["Emma", "Olivia", "Charlotte", "Sophia", "Isabella", "Ava", "Mia", "Amelia", "Harper", "Evelyn"],
    "AU": ["Charlotte", "Olivia", "Amelia", "Isla", "Mia", "Ava", "Grace", "Willow", "Freya", "Chloe"]
}

# Теги для вайфу
TAGS = [
    "cute", "cool", "mysterious", "energetic", "calm", "playful", 
    "serious", "romantic", "adventurous", "shy", "confident", 
    "loyal", "independent", "caring", "funny", "elegant"
]
