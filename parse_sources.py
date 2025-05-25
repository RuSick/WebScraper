#!/usr/bin/env python3
"""
Простой скрипт для запуска парсинга всех источников
"""
import os
import sys
import django

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from scraper.tasks import parse_all_sources

def main():
    print("🚀 Запускаем парсинг всех источников...")
    
    try:
        # Запускаем задачу парсинга
        result = parse_all_sources.delay()
        print(f"✅ Задача парсинга запущена с ID: {result.id}")
        print("📊 Проверить статус можно в админке или через API")
        
    except Exception as e:
        print(f"❌ Ошибка при запуске парсинга: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 