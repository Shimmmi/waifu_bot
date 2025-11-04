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
    "JP": [
        "Sakura", "Yuki", "Hana", "Rei", "Mai", "Ayumi", "Hinata", "Akari", "Chika", "Elena",
        "Fumiko", "Haruka", "Iroha", "Kaede", "Kiko", "Momoka", "Nana", "Osaki", "Rin",
        "Saki", "Tomomi", "Umi", "Yuna", "Aiko", "Botan", "Chiyo", "Emi", "Fuka", "Haru",
        "Ichika", "Juri", "Kana", "Luna", "Mio", "Nanami", "Oriko", "Riko", "Satsuki",
        "Tsubaki", "Ume", "Yoshino", "Akane", "Ayame", "Chiyoko", "Eri", "Fubuki", "Hotaru",
        "Ibuki", "Kazumi", "Midori"
    ],
    "CN": [
        "Mei", "Li", "Hua", "Ying", "Xiu", "Jing", "Yan", "Bai", "Chen", "Dai",
        "Fang", "Guan", "Hong", "Jia", "Kai", "Lan", "Ming", "Ning", "Peng",
        "Qian", "Rui", "Shan", "Tao", "Wei", "Xia", "Ye", "Zhen", "An", "Bing",
        "Cai", "Dan", "En", "Fei", "Gao", "Hui", "In", "Jin", "Ke", "Lian",
        "Mei-Li", "Na", "Ou", "Pei", "Qi", "Ran", "Shui", "Tang", "U", "Ve", "Wen"
    ],
    "KR": [
        "Min-ji", "Ji-woo", "Soo-jin", "Hye-jin", "So-young", "Hae-in", "Bo-ra", "Chae-won", "Da-eun", "Eun-bi",
        "Ga-young", "Ha-yoon", "I-seul", "Jae-ah", "Kang-mi", "Lee-na", "Mi-sun", "Na-young", "Ok-ju", "Park-seo",
        "Ra-ae", "Seo-yeon", "Tae-hee", "U-ri", "Ye-jin", "Yoo-na", "Ae-cha", "Bae-su", "Chin-ae", "Dae-ri",
        "Eun-ah", "Geu-roo", "Hae-rin", "Il-mae", "Jia-ae", "Kyong-ja", "Min-seo", "Nayoon", "Ok-ran", "Pil-gyu",
        "Ri-na", "Seong-mi", "Tae-im", "Un-mi", "Yeon-mi", "Yoo-ri", "A-ran", "Bin-na", "Cha-rin", "Doh-un"
    ],
    "US": [
        "Emma", "Olivia", "Ava", "Isabella", "Sophia", "Mia", "Charlotte", "Amelia", "Harper", "Evelyn",
        "Abigail", "Emily", "Elizabeth", "Mila", "Ella", "Avery", "Sofia", "Camila", "Aria", "Scarlett",
        "Victoria", "Madison", "Luna", "Grace", "Chloe", "Penelope", "Layla", "Riley", "Zoey", "Nora",
        "Lily", "Eleanor", "Hannah", "Lillian", "Addison", "Aubrey", "Ellie", "Stella", "Natalie", "Zoe",
        "Leah", "Hazel", "Violet", "Aurora", "Savannah", "Audrey", "Brooklyn", "Bella", "Claire", "Skylar"
    ],
    "GB": [
        "Emily", "Charlotte", "Sophie", "Amelia", "Grace", "Olivia", "Jessica", "Sophia", "Isabella", "Lily",
        "Ella", "Mia", "Ruby", "Poppy", "Freya", "Florence", "Evie", "Willow", "Isla", "Rosie",
        "Phoebe", "Georgia", "Matilda", "Harriet", "Maya", "Ava", "Eva", "Luna", "Rose", "Esme",
        "Hannah", "Lucy", "Grace", "Alice", "Flora", "Violet", "Sienna", "Chloe", "Zara", "Elsie",
        "Anna", "Emma", "Tilly", "Iris", "Thea", "Bonnie", "Nancy", "Erin", "Holly", "Lottie"
    ],
    "FR": [
        "Camille", "Léa", "Chloé", "Emma", "Manon", "Sarah", "Inès", "Lola", "Jade", "Marie",
        "Anaïs", "Louise", "Romane", "Mila", "Ambre", "Rose", "Julia", "Alice", "Anna", "Zoé",
        "Lucie", "Jeanne", "Léna", "Pauline", "Margot", "Lina", "Elise", "Olivia", "Eva", "Giulia",
        "Clara", "Sophie", "Raphaëlle", "Laura", "Alicia", "Élise", "Luna", "Charlotte", "Garance", "Inaya",
        "Victoire", "Sara", "Capucine", "Valentine", "Lou", "Juliette", "Amélie", "Éva", "Lise", "Maëlys"
    ],
    "DE": [
        "Emma", "Hannah", "Mia", "Sophia", "Anna", "Marie", "Emilia", "Mila", "Lina", "Leni",
        "Ella", "Clara", "Mathilda", "Frieda", "Luise", "Greta", "Lilly", "Paula", "Maya", "Nora",
        "Amelie", "Lia", "Leni", "Helena", "Charlotte", "Ida", "Leonie", "Luisa", "Emely", "Elisa",
        "Lotta", "Melina", "Isabella", "Thea", "Nele", "Finja", "Antonia", "Laura", "Leni", "Alina",
        "Marlene", "Stella", "Olivia", "Amalia", "Helene", "Marie", "Elena", "Malina", "Lea", "Mathilde"
    ],
    "IT": [
        "Sofia", "Giulia", "Aurora", "Alice", "Ginevra", "Beatrice", "Emma", "Giorgia", "Vittoria", "Matilde",
        "Francesca", "Anna", "Bianca", "Noemi", "Greta", "Isabella", "Nicole", "Alessia", "Elisa", "Camilla",
        "Chiara", "Ludovica", "Martina", "Margherita", "Arianna", "Gaia", "Cecilia", "Rebecca", "Sara", "Emma",
        "Valentina", "Viola", "Azur", "Carolina", "Linda", "Lucia", "Rosa", "Luna", "Asia", "Elena",
        "Eva", "Lara", "Miriam", "Olivia", "Paola", "Rachele", "Serena", "Stella", "Sveva", "Teresa"
    ],
    "RU": [
        "Anastasia", "Maria", "Daria", "Ekaterina", "Polina", "Viktoria", "Ksenia", "Anastasiya", "Anna", "Sophia",
        "Alisa", "Arina", "Kristina", "Elizaveta", "Yelena", "Irina", "Natalia", "Olga", "Tatiana", "Yulia",
        "Alexandra", "Veronika", "Valeria", "Milana", "Margarita", "Vera", "Sofia", "Angelina", "Yana", "Karina",
        "Diana", "Mariya", "Anastasiia", "Yulia", "Elizaveta", "Varvara", "Liza", "Alina", "Mila", "Zoya",
        "Nadezhda", "Svetlana", "Taisiya", "Valentina", "Lilia", "Galina", "Lyudmila", "Raisa", "Larisa", "Tanya"
    ],
    "BR": [
        "Maria", "Ana", "Julia", "Beatriz", "Larissa", "Gabriela", "Fernanda", "Mariana", "Carolina", "Amanda",
        "Priscila", "Camila", "Bruna", "Patricia", "Vanessa", "Renata", "Cristina", "Leticia", "Roberta", "Isabela",
        "Daniela", "Juliana", "Julieta", "Pamela", "Samantha", "Tatiana", "Thais", "Valentina", "Victoria", "Yasmin",
        "Adriana", "Bianca", "Carla", "Diana", "Elaine", "Fabiana", "Giovanna", "Helena", "Ingrid", "Joana",
        "Karina", "Larissa", "Marina", "Natasha", "Paula", "Raquel", "Sandra", "Tais", "Ursula", "Vania"
    ],
    "IN": [
        "Priya", "Ananya", "Diya", "Aanya", "Aadhya", "Shreya", "Arushi", "Avni", "Ishani", "Kavya",
        "Meera", "Niya", "Riya", "Saanvi", "Tanya", "Urvi", "Vanya", "Aditi", "Amisha", "Bhumika",
        "Charvi", "Devika", "Esha", "Fatima", "Gauri", "Harsha", "Indira", "Juhi", "Khushi", "Lavanya",
        "Mahika", "Naina", "Ojasvi", "Pari", "Rashi", "Samaira", "Tara", "Uma", "Veda", "Yashika",
        "Zara", "Aarohi", "Bhavya", "Chhavi", "Disha", "Ekta", "Falguni", "Gayatri", "Hamsika", "Ishika"
    ],
    "CA": [
        "Emma", "Olivia", "Ava", "Charlotte", "Sophia", "Isabella", "Mia", "Amelia", "Harper", "Evelyn",
        "Abigail", "Emily", "Ella", "Elizabeth", "Camila", "Luna", "Sofia", "Avery", "Mila", "Scarlett",
        "Victoria", "Madison", "Lily", "Grace", "Chloe", "Penelope", "Layla", "Riley", "Zoey", "Nora",
        "Eleanor", "Hannah", "Lillian", "Addison", "Aubrey", "Ellie", "Stella", "Natalie", "Zoe", "Leah",
        "Hazel", "Violet", "Aurora", "Savannah", "Audrey", "Brooklyn", "Bella", "Claire", "Skylar", "Lucy"
    ],
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
    # Legacy events (backward compatibility)
    "dance": {
        "base_stats": ["charm", "speed", "luck"], 
        "profession_bonus": "Dancer",
        "name": "Танцевальный конкурс",
        "description": "Покажи свои танцевальные навыки!",
        "filter_type": "none",
        "sort_by": "power"
    },
    "hunt": {
        "base_stats": ["power", "speed", "luck"], 
        "profession_bonus": "Warrior",
        "name": "Охота на монстров",
        "description": "Сражайся с опасными существами!",
        "filter_type": "none",
        "sort_by": "power"
    },
    "quiz": {
        "base_stats": ["intellect", "charm", "luck"], 
        "profession_bonus": "Scholar",
        "name": "Интеллектуальная викторина",
        "description": "Проверь свои знания!",
        "filter_type": "none",
        "sort_by": "power"
    },
    "cooking": {
        "base_stats": ["intellect", "charm", "luck"], 
        "profession_bonus": "Chef",
        "name": "Кулинарный конкурс",
        "description": "Приготовь самое вкусное блюдо!",
        "filter_type": "none",
        "sort_by": "power"
    },
    "singing": {
        "base_stats": ["charm", "intellect", "luck"], 
        "profession_bonus": "Singer",
        "name": "Вокальный конкурс",
        "description": "Покажи свой голос!",
        "filter_type": "none",
        "sort_by": "power"
    },
    
    # Overall Power events
    "power_arena": {
        "base_stats": ["power", "charm", "intellect", "speed", "luck", "affection"],
        "profession_bonus": None,
        "name": "Арена силы",
        "description": "Проверка общей мощи вайфу",
        "filter_type": "none",
        "sort_by": "power"
    },
    "total_combat": {
        "base_stats": ["power", "charm", "intellect", "speed", "luck", "affection"],
        "profession_bonus": None,
        "name": "Общий бой",
        "description": "Сражение с использованием всех навыков",
        "filter_type": "none",
        "sort_by": "power"
    },
    "grand_tournament": {
        "base_stats": ["power", "charm", "intellect", "speed", "luck", "affection"],
        "profession_bonus": None,
        "name": "Большой турнир",
        "description": "Турнир, требующий всесторонней подготовки",
        "filter_type": "none",
        "sort_by": "power"
    },
    "ultimate_challenge": {
        "base_stats": ["power", "charm", "intellect", "speed", "luck", "affection"],
        "profession_bonus": None,
        "name": "Финальный вызов",
        "description": "Испытание для самых сильных вайфу",
        "filter_type": "none",
        "sort_by": "power"
    },
    
    # Race-specific events
    "elf_magic_contest": {
        "base_stats": ["intellect", "charm", "luck"],
        "profession_bonus": "Mage",
        "name": "Магический конкурс эльфов",
        "description": "Демонстрация магических способностей эльфов",
        "filter_type": "race",
        "filter_value": "Elf",
        "sort_by": "power"
    },
    "demon_dark_tournament": {
        "base_stats": ["power", "intellect", "luck"],
        "profession_bonus": "Warrior",
        "name": "Темный турнир демонов",
        "description": "Соревнование силы и темной магии",
        "filter_type": "race",
        "filter_value": "Demon",
        "sort_by": "power"
    },
    "angel_divine_ceremony": {
        "base_stats": ["charm", "intellect", "luck"],
        "profession_bonus": "Healer",
        "name": "Божественная церемония",
        "description": "Проверка чистоты и силы ангелов",
        "filter_type": "race",
        "filter_value": "Angel",
        "sort_by": "power"
    },
    "vampire_night_ball": {
        "base_stats": ["charm", "speed", "luck"],
        "profession_bonus": "Assassin",
        "name": "Ночной бал вампиров",
        "description": "Элегантное соревнование в ночи",
        "filter_type": "race",
        "filter_value": "Vampire",
        "sort_by": "power"
    },
    "dragon_flight_race": {
        "base_stats": ["power", "speed", "luck"],
        "profession_bonus": "Warrior",
        "name": "Гонка драконов",
        "description": "Испытание скорости и силы драконов",
        "filter_type": "race",
        "filter_value": "Dragon",
        "sort_by": "power"
    },
    "beast_wild_hunt": {
        "base_stats": ["power", "speed", "luck"],
        "profession_bonus": "Warrior",
        "name": "Дикая охота",
        "description": "Проверка инстинктов и силы зверей",
        "filter_type": "race",
        "filter_value": "Beast",
        "sort_by": "power"
    },
    "fairy_enchantment_show": {
        "base_stats": ["charm", "intellect", "luck"],
        "profession_bonus": "Mage",
        "name": "Шоу очарования фей",
        "description": "Демонстрация магии и красоты фей",
        "filter_type": "race",
        "filter_value": "Fairy",
        "sort_by": "power"
    },
    "human_worldly_skills": {
        "base_stats": ["power", "charm", "intellect", "speed", "luck", "affection"],
        "profession_bonus": None,
        "name": "Мирские навыки",
        "description": "Проверка разнообразия навыков людей",
        "filter_type": "race",
        "filter_value": "Human",
        "sort_by": "power"
    },
    
    # Profession-specific events
    "warrior_melee_tournament": {
        "base_stats": ["power", "speed", "luck"],
        "profession_bonus": "Warrior",
        "name": "Турнир ближнего боя",
        "description": "Сражение на мечах и щитах",
        "filter_type": "profession",
        "filter_value": "Warrior",
        "sort_by": "power"
    },
    "mage_spell_casting": {
        "base_stats": ["intellect", "charm", "luck"],
        "profession_bonus": "Mage",
        "name": "Турнир заклинателей",
        "description": "Соревнование в магических способностях",
        "filter_type": "profession",
        "filter_value": "Mage",
        "sort_by": "power"
    },
    "assassin_shadow_contest": {
        "base_stats": ["speed", "power", "luck"],
        "profession_bonus": "Assassin",
        "name": "Конкурс теней",
        "description": "Испытание скрытности и ловкости",
        "filter_type": "profession",
        "filter_value": "Assassin",
        "sort_by": "power"
    },
    "knight_honor_duel": {
        "base_stats": ["power", "charm", "luck"],
        "profession_bonus": "Knight",
        "name": "Рыцарский поединок",
        "description": "Поединок чести и доблести",
        "filter_type": "profession",
        "filter_value": "Knight",
        "sort_by": "power"
    },
    "archer_precision_contest": {
        "base_stats": ["speed", "power", "luck"],
        "profession_bonus": "Archer",
        "name": "Конкурс точности",
        "description": "Проверка меткости и скорости",
        "filter_type": "profession",
        "filter_value": "Archer",
        "sort_by": "power"
    },
    "healer_healing_competition": {
        "base_stats": ["intellect", "charm", "luck"],
        "profession_bonus": "Healer",
        "name": "Соревнование целителей",
        "description": "Проверка навыков исцеления",
        "filter_type": "profession",
        "filter_value": "Healer",
        "sort_by": "power"
    },
    "merchant_trading_challenge": {
        "base_stats": ["charm", "intellect", "luck"],
        "profession_bonus": "Merchant",
        "name": "Торговое испытание",
        "description": "Проверка навыков торговли",
        "filter_type": "profession",
        "filter_value": "Merchant",
        "sort_by": "power"
    },
    
    # Nationality-specific events
    "japanese_tradition_festival": {
        "base_stats": ["charm", "intellect", "luck"],
        "profession_bonus": None,
        "name": "Фестиваль традиций",
        "description": "Демонстрация японской культуры",
        "filter_type": "nationality",
        "filter_value": "JP",
        "sort_by": "power"
    },
    "chinese_martial_arts": {
        "base_stats": ["power", "speed", "luck"],
        "profession_bonus": "Warrior",
        "name": "Турнир боевых искусств",
        "description": "Проверка навыков боевых искусств",
        "filter_type": "nationality",
        "filter_value": "CN",
        "sort_by": "power"
    },
    "korean_kpop_showcase": {
        "base_stats": ["charm", "speed", "luck"],
        "profession_bonus": None,
        "name": "K-pop шоукейс",
        "description": "Соревнование в танцах и пении",
        "filter_type": "nationality",
        "filter_value": "KR",
        "sort_by": "power"
    },
    "american_superhero_contest": {
        "base_stats": ["power", "charm", "luck"],
        "profession_bonus": None,
        "name": "Конкурс супергероев",
        "description": "Проверка силы и героизма",
        "filter_type": "nationality",
        "filter_value": "US",
        "sort_by": "power"
    },
    "british_royal_gala": {
        "base_stats": ["charm", "intellect", "luck"],
        "profession_bonus": None,
        "name": "Королевский гала",
        "description": "Элегантное соревнование",
        "filter_type": "nationality",
        "filter_value": "GB",
        "sort_by": "power"
    },
    "french_art_salon": {
        "base_stats": ["charm", "intellect", "luck"],
        "profession_bonus": None,
        "name": "Салон искусств",
        "description": "Демонстрация художественных талантов",
        "filter_type": "nationality",
        "filter_value": "FR",
        "sort_by": "power"
    },
    "german_engineering_show": {
        "base_stats": ["intellect", "power", "luck"],
        "profession_bonus": None,
        "name": "Выставка инженерии",
        "description": "Проверка интеллекта и точности",
        "filter_type": "nationality",
        "filter_value": "DE",
        "sort_by": "power"
    },
    "italian_culinary_master": {
        "base_stats": ["intellect", "charm", "luck"],
        "profession_bonus": None,
        "name": "Кулинарный мастер",
        "description": "Соревнование в кулинарии",
        "filter_type": "nationality",
        "filter_value": "IT",
        "sort_by": "power"
    },
    "russian_winter_games": {
        "base_stats": ["power", "speed", "luck"],
        "profession_bonus": None,
        "name": "Зимние игры",
        "description": "Испытание силы и выносливости",
        "filter_type": "nationality",
        "filter_value": "RU",
        "sort_by": "power"
    },
    "brazilian_carnival_dance": {
        "base_stats": ["charm", "speed", "luck"],
        "profession_bonus": None,
        "name": "Карнавальный танец",
        "description": "Проверка танцевальных навыков",
        "filter_type": "nationality",
        "filter_value": "BR",
        "sort_by": "power"
    },
    "indian_spiritual_quest": {
        "base_stats": ["intellect", "charm", "luck"],
        "profession_bonus": None,
        "name": "Духовный квест",
        "description": "Проверка мудрости и духовности",
        "filter_type": "nationality",
        "filter_value": "IN",
        "sort_by": "power"
    },
    "canadian_wilderness_race": {
        "base_stats": ["power", "speed", "luck"],
        "profession_bonus": None,
        "name": "Гонка в дикой природе",
        "description": "Испытание выживания и силы",
        "filter_type": "nationality",
        "filter_value": "CA",
        "sort_by": "power"
    },
    
    # Rarity-specific events
    "common_rookie_arena": {
        "base_stats": ["power", "charm", "intellect", "speed", "luck", "affection"],
        "profession_bonus": None,
        "name": "Арена новичков",
        "description": "Событие для начинающих вайфу",
        "filter_type": "rarity",
        "filter_value": "Common",
        "rarity_min": "Common",
        "sort_by": "power"
    },
    "uncommon_rising_stars": {
        "base_stats": ["power", "charm", "intellect", "speed", "luck", "affection"],
        "profession_bonus": None,
        "name": "Восходящие звезды",
        "description": "Турнир для развивающихся вайфу",
        "filter_type": "rarity",
        "filter_value": "Uncommon",
        "rarity_min": "Uncommon",
        "sort_by": "power"
    },
    "rare_elite_tournament": {
        "base_stats": ["power", "charm", "intellect", "speed", "luck", "affection"],
        "profession_bonus": None,
        "name": "Элитный турнир",
        "description": "Соревнование для редких вайфу",
        "filter_type": "rarity",
        "filter_value": "Rare",
        "rarity_min": "Rare",
        "sort_by": "power"
    },
    "epic_legendary_battle": {
        "base_stats": ["power", "charm", "intellect", "speed", "luck", "affection"],
        "profession_bonus": None,
        "name": "Легендарная битва",
        "description": "Испытание для эпических вайфу",
        "filter_type": "rarity",
        "filter_value": "Epic",
        "rarity_min": "Epic",
        "sort_by": "power"
    },
    "legendary_ultimate_showdown": {
        "base_stats": ["power", "charm", "intellect", "speed", "luck", "affection"],
        "profession_bonus": None,
        "name": "Финальная схватка",
        "description": "Вызов только для легендарных вайфу",
        "filter_type": "rarity",
        "filter_value": "Legendary",
        "rarity_min": "Legendary",
        "sort_by": "power"
    },
    
    # Primary Stat Challenges - Power
    "strength_arena": {
        "base_stats": ["power"],
        "profession_bonus": "Warrior",
        "name": "Арена силы",
        "description": "Проверка физической силы",
        "filter_type": "none",
        "sort_by": "power_stat"
    },
    "power_lifting_contest": {
        "base_stats": ["power"],
        "profession_bonus": "Warrior",
        "name": "Соревнование по тяжелой атлетике",
        "description": "Поднятие тяжестей",
        "filter_type": "none",
        "sort_by": "power_stat"
    },
    "might_tournament": {
        "base_stats": ["power"],
        "profession_bonus": "Warrior",
        "name": "Турнир могущества",
        "description": "Испытание силы",
        "filter_type": "none",
        "sort_by": "power_stat"
    },
    "brute_force_challenge": {
        "base_stats": ["power"],
        "profession_bonus": "Warrior",
        "name": "Вызов грубой силы",
        "description": "Проверка физической мощи",
        "filter_type": "none",
        "sort_by": "power_stat"
    },
    "destruction_competition": {
        "base_stats": ["power"],
        "profession_bonus": "Warrior",
        "name": "Соревнование разрушителей",
        "description": "Испытание разрушающей силы",
        "filter_type": "none",
        "sort_by": "power_stat"
    },
    
    # Primary Stat Challenges - Charm
    "charm_contest": {
        "base_stats": ["charm"],
        "profession_bonus": None,
        "name": "Конкурс очарования",
        "description": "Проверка привлекательности",
        "filter_type": "none",
        "sort_by": "charm_stat"
    },
    "beauty_pageant": {
        "base_stats": ["charm"],
        "profession_bonus": None,
        "name": "Конкурс красоты",
        "description": "Соревнование красоты",
        "filter_type": "none",
        "sort_by": "charm_stat"
    },
    "charisma_show": {
        "base_stats": ["charm"],
        "profession_bonus": None,
        "name": "Шоу харизмы",
        "description": "Демонстрация обаяния",
        "filter_type": "none",
        "sort_by": "charm_stat"
    },
    "attraction_battle": {
        "base_stats": ["charm"],
        "profession_bonus": None,
        "name": "Битва притягательности",
        "description": "Проверка магнетизма",
        "filter_type": "none",
        "sort_by": "charm_stat"
    },
    "elegance_competition": {
        "base_stats": ["charm"],
        "profession_bonus": None,
        "name": "Соревнование элегантности",
        "description": "Испытание изящества",
        "filter_type": "none",
        "sort_by": "charm_stat"
    },
    
    # Primary Stat Challenges - Intellect
    "intellect_quiz": {
        "base_stats": ["intellect"],
        "profession_bonus": "Mage",
        "name": "Интеллектуальная викторина",
        "description": "Проверка знаний",
        "filter_type": "none",
        "sort_by": "intellect_stat"
    },
    "mind_puzzle_challenge": {
        "base_stats": ["intellect"],
        "profession_bonus": "Mage",
        "name": "Головоломка разума",
        "description": "Решение сложных задач",
        "filter_type": "none",
        "sort_by": "intellect_stat"
    },
    "strategy_tournament": {
        "base_stats": ["intellect"],
        "profession_bonus": "Mage",
        "name": "Турнир стратегов",
        "description": "Проверка стратегического мышления",
        "filter_type": "none",
        "sort_by": "intellect_stat"
    },
    "wisdom_contest": {
        "base_stats": ["intellect"],
        "profession_bonus": "Mage",
        "name": "Конкурс мудрости",
        "description": "Испытание мудрости",
        "filter_type": "none",
        "sort_by": "intellect_stat"
    },
    "brain_power_show": {
        "base_stats": ["intellect"],
        "profession_bonus": "Mage",
        "name": "Шоу интеллекта",
        "description": "Демонстрация умственных способностей",
        "filter_type": "none",
        "sort_by": "intellect_stat"
    },
    
    # Primary Stat Challenges - Speed
    "speed_race": {
        "base_stats": ["speed"],
        "profession_bonus": "Assassin",
        "name": "Гонка скорости",
        "description": "Проверка быстроты",
        "filter_type": "none",
        "sort_by": "speed_stat"
    },
    "agility_contest": {
        "base_stats": ["speed"],
        "profession_bonus": "Assassin",
        "name": "Конкурс ловкости",
        "description": "Испытание проворства",
        "filter_type": "none",
        "sort_by": "speed_stat"
    },
    "flash_challenge": {
        "base_stats": ["speed"],
        "profession_bonus": "Assassin",
        "name": "Вызов молнии",
        "description": "Проверка скорости реакции",
        "filter_type": "none",
        "sort_by": "speed_stat"
    },
    "rapid_tournament": {
        "base_stats": ["speed"],
        "profession_bonus": "Assassin",
        "name": "Турнир скорости",
        "description": "Соревнование в быстроте",
        "filter_type": "none",
        "sort_by": "speed_stat"
    },
    "lightning_strike_competition": {
        "base_stats": ["speed"],
        "profession_bonus": "Assassin",
        "name": "Соревнование молний",
        "description": "Испытание молниеносной скорости",
        "filter_type": "none",
        "sort_by": "speed_stat"
    },
    
    # Primary Stat Challenges - Luck
    "luck_roulette": {
        "base_stats": ["luck"],
        "profession_bonus": None,
        "name": "Рулетка удачи",
        "description": "Проверка везения",
        "filter_type": "none",
        "sort_by": "luck_stat"
    },
    "fortune_wheel": {
        "base_stats": ["luck"],
        "profession_bonus": None,
        "name": "Колесо фортуны",
        "description": "Испытание удачи",
        "filter_type": "none",
        "sort_by": "luck_stat"
    },
    "chance_competition": {
        "base_stats": ["luck"],
        "profession_bonus": None,
        "name": "Соревнование шансов",
        "description": "Проверка случайности",
        "filter_type": "none",
        "sort_by": "luck_stat"
    },
    "lucky_draw": {
        "base_stats": ["luck"],
        "profession_bonus": None,
        "name": "Счастливая жеребьевка",
        "description": "Испытание фортуны",
        "filter_type": "none",
        "sort_by": "luck_stat"
    },
    "fate_tournament": {
        "base_stats": ["luck"],
        "profession_bonus": None,
        "name": "Турнир судьбы",
        "description": "Проверка благосклонности судьбы",
        "filter_type": "none",
        "sort_by": "luck_stat"
    },
    
    # Primary Stat Challenges - Affection
    "affection_ceremony": {
        "base_stats": ["affection"],
        "profession_bonus": None,
        "name": "Церемония привязанности",
        "description": "Проверка близости",
        "filter_type": "none",
        "sort_by": "affection_stat"
    },
    "bond_challenge": {
        "base_stats": ["affection"],
        "profession_bonus": None,
        "name": "Вызов связи",
        "description": "Испытание привязанности",
        "filter_type": "none",
        "sort_by": "affection_stat"
    },
    "love_contest": {
        "base_stats": ["affection"],
        "profession_bonus": None,
        "name": "Конкурс любви",
        "description": "Соревнование в любви",
        "filter_type": "none",
        "sort_by": "affection_stat"
    },
    "devotion_tournament": {
        "base_stats": ["affection"],
        "profession_bonus": None,
        "name": "Турнир преданности",
        "description": "Проверка верности",
        "filter_type": "none",
        "sort_by": "affection_stat"
    },
    "connection_competition": {
        "base_stats": ["affection"],
        "profession_bonus": None,
        "name": "Соревнование связи",
        "description": "Испытание эмоциональной связи",
        "filter_type": "none",
        "sort_by": "affection_stat"
    }
}
