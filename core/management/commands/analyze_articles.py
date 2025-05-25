"""
Django management команда для анализа текста статей.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from core.models import Article
from core.text_analyzer import analyze_article_content
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Анализирует текст статей для определения тематики, тегов и локаций'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Количество статей для обработки за раз (по умолчанию: 100)',
        )
        parser.add_argument(
            '--only-unanalyzed',
            action='store_true',
            help='Анализировать только непроанализированные статьи',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Принудительно перезаписать результаты анализа',
        )
        parser.add_argument(
            '--source-id',
            type=int,
            help='Анализировать только статьи из конкретного источника',
        )
        parser.add_argument(
            '--article-id',
            type=int,
            help='Анализировать только конкретную статью',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать что будет сделано, без выполнения изменений',
        )

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        only_unanalyzed = options['only_unanalyzed']
        force = options['force']
        source_id = options['source_id']
        article_id = options['article_id']
        dry_run = options['dry_run']

        # Строим запрос для получения статей
        queryset = Article.objects.filter(is_active=True)

        if article_id:
            # Анализируем конкретную статью
            queryset = queryset.filter(id=article_id)
        else:
            # Фильтры для множественного анализа
            if source_id:
                queryset = queryset.filter(source_id=source_id)
            
            if only_unanalyzed and not force:
                queryset = queryset.filter(is_analyzed=False)

        total_articles = queryset.count()

        if total_articles == 0:
            self.stdout.write(
                self.style.WARNING('Нет статей для анализа с указанными критериями')
            )
            return

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Будет проанализировано {total_articles} статей')
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f'Начинаем анализ {total_articles} статей...')
        )

        processed = 0
        successful = 0
        errors = 0

        # Обрабатываем статьи батчами
        for offset in range(0, total_articles, batch_size):
            batch = queryset[offset:offset + batch_size]
            
            self.stdout.write(
                f'Обрабатываем батч {offset // batch_size + 1}: '
                f'статьи {offset + 1}-{min(offset + batch_size, total_articles)}'
            )

            for article in batch:
                try:
                    # Проверяем, нужно ли анализировать
                    if article.is_analyzed and not force:
                        self.stdout.write(
                            f'  - Пропускаем статью {article.id} (уже проанализирована)'
                        )
                        processed += 1
                        continue

                    # Выполняем анализ
                    result = analyze_article_content(article)

                    # Сохраняем результаты в транзакции
                    with transaction.atomic():
                        article.topic = result['topic']
                        article.tags = result['tags']
                        article.locations = result['locations']
                        article.is_analyzed = True
                        article.save(update_fields=['topic', 'tags', 'locations', 'is_analyzed'])

                    successful += 1
                    processed += 1

                    # Выводим прогресс
                    if successful % 10 == 0:
                        self.stdout.write(
                            f'  ✓ Обработано {successful} статей...'
                        )

                    # Выводим детали анализа
                    if options['verbosity'] >= 2:
                        self.stdout.write(
                            f'  ✓ Статья {article.id}: '
                            f'тема={result["topic"]}, '
                            f'тегов={len(result["tags"])}, '
                            f'локаций={len(result["locations"])}'
                        )

                except Exception as e:
                    errors += 1
                    processed += 1
                    logger.error(f"Ошибка анализа статьи {article.id}: {str(e)}")
                    self.stdout.write(
                        self.style.ERROR(
                            f'  ✗ Ошибка при анализе статьи {article.id}: {str(e)}'
                        )
                    )

        # Итоговая статистика
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(f'Анализ завершен!')
        )
        self.stdout.write(f'Всего обработано: {processed}')
        self.stdout.write(
            self.style.SUCCESS(f'Успешно проанализировано: {successful}')
        )
        if errors > 0:
            self.stdout.write(
                self.style.ERROR(f'Ошибок: {errors}')
            )

        # Статистика по результатам анализа
        if successful > 0:
            self.stdout.write('\nСтатистика анализа:')
            
            # Подсчет по темам
            analyzed_articles = Article.objects.filter(is_analyzed=True, is_active=True)
            topics_stats = {}
            for article in analyzed_articles:
                topic_display = article.get_topic_display()
                topics_stats[topic_display] = topics_stats.get(topic_display, 0) + 1
            
            self.stdout.write('Распределение по темам:')
            for topic, count in sorted(topics_stats.items(), key=lambda x: x[1], reverse=True):
                self.stdout.write(f'  - {topic}: {count}')

            # Общая статистика
            total_analyzed = analyzed_articles.count()
            total_with_tags = analyzed_articles.exclude(tags=[]).count()
            total_with_locations = analyzed_articles.exclude(locations=[]).count()
            
            self.stdout.write(f'\nОбщая статистика:')
            self.stdout.write(f'  - Всего проанализированных статей: {total_analyzed}')
            self.stdout.write(f'  - Статей с тегами: {total_with_tags}')
            self.stdout.write(f'  - Статей с локациями: {total_with_locations}') 