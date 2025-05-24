from typing import List, Dict, Any
import feedparser
from datetime import datetime
import logging
from .base import BaseParser

logger = logging.getLogger(__name__)

class RSSParser(BaseParser):
    """Парсер для RSS источников."""
    
    async def fetch_articles(self) -> List[Dict[str, Any]]:
        """Получение статей из RSS ленты."""
        try:
            content = await self.fetch_url(self.source_url)
            feed = feedparser.parse(content)
            
            articles = []
            for entry in feed.entries:
                try:
                    article = {
                        'title': self.clean_text(entry.title),
                        'content': self.clean_text(entry.description),
                        'url': entry.link,
                        'published_at': self.normalize_date(entry.published),
                        'source_name': self.source_name
                    }
                    articles.append(article)
                except Exception as e:
                    logger.error(f"Error parsing RSS entry: {str(e)}")
                    continue
            
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching RSS feed {self.source_url}: {str(e)}")
            raise
    
    def normalize_date(self, date_str: str) -> datetime:
        """Нормализация даты из RSS формата."""
        try:
            # Пробуем стандартный формат RSS
            return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
        except ValueError:
            try:
                # Альтернативный формат
                return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")
            except ValueError:
                logger.warning(f"Unknown date format: {date_str}")
                return datetime.now() 