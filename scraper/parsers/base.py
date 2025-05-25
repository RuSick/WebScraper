from abc import ABC, abstractmethod
from typing import List, Dict, Any
import aiohttp
import logging
from datetime import datetime
from django.conf import settings

logger = logging.getLogger(__name__)

class BaseParser(ABC):
    """Базовый класс для всех парсеров новостей."""
    
    def __init__(self, source_url: str, source_name: str):
        self.source_url = source_url
        self.source_name = source_name
        self.session = None
    
    async def __aenter__(self):
        """Создание aiohttp сессии при входе в контекст."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие сессии при выходе из контекста."""
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def fetch_articles(self) -> List[Dict[str, Any]]:
        """Получение списка статей из источника."""
        pass
    
    async def fetch_url(self, url: str) -> str:
        """
        Получение содержимого по URL с fallback на headless-парсинг.
        
        Стратегия:
        1. Пытаемся получить HTML через обычный HTTP-запрос
        2. Если HTML подозрительно короткий или это известный SPA-сайт,
           пытаемся использовать headless-парсинг (если включен)
        3. Возвращаем лучший доступный результат
        """
        if not self.session:
            raise RuntimeError("Parser must be used as async context manager")
        
        try:
            # Основная стратегия: обычный HTTP-запрос
            async with self.session.get(url) as response:
                response.raise_for_status()
                html_content = await response.text()
                
                # Проверяем, нужен ли fallback на headless-парсинг
                if self._should_try_headless_fallback(html_content, url):
                    logger.info(f"Пытаемся headless-парсинг для {url}")
                    
                    try:
                        headless_html = await self._try_headless_parsing(url)
                        if headless_html and len(headless_html) > len(html_content):
                            logger.info(f"Headless-парсинг успешен для {url}")
                            return headless_html
                        else:
                            logger.warning(f"Headless-парсинг не улучшил результат для {url}")
                    except Exception as e:
                        logger.warning(f"Headless-парсинг не удался для {url}: {e}")
                
                return html_content
                
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            raise
    
    def _should_try_headless_fallback(self, html_content: str, url: str) -> bool:
        """
        Определяет, стоит ли попробовать headless-парсинг.
        
        Возвращает True если:
        1. Headless-парсинг включен в настройках
        2. HTML подозрительно короткий (вероятно SPA)
        3. Или это известный SPA-сайт
        """
        # Проверяем настройку
        if not getattr(settings, 'ENABLE_HEADLESS_PARSING', False):
            return False
        
        # Импортируем функции проверки (отложенный импорт для избежания циклических зависимостей)
        try:
            from scraper.browser.fallback_playwright import should_use_headless, is_known_spa_site
            
            # Проверяем известные SPA-сайты
            if is_known_spa_site(url):
                logger.info(f"Обнаружен известный SPA-сайт: {url}")
                return True
            
            # Проверяем по содержимому HTML
            return should_use_headless(html_content, url)
            
        except ImportError as e:
            logger.warning(f"Не удалось импортировать headless-модуль: {e}")
            return False
    
    async def _try_headless_parsing(self, url: str) -> str:
        """
        Попытка headless-парсинга.
        
        Возвращает HTML после JavaScript-рендеринга или поднимает исключение.
        """
        try:
            from scraper.browser.fallback_playwright import fetch_with_playwright
            return await fetch_with_playwright(url)
        except ImportError:
            logger.error("Headless-модуль недоступен")
            raise NotImplementedError("Headless-парсинг недоступен")
        except Exception as e:
            logger.error(f"Ошибка headless-парсинга для {url}: {e}")
            raise
    
    def normalize_date(self, date_str: str) -> datetime:
        """Нормализация даты из разных форматов."""
        # TODO: Реализовать парсинг разных форматов дат
        pass
    
    def clean_text(self, text: str) -> str:
        """Очистка текста от лишних пробелов и переносов строк."""
        return " ".join(text.split()) 