import sys
from pathlib import Path
import os

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Устанавливаем переменные окружения для SQLite
os.environ["BOT_TOKEN"] = "7401283035:AAGiaoJnrzqkuLQYYjNSTPLCReQVdH5oDe4"
os.environ["DATABASE_URL"] = "sqlite:///./waifu_bot.db"
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["ENV"] = "development"

from sqlalchemy import create_engine, text
from bot.models import Base

def update_database():
    """Обновление базы данных с новыми таблицами"""
    print("Обновление базы данных...")
    try:
        # Создаем движок для SQLite
        engine = create_engine("sqlite:///./waifu_bot.db", echo=True)
        
        # Создаем новые таблицы
        with engine.connect() as conn:
            # Создаем таблицу waifu
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS waifu (
                    id TEXT PRIMARY KEY,
                    card_number INTEGER UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    rarity TEXT NOT NULL,
                    race TEXT NOT NULL,
                    profession TEXT NOT NULL,
                    nationality TEXT NOT NULL,
                    image_url TEXT,
                    owner_id INTEGER,
                    level INTEGER DEFAULT 1 NOT NULL,
                    xp INTEGER DEFAULT 0 NOT NULL,
                    stats TEXT NOT NULL,
                    dynamic TEXT NOT NULL,
                    tags TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Создаем таблицу events
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    end_time DATETIME,
                    rewards TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Создаем таблицу event_participations
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS event_participations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    waifu_id TEXT NOT NULL,
                    event_id INTEGER NOT NULL,
                    score REAL NOT NULL,
                    rewards_received TEXT,
                    participated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (waifu_id) REFERENCES waifu (id),
                    FOREIGN KEY (event_id) REFERENCES events (id)
                )
            """))
            
            conn.commit()
        
        print("База данных успешно обновлена!")
        return True
    except Exception as e:
        print(f"Ошибка при обновлении базы данных: {e}")
        return False

if __name__ == "__main__":
    print("Обновление базы данных Waifu Bot...")
    if update_database():
        print("Готово!")
    else:
        print("Ошибка!")
