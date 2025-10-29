#!/usr/bin/env python3
"""
Скрипт для применения миграции исправления характеристик
"""
import os
import sys
from sqlalchemy import create_engine, text

# Настройка подключения к базе данных
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://username:password@localhost/waifu_bot')

def apply_migration():
    """Применяет миграцию исправления характеристик"""
    try:
        engine = create_engine(DATABASE_URL)
        
        # Читаем SQL файл миграции
        with open('sql/010_fix_dexterity_and_loyalty.sql', 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # Выполняем миграцию
        with engine.connect() as conn:
            # Разделяем SQL на отдельные запросы
            statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
            
            for i, statement in enumerate(statements):
                if statement:
                    print(f"Выполняем запрос {i+1}/{len(statements)}...")
                    try:
                        result = conn.execute(text(statement))
                        conn.commit()
                        print(f"✅ Запрос {i+1} выполнен успешно")
                    except Exception as e:
                        print(f"❌ Ошибка в запросе {i+1}: {e}")
                        conn.rollback()
        
        print("\n🎉 Миграция применена успешно!")
        
        # Проверяем результат
        print("\n📊 Проверяем результат...")
        with engine.connect() as conn:
            # Проверяем статистику
            result = conn.execute(text("""
                SELECT 
                    rarity,
                    COUNT(*) as count,
                    ROUND(AVG((dynamic->>'bond')::int), 1) as avg_bond,
                    ROUND(AVG((dynamic->>'loyalty')::int), 1) as avg_loyalty
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
            """))
            
            print("Результат после миграции:")
            print("Редкость | Кол-во | Средн. ловкость | Средн. лояльность")
            print("-" * 50)
            for row in result:
                print(f"{row[0]:<8} | {row[1]:<6} | {row[2]:<14} | {row[3]}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    apply_migration()
