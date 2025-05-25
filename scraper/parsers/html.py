from typing import List, Dict, Any
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
import logging
from .base import BaseParser

logger = logging.getLogger(__name__)

class HTMLParser(BaseParser):
    """Парсер для HTML сайтов."""
    
    async def fetch_articles(self) -> List[Dict[str, Any]]:
        """Получение статей с HTML страницы."""
        try:
            content = await self.fetch_url(self.source_url)
            soup = BeautifulSoup(content, 'html.parser')
            
            articles = []
            # Для rbc.ru ищем div.main__feed__item
            article_elements = soup.find_all('div', class_=['main__feed__item', 'card', 'card-news', 'article', 'news-item', 'post'])
            
            for element in article_elements:
                try:
                    # Для rbc.ru заголовок и ссылка обычно в <a>
                    a_tag = element.find('a', href=True)
                    title = a_tag.get_text(strip=True) if a_tag else self._get_title(element)
                    url = a_tag['href'] if a_tag else self._get_url(element)
                    if url and url.startswith('/'):
                        from urllib.parse import urljoin
                        url = urljoin(self.source_url, url)
                    content = self._get_content(element)
                    published_at = self._get_date(element)
                    
                    if not all([title, url]):
                        continue
                    
                    article = {
                        'title': self.clean_text(title),
                        'content': self.clean_text(content),
                        'url': url,
                        'published_at': published_at or datetime.now(),
                        'source_name': self.source_name
                    }
                    articles.append(article)
                    
                except Exception as e:
                    logger.error(f"Error parsing HTML article: {str(e)}")
                    continue
            
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching HTML page {self.source_url}: {str(e)}")
            raise
    
    def _get_title(self, element) -> str:
        """Извлечение заголовка статьи."""
        # Ищем заголовок в разных тегах и классах
        title = (
            element.find('h1') or 
            element.find('h2') or 
            element.find(class_=['title', 'headline'])
        )
        return title.get_text() if title else ''
    
    def _get_content(self, element) -> str:
        """Извлечение содержимого статьи."""
        # Ищем контент в разных тегах и классах
        content = (
            element.find('div', class_=['content', 'article-content', 'post-content']) or
            element.find('article') or
            element.find('section')
        )
        return content.get_text() if content else ''
    
    def _get_url(self, element) -> str:
        """Извлечение URL статьи."""
        # Ищем ссылку в разных местах
        link = (
            element.find('a', href=True) or
            element.find('link', rel='canonical') or
            element.find('meta', property='og:url')
        )
        
        if not link:
            return ''
            
        return link.get('href', '')
    
    def _get_date(self, element) -> datetime:
        """Извлечение даты публикации."""
        # Ищем дату в разных форматах и местах
        date_element = (
            element.find('time') or
            element.find(class_=['date', 'published', 'post-date']) or
            element.find('meta', property='article:published_time')
        )
        
        if not date_element:
            return datetime.now()
            
        date_str = date_element.get('datetime', '') or date_element.get_text()
        try:
            # Пробуем разные форматы даты
            formats = [
                "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%d %H:%M:%S",
                "%d.%m.%Y %H:%M",
                "%B %d, %Y"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
                    
            return datetime.now()
            
        except Exception as e:
            logger.warning(f"Error parsing date {date_str}: {str(e)}")
            return datetime.now() 