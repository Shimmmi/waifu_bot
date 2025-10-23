#!/usr/bin/env python3
"""
Скрипт для создания тестовых вайфу в базе данных
"""

import sys
import os
from pathlib import Path
from sqlalchemy import select, func

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Загружаем переменные окружения
from dotenv import load_dotenv
load_dotenv("config.env")

from bot.db import SessionLocal, engine
from bot.models import Base, Waifu, User
from bot.services.waifu_generator import generate_waifu

def create_test_waifu():
    """Создает 5 тестовых вайфу различной редкости"""
    print("Создание тестовых вайфу...")
    
    # Создаем таблицы если их нет
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    try:
        # Получаем первого пользователя (администратора)
        admin_user = session.execute(
            select(User).where(User.tg_id == 305174198)
        ).scalar_one_or_none()
        
        if not admin_user:
            print("ERROR: Administrator not found! First run the bot and use /start")
            return
        
        print(f"SUCCESS: Found administrator: {admin_user.display_name}")
        
        # Получаем текущий максимальный номер карты
        max_card = session.execute(select(func.max(Waifu.card_number))).scalar() or 0
        
        # Создаем 5 тестовых вайфу
        test_waifus = []
        for i in range(5):
            card_number = max_card + i + 1
            waifu_data = generate_waifu(card_number, admin_user.id)
            
            # Создаем вайфу в базе
            waifu = Waifu(**waifu_data)
            session.add(waifu)
            test_waifus.append(waifu)
            
            print(f"SUCCESS: Created waifu: {waifu.name} [{waifu.rarity}] (ID: {waifu.id})")
        
        # Сохраняем в базу
        session.commit()
        
        print(f"\nSUCCESS: Created {len(test_waifus)} test waifus!")
        print("Now you can use /debug command for testing")
        
    except Exception as e:
        print(f"ERROR: Failed to create test waifus: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    create_test_waifu()
