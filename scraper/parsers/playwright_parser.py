from typing import List, Dict, Any
import asyncio
from datetime import datetime
import logging
from playwright.async_api import async_playwright, TimeoutError
from bs4 import BeautifulSoup
from .base import BaseParser

logger = logging.getLogger(__name__)

class PlaywrightParser(BaseParser):
    """Парсер для сайтов с динамическим контентом."""
    
    async def fetch_articles(self) -> List[Dict[str, Any]]:
        """Получение статей с веб-страницы."""
        try:
            # Ждем загрузки статей
            await self.page.wait_for_selector('article.tm-article-card', timeout=30000)
            
            # Получаем HTML после загрузки
            html = await self.page.content()
            self.logger.info(f"Полученный HTML (первые 5000 символов):\n{html[:5000]}")
            
            soup = BeautifulSoup(html, 'html.parser')
            articles = []
            
            # Ищем все статьи на странице
            for article in soup.find_all('article', class_='tm-article-card'):
                try:
                    # Получаем заголовок
                    title_elem = article.find('h2', class_='tm-article-card__title')
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    
                    # Получаем ссылку
                    link_elem = title_elem.find('a')
                    if not link_elem:
                        continue
                    url = link_elem.get('href')
                    if not url.startswith('http'):
                        url = f"https://habr.com{url}"
                    
                    # Получаем дату публикации
                    time_elem = article.find('time')
                    pub_date = time_elem.get('datetime') if time_elem else None
                    
                    # Получаем краткое описание
                    description_elem = article.find('div', class_='tm-article-card__snippet')
                    description = description_elem.get_text(strip=True) if description_elem else ""
                    
                    articles.append({
                        'title': title,
                        'url': url,
                        'pub_date': pub_date,
                        'description': description,
                        'source': self.source
                    })
                    
                except Exception as e:
                    self.logger.error(f"Ошибка при парсинге статьи: {str(e)}")
                    continue
            
            return articles
            
        except Exception as e:
            self.logger.error(f"Ошибка при получении статей: {str(e)}")
            return []
    
    def _get_title(self, element) -> str:
        """Извлечение заголовка статьи."""
        # Ищем заголовок в разных тегах и классах
        title = (
            element.find('h1') or 
            element.find('h2') or 
            element.find('h3') or
            element.find('a', class_=['title', 'headline', 'card-title']) or
            element.find(class_=['title', 'headline', 'card-title'])
        )
        return title.get_text(strip=True) if title else ''
    
    def _get_content(self, element) -> str:
        """Извлечение содержимого статьи."""
        # Ищем контент в разных тегах и классах
        content = (
            element.find('div', class_=['content', 'article-content', 'post-content', 'card-text']) or
            element.find('article') or
            element.find('section') or
            element.find('p', class_=['card-text', 'article-text'])
        )
        return content.get_text(strip=True) if content else ''
    
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
            
        url = link.get('href', '')
        # Если URL относительный, добавляем домен
        if url.startswith('/'):
            from urllib.parse import urljoin
            url = urljoin(self.source_url, url)
            
        return url
    
    def _get_date(self, element) -> datetime:
        """Извлечение даты публикации."""
        # Ищем дату в разных форматах и местах
        date_element = (
            element.find('time') or
            element.find(class_=['date', 'published', 'post-date', 'card-date']) or
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
                "%B %d, %Y",
                "%H:%M"  # для случаев, когда дата только время
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