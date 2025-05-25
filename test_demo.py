#!/usr/bin/env python3
"""
Тест демонстрации MediaScope API
"""

import requests
import time

def test_demo():
    base_url = "http://localhost:8000"
    
    print("🧪 Тестирование MediaScope Demo...")
    
    # Ждем запуска сервера
    time.sleep(3)
    
    try:
        # Тест главной страницы
        print("📄 Тест главной страницы...")
        response = requests.get(f"{base_url}/")
        assert response.status_code == 200
        assert "MediaScope" in response.text
        print("✅ Главная страница работает")
        
        # Тест API статей
        print("📰 Тест API статей...")
        response = requests.get(f"{base_url}/api/articles/")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        print(f"✅ API статей работает. Найдено {data.get('count', 0)} статей")
        
        # Тест API источников
        print("🌐 Тест API источников...")
        response = requests.get(f"{base_url}/api/sources/")
        assert response.status_code == 200
        data = response.json()
        print(f"✅ API источников работает. Найдено {len(data.get('results', []))} источников")
        
        # Тест статистики
        print("📊 Тест статистики...")
        response = requests.get(f"{base_url}/api/stats/articles/")
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Статистика работает. Всего статей: {data.get('total_articles', 0)}")
        
        # Тест поиска
        print("🔍 Тест поиска...")
        response = requests.get(f"{base_url}/api/articles/?search=технологии")
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Поиск работает. Найдено: {len(data.get('results', []))} статей по запросу 'технологии'")
        
        # Тест Swagger документации
        print("📚 Тест документации...")
        response = requests.get(f"{base_url}/api/docs/")
        assert response.status_code == 200
        print("✅ Swagger документация доступна")
        
        print("\n🎉 Все тесты прошли успешно!")
        print(f"🌐 Демонстрация доступна: {base_url}/")
        print(f"📖 API документация: {base_url}/api/docs/")
        print(f"⚙️  Админ панель: {base_url}/admin/")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Сервер не запущен. Запустите: python manage.py runserver")
        return False
    except AssertionError as e:
        print(f"❌ Тест не прошел: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    test_demo() 