"""
Quick test script to verify stat system is working
"""
import sys
from pathlib import Path
from datetime import datetime

# Fix Windows encoding for emojis
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from bot.db import SessionLocal
from bot.models import Waifu
from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified


def test_stat_system():
    """Test that stat updates work correctly"""
    session = SessionLocal()
    
    try:
        print("🔍 Testing Stat System...\n")
        
        # Get a waifu (first one)
        result = session.execute(select(Waifu).limit(1))
        waifu = result.scalar_one_or_none()
        
        if not waifu:
            print("❌ No waifus found in database!")
            print("   Please generate some waifus first.")
            return
        
        print(f"📋 Testing with: {waifu.name} (ID: {waifu.id})")
        print(f"   Rarity: {waifu.rarity}")
        print()
        
        # Show current stats
        print("📊 Current Stats:")
        print(f"   XP: {waifu.xp}")
        print(f"   Dynamic: {waifu.dynamic}")
        print()
        
        # Test 1: Update XP
        print("✅ Test 1: Updating XP...")
        old_xp = waifu.xp
        waifu.xp += 30
        session.commit()
        session.refresh(waifu)
        print(f"   XP: {old_xp} → {waifu.xp}")
        assert waifu.xp == old_xp + 30, "XP update failed!"
        print("   ✅ XP update works!")
        print()
        
        # Test 2: Update dynamic stats
        print("✅ Test 2: Updating dynamic stats...")
        
        # Initialize if needed
        if not waifu.dynamic:
            waifu.dynamic = {
                "energy": 100,
                "mood": 50,
                "loyalty": 50,
                "last_restore": datetime.now().isoformat()
            }
            flag_modified(waifu, "dynamic")
            session.commit()
            session.refresh(waifu)
        
        old_energy = int(waifu.dynamic.get("energy", 100))
        old_mood = int(waifu.dynamic.get("mood", 50))
        old_loyalty = int(waifu.dynamic.get("loyalty", 50))
        
        # Update stats
        waifu.dynamic = {
            **waifu.dynamic,
            "energy": max(0, old_energy - 20),
            "mood": min(100, old_mood + 5),
            "loyalty": min(100, old_loyalty + 2),
            "last_restore": datetime.now().isoformat()
        }
        flag_modified(waifu, "dynamic")
        session.commit()
        session.flush()
        session.refresh(waifu)
        
        new_energy = int(waifu.dynamic.get("energy", 100))
        new_mood = int(waifu.dynamic.get("mood", 50))
        new_loyalty = int(waifu.dynamic.get("loyalty", 50))
        
        print(f"   Energy: {old_energy} → {new_energy}")
        print(f"   Mood: {old_mood} → {new_mood}")
        print(f"   Loyalty: {old_loyalty} → {new_loyalty}")
        
        assert new_energy == max(0, old_energy - 20), "Energy update failed!"
        assert new_mood == min(100, old_mood + 5), "Mood update failed!"
        assert new_loyalty == min(100, old_loyalty + 2), "Loyalty update failed!"
        
        print("   ✅ Dynamic stats update works!")
        print()
        
        # Test 3: Verify persistence
        print("✅ Test 3: Verifying persistence...")
        waifu_id = waifu.id
        session.close()
        
        # Open new session and fetch again
        session = SessionLocal()
        result = session.execute(select(Waifu).where(Waifu.id == waifu_id))
        waifu_reloaded = result.scalar_one()
        
        print(f"   Reloaded XP: {waifu_reloaded.xp}")
        print(f"   Reloaded Dynamic: {waifu_reloaded.dynamic}")
        
        assert waifu_reloaded.xp == waifu.xp, "XP not persisted!"
        assert waifu_reloaded.dynamic == waifu.dynamic, "Dynamic not persisted!"
        
        print("   ✅ Data persists correctly!")
        print()
        
        print("🎉 All tests passed! Stat system is working correctly!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    test_stat_system()

