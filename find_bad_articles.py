#!/usr/bin/env python3
"""
Скрипт для поиска проблемных статей в базе данных
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
from django.db.models import Q

def main():
    print("🔍 Поиск проблемных статей...")
    print("=" * 50)
    
    # Ищем статьи с проблемными заголовками
    bad_titles = Article.objects.filter(
        title__icontains="Комментарии"
    ).values('id', 'title', 'url', 'source__name')
    
    print(f"📝 Статьи с 'Комментарии' в заголовке: {len(bad_titles)}")
    for article in bad_titles[:10]:  # Показываем первые 10
        print(f"  ID: {article['id']}, Заголовок: '{article['title'][:50]}...', URL: {article['url'][:60]}...")
    
    # Ищем статьи без контента или с пустым контентом
    empty_content = Article.objects.filter(
        Q(content__isnull=True) | Q(content='')
    ).count()
    
    print(f"\n📄 Статьи без контента: {empty_content}")
    
    # Ищем статьи без summary или с пустым summary
    empty_summary = Article.objects.filter(
        Q(summary__isnull=True) | Q(summary='')
    ).count()
    
    print(f"📝 Статьи без summary: {empty_summary}")
    
    # Ищем статьи с подозрительными URL
    suspicious_urls = Article.objects.filter(
        url__iregex=r'.*(comments|users|sandbox|company|promo|newsletters).*'
    ).values('id', 'title', 'url', 'source__name')
    
    print(f"\n🚨 Статьи с подозрительными URL: {len(suspicious_urls)}")
    for article in suspicious_urls[:10]:
        print(f"  ID: {article['id']}, URL: {article['url']}")
    
    # Ищем статьи с нулевыми просмотрами и проблемами
    empty_articles = Article.objects.filter(
        read_count=0
    ).filter(
        Q(content__isnull=True) | Q(content='') | Q(summary__isnull=True) | Q(summary='')
    ).values('id', 'title', 'url', 'content', 'summary')
    
    print(f"\n🗑️ Потенциально пустые статьи (0 просмотров + проблемы с контентом): {len(empty_articles)}")
    for article in empty_articles[:5]:
        print(f"  ID: {article['id']}")
        print(f"    Заголовок: '{article['title'][:50]}...'")
        print(f"    URL: {article['url'][:60]}...")
        print(f"    Контент: '{str(article['content'])[:50]}...'")
        print(f"    Summary: '{str(article['summary'])[:50]}...'")
        print()
    
    # Общая статистика проблемных статей
    total_bad = Article.objects.filter(
        Q(title__icontains="Комментарии") |
        Q(url__iregex=r'.*(comments|users|sandbox|company|promo|newsletters).*') |
        Q(content__isnull=True) | Q(content='') |
        Q(summary__isnull=True) | Q(summary='')
    ).count()
    
    print(f"\n📊 Общее количество проблемных статей: {total_bad}")
    print("✅ Анализ завершен!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 