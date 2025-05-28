from celery import shared_task
from typing import List, Dict, Any
import asyncio
import logging
from datetime import datetime
from django.utils import timezone
from dateutil import parser as date_parser

from core.models import Source, Article
from core.text_analyzer import analyze_article_content
from .parsers.universal_parser import fetch_generic_articles
# TODO: Импортировать другие парсеры при необходимости

logger = logging.getLogger(__name__)

@shared_task
def parse_source(source_id: int) -> Dict[str, Any]:
    """
    Задача для парсинга одного источника.
    
    Использует универсальный парсер и отправляет каждую статью 
    в отдельную задачу save_article для сохранения и анализа.
    """
    try:
        source = Source.objects.get(id=source_id)
        if not source.is_active:
            logger.info(f"Source {source.name} is inactive, skipping")
            return {'status': 'inactive', 'saved_count': 0}
        
        logger.info(f"Начинаем парсинг {source.name} (тип: {source.type})")
        
        # Используем универсальный парсер
        articles = asyncio.run(fetch_generic_articles(source))
        
        if not articles:
            logger.warning(f"Не найдено статей для {source.name}")
            return {'status': 'no_articles', 'saved_count': 0}
        
        # Отправляем каждую статью в отдельную задачу сохранения
        scheduled_count = 0
        for article_data in articles:
            try:
                # Подготавливаем данные для задачи сохранения
                save_data = {
                    'title': article_data['title'],
                    'content': article_data.get('content', ''),
                    'summary': article_data.get('summary', ''),
                    'url': article_data['url'],
                    'published_at': article_data.get('published_at'),
                    'source_id': source.id,
                    'topic': article_data.get('topic', 'other')
                }
                
                # Запускаем задачу сохранения асинхронно
                save_article.delay(save_data)
                scheduled_count += 1
                
            except Exception as e:
                logger.error(f"Ошибка планирования сохранения статьи {article_data.get('url', 'unknown')}: {e}")
                continue
        
        # Обновляем время последнего парсинга
        source.last_parsed = timezone.now()
        source.save(update_fields=['last_parsed'])
        
        logger.info(f"Запланировано сохранение {scheduled_count} статей из {source.name}")
        
        return {
            'status': 'success',
            'source_name': source.name,
            'found_articles': len(articles),
            'scheduled_count': scheduled_count
        }
        
    except Source.DoesNotExist:
        logger.error(f"Source {source_id} not found")
        return {'status': 'not_found', 'error': f'Source {source_id} not found'}
    except Exception as e:
        logger.error(f"Error parsing source {source_id}: {str(e)}")
        return {'status': 'error', 'error': str(e)}

