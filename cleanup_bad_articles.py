#!/usr/bin/env python3
"""
Скрипт для очистки проблемных статей из базы данных
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
    print("🧹 Очистка проблемных статей из базы данных...")
    print("=" * 50)
    
    # Находим проблемные статьи
    bad_articles = Article.objects.filter(
        Q(title__icontains="Комментарии") |
        Q(url__iregex=r'.*(comments|users|sandbox|company|promo|newsletters).*') |
        Q(content__isnull=True) | Q(content='') |
        Q(summary__isnull=True) | Q(summary='')
    )
    
    total_bad = bad_articles.count()
    print(f"🗑️ Найдено проблемных статей: {total_bad}")
    
    if total_bad == 0:
        print("✅ Проблемных статей не найдено!")
        return 0
    
    # Показываем примеры
    print("\n📝 Примеры проблемных статей:")
    for article in bad_articles[:5]:
        print(f"  ID: {article.id}")
        print(f"    Заголовок: '{article.title[:50]}...'")
        print(f"    URL: {article.url[:60]}...")
        print(f"    Контент: {len(article.content or '')} символов")
        print()
    
    # Подтверждение удаления
    response = input(f"\n❓ Удалить {total_bad} проблемных статей? (y/N): ")
    if response.lower() != 'y':
        print("❌ Удаление отменено")
        return 0
    
    # Удаляем проблемные статьи
    deleted_count, _ = bad_articles.delete()
    print(f"✅ Удалено {deleted_count} проблемных статей")
    
    # Показываем новую статистику
    remaining_articles = Article.objects.count()
    print(f"📊 Осталось статей в базе: {remaining_articles}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 