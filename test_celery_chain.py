#!/usr/bin/env python
"""
Тестовый скрипт для демонстрации цепочки задач Celery:
parse_source -> save_article -> analyze_article_text
"""

import os
import sys
import django
import time
from datetime import datetime

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Source, Article
from scraper.tasks import parse_source
from celery.result import AsyncResult


def test_celery_chain():
    """Тестирует полную цепочку задач Celery."""
    
    print("🚀 Тестирование цепочки задач Celery")
    print("=" * 50)
    
    # Получаем активный источник для тестирования
    source = Source.objects.filter(is_active=True).first()
    if not source:
        print("❌ Нет активных источников для тестирования")
        return
    
    print(f"📰 Тестируем источник: {source.name} (ID: {source.id})")
    print(f"🔗 URL: {source.url}")
    
    # Считаем статьи до парсинга
    articles_before = Article.objects.count()
    analyzed_before = Article.objects.filter(is_analyzed=True).count()
    
    print(f"\n📊 Статистика ДО парсинга:")
    print(f"   Всего статей: {articles_before}")
    print(f"   Проанализировано: {analyzed_before}")
    
    # Запускаем парсинг
    print(f"\n🔄 Запускаем парсинг источника {source.id}...")
    task_result = parse_source.delay(source.id)
    task_id = task_result.id
    
    print(f"📋 Task ID: {task_id}")
    print("⏳ Ожидаем завершения парсинга...")
    
    # Ждем завершения основной задачи парсинга
    start_time = time.time()
    timeout = 60  # 60 секунд таймаут
    
    while not task_result.ready() and (time.time() - start_time) < timeout:
        print(".", end="", flush=True)
        time.sleep(2)
    
    print()
    
    if task_result.ready():
        result = task_result.result
        print(f"✅ Парсинг завершен!")
        print(f"   Статус: {result.get('status')}")
        print(f"   Найдено статей: {result.get('found_articles', 0)}")
        print(f"   Запланировано сохранение: {result.get('scheduled_count', 0)}")
        
        # Ждем некоторое время для выполнения задач сохранения и анализа
        print("\n⏳ Ожидаем выполнения задач сохранения и анализа (30 сек)...")
        time.sleep(30)
        
        # Проверяем результаты
        articles_after = Article.objects.count()
        analyzed_after = Article.objects.filter(is_analyzed=True).count()
        
        print(f"\n📊 Статистика ПОСЛЕ парсинга:")
        print(f"   Всего статей: {articles_after}")
        print(f"   Проанализировано: {analyzed_after}")
        print(f"   Добавлено новых: {articles_after - articles_before}")
        print(f"   Новых проанализированных: {analyzed_after - analyzed_before}")
        
        # Показываем последние добавленные статьи
        recent_articles = Article.objects.filter(
            source=source
        ).order_by('-created_at')[:3]
        
        if recent_articles:
            print(f"\n📝 Последние статьи из {source.name}:")
            for i, article in enumerate(recent_articles, 1):
                status = "✅ Проанализирована" if article.is_analyzed else "⏳ В процессе анализа"
                print(f"   {i}. {article.title[:60]}...")
                print(f"      {status}")
                if article.is_analyzed and article.tags:
                    tags = article.tags[:3] if len(article.tags) > 3 else article.tags
                    print(f"      Теги: {', '.join(tags)}")
                print()
        
        print("🎉 Тест цепочки задач завершен!")
        print("\n💡 Цепочка работает следующим образом:")
        print("   1. parse_source() - парсит источник и находит статьи")
        print("   2. save_article() - сохраняет каждую статью в БД")
        print("   3. analyze_article_text() - анализирует текст статьи")
        print("   Каждый шаг автоматически запускает следующий!")
        
    else:
        print("❌ Таймаут! Парсинг не завершился за 60 секунд")
        print("   Возможно, источник недоступен или парсинг занимает много времени")


if __name__ == "__main__":
    test_celery_chain() 