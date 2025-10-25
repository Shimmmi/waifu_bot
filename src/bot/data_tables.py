"""
Data tables for waifu generation system with image URLs
"""

# Image URLs organized by race, profession, and nationality
# Replace these URLs with your own hosted images

WAIFU_IMAGES_BY_RACE = {
    "Human": [
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Human1",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Human2",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Human3",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Human4",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Human5",
    ],
    "Elf": [
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Elf1",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Elf2",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Elf3",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Elf4",
    ],
    "Demon": [
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Demon1",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Demon2",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Demon3",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Demon4",
    ],
    "Angel": [
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Angel1",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Angel2",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Angel3",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Angel4",
    ],
    "Vampire": [
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Vampire1",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Vampire2",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Vampire3",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Vampire4",
    ],
    "Dragon": [
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Dragon1",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Dragon2",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Dragon3",
    ],
    "Beast": [
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Beast1",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Beast2",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Beast3",
    ],
    "Fairy": [
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Fairy1",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Fairy2",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Fairy3",
    ],
}

# Optional: Images by profession for more variety
WAIFU_IMAGES_BY_PROFESSION = {
    "Warrior": [
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Warrior1",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Warrior2",
    ],
    "Mage": [
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Mage1",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Mage2",
    ],
    "Assassin": [
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Assassin1",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Assassin2",
    ],
    "Knight": [
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Knight1",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Knight2",
    ],
    "Archer": [
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Archer1",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Archer2",
    ],
    "Healer": [
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Healer1",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Healer2",
    ],
    "Merchant": [
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Merchant1",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Merchant2",
    ],
}

# Optional: Images by nationality for cultural themes
WAIFU_IMAGES_BY_NATIONALITY = {
    "JP": [  # Japanese
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Japanese1",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Japanese2",
    ],
    "CN": [  # Chinese
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Chinese1",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Chinese2",
    ],
    "KR": [  # Korean
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Korean1",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Korean2",
    ],
    "US": [  # American
        "https://api.dicebear.com/7.x/adventurer/svg?seed=American1",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=American2",
    ],
    "GB": [  # British
        "https://api.dicebear.com/7.x/adventurer/svg?seed=British1",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=British2",
    ],
    "FR": [  # French
        "https://api.dicebear.com/7.x/adventurer/svg?seed=French1",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=French2",
    ],
    "DE": [  # German
        "https://api.dicebear.com/7.x/adventurer/svg?seed=German1",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=German2",
    ],
    "IT": [  # Italian
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Italian1",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Italian2",
    ],
    "RU": [  # Russian
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Russian1",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Russian2",
    ],
    "BR": [  # Brazilian
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Brazilian1",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Brazilian2",
    ],
    "IN": [  # Indian
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Indian1",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Indian2",
    ],
    "CA": [  # Canadian
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Canadian1",
        "https://api.dicebear.com/7.x/adventurer/svg?seed=Canadian2",
    ],
}

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
    "Common": {"min": 5, "max": 15},
    "Uncommon": {"min": 10, "max": 20},
    "Rare": {"min": 15, "max": 25},
    "Epic": {"min": 20, "max": 35},
    "Legendary": {"min": 30, "max": 50},
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
