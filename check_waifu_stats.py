#!/usr/bin/env python3
"""
Скрипт для проверки текущих значений характеристик вайфу
"""
import os
import sys
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Добавляем путь к модулям
sys.path.append('src')

# Настройка подключения к базе данных
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://username:password@localhost/waifu_bot')

def check_waifu_stats():
    """Проверяет текущие значения характеристик вайфу"""
    try:
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Получаем статистику по характеристикам
        query = text("""
            SELECT 
                rarity,
                COUNT(*) as count,
                AVG((dynamic->>'bond')::int) as avg_bond,
                AVG((dynamic->>'loyalty')::int) as avg_loyalty,
                MIN((dynamic->>'bond')::int) as min_bond,
                MAX((dynamic->>'bond')::int) as max_bond,
                MIN((dynamic->>'loyalty')::int) as min_loyalty,
                MAX((dynamic->>'loyalty')::int) as max_loyalty
            FROM waifu 
            WHERE dynamic IS NOT NULL
            GROUP BY rarity
            ORDER BY 
                CASE rarity 
                    WHEN 'Common' THEN 1
                    WHEN 'Uncommon' THEN 2
                    WHEN 'Rare' THEN 3
                    WHEN 'Epic' THEN 4
                    WHEN 'Legendary' THEN 5
                END
        """)
        
        result = session.execute(query)
        rows = result.fetchall()
        
        print("📊 Статистика характеристик вайфу:")
        print("=" * 80)
        print(f"{'Редкость':<12} {'Кол-во':<8} {'Ловкость (bond)':<20} {'Лояльность (loyalty)':<20}")
        print(f"{'':<12} {'':<8} {'Средн.':<8} {'Мин-Макс':<10} {'Средн.':<8} {'Мин-Макс':<10}")
        print("-" * 80)
        
        for row in rows:
            rarity = row[0]
            count = row[1]
            avg_bond = round(row[2] or 0, 1)
            avg_loyalty = round(row[3] or 0, 1)
            min_bond = row[4] or 0
            max_bond = row[5] or 0
            min_loyalty = row[6] or 0
            max_loyalty = row[7] or 0
            
            print(f"{rarity:<12} {count:<8} {avg_bond:<8} {f'{min_bond}-{max_bond}':<10} {avg_loyalty:<8} {f'{min_loyalty}-{max_loyalty}':<10}")
        
        # Проверяем, есть ли вайфу с bond = 0
        zero_bond_query = text("""
            SELECT COUNT(*) 
            FROM waifu 
            WHERE (dynamic->>'bond')::int = 0 OR dynamic->>'bond' IS NULL
        """)
        
        zero_bond_count = session.execute(zero_bond_query).scalar()
        print(f"\n🔍 Вайфу с ловкостью = 0: {zero_bond_count}")
        
        # Проверяем, есть ли вайфу с loyalty > 0
        non_zero_loyalty_query = text("""
            SELECT COUNT(*) 
            FROM waifu 
            WHERE (dynamic->>'loyalty')::int > 0
        """)
        
        non_zero_loyalty_count = session.execute(non_zero_loyalty_query).scalar()
        print(f"🔍 Вайфу с лояльностью > 0: {non_zero_loyalty_count}")
        
        session.close()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    check_waifu_stats()
