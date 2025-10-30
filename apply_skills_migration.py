"""
Apply skills system migration to database
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL not found in environment")
    exit(1)

# Create engine
engine = create_engine(DATABASE_URL)

# Read migration file
with open("sql/010_create_skills_system.sql", "r", encoding="utf-8") as f:
    migration_sql = f.read()

# Apply migration
try:
    with engine.connect() as connection:
        # Begin transaction
        trans = connection.begin()
        try:
            print("🚀 Applying skills system migration...")
            
            # Execute migration
            connection.execute(text(migration_sql))
            
            # Commit transaction
            trans.commit()
            print("✅ Migration applied successfully!")
            
        except Exception as e:
            # Rollback on error
            trans.rollback()
            print(f"❌ Error applying migration: {e}")
            raise
            
except Exception as e:
    print(f"❌ Database connection error: {e}")
    exit(1)
