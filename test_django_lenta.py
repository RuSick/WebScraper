#!/usr/bin/env python3
"""
Тест интеграции LentaParser с Django.
"""

import os
import django
import sys

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from scraper.tasks import collect_lenta_articles
from core.models import Source, Article

def test_django_integration():
    """Тест интеграции с Django."""
    print("🚀 Тестируем интеграцию LentaParser с Django...")
    
    # Очищаем предыдущие статьи Lenta.ru для чистого теста
    lenta_articles_before = Article.objects.filter(source__name='Lenta.ru').count()
    print(f"📊 Статей Lenta.ru в БД до парсинга: {lenta_articles_before}")
    
    # Запускаем задачу сбора статей
    print("⏳ Запускаем сбор статей с Lenta.ru...")
    result = collect_lenta_articles()
    
    print(f"✅ Результат выполнения задачи:")
    print(f"   - Статус: {result['status']}")
    if result['status'] == 'success':
        print(f"   - Новых статей: {result['new_articles']}")
        print(f"   - Обновлено статей: {result['updated_articles']}")
        print(f"   - Всего обработано: {result['total_processed']}")
        print(f"   - Сообщение: {result['message']}")
    else:
        print(f"   - Ошибка: {result['error']}")
    
    # Проверяем состояние БД после парсинга
    lenta_articles_after = Article.objects.filter(source__name='Lenta.ru').count()
    print(f"📊 Статей Lenta.ru в БД после парсинга: {lenta_articles_after}")
    
    # Показываем несколько последних статей
    latest_articles = Article.objects.filter(source__name='Lenta.ru').order_by('-created_at')[:3]
    if latest_articles:
        print(f"\n📰 Последние статьи в БД:")
        for i, article in enumerate(latest_articles, 1):
            print(f"{i}. {article.title}")
            print(f"   URL: {article.url}")
            print(f"   Дата публикации: {article.published_at}")
            print(f"   Добавлено в БД: {article.created_at}")
    
    # Проверяем источник
    lenta_source = Source.objects.filter(name='Lenta.ru').first()
    if lenta_source:
        print(f"\n🔧 Источник Lenta.ru:")
        print(f"   ID: {lenta_source.id}")
        print(f"   URL: {lenta_source.url}")
        print(f"   Тип: {lenta_source.type}")
        print(f"   Активен: {lenta_source.is_active}")
    
    return result

if __name__ == "__main__":
    test_django_integration() 