@shared_task
def save_article(article_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Задача для сохранения статьи в БД.
    
    Проверяет уникальность по URL, сохраняет новую статью
    и автоматически запускает анализ текста.
    """
    try:
        url = article_data['url']
        source_id = article_data['source_id']
        
        # Проверяем, существует ли уже статья с таким URL
        if Article.objects.filter(url=url).exists():
            logger.debug(f"Статья уже существует: {url}")
            return {'status': 'duplicate', 'url': url}
        
        # Получаем источник
        try:
            source = Source.objects.get(id=source_id)
        except Source.DoesNotExist:
            logger.error(f"Source {source_id} not found for article {url}")
            return {'status': 'source_not_found', 'url': url}
        
        # Обрабатываем дату публикации
        published_at = article_data.get('published_at')
        if published_at is None:
            published_at = timezone.now()
        elif isinstance(published_at, str):
            try:
                published_at = date_parser.parse(published_at)
                # Если дата naive, делаем её aware
                if published_at.tzinfo is None:
                    published_at = timezone.make_aware(published_at)
            except Exception as e:
                logger.warning(f"Не удалось распарсить дату '{published_at}': {e}")
                published_at = timezone.now()
        
        # Создаем новую статью
        article = Article.objects.create(
            title=article_data['title'],
            content=article_data.get('content', ''),
            summary=article_data.get('summary', ''),
            url=url,
            published_at=published_at,
            source=source,
            topic=article_data.get('topic', 'other'),
            is_featured=False,
            is_active=True,
            is_analyzed=False  # Будет установлено в True после анализа
        )
        
        logger.info(f"Сохранена новая статья: {article.title} (ID: {article.id})")
        
        # Обновляем счетчик статей в источнике
        source.articles_count = source.articles.count()
        source.save(update_fields=['articles_count'])
        
        # Автоматически запускаем анализ текста
        analyze_article_text.delay(article.id)
        
        return {
            'status': 'created',
            'article_id': article.id,
            'title': article.title,
            'url': url,
            'analysis_scheduled': True
        }
        
    except Exception as e:
        logger.error(f"Ошибка сохранения статьи {article_data.get('url', 'unknown')}: {str(e)}")
        return {'status': 'error', 'error': str(e), 'url': article_data.get('url')}

@shared_task
def analyze_article_text(article_id: int) -> Dict[str, Any]:
    """
    Задача для анализа текста конкретной статьи.
    
    Определяет тему, теги и локации с помощью NLP-анализа
    и сохраняет результаты в БД.
    
    Поддерживает два типа анализаторов:
    - spaCy (ML-based) - более точный, медленнее
    - Legacy (dictionary-based) - быстрый, менее точный
    """
    try:
        article = Article.objects.get(id=article_id)
        
        if article.is_analyzed:
            logger.info(f"Article {article_id} already analyzed, skipping")
            return {'status': 'already_analyzed', 'article_id': article_id}
        
        logger.info(f"Начинаем анализ статьи: {article.title} (ID: {article_id})")
        
        # Выбираем анализатор на основе настроек
        from django.conf import settings
        use_spacy = getattr(settings, 'USE_SPACY_ANALYZER', False)
        
        if use_spacy:
            try:
                # Используем spaCy анализатор
                from core.spacy_analyzer import analyze_article_content_spacy
                result = analyze_article_content_spacy(article)
                analyzer_type = 'spacy'
                logger.info(f"Использован spaCy анализатор для статьи {article_id}")
            except Exception as e:
                logger.error(f"Ошибка spaCy анализатора: {e}")
                # Fallback на legacy анализатор
                from core.text_analyzer import analyze_article_content
                result = analyze_article_content(article)
                analyzer_type = 'legacy_fallback'
                logger.info(f"Переключились на legacy анализатор для статьи {article_id}")
        else:
            # Используем legacy анализатор
            from core.text_analyzer import analyze_article_content
            result = analyze_article_content(article)
            analyzer_type = 'legacy'
            logger.info(f"Использован legacy анализатор для статьи {article_id}")
        
        # Обновляем статью с результатами анализа
        article.topic = result['topic']
        article.tags = result['tags']
        article.locations = result['locations']
        article.is_analyzed = True
        article.save(update_fields=['topic', 'tags', 'locations', 'is_analyzed'])
        
        # Подготавливаем результат для логирования
        entities_info = ""
        if 'entities' in result and result['entities']:
            entities_count = len(result['entities'])
            entities_info = f", сущностей={entities_count}"
        
        logger.info(f"Анализ завершен для статьи {article_id} ({analyzer_type}): "
                   f"тема={result['topic']}, тегов={len(result['tags'])}, "
                   f"локаций={len(result['locations'])}{entities_info}")
        
        return {
            'status': 'success',
            'article_id': article_id,
            'analyzer_type': analyzer_type,
            'topic': result['topic'],
            'tags_count': len(result['tags']),
            'locations_count': len(result['locations']),
            'entities_count': len(result.get('entities', [])),
            'tags': result['tags'][:5],  # Первые 5 тегов для логирования
            'locations': result['locations'][:3],  # Первые 3 локации
            'entities': [ent['text'] for ent in result.get('entities', [])][:3]  # Первые 3 сущности
        }
        
    except Article.DoesNotExist:
        logger.error(f"Article {article_id} not found")
        return {'status': 'not_found', 'error': f'Article {article_id} not found'}
    except Exception as e:
        logger.error(f"Error analyzing article {article_id}: {str(e)}")
        return {'status': 'error', 'error': str(e), 'article_id': article_id}

@shared_task
def analyze_unanalyzed_articles(batch_size: int = 50) -> Dict[str, Any]:
    """
    Задача для анализа всех непроанализированных статей.
    
    Запускает анализ для статей, которые еще не были проанализированы.
    """
    try:
        # Получаем непроанализированные статьи
        unanalyzed_articles = Article.objects.filter(
            is_analyzed=False,
            is_active=True
        ).only('id')[:batch_size]
        
        total_count = unanalyzed_articles.count()
        if total_count == 0:
            logger.info("No unanalyzed articles found")
            return {'status': 'no_articles', 'processed': 0}
        
        # Запускаем анализ для каждой статьи
        success_count = 0
        error_count = 0
        
        for article in unanalyzed_articles:
            try:
                # Запускаем задачу анализа асинхронно
                analyze_article_text.delay(article.id)
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to schedule analysis for article {article.id}: {str(e)}")
                error_count += 1
        
        logger.info(f"Scheduled analysis for {success_count} articles, {error_count} errors")
        
        return {
            'status': 'success',
            'scheduled': success_count,
            'errors': error_count,
            'total_found': total_count
        }
        
    except Exception as e:
        logger.error(f"Error in analyze_unanalyzed_articles: {str(e)}")
        return {'status': 'error', 'error': str(e)}

@shared_task
def parse_all_sources() -> Dict[str, Any]:
    """
    Задача для парсинга всех активных источников.
    
    Запускает отдельные задачи парсинга для каждого активного источника.
    """
    try:
        sources = Source.objects.filter(is_active=True)
        
        if not sources.exists():
            logger.info("No active sources found")
            return {'status': 'no_sources', 'scheduled': 0}
        
        scheduled_count = 0
        error_count = 0
        
        for source in sources:
            try:
                parse_source.delay(source.id)
                scheduled_count += 1
                logger.info(f"Scheduled parsing for {source.name}")
            except Exception as e:
                logger.error(f"Error scheduling parse for source {source.id}: {str(e)}")
                error_count += 1
        
        logger.info(f"Scheduled parsing for {scheduled_count} sources, {error_count} errors")
        
        return {
            'status': 'success',
            'scheduled': scheduled_count,
            'errors': error_count,
            'total_sources': sources.count()
        }
        
    except Exception as e:
        logger.error(f"Error in parse_all_sources: {str(e)}")
        return {'status': 'error', 'error': str(e)}

@shared_task
def collect_habr_articles(include_content=True, max_articles=20):
    """
    Celery задача для сбора статей с Хабра.
    
    Args:
        include_content: Получать ли полный контент статей
        max_articles: Максимальное количество статей для обработки
    """
    try:
        # Получаем или создаем источник для Хабра
        habr_source, created = Source.objects.get_or_create(
            url='https://habr.com',
            defaults={
                'name': 'Habr',
                'type': 'html',
                'is_active': True
            }
        )
        
        # Запускаем асинхронную функцию в синхронном контексте Celery
        articles = asyncio.run(fetch_habr_articles(include_content, max_articles))
        
        new_articles_count = 0
        updated_articles_count = 0
        
        for article_data in articles:
            try:
                # Парсим дату публикации
                pub_date = None
                if article_data.get('pub_date'):
                    try:
                        pub_date = datetime.fromisoformat(article_data['pub_date'].replace('Z', '+00:00'))
                    except ValueError:
                        pub_date = timezone.now()
                else:
                    pub_date = timezone.now()
                
                # Проверяем, существует ли статья с таким URL
                article, created = Article.objects.get_or_create(
                    url=article_data['url'],
                    defaults={
                        'title': article_data['title'],
                        'content': article_data.get('content', ''),
                        'published_at': pub_date,
                        'source': habr_source,
                    }
                )
                
                if created:
                    new_articles_count += 1
                    logger.info(f"Добавлена новая статья: {article.title}")
                else:
                    # Обновляем контент, если он был пустым
                    if not article.content and article_data.get('content'):
                        article.content = article_data['content']
                        article.save()
                        updated_articles_count += 1
                        logger.info(f"Обновлен контент статьи: {article.title}")
                        
            except Exception as e:
                logger.error(f"Ошибка при сохранении статьи {article_data.get('url', 'unknown')}: {str(e)}")
                continue
        
        result_message = f"Завершен сбор статей с Хабра. Новых: {new_articles_count}, обновлено: {updated_articles_count}"
        logger.info(result_message)
        
        return {
            'status': 'success',
            'new_articles': new_articles_count,
            'updated_articles': updated_articles_count,
            'total_processed': len(articles),
            'message': result_message
        }
        
    except Exception as e:
        error_message = f"Ошибка при сборе статей с Хабра: {str(e)}"
        logger.error(error_message)
        return {
            'status': 'error',
            'error': error_message
        }

@shared_task
def collect_lenta_articles():
    """
    Celery задача для сбора статей с Lenta.ru.
    """
    try:
        # Получаем или создаем источник для Lenta.ru
        lenta_source, created = Source.objects.get_or_create(
            url='https://lenta.ru',
            defaults={
                'name': 'Lenta.ru',
                'type': 'lenta',
                'is_active': True
            }
        )
        
        # Запускаем асинхронную функцию парсера
        async def fetch_lenta():
            async with LentaParser() as parser:
                return await parser.fetch_articles()
        
        articles = asyncio.run(fetch_lenta())
        
        new_articles_count = 0
        updated_articles_count = 0
        
        for article_data in articles:
            try:
                # Парсим дату публикации
                pub_date = None
                if article_data.get('published_at'):
                    try:
                        # Парсим дату и делаем её timezone-aware
                        naive_date = datetime.fromisoformat(article_data['published_at'])
                        # Если дата naive, добавляем UTC timezone
                        if naive_date.tzinfo is None:
                            pub_date = timezone.make_aware(naive_date)
                        else:
                            pub_date = naive_date
                    except ValueError:
                        pub_date = timezone.now()
                else:
                    pub_date = timezone.now()
                
                # Проверяем, существует ли статья с таким URL
                article, created = Article.objects.get_or_create(
                    url=article_data['url'],
                    defaults={
                        'title': article_data['title'],
                        'content': article_data.get('content', ''),
                        'published_at': pub_date,
                        'source': lenta_source,
                    }
                )
                
                if created:
                    new_articles_count += 1
                    logger.info(f"Добавлена новая статья с Lenta.ru: {article.title}")
                else:
                    # Обновляем контент, если он был пустым
                    if not article.content and article_data.get('content'):
                        article.content = article_data['content']
                        article.save()
                        updated_articles_count += 1
                        logger.info(f"Обновлен контент статьи с Lenta.ru: {article.title}")
                        
            except Exception as e:
                logger.error(f"Ошибка при сохранении статьи с Lenta.ru {article_data.get('url', 'unknown')}: {str(e)}")
                continue
        
        result_message = f"Завершен сбор статей с Lenta.ru. Новых: {new_articles_count}, обновлено: {updated_articles_count}"
        logger.info(result_message)
        
        return {
            'status': 'success',
            'new_articles': new_articles_count,
            'updated_articles': updated_articles_count,
            'total_processed': len(articles),
            'message': result_message
        }
        
    except Exception as e:
        error_message = f"Ошибка при сборе статей с Lenta.ru: {str(e)}"
        logger.error(error_message)
        return {
            'status': 'error',
            'error': error_message
        }

@shared_task
def collect_all_sources():
    """Задача для сбора новостей со всех источников."""
    results = []
    
    # Собираем с Хабра
    habr_result = collect_habr_articles(include_content=True, max_articles=20)
    results.append(('Habr', habr_result))
    
    # Собираем с Lenta.ru
    lenta_result = collect_lenta_articles()
    results.append(('Lenta.ru', lenta_result))
    
    return {
        'status': 'completed',
        'sources': results,
        'timestamp': timezone.now().isoformat()
    }

@shared_task
def test_universal_parser(source_url: str, source_name: str = None):
    """
    Тестовая задача для проверки универсального парсера на произвольном URL.
    
    Args:
        source_url: URL для тестирования
        source_name: Имя источника (опционально)
    
    Returns:
        Результат парсинга
    """
    try:
        # Создаем временный объект источника
        from types import SimpleNamespace
        temp_source = SimpleNamespace()
        temp_source.url = source_url
        temp_source.name = source_name or source_url
        
        # Запускаем универсальный парсер
        articles = asyncio.run(fetch_generic_articles(temp_source))
        
        result = {
            'status': 'success',
            'url': source_url,
            'articles_found': len(articles),
            'articles': articles[:5],  # Первые 5 для демонстрации
            'message': f"Универсальный парсер нашел {len(articles)} статей на {source_url}"
        }
        
        logger.info(result['message'])
        return result
        
    except Exception as e:
        error_message = f"Ошибка универсального парсера для {source_url}: {str(e)}"
        logger.error(error_message)
        return {
            'status': 'error',
            'url': source_url,
            'error': error_message
        }

@shared_task
def collect_universal_articles(source_id: int):
    """
    Сбор статей с помощью универсального парсера для конкретного источника.
    
    Args:
        source_id: ID источника в базе данных
    """
    try:
        source = Source.objects.get(id=source_id)
        
        # Запускаем универсальный парсер
        articles = asyncio.run(fetch_generic_articles(source))
        
        new_articles_count = 0
        updated_articles_count = 0
        
        for article_data in articles:
            try:
                # Парсим дату публикации
                pub_date = None
                if article_data.get('published_at'):
                    try:
                        # Парсим дату и делаем её timezone-aware
                        naive_date = datetime.fromisoformat(article_data['published_at'])
                        # Если дата naive, добавляем UTC timezone
                        if naive_date.tzinfo is None:
                            pub_date = timezone.make_aware(naive_date)
                        else:
                            pub_date = naive_date
                    except ValueError:
                        pub_date = timezone.now()
                else:
                    pub_date = timezone.now()
                
                # Проверяем, существует ли статья с таким URL
                article, created = Article.objects.get_or_create(
                    url=article_data['url'],
                    defaults={
                        'title': article_data['title'],
                        'content': article_data.get('content', ''),
                        'published_at': pub_date,
                        'source': source,
                    }
                )
                
                if created:
                    new_articles_count += 1
                    logger.info(f"Добавлена новая статья (универсальный парсер): {article.title}")
                else:
                    # Обновляем контент, если он был пустым
                    if not article.content and article_data.get('content'):
                        article.content = article_data['content']
                        article.save()
                        updated_articles_count += 1
                        logger.info(f"Обновлен контент статьи (универсальный парсер): {article.title}")
                        
            except Exception as e:
                logger.error(f"Ошибка при сохранении статьи {article_data.get('url', 'unknown')}: {str(e)}")
                continue
        
        result_message = f"Универсальный парсер для {source.name}: новых {new_articles_count}, обновлено {updated_articles_count}"
        logger.info(result_message)
        
        return {
            'status': 'success',
            'source_name': source.name,
            'new_articles': new_articles_count,
            'updated_articles': updated_articles_count,
            'total_processed': len(articles),
            'message': result_message
        }
        
    except Source.DoesNotExist:
        error_message = f"Источник с ID {source_id} не найден"
        logger.error(error_message)
        return {
            'status': 'error',
            'error': error_message
        }
    except Exception as e:
        error_message = f"Ошибка универсального парсера для источника {source_id}: {str(e)}"
        logger.error(error_message)
        return {
            'status': 'error',
            'error': error_message
        } 