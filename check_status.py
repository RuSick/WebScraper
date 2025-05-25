#!/usr/bin/env python3
"""
Простой скрипт для проверки статуса системы MediaScope
"""
import os
import sys
import django

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Source, Article
from django.db.models import Count

def main():
    print("📊 Статус системы MediaScope")
    print("=" * 50)
    
    # Статистика источников
    total_sources = Source.objects.count()
    active_sources = Source.objects.filter(is_active=True).count()
    print(f"📰 Источники: {active_sources}/{total_sources} активных")
    
    # Статистика статей
    total_articles = Article.objects.count()
    active_articles = Article.objects.filter(is_active=True).count()
    analyzed_articles = Article.objects.filter(is_analyzed=True).count()
    unanalyzed_articles = Article.objects.filter(is_analyzed=False).count()
    
    print(f"📄 Статьи: {total_articles} всего")
    print(f"   ├─ Активных: {active_articles}")
    print(f"   ├─ Проанализированных: {analyzed_articles}")
    print(f"   └─ Ожидают анализа: {unanalyzed_articles}")
    
    # Топ источников по количеству статей
    print("\n🏆 Топ-5 источников по количеству статей:")
    top_sources = Source.objects.annotate(
        article_count=Count('articles')
    ).filter(article_count__gt=0).order_by('-article_count')[:5]
    
    for i, source in enumerate(top_sources, 1):
        print(f"   {i}. {source.name}: {source.article_count} статей")
    
    # Статистика по темам
    print("\n📊 Распределение по темам:")
    topics = Article.objects.filter(is_analyzed=True).values('topic').annotate(
        count=Count('topic')
    ).order_by('-count')
    
    for topic_data in topics:
        topic_code = topic_data['topic']
        # Получаем человекочитаемое название темы
        topic_choices = dict(Article.TOPIC_CHOICES)
        topic_name = topic_choices.get(topic_code, topic_code)
        count = topic_data['count']
        print(f"   • {topic_name}: {count}")
    
    print("\n✅ Проверка завершена!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 