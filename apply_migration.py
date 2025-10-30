"""
Apply skills system migration to database
"""

import os
import sys
from pathlib import Path

# Add src/ to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL not found in environment")
    print("Please set DATABASE_URL in .env file")
    sys.exit(1)

print(f"📊 Database URL: {DATABASE_URL[:50]}...")

# Create engine
engine = create_engine(DATABASE_URL)

# Read migration file
migration_file = Path(__file__).parent / "sql" / "010_create_skills_system.sql"
if not migration_file.exists():
    print(f"❌ Migration file not found: {migration_file}")
    sys.exit(1)

print(f"📄 Reading migration file: {migration_file}")
with open(migration_file, "r", encoding="utf-8") as f:
    migration_sql = f.read()

# Apply migration
try:
    with engine.connect() as connection:
        # Begin transaction
        trans = connection.begin()
        try:
            print("🚀 Applying skills system migration...")
            print("   This may take a few moments...")
            
            # Execute migration
            connection.execute(text(migration_sql))
            
            # Commit transaction
            trans.commit()
            print("✅ Migration applied successfully!")
            print("   Skills tables have been created and populated")
            
        except Exception as e:
            # Rollback on error
            trans.rollback()
            print(f"❌ Error applying migration: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
            
except Exception as e:
    print(f"❌ Database connection error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

