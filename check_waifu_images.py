"""
Quick script to check what image URLs are in the database
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from bot.db import SessionLocal
from bot.models import Waifu

def check_images():
    """Check image URLs for all waifus"""
    session = SessionLocal()
    
    try:
        # Get all waifus
        waifus = session.query(Waifu).order_by(Waifu.created_at.desc()).limit(10).all()
        print(f"📊 Checking last {len(waifus)} waifus:\n")
        
        for waifu in waifus:
            print(f"{'='*60}")
            print(f"👤 Name: {waifu.name}")
            print(f"🧬 Race: {waifu.race}")
            print(f"🎭 Rarity: {waifu.rarity}")
            print(f"📅 Created: {waifu.created_at}")
            print(f"🖼️  Image URL: {waifu.image_url}")
            print(f"   URL starts with: {waifu.image_url[:50] if waifu.image_url else 'None'}...")
            if waifu.image_url:
                if 'github' in waifu.image_url.lower():
                    print(f"   ✅ GitHub URL")
                elif 'dicebear' in waifu.image_url.lower():
                    print(f"   ⚠️  DiceBear URL (old)")
                else:
                    print(f"   ❓ Unknown source")
            else:
                print(f"   ❌ No image URL")
            print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    print("🔍 Checking waifu image URLs in database...\n")
    check_images()

