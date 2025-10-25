"""
Migration script to add image URLs to existing waifus and update the image generation logic
"""
import sys
from pathlib import Path

# Fix Windows console encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from bot.db import SessionLocal
from bot.models import Waifu
from sqlalchemy.orm import Session
import random

# Curated list of anime waifu images (safe for work)
# Using DiceBear API that generates consistent anime-style avatars
WAIFU_IMAGES = [
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Bella",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Sophie",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Luna",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Mia",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Zoe",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Lily",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Chloe",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Emma",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Ava",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Aria",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Nora",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Ruby",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Jade",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Rose",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Iris",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Maya",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Nova",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Star",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Sky",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Dawn",
]

def get_random_image() -> str:
    """Get a random image URL from the predefined list"""
    return random.choice(WAIFU_IMAGES)

def main(force_update=False):
    print("=" * 60)
    print("🎨 Adding Images to Waifus")
    if force_update:
        print("⚠️  FORCE UPDATE MODE - All images will be replaced!")
    print("=" * 60)
    
    session: Session = SessionLocal()
    
    try:
        # Get all waifus
        waifus = session.query(Waifu).all()
        print(f"📊 Found {len(waifus)} waifus in database")
        
        updated_count = 0
        skipped_count = 0
        
        for waifu in waifus:
            if force_update or waifu.image_url is None or waifu.image_url == "":
                # Assign a random image from our curated list
                waifu.image_url = get_random_image()
                updated_count += 1
                
                # Commit each waifu individually to avoid connection timeouts
                try:
                    session.commit()
                    print(f"  ✅ Updated {waifu.name} (ID: {waifu.id})")
                except Exception as e:
                    print(f"  ❌ Failed to update {waifu.name}: {e}")
                    session.rollback()
            else:
                skipped_count += 1
                print(f"  ⏭️  Skipped {waifu.name} (already has image)")
        
        if updated_count > 0:
            print(f"\n✅ Successfully updated {updated_count} waifus")
        
        if skipped_count > 0:
            print(f"⏭️  Skipped {skipped_count} waifus (already had images)")
            
        print("\n" + "=" * 60)
        print("🎉 Migration Complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    import sys
    force = "--force" in sys.argv
    main(force_update=force)

