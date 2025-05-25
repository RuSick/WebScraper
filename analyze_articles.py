#!/usr/bin/env python3
"""
Простой скрипт для запуска анализа статей
"""
import os
import sys
import django

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Article
from scraper.tasks import analyze_unanalyzed_articles

def main():
    print("🔍 Запускаем анализ статей...")
    
    # Проверяем количество непроанализированных статей
    unanalyzed_count = Article.objects.filter(is_analyzed=False).count()
    print(f"📊 Найдено {unanalyzed_count} непроанализированных статей")
    
    if unanalyzed_count == 0:
        print("✅ Все статьи уже проанализированы!")
        return 0
    
    try:
        # Запускаем задачу анализа
        result = analyze_unanalyzed_articles.delay()
        print(f"✅ Задача анализа запущена с ID: {result.id}")
        print("📊 Проверить статус можно в админке или через API")
        
    except Exception as e:
        print(f"❌ Ошибка при запуске анализа: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 