"""
Data tables for waifu generation system with image URLs
"""

# Image URLs organized by race, profession, and nationality
# Replace these URLs with your own hosted images

WAIFU_IMAGES_BY_RACE = {
    "Human": [
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/human/Human_1.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/human/Human_2.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/human/Human_3.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/human/Human_4.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/human/Human_5.jpeg",
    ],
    "Elf": [
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/elf/Elf_1.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/elf/Elf_2.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/elf/Elf_3.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/elf/Elf_4.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/elf/Elf_5.jpeg",
    ],
    "Demon": [
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/demon/Demon_1.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/demon/Demon_2.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/demon/Demon_3.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/demon/Demon_4.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/demon/Demon_5.jpeg",
    ],
    "Angel": [
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/angel/Angel_1.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/angel/Angel_2.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/angel/Angel_3.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/angel/Angel_4.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/angel/Angel_5.jpeg",
    ],
    "Vampire": [
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/vampire/Vampire_1.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/vampire/Vampire_2.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/vampire/Vampire_3.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/vampire/Vampire_4.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/vampire/Vampire_5.jpeg",
    ],
    "Dragon": [
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/dragon/Dragon_1.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/dragon/Dragon_2.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/dragon/Dragon_3.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/dragon/Dragon_4.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/dragon/Dragon_5.jpeg",
    ],
    "Beast": [
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/beast/Beast_1.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/beast/Beast_2.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/beast/Beast_3.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/beast/Beast_4.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/beast/Beast_5.jpeg",
    ],
    "Fairy": [
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/fairy/Fairy_1.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/fairy/Fairy_2.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/fairy/Fairy_3.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/fairy/Fairy_4.jpeg",
        "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/fairy/Fairy_5.jpeg",
    ],
}

# Optional: Images by profession for more variety
# Leave empty to use race-based images only
WAIFU_IMAGES_BY_PROFESSION = {}

# Optional: Images by nationality for cultural themes
# Leave empty to use race-based images only
WAIFU_IMAGES_BY_NATIONALITY = {}

# Existing data tables (races, professions, etc.)
RACES = {
    "Human": {"base_power": 10, "base_charm": 10},
    "Elf": {"base_power": 8, "base_charm": 14},
    "Demon": {"base_power": 15, "base_charm": 12},
    "Angel": {"base_power": 12, "base_charm": 15},
    "Vampire": {"base_power": 13, "base_charm": 13},
    "Dragon": {"base_power": 18, "base_charm": 10},
    "Beast": {"base_power": 16, "base_charm": 8},
    "Fairy": {"base_power": 6, "base_charm": 16},
}

PROFESSIONS = {
    "Warrior": {"power_mod": 5, "charm_mod": -2},
    "Mage": {"power_mod": 3, "charm_mod": 2},
    "Assassin": {"power_mod": 4, "charm_mod": 0},
    "Knight": {"power_mod": 4, "charm_mod": 1},
    "Archer": {"power_mod": 3, "charm_mod": 1},
    "Healer": {"power_mod": 1, "charm_mod": 4},
    "Merchant": {"power_mod": 0, "charm_mod": 5},
}

NATIONALITIES = {
    "JP": "Japanese",
    "CN": "Chinese",
    "KR": "Korean",
    "US": "American",
    "GB": "British",
    "FR": "French",
    "DE": "German",
    "IT": "Italian",
    "RU": "Russian",
    "BR": "Brazilian",
    "IN": "Indian",
    "CA": "Canadian",
}

RARITIES = {
    "Common": {"multiplier": 1.0},
    "Uncommon": {"multiplier": 1.2},
    "Rare": {"multiplier": 1.5},
    "Epic": {"multiplier": 2.0},
    "Legendary": {"multiplier": 3.0},
}

STATS_DISTRIBUTION = {
    "Common": {
        "power": (5, 15),
        "charm": (5, 15),
        "luck": (5, 15),
        "affection": (5, 15),
        "intellect": (5, 15),
        "speed": (5, 15)
    },
    "Uncommon": {
        "power": (10, 20),
        "charm": (10, 20),
        "luck": (10, 20),
        "affection": (10, 20),
        "intellect": (10, 20),
        "speed": (10, 20)
    },
    "Rare": {
        "power": (15, 25),
        "charm": (15, 25),
        "luck": (15, 25),
        "affection": (15, 25),
        "intellect": (15, 25),
        "speed": (15, 25)
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

NAMES_BY_NATIONALITY = {
    "JP": ["Sakura", "Yuki", "Hana", "Rei", "Mai", "Ayumi", "Hinata"],
    "CN": ["Mei", "Li", "Hua", "Ying", "Xiu", "Jing", "Yan"],
    "KR": ["Min-ji", "Ji-woo", "Soo-jin", "Hye-jin", "So-young", "Hae-in"],
    "US": ["Emma", "Olivia", "Ava", "Isabella", "Sophia", "Mia"],
    "GB": ["Emily", "Charlotte", "Sophie", "Amelia", "Grace"],
    "FR": ["Camille", "Léa", "Chloé", "Emma", "Manon"],
    "DE": ["Emma", "Hannah", "Mia", "Sophia", "Anna"],
    "IT": ["Sofia", "Giulia", "Aurora", "Alice", "Ginevra"],
    "RU": ["Anastasia", "Maria", "Daria", "Ekaterina", "Polina"],
    "BR": ["Maria", "Ana", "Julia", "Beatriz", "Larissa"],
    "IN": ["Priya", "Ananya", "Diya", "Aanya", "Aadhya", "Shreya"],
    "CA": ["Emma", "Olivia", "Ava", "Charlotte", "Sophia"],
}

TAGS = [
    "shy", "brave", "kind", "mysterious", "cheerful", 
    "cold", "energetic", "calm", "playful", "serious",
    "romantic", "tsundere", "yandere", "kuudere", "dandere",
    "loyal", "independent", "wise", "naive", "cunning",
    "gentle", "fierce", "elegant", "tomboyish", "graceful",
    "adventurous", "homebody", "ambitious", "laid-back",
    "protective", "competitive", "artistic", "intellectual",
    "funny", "stoic", "optimistic", "pessimistic", "sarcastic"
]

# Events and their requirements
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
