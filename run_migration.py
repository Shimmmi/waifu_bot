"""
Run database migration to initialize dynamic stats
"""
import sys
from pathlib import Path

# Fix Windows encoding for emojis
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from bot.db import SessionLocal
from sqlalchemy import text


def run_migration():
    """Run the dynamic stats migration"""
    session = SessionLocal()
    
    try:
        print("🔄 Running migration: Initialize dynamic stats...")
        
        # Detect database type
        from bot.config import get_settings
        settings = get_settings()
        is_sqlite = 'sqlite' in settings.database_url.lower()
        
        print(f"   Database: {'SQLite' if is_sqlite else 'PostgreSQL'}")
        
        # Import the Waifu model
        from bot.models import Waifu
        from sqlalchemy import select
        from sqlalchemy.orm.attributes import flag_modified
        from datetime import datetime
        
        # Get all waifus
        result = session.execute(select(Waifu))
        waifus = result.scalars().all()
        
        print(f"   Found {len(waifus)} waifus to update")
        
        updated_count = 0
        for waifu in waifus:
            # Check if dynamic needs initialization
            needs_update = False
            
            if not waifu.dynamic:
                waifu.dynamic = {}
                needs_update = True
            
            # Initialize missing fields
            if 'energy' not in waifu.dynamic:
                waifu.dynamic['energy'] = 100
                needs_update = True
            
            if 'mood' not in waifu.dynamic:
                waifu.dynamic['mood'] = 50
                needs_update = True
            
            if 'loyalty' not in waifu.dynamic:
                waifu.dynamic['loyalty'] = 50
                needs_update = True
            
            if 'last_restore' not in waifu.dynamic:
                waifu.dynamic['last_restore'] = datetime.now().isoformat()
                needs_update = True
            
            if needs_update:
                # Create new dict to trigger SQLAlchemy change detection
                waifu.dynamic = dict(waifu.dynamic)
                flag_modified(waifu, 'dynamic')
                updated_count += 1
        
        session.commit()
        
        print(f"✅ Migration completed successfully!")
        print(f"✅ Updated {updated_count} waifus with initialized dynamic stats")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    run_migration()

