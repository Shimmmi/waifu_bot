"""
Migration script to update existing waifu images to use GitHub hosted URLs
Run this after pushing images to GitHub
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from bot.db import SessionLocal
from bot.models import Waifu
from bot.data_tables import WAIFU_IMAGES_BY_RACE
import random

def update_waifu_images():
    """Update all existing waifus to use GitHub hosted images"""
    session = SessionLocal()
    
    try:
        # Get all waifus
        waifus = session.query(Waifu).all()
        print(f"Found {len(waifus)} waifus to update")
        
        updated_count = 0
        
        for waifu in waifus:
            # Get the race
            race = waifu.race
            
            # Get appropriate image based on race
            if race in WAIFU_IMAGES_BY_RACE and WAIFU_IMAGES_BY_RACE[race]:
                new_image_url = random.choice(WAIFU_IMAGES_BY_RACE[race])
                
                # Update the image URL
                waifu.image_url = new_image_url
                print(f"✅ Updated {waifu.name} ({race}) -> {new_image_url}")
                updated_count += 1
            else:
                print(f"⚠️  No image found for {waifu.name} ({race})")
        
        # Commit all changes at once
        session.commit()
        print(f"\n✨ Successfully updated {updated_count} waifus with new GitHub images!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    print("🎨 Starting waifu image update to GitHub URLs...")
    update_waifu_images()

