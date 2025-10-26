"""
Script to create the complete folder structure for waifu images
Structure: waifu-images/{Race}/{Nationality}/
"""
import os
import sys
import io
from pathlib import Path

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Define the structure
RACES = [
    "Angel",
    "Beast",
    "Demon",
    "Dragon",
    "Elf",
    "Fairy",
    "Human",
    "Vampire"
]

NATIONALITIES = [
    "Japanese",
    "Chinese",
    "Korean",
    "American",
    "British",
    "French",
    "German",
    "Italian",
    "Russian",
    "Brazilian",
    "Indian",
    "Canadian"
]

def create_folder_structure():
    """Create all necessary folders for the image structure"""
    base_path = Path("waifu-images")
    
    total_folders = 0
    
    for race in RACES:
        race_path = base_path / race
        
        for nationality in NATIONALITIES:
            folder_path = race_path / nationality
            folder_path.mkdir(parents=True, exist_ok=True)
            total_folders += 1
            print(f"✅ Created: {folder_path}")
    
    print(f"\n🎉 Total folders created: {total_folders}")
    print(f"📊 Structure: {len(RACES)} races × {len(NATIONALITIES)} nationalities = {total_folders} folders")
    print(f"\n📝 Each folder should contain 7 profession images:")
    print("   - Warrior.jpeg")
    print("   - Mage.jpeg")
    print("   - Assassin.jpeg")
    print("   - Knight.jpeg")
    print("   - Archer.jpeg")
    print("   - Healer.jpeg")
    print("   - Merchant.jpeg")
    print(f"\n📦 Total images needed: {total_folders * 7} = {len(RACES)} × {len(NATIONALITIES)} × 7")

def create_readme():
    """Create README files in each race folder"""
    base_path = Path("waifu-images")
    
    for race in RACES:
        race_path = base_path / race
        readme_path = race_path / "README.md"
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"# {race} Waifu Images\n\n")
            f.write(f"This folder contains {race} waifu images organized by nationality.\n\n")
            f.write("## Structure\n\n")
            f.write("```\n")
            for nationality in NATIONALITIES:
                f.write(f"{race}/{nationality}/\n")
                f.write(f"├── Warrior.jpeg\n")
                f.write(f"├── Mage.jpeg\n")
                f.write(f"├── Assassin.jpeg\n")
                f.write(f"├── Knight.jpeg\n")
                f.write(f"├── Archer.jpeg\n")
                f.write(f"├── Healer.jpeg\n")
                f.write(f"└── Merchant.jpeg\n\n")
            f.write("```\n\n")
            f.write(f"## Image Requirements\n\n")
            f.write("- **Format:** JPEG\n")
            f.write("- **Resolution:** 512x512 or 800x800\n")
            f.write("- **Theme:** Must match race, nationality, and profession\n")
            f.write(f"- **Race Theme:** {get_race_theme(race)}\n")
        
        print(f"📄 Created README: {readme_path}")

def get_race_theme(race):
    """Get theme description for a race"""
    themes = {
        "Angel": "Wings, halos, holy/divine elements, light colors",
        "Beast": "Animal features (ears, tail), wild/feral elements",
        "Demon": "Horns, wings, dark/red colors, demonic features",
        "Dragon": "Dragon features (horns, scales, tail), powerful presence",
        "Elf": "Pointed ears, nature elements, elegant appearance",
        "Fairy": "Small wings, magical elements, delicate appearance",
        "Human": "No special features, diverse appearances",
        "Vampire": "Fangs, pale skin, elegant/gothic style"
    }
    return themes.get(race, "Thematic elements matching the race")

if __name__ == "__main__":
    print("🗂️  Creating waifu image folder structure...\n")
    create_folder_structure()
    print("\n" + "="*60 + "\n")
    create_readme()
    print("\n✨ Folder structure created successfully!")
    print("\nNext steps:")
    print("1. Add images to each folder (7 per nationality)")
    print("2. Images should be named: Warrior.jpeg, Mage.jpeg, etc.")
    print("3. Commit and push to GitHub")
    print("4. Update waifu_generator.py to use new structure")

