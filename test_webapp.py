#!/usr/bin/env python3
"""
Скрипт для тестирования WebApp API
"""

import requests
import json
import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent / "src"))

from bot.db import SessionLocal
from bot.models import Waifu

def test_api_endpoint():
    """Тестирование API endpoint"""
    base_url = "http://localhost:8000"
    
    # Получаем первую вайфу из базы данных
    session = SessionLocal()
    try:
        waifu = session.query(Waifu).first()
        if not waifu:
            print("❌ В базе данных нет вайфу для тестирования")
            return
        
        waifu_id = waifu.id
        print(f"🧪 Тестируем API для вайфу ID: {waifu_id}")
        
    finally:
        session.close()
    
    # Тестируем API endpoint
    try:
        response = requests.get(f"{base_url}/api/waifu/{waifu_id}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API endpoint работает корректно!")
            print(f"📋 Данные вайфу: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ API endpoint вернул ошибку: {response.status_code}")
            print(f"📝 Ответ: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Не удалось подключиться к API серверу")
        print("💡 Убедитесь, что API сервер запущен: python run_api_server.py")
    except Exception as e:
        print(f"❌ Ошибка при тестировании API: {e}")

def test_webapp_page():
    """Тестирование WebApp страницы"""
    base_url = "http://localhost:8000"
    
    try:
        response = requests.get(f"{base_url}/")
        
        if response.status_code == 200:
            print("✅ WebApp страница доступна!")
            print(f"📄 Размер страницы: {len(response.text)} символов")
        else:
            print(f"❌ WebApp страница недоступна: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Не удалось подключиться к WebApp серверу")
        print("💡 Убедитесь, что API сервер запущен: python run_api_server.py")
    except Exception as e:
        print(f"❌ Ошибка при тестировании WebApp: {e}")

def test_health_check():
    """Тестирование health check"""
    base_url = "http://localhost:8000"
    
    try:
        response = requests.get(f"{base_url}/health")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check работает!")
            print(f"📋 Статус: {data}")
        else:
            print(f"❌ Health check вернул ошибку: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Не удалось подключиться к серверу")
    except Exception as e:
        print(f"❌ Ошибка при тестировании health check: {e}")

if __name__ == "__main__":
    print("🧪 Тестирование WebApp API")
    print("=" * 50)
    
    print("\n1. Тестирование health check...")
    test_health_check()
    
    print("\n2. Тестирование WebApp страницы...")
    test_webapp_page()
    
    print("\n3. Тестирование API endpoint...")
    test_api_endpoint()
    
    print("\n" + "=" * 50)
    print("🎉 Тестирование завершено!")
