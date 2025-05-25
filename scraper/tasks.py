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
def analyze_article_text(article_id: int) -> Dict[str, Any]:
    """
    Задача для анализа текста конкретной статьи.
    
    Args:
        article_id: ID статьи для анализа
        
    Returns:
        Результат анализа
    """
    try:
        article = Article.objects.get(id=article_id)
        
        if article.is_analyzed:
            logger.info(f"Article {article_id} already analyzed, skipping")
            return {'status': 'already_analyzed'}
        
        # Выполняем анализ
        result = analyze_article_content(article)
        
        # Обновляем статью с результатами анализа
        article.topic = result['topic']
        article.tags = result['tags']
        article.locations = result['locations']
        article.is_analyzed = True
        article.save(update_fields=['topic', 'tags', 'locations', 'is_analyzed'])
        
        logger.info(f"Article {article_id} analyzed successfully: topic={result['topic']}, tags={len(result['tags'])}, locations={len(result['locations'])}")
        
        return {
            'status': 'success',
            'article_id': article_id,
            'topic': result['topic'],
            'tags_count': len(result['tags']),
            'locations_count': len(result['locations'])
        }
        
    except Article.DoesNotExist:
        logger.error(f"Article {article_id} not found")
        return {'status': 'not_found', 'error': f'Article {article_id} not found'}
    except Exception as e:
        logger.error(f"Error analyzing article {article_id}: {str(e)}")
        return {'status': 'error', 'error': str(e)}


@shared_task
def analyze_unanalyzed_articles(batch_size: int = 50) -> Dict[str, Any]:
    """
    Задача для анализа всех непроанализированных статей.
    
    Args:
        batch_size: Количество статей для обработки за раз
        
    Returns:
        Статистика обработки
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
def parse_source(source_id: int) -> int:
    """
    Задача для парсинга одного источника.
    
    Использует универсальный парсер для всех источников.
    """
    try:
        source = Source.objects.get(id=source_id)
        if not source.is_active:
            logger.info(f"Source {source.name} is inactive, skipping")
            return 0
        
        # Используем универсальный парсер для всех источников
        logger.info(f"Используем универсальный парсер для {source.name} (тип: {source.type})")
        articles = asyncio.run(fetch_generic_articles(source))
        
        # Сохраняем статьи
        saved_count = save_articles(articles, source)
        logger.info(f"Saved {saved_count} articles from {source.name}")
        return saved_count
        
    except Exception as e:
        logger.error(f"Error parsing source {source_id}: {str(e)}")
        raise

async def parse_articles(parser) -> List[Dict[str, Any]]:
    """Асинхронный парсинг статей."""
    async with parser as p:
        return await p.fetch_articles()

def save_articles(articles: List[Dict[str, Any]], source: Source) -> int:
    """Сохранение статей в базу данных."""
    saved_count = 0
    created_article_ids = []
    
    for article_data in articles:
        try:
            # Проверяем, существует ли уже статья с таким URL
            if Article.objects.filter(url=article_data['url']).exists():
                continue
            
            # Определяем дату публикации
            published_at = article_data.get('published_at')
            if published_at is None:
                published_at = timezone.now()
            elif isinstance(published_at, str):
                try:
                    published_at = date_parser.parse(published_at)
                except:
                    published_at = timezone.now()
            
            # Создаем новую статью (без tone поля)
            article = Article.objects.create(
                title=article_data['title'],
                content=article_data.get('content', ''),
                summary=article_data.get('summary', ''),
                url=article_data['url'],
                published_at=published_at,
                source=source,
                topic=article_data.get('topic', 'other'),
                is_featured=False,
                is_active=True,
                is_analyzed=False  # Новые статьи не проанализированы
            )
            saved_count += 1
            created_article_ids.append(article.id)
            
        except Exception as e:
            logger.error(f"Error saving article {article_data['url']}: {str(e)}")
            continue
    
    # Обновляем счетчик статей в источнике
    source.articles_count = source.articles.count()
    source.last_parsed = timezone.now()
    source.save()
    
    # Запускаем анализ для новых статей
    if created_article_ids:
        logger.info(f"Scheduling text analysis for {len(created_article_ids)} new articles")
        for article_id in created_article_ids:
            analyze_article_text.delay(article_id)
    
    return saved_count

@shared_task
def parse_all_sources():
    """Задача для парсинга всех активных источников."""
    sources = Source.objects.filter(is_active=True)
    scheduled_tasks = 0
    
    for source in sources:
        try:
            # Запускаем задачу парсинга асинхронно
            parse_source.delay(source.id)
            scheduled_tasks += 1
            logger.info(f"Scheduled parsing for source {source.name} (ID: {source.id})")
        except Exception as e:
            logger.error(f"Error scheduling parse for source {source.id}: {str(e)}")
    
    logger.info(f"Scheduled parsing for {scheduled_tasks} sources")
    return scheduled_tasks

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