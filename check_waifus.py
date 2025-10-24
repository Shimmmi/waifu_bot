#!/usr/bin/env python3
"""
Скрипт для проверки вайфу в базе данных
"""

import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from bot.db import SessionLocal
from bot.models import User, Waifu

def check_waifus():
    """Проверка вайфу в базе данных"""
    session = SessionLocal()
    try:
        # Получаем всех пользователей
        users = session.query(User).all()
        print(f"Найдено пользователей: {len(users)}")
        
        for user in users:
            print(f"\nПользователь: {user.display_name} (ID: {user.tg_id})")
            
            # Получаем вайфу пользователя
            waifus = session.query(Waifu).filter(Waifu.owner_id == user.id).all()
            print(f"  Вайфу: {len(waifus)}")
            
            for waifu in waifus:
                print(f"    - {waifu.name} (ID: {waifu.id})")
                print(f"      Редкость: {waifu.rarity}")
                print(f"      Раса: {waifu.race}")
                print(f"      Уровень: {waifu.level}")
                print(f"      XP: {waifu.xp}")
                print(f"      Статы: {waifu.stats}")
                print(f"      Динамика: {waifu.dynamic}")
                print()
                
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    check_waifus()
