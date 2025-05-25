#!/usr/bin/env python3
"""
Отладка парсера - проверяем что происходит при парсинге
"""
import os
import sys
import django
import asyncio
import logging
from django.utils import timezone

# Настраиваем подробное логирование
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Source, Article
from scraper.parsers.universal_parser import fetch_generic_articles
from asgiref.sync import sync_to_async

async def debug_habr_parsing():
    """Отладка парсинга Habr"""
    print("🔍 Отладка парсера Habr...")
    
    # Получаем источник Habr
    try:
        habr_source = await sync_to_async(Source.objects.get)(name__icontains="Habr")
        print(f"📰 Источник: {habr_source.name}")
        print(f"🔗 URL: {habr_source.url}")
        print(f"📊 Тип: {habr_source.type}")
        print(f"✅ Активен: {habr_source.is_active}")
    except Source.DoesNotExist:
        print("❌ Источник Habr не найден")
        return
    
    print("\n🚀 Запуск парсинга...")
    
    # Запускаем парсинг с подробным логированием
    articles = await fetch_generic_articles(habr_source)
    
    print(f"\n📊 Результаты:")
    print(f"   Найдено статей: {len(articles)}")
    
    if articles:
        print(f"\n📝 Первые 3 статьи:")
        for i, article in enumerate(articles[:3], 1):
            print(f"\n   {i}. Заголовок: {article['title']}")
            print(f"      URL: {article['url']}")
            print(f"      Контент: {len(article.get('content', ''))} символов")
            print(f"      Summary: {len(article.get('summary', ''))} символов")
            print(f"      Дата: {article.get('published_at', 'Не указана')}")
            
            # Показываем начало контента
            content = article.get('content', '')
            if content:
                print(f"      Начало контента: {content[:100]}...")
    else:
        print("\n⚠️ Статьи не найдены!")
        print("Возможные причины:")
        print("1. Слишком строгие фильтры")
        print("2. Неправильные селекторы")
        print("3. Сайт изменил структуру")
        print("4. Проблемы с сетью")

async def test_save_to_db():
    """Тестируем сохранение в БД"""
    print("\n💾 Тестирование сохранения в БД...")
    
    # Проверяем текущее количество статей
    current_count = await sync_to_async(Article.objects.count)()
    print(f"📊 Статей в БД до парсинга: {current_count}")
    
    # Получаем Habr
    habr_source = await sync_to_async(Source.objects.get)(name__icontains="Habr")
    
    # Парсим
    articles = await fetch_generic_articles(habr_source)
    
    if articles:
        print(f"🔄 Пытаемся сохранить {len(articles)} статей...")
        saved_count = 0
        
        for article_data in articles:
            try:
                # Проверяем дубликаты
                existing = await sync_to_async(Article.objects.filter(url=article_data['url']).exists)()
                if existing:
                    print(f"   ⚠️ Статья уже существует: {article_data['title'][:50]}...")
                    continue
                
                # Создаем статью
                article = Article(
                    title=article_data['title'],
                    content=article_data.get('content', ''),
                    summary=article_data.get('summary', ''),
                    url=article_data['url'],
                    source=habr_source,
                    published_at=article_data.get('published_at') or timezone.now(),
                )
                await sync_to_async(article.save)()
                saved_count += 1
                print(f"   ✅ Сохранена: {article_data['title'][:50]}...")
                
            except Exception as e:
                print(f"   ❌ Ошибка сохранения: {e}")
        
        print(f"\n📊 Результат сохранения:")
        print(f"   Найдено статей: {len(articles)}")
        print(f"   Сохранено новых: {saved_count}")
        
        # Проверяем итоговое количество
        final_count = await sync_to_async(Article.objects.count)()
        print(f"   Статей в БД после парсинга: {final_count}")
        print(f"   Прирост: +{final_count - current_count}")
    else:
        print("❌ Нет статей для сохранения")

def main():
    print("🔧 Отладка универсального парсера")
    print("=" * 50)
    
    # Запускаем отладку
    asyncio.run(debug_habr_parsing())
    
    # Тестируем сохранение
    asyncio.run(test_save_to_db())
    
    print("\n✅ Отладка завершена!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 