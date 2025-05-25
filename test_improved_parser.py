#!/usr/bin/env python3
"""
Тестирование улучшенного парсера с фильтрацией
"""
import os
import sys
import django
import asyncio
import logging

# Настраиваем логирование
logging.basicConfig(level=logging.DEBUG)

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Source
from scraper.parsers.universal_parser import fetch_generic_articles
from asgiref.sync import sync_to_async

async def test_habr_parsing():
    """Тестируем парсинг Habr с новой фильтрацией"""
    print("🧪 Тестирование улучшенного парсера Habr...")
    
    # Получаем источник Habr асинхронно
    try:
        habr_source = await sync_to_async(Source.objects.get)(name__icontains="Habr")
        print(f"📰 Источник: {habr_source.name} ({habr_source.url})")
    except Source.DoesNotExist:
        print("❌ Источник Habr не найден в базе данных")
        return
    
    # Запускаем парсинг
    print("🔄 Запуск парсинга...")
    articles = await fetch_generic_articles(habr_source)
    
    print(f"\n📊 Результаты парсинга:")
    print(f"   Найдено статей: {len(articles)}")
    
    if articles:
        print(f"\n📝 Первые 5 статей:")
        for i, article in enumerate(articles[:5], 1):
            print(f"   {i}. {article['title'][:60]}...")
            print(f"      URL: {article['url'][:80]}...")
            print(f"      Контент: {len(article.get('content', ''))} символов")
            print()
    else:
        print("⚠️ Статьи не найдены. Возможные причины:")
        print("   - Слишком строгие фильтры")
        print("   - Проблемы с селекторами")
        print("   - Сайт изменил структуру")
    
    # Проверяем на наличие проблемных статей
    bad_articles = []
    for article in articles:
        title = article.get('title', '')
        url = article.get('url', '')
        content = article.get('content', '')
        
        if 'комментарии' in title.lower() or 'comments' in url.lower():
            bad_articles.append(article)
    
    if bad_articles:
        print(f"⚠️ Найдено {len(bad_articles)} потенциально проблемных статей:")
        for article in bad_articles[:3]:
            print(f"   - {article['title'][:50]}... ({article['url'][:60]}...)")
    else:
        print("✅ Проблемных статей не найдено!")

def main():
    print("🔍 Тестирование улучшенного универсального парсера")
    print("=" * 60)
    
    # Запускаем асинхронный тест
    asyncio.run(test_habr_parsing())
    
    print("\n✅ Тестирование завершено!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 