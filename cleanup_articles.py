#!/usr/bin/env python
"""
Скрипт для очистки базы данных от неинформационных статей.

Удаляет:
1. Статьи с подозрительными заголовками (служебные страницы, соцсети, etc.)
2. Статьи с очень коротким или пустым контентом
3. Дублирующиеся статьи по URL

Использование:
    python cleanup_articles.py [--dry-run] [--verbose]
"""

import os
import sys
import django
import re
from datetime import datetime

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Article


def cleanup_suspicious_titles(dry_run=False, verbose=False):
    """Удаление статей с подозрительными заголовками."""
    
    suspicious_patterns = [
        r'(связаться|контакт|правила|регистрация|главная|о сайте)',
        r'(about|contact|rules|register|login|policy|main|index)',
        r'(comment|вконтакте|facebook|twitter|instagram|youtube|telegram)',
        r'(подписывайтесь|следите|смотрите|поделиться)',
        r'(реклама|advertisement|ads|размещение рекламы)',
        r'(помощь|help|support|поддержка|faq)',
        r'(404|error|ошибка|страница не найдена)',
        r'(loading|загрузка|подождите|maintenance)',
        r'(cookie|куки|согласие|gdpr|privacy)',
        r'^(меню|menu|навигация|navigation|поиск|search)$',
        r'^(undefined|null|none|empty|blank|test|тест|demo|демо)$',
    ]
    
    pattern = '|'.join(f'({p})' for p in suspicious_patterns)
    
    suspicious_articles = Article.objects.filter(
        title__iregex=pattern
    )
    
    count = suspicious_articles.count()
    
    if verbose:
        print(f"Найдено {count} статей с подозрительными заголовками:")
        for article in suspicious_articles[:10]:  # Показываем первые 10
            print(f"  - {article.title[:60]}... (ID: {article.id})")
        if count > 10:
            print(f"  ... и ещё {count - 10} статей")
    
    if not dry_run and count > 0:
        suspicious_articles.delete()
        print(f"✅ Удалено {count} статей с подозрительными заголовками")
    elif dry_run:
        print(f"🔍 [DRY RUN] Будет удалено {count} статей с подозрительными заголовками")
    
    return count


def cleanup_short_content(dry_run=False, verbose=False, min_length=100):
    """Удаление статей с очень коротким контентом."""
    
    short_articles = Article.objects.filter(
        content__isnull=False
    ).extra(
        where=[f'LENGTH(content) < {min_length}']
    )
    
    count = short_articles.count()
    
    if verbose:
        print(f"Найдено {count} статей с контентом короче {min_length} символов:")
        for article in short_articles[:5]:  # Показываем первые 5
            content_len = len(article.content) if article.content else 0
            print(f"  - {article.title[:50]}... ({content_len} символов)")
        if count > 5:
            print(f"  ... и ещё {count - 5} статей")
    
    if not dry_run and count > 0:
        short_articles.delete()
        print(f"✅ Удалено {count} статей с коротким контентом")
    elif dry_run:
        print(f"🔍 [DRY RUN] Будет удалено {count} статей с коротким контентом")
    
    return count


def cleanup_empty_content(dry_run=False, verbose=False):
    """Удаление статей с пустым контентом и коротким заголовком."""
    
    empty_articles = Article.objects.filter(
        content__isnull=True
    ).extra(
        where=['LENGTH(title) < 15']
    ).union(
        Article.objects.filter(
            content__exact=''
        ).extra(
            where=['LENGTH(title) < 15']
        )
    )
    
    count = empty_articles.count()
    
    if verbose:
        print(f"Найдено {count} статей с пустым контентом и коротким заголовком:")
        for article in empty_articles[:5]:
            print(f"  - {article.title[:50]}... (ID: {article.id})")
        if count > 5:
            print(f"  ... и ещё {count - 5} статей")
    
    if not dry_run and count > 0:
        empty_articles.delete()
        print(f"✅ Удалено {count} статей с пустым контентом")
    elif dry_run:
        print(f"🔍 [DRY RUN] Будет удалено {count} статей с пустым контентом")
    
    return count


def cleanup_duplicate_urls(dry_run=False, verbose=False):
    """Удаление дублирующихся статей по URL."""
    
    # Находим дублирующиеся URL
    from django.db.models import Count
    
    duplicate_urls = Article.objects.values('url').annotate(
        count=Count('url')
    ).filter(count__gt=1)
    
    total_duplicates = 0
    
    for dup in duplicate_urls:
        url = dup['url']
        articles = Article.objects.filter(url=url).order_by('created_at')
        
        # Оставляем самую старую статью, удаляем остальные
        duplicates_to_delete = articles[1:]
        count = duplicates_to_delete.count()
        total_duplicates += count
        
        if verbose and count > 0:
            print(f"URL {url}: найдено {count + 1} дубликатов, удаляем {count}")
        
        if not dry_run and count > 0:
            duplicates_to_delete.delete()
    
    if total_duplicates > 0:
        if not dry_run:
            print(f"✅ Удалено {total_duplicates} дублирующихся статей")
        else:
            print(f"🔍 [DRY RUN] Будет удалено {total_duplicates} дублирующихся статей")
    
    return total_duplicates


def main():
    """Основная функция очистки."""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Очистка базы данных от неинформационных статей')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Показать что будет удалено, но не удалять')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Подробный вывод')
    parser.add_argument('--min-content-length', type=int, default=100,
                       help='Минимальная длина контента (по умолчанию: 100)')
    
    args = parser.parse_args()
    
    print(f"🧹 Начинаем очистку базы данных от неинформационных статей")
    print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if args.dry_run:
        print("🔍 Режим DRY RUN - изменения не будут сохранены")
    
    print()
    
    # Статистика до очистки
    total_before = Article.objects.count()
    print(f"📊 Статей в базе до очистки: {total_before}")
    print()
    
    # Выполняем очистку
    deleted_suspicious = cleanup_suspicious_titles(args.dry_run, args.verbose)
    print()
    
    deleted_short = cleanup_short_content(args.dry_run, args.verbose, args.min_content_length)
    print()
    
    deleted_empty = cleanup_empty_content(args.dry_run, args.verbose)
    print()
    
    deleted_duplicates = cleanup_duplicate_urls(args.dry_run, args.verbose)
    print()
    
    # Статистика после очистки
    if not args.dry_run:
        total_after = Article.objects.count()
        total_deleted = deleted_suspicious + deleted_short + deleted_empty + deleted_duplicates
        
        print(f"📊 Результаты очистки:")
        print(f"  Статей до очистки: {total_before}")
        print(f"  Статей после очистки: {total_after}")
        print(f"  Всего удалено: {total_deleted}")
        print(f"  Подозрительные заголовки: {deleted_suspicious}")
        print(f"  Короткий контент: {deleted_short}")
        print(f"  Пустой контент: {deleted_empty}")
        print(f"  Дубликаты: {deleted_duplicates}")
        
        if total_deleted > 0:
            print(f"✅ Очистка завершена успешно!")
        else:
            print(f"ℹ️  Статей для удаления не найдено")
    else:
        total_to_delete = deleted_suspicious + deleted_short + deleted_empty + deleted_duplicates
        print(f"🔍 [DRY RUN] Всего будет удалено: {total_to_delete} статей")


if __name__ == '__main__':
    main() 