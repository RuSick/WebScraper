from typing import List, Dict, Any, Optional
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re
import logging
from .base import BaseParser

logger = logging.getLogger(__name__)

class LentaParser(BaseParser):
    """Специализированный парсер для Lenta.ru."""
    
    def __init__(self, source_url: str = "https://lenta.ru", source_name: str = "Lenta.ru"):
        super().__init__(source_url, source_name)
        # Headers для имитации реального браузера
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    async def __aenter__(self):
        """Создание aiohttp сессии с custom headers."""
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            connector=connector,
            timeout=timeout
        )
        return self
    
    async def fetch_articles(self) -> List[Dict[str, Any]]:
        """Получение статей с главной страницы Lenta.ru."""
        try:
            content = await self.fetch_url(self.source_url)
            soup = BeautifulSoup(content, 'html.parser')
            
            articles = []
            
            # Ищем статьи по CSS-селектору a.card-mini
            article_links = soup.select('a.card-mini')
            
            logger.info(f"Найдено {len(article_links)} статей с селектором 'a.card-mini'")
            
            for link in article_links:
                try:
                    article_data = self._parse_article_link(link)
                    if article_data:
                        articles.append(article_data)
                        
                except Exception as e:
                    logger.error(f"Ошибка при парсинге статьи: {str(e)}")
                    continue
            
            logger.info(f"Успешно обработано {len(articles)} статей")
            return articles
            
        except Exception as e:
            logger.error(f"Ошибка при получении страницы {self.source_url}: {str(e)}")
            raise
    
    def _parse_article_link(self, link_element) -> Optional[Dict[str, Any]]:
        """Парсинг одной статьи из элемента ссылки."""
        try:
            # Извлекаем URL
            url = link_element.get('href', '')
            if not url:
                return None
            
            # Преобразуем относительную ссылку в абсолютную
            if url.startswith('/'):
                url = urljoin(self.source_url, url)
            
            # Ищем заголовок в h3.card-mini__title
            title_element = link_element.select_one('h3.card-mini__title')
            if not title_element:
                # Альтернативный поиск заголовка
                title_element = link_element.find(['h1', 'h2', 'h3', 'h4'])
            
            if not title_element:
                return None
            
            title = self.clean_text(title_element.get_text())
            
            # Извлекаем дату из URL
            published_at = self._extract_date_from_url(url)
            
            article = {
                'title': title,
                'url': url,
                'content': '',  # Контент пока оставляем пустым
                'published_at': published_at,
                'source_name': self.source_name
            }
            
            return article
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге элемента статьи: {str(e)}")
            return None
    
    def _extract_date_from_url(self, url: str) -> Optional[str]:
        """Извлечение даты из URL в формате /YYYY/MM/DD/."""
        try:
            # Паттерн для поиска даты в URL: /YYYY/MM/DD/
            date_pattern = r'/(\d{4})/(\d{2})/(\d{2})/'
            match = re.search(date_pattern, url)
            
            if match:
                year, month, day = match.groups()
                # Возвращаем дату в ISO формате
                date_obj = datetime(int(year), int(month), int(day))
                return date_obj.isoformat()
            
            return None
            
        except Exception as e:
            logger.warning(f"Ошибка при извлечении даты из URL {url}: {str(e)}")
            return None
    
    async def fetch_url(self, url: str) -> str:
        """Переопределенный метод для получения содержимого с дополнительной обработкой."""
        if not self.session:
            raise RuntimeError("Parser must be used as async context manager")
        
        try:
            async with self.session.get(url) as response:
                # Проверяем статус ответа
                if response.status == 403:
                    logger.warning(f"Получен статус 403 для {url}, возможно срабатывает защита от ботов")
                elif response.status == 429:
                    logger.warning(f"Получен статус 429 для {url}, слишком много запросов")
                
                response.raise_for_status()
                content = await response.text()
                
                # Логируем размер полученного контента для отладки
                logger.debug(f"Получено {len(content)} символов с {url}")
                
                return content
                
        except aiohttp.ClientError as e:
            logger.error(f"HTTP ошибка при получении {url}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении {url}: {str(e)}")
            raise 