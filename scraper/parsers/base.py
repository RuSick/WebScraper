from abc import ABC, abstractmethod
from typing import List, Dict, Any
import aiohttp
import logging
from datetime import datetime

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
        """Получение содержимого по URL."""
        if not self.session:
            raise RuntimeError("Parser must be used as async context manager")
        
        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                return await response.text()
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            raise
    
    def normalize_date(self, date_str: str) -> datetime:
        """Нормализация даты из разных форматов."""
        # TODO: Реализовать парсинг разных форматов дат
        pass
    
    def clean_text(self, text: str) -> str:
        """Очистка текста от лишних пробелов и переносов строк."""
        return " ".join(text.split()) 