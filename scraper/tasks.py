from celery import shared_task
from typing import List, Dict, Any
import asyncio
import logging
from datetime import datetime

from core.models import Source, Article
from .parsers.rss import RSSParser
# TODO: Импортировать другие парсеры

logger = logging.getLogger(__name__)

@shared_task
def parse_source(source_id: int) -> int:
    """Задача для парсинга одного источника."""
    try:
        source = Source.objects.get(id=source_id)
        if not source.is_active:
            logger.info(f"Source {source.name} is inactive, skipping")
            return 0
        
        # Выбираем парсер в зависимости от типа источника
        parser_class = {
            'rss': RSSParser,
            # TODO: Добавить другие парсеры
        }.get(source.type)
        
        if not parser_class:
            logger.error(f"Unknown source type: {source.type}")
            return 0
        
        # Запускаем асинхронный парсинг
        parser = parser_class(source.url, source.name)
        articles = asyncio.run(parse_articles(parser))
        
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
    for article_data in articles:
        try:
            # Проверяем, существует ли уже статья с таким URL
            if Article.objects.filter(url=article_data['url']).exists():
                continue
            
            # Создаем новую статью
            Article.objects.create(
                title=article_data['title'],
                content=article_data['content'],
                url=article_data['url'],
                published_at=article_data['published_at'],
                source=source
            )
            saved_count += 1
            
        except Exception as e:
            logger.error(f"Error saving article {article_data['url']}: {str(e)}")
            continue
    
    return saved_count

@shared_task
def parse_all_sources():
    """Задача для парсинга всех активных источников."""
    sources = Source.objects.filter(is_active=True)
    total_saved = 0
    
    for source in sources:
        try:
            saved = parse_source.delay(source.id)
            total_saved += saved
        except Exception as e:
            logger.error(f"Error scheduling parse for source {source.id}: {str(e)}")
    
    return total_saved 