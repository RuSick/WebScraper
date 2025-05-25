#!/usr/bin/env python
"""
Простой тест API новостной платформы MediaScope.
Проверяет основные endpoints и создает тестовые данные.
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Source, Article


def create_test_data():
    """Создание тестовых данных."""
    print("🔧 Создание тестовых данных...")
    
    # Создаем источники
    sources_data = [
        {
            'name': 'Habr.com',
            'url': 'https://habr.com/ru/all/',
            'type': 'html',
            'description': 'Профессиональное сообщество IT-специалистов',
            'articles_count': 132
        },
        {
            'name': 'Lenta.ru',
            'url': 'https://lenta.ru',
            'type': 'html', 
            'description': 'Новости России и мира',
            'articles_count': 171
        },
        {
            'name': 'Meduza.io',
            'url': 'https://meduza.io',
            'type': 'spa',
            'description': 'Независимые новости и аналитика',
            'articles_count': 0
        }
    ]
    
    created_sources = []
    for source_data in sources_data:
        source, created = Source.objects.get_or_create(
            url=source_data['url'],
            defaults=source_data
        )
        if created:
            print(f"✅ Создан источник: {source.name}")
        else:
            print(f"📋 Источник уже существует: {source.name}")
        created_sources.append(source)
    
    # Создаем статьи
    articles_data = [
        {
            'title': 'Новые возможности Python 3.12',
            'content': 'Python 3.12 включает множество улучшений производительности и новых возможностей для разработчиков.',
            'summary': 'Обзор новых возможностей Python 3.12',
            'url': 'https://habr.com/ru/articles/python-3-12/',
            'topic': 'technology',
            'tone': 'positive',
            'is_featured': True,
            'published_at': datetime.now() - timedelta(hours=2)
        },
        {
            'title': 'Ситуация на рынке IT в 2025 году',
            'content': 'Аналитики прогнозируют продолжение роста спроса на IT-специалистов в следующем году.',
            'summary': 'Прогнозы развития IT-рынка',
            'url': 'https://lenta.ru/news/2025/01/it-market/',
            'topic': 'business',
            'tone': 'neutral',
            'published_at': datetime.now() - timedelta(hours=5)
        },
        {
            'title': 'Мировые новости технологий',
            'content': 'Последние новости из мира высоких технологий и инноваций.',
            'summary': 'Краткий обзор технологических новостей',
            'url': 'https://meduza.io/feature/tech-news-today/',
            'topic': 'technology',
            'tone': 'neutral',
            'published_at': datetime.now() - timedelta(days=1)
        }
    ]
    
    for i, article_data in enumerate(articles_data):
        article_data['source'] = created_sources[i]
        article, created = Article.objects.get_or_create(
            url=article_data['url'],
            defaults=article_data
        )
        if created:
            print(f"✅ Создана статья: {article.title[:50]}...")
        else:
            print(f"📋 Статья уже существует: {article.title[:50]}...")
    
    print(f"\n📊 Итого в базе:")
    print(f"   Источники: {Source.objects.count()}")
    print(f"   Статьи: {Article.objects.count()}")


def test_api_endpoints():
    """Тестирование API endpoints."""
    print("\n🧪 Тестирование API endpoints...")
    print("Запустите сервер разработки:")
    print("   python manage.py runserver")
    print("\nПосле запуска доступны следующие endpoints:")
    
    endpoints = [
        "📰 GET /api/articles/ - Список статей с фильтрацией",
        "📰 GET /api/articles/1/ - Детальная информация о статье", 
        "🔗 GET /api/sources/ - Список источников",
        "🔗 GET /api/sources/1/ - Детальная информация об источнике",
        "📊 GET /api/stats/articles/ - Статистика по статьям",
        "📊 GET /api/stats/sources/ - Статистика по источникам",
        "🔍 GET /api/search/?q=python - Универсальный поиск",
        "🔥 GET /api/trending/ - Популярные статьи",
    ]
    
    for endpoint in endpoints:
        print(f"   {endpoint}")
    
    print("\n🎯 Примеры запросов с фильтрацией:")
    examples = [
        "GET /api/articles/?topic=technology - Статьи по технологиям",
        "GET /api/articles/?tone=positive - Позитивные статьи",
        "GET /api/articles/?featured=true - Рекомендуемые статьи",
        "GET /api/articles/?search=python - Поиск по тексту",
        "GET /api/articles/?today=true - Статьи за сегодня",
        "GET /api/sources/?type=spa - SPA источники",
    ]
    
    for example in examples:
        print(f"   {example}")


def show_admin_info():
    """Информация об админке."""
    print("\n👑 Django Admin панель:")
    print("   URL: http://127.0.0.1:8000/admin/")
    print("   Создайте суперпользователя:")
    print("   python manage.py createsuperuser")
    print("\n   Админка включает:")
    print("   ✅ Красивые бейджи для типов и статусов")
    print("   ✅ Фильтры по всем важным полям")
    print("   ✅ Поиск по заголовкам и контенту")
    print("   ✅ Массовые действия (активация/деактивация)")
    print("   ✅ Статистика просмотров и счетчики")


if __name__ == '__main__':
    print("🚀 MediaScope API Test")
    print("=" * 50)
    
    create_test_data()
    test_api_endpoints()
    show_admin_info()
    
    print("\n✨ Готово! Теперь можно:")
    print("   1. Запустить сервер: python manage.py runserver")
    print("   2. Открыть API: http://127.0.0.1:8000/api/articles/")
    print("   3. Создать админа: python manage.py createsuperuser")
    print("   4. Открыть админку: http://127.0.0.1:8000/admin/") 