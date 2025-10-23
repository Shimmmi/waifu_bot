#!/usr/bin/env python3
"""
Скрипт для настройки бота без Docker
Используйте этот скрипт, если у вас проблемы с Docker/WSL
"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent / "src"))

from bot.db import SessionLocal, engine
from bot.models import Base
from sqlalchemy import text


def create_tables():
    """Создание таблиц в базе данных"""
    print("Создание таблиц...")
    Base.metadata.create_all(bind=engine)
    print("Таблицы созданы!")


def add_seed_data():
    """Добавление тестовых данных"""
    print("Добавление тестовых данных...")
    
    seed_data = """
    INSERT INTO waifu_templates (code, name, rarity, artwork_url, base_stats, skills, tags) VALUES
    ('WF_001', 'Sakura', 'common', 'https://example.com/sakura.png', '{"hp": 100, "atk": 10, "def": 5, "spd": 3}', '{"skills": [{"id": "S1", "name": "Basic Attack", "desc": "Deals ATK damage"}]}', '["student", "cheerful"]'),
    ('WF_002', 'Yuki', 'common', 'https://example.com/yuki.png', '{"hp": 95, "atk": 12, "def": 4, "spd": 4}', '{"skills": [{"id": "S1", "name": "Ice Shard", "desc": "Deals ATK*1.2 damage"}]}', '["mage", "calm"]'),
    ('WF_003', 'Hana', 'uncommon', 'https://example.com/hana.png', '{"hp": 120, "atk": 15, "def": 8, "spd": 5}', '{"skills": [{"id": "S1", "name": "Flower Power", "desc": "Deals ATK*1.3 damage"}, {"id": "S2", "name": "Heal", "desc": "Restores 20 HP"}]}', '["healer", "gentle"]'),
    ('WF_004', 'Akane', 'rare', 'https://example.com/akane.png', '{"hp": 150, "atk": 25, "def": 10, "spd": 7}', '{"skills": [{"id": "S1", "name": "Fire Slash", "desc": "Deals ATK*1.5 damage"}, {"id": "S2", "name": "Flame Shield", "desc": "Reduces damage by 25% for 2 turns"}]}', '["warrior", "fiery"]'),
    ('WF_005', 'Luna', 'epic', 'https://example.com/luna.png', '{"hp": 200, "atk": 35, "def": 15, "spd": 10}', '{"skills": [{"id": "S1", "name": "Moon Beam", "desc": "Deals ATK*2.0 damage"}, {"id": "S2", "name": "Lunar Blessing", "desc": "Increases all stats by 20% for 3 turns"}]}', '["priestess", "mystical"]'),
    ('WF_006', 'Aria', 'legendary', 'https://example.com/aria.png', '{"hp": 300, "atk": 50, "def": 25, "spd": 15}', '{"skills": [{"id": "S1", "name": "Divine Strike", "desc": "Deals ATK*2.5 damage"}, {"id": "S2", "name": "Celestial Protection", "desc": "Makes user invulnerable for 1 turn"}, {"id": "S3", "name": "Heavenly Light", "desc": "Full party heal + buff"}]}', '["goddess", "divine"]')
    ON CONFLICT (code) DO NOTHING;
    """
    
    try:
        session = SessionLocal()
        session.execute(text(seed_data))
        session.commit()
        session.close()
        print("Тестовые данные добавлены!")
    except Exception as e:
        print(f"Ошибка при добавлении тестовых данных: {e}")


def check_connection():
    """Проверка подключения к базе данных"""
    print("Проверка подключения к базе данных...")
    try:
        session = SessionLocal()
        result = session.execute(text("SELECT 1"))
        result.scalar()
        session.close()
        print("Подключение к базе данных успешно!")
        return True
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        print("Проверьте настройки в файле .env")
        return False


def main():
    """Основная функция настройки"""
    print("Настройка Waifu Bot без Docker")
    print("=" * 50)
    
    # Проверяем подключение
    if not check_connection():
        print("\nНе удалось подключиться к базе данных.")
        print("Убедитесь, что:")
        print("1. Файл .env настроен правильно")
        print("2. База данных PostgreSQL запущена")
        print("3. Redis запущен (если используется)")
        return
    
    # Создаем таблицы
    create_tables()
    
    # Добавляем тестовые данные
    add_seed_data()
    
    print("\nНастройка завершена!")
    print("Теперь вы можете запустить бота командой:")
    print("python -m bot.main")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nНастройка прервана пользователем")
    except Exception as e:
        print(f"\nОшибка: {e}")
        print("Проверьте настройки и попробуйте снова")
