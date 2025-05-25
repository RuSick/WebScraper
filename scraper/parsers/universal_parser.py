"""
Универсальный HTML-парсер для новостных сайтов.

Этот парсер предназначен для замены кастомных парсеров (habr.py, lenta.py)
и автоматического извлечения статей с любых новостных сайтов.
"""

import aiohttp
import asyncio
import logging
import re
from typing import List, Dict, Optional, Any, Protocol
from urllib.parse import urljoin, urlparse
from datetime import datetime
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)


class SourceProtocol(Protocol):
    """Протокол для объекта источника."""
    url: str
    name: str


class UniversalNewsParser:
    """
    Универсальный парсер новостных сайтов с адаптивными стратегиями поиска.
    """
    
    def __init__(self):
        self.session = None
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
        
        # Селекторы для поиска контейнеров статей
        self.article_container_selectors = [
            'article',  # Семантический HTML5 тег
            'div[class*="post"]', 'div[class*="card"]', 'div[class*="news"]', 
            'div[class*="item"]', 'div[class*="story"]', 'div[class*="entry"]',
            'div[class*="article"]', 'div[class*="content"]',
            'li[class*="item"]', 'li[class*="post"]', 'li[class*="news"]',
            # Специфичные для habr.com
            'div[class*="tm-article"]', 'div[class*="tm-title"]',
            # Специфичные для lenta.ru
            'a[class*="card-mini"]', 'div[class*="card"]',
            # Специфичные для meduza.io
            'article.Card',
            # Специфичные для tjournal.ru, vc.ru, dtf.ru
            'div.feed__item',
            # Специфичные для cnews.ru
            'div.allnews', 'div[class*="allnews"]',
            # Специфичные для vedomosti.ru
            'div.article-card', 'div[class*="article-card"]',
            # Специфичные для kommersant.ru
            'div.article__content', 'div[class*="article__content"]',
            # Специфичные для RT
            'div.card',
            # Общие паттерны
            'div[class*="feed"]', 'div[class*="list"]',
        ]
        
        # Селекторы для заголовков (по приоритету)
        self.title_selectors = [
            'h1', 'h2', 'h3', 'h4',
            'div[class*="title"]', 'span[class*="title"]',
            'div[class*="headline"]', 'span[class*="headline"]',
            'a[class*="title"]', 'a[class*="headline"]',
            # Специфичные селекторы
            'h3.card-mini__title',  # lenta.ru
            '.tm-title__link',      # habr.com
            'h2.tm-title',         # habr.com альтернативный
            'h2.entry__title',     # tjournal.ru
            'h2.content-title',    # vc.ru, dtf.ru
            'h3.card__title',      # RT
            'a.article-card__link', # vedomosti.ru
        ]
        
        # Селекторы для контента
        self.content_selectors = [
            'div[class*="body"]', 'div[class*="text"]', 'div[class*="content"]',
            'div[class*="description"]', 'div[class*="excerpt"]',
            'div[class*="summary"]', 'div[class*="intro"]',
            'article', 'section',
            'p',  # Fallback для параграфов
        ]
        
        # Селекторы для дат
        self.date_selectors = [
            'time[datetime]', 'time',
            'meta[property*="date"]', 'meta[name*="date"]',
            'span[class*="date"]', 'div[class*="date"]',
            'span[class*="time"]', 'div[class*="time"]',
            'span[class*="published"]', 'div[class*="published"]',
            # Специфичные селекторы
            '[data-publication-time]',  # meduza.io
            'div.article-card__info',   # vedomosti.ru
            'span.card__date',          # RT
            'span.date',                # cnews.ru
        ]
    
    async def __aenter__(self):
        """Создание aiohttp сессии."""
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            connector=connector,
            timeout=timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие сессии."""
        if self.session:
            await self.session.close()
    
    async def fetch_page(self, url: str) -> Optional[str]:
        """
        Получение HTML страницы с обработкой ошибок и fallback на headless-парсинг.
        
        Стратегия:
        1. Пытаемся получить HTML через обычный HTTP-запрос
        2. Если HTML подозрительно короткий или это известный SPA-сайт,
           пытаемся использовать headless-парсинг (если включен)
        3. Возвращаем лучший доступный результат
        """
        try:
            async with self.session.get(url) as response:
                if response.status == 403:
                    logger.warning(f"Получен статус 403 для {url}, возможна защита от ботов")
                elif response.status == 429:
                    logger.warning(f"Получен статус 429 для {url}, слишком много запросов")
                
                response.raise_for_status()
                content = await response.text()
                logger.debug(f"Получено {len(content)} символов с {url}")
                
                # Проверяем, нужен ли fallback на headless-парсинг
                if self._should_try_headless_fallback(content, url):
                    logger.info(f"Пытаемся headless-парсинг для {url}")
                    
                    try:
                        headless_html = await self._try_headless_parsing(url)
                        if headless_html and len(headless_html) > len(content):
                            logger.info(f"Headless-парсинг улучшил результат для {url}: {len(content)} → {len(headless_html)} символов")
                            return headless_html
                        else:
                            logger.warning(f"Headless-парсинг не улучшил результат для {url}")
                    except Exception as e:
                        logger.warning(f"Headless-парсинг не удался для {url}: {e}")
                
                return content
                
        except aiohttp.ClientError as e:
            logger.error(f"HTTP ошибка при получении {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении {url}: {e}")
            return None
    
    def _should_try_headless_fallback(self, html_content: str, url: str) -> bool:
        """
        Определяет, стоит ли попробовать headless-парсинг для универсального парсера.
        
        Возвращает True если:
        1. Headless-парсинг включен в настройках
        2. HTML подозрительно короткий (вероятно SPA)
        3. Или это известный SPA-сайт
        """
        # Проверяем настройку Django
        try:
            from django.conf import settings
            if not getattr(settings, 'ENABLE_HEADLESS_PARSING', False):
                return False
        except ImportError:
            # Если Django не настроен, пропускаем headless
            return False
        
        # Импортируем функции проверки (отложенный импорт)
        try:
            from scraper.browser.fallback_playwright import should_use_headless, is_known_spa_site
            
            # Проверяем известные SPA-сайты
            if is_known_spa_site(url):
                logger.info(f"Обнаружен известный SPA-сайт: {url}")
                return True
            
            # Проверяем по содержимому HTML
            return should_use_headless(html_content, url)
            
        except ImportError as e:
            logger.debug(f"Headless-модуль недоступен: {e}")
            return False
    
    async def _try_headless_parsing(self, url: str) -> str:
        """
        Попытка headless-парсинга для универсального парсера.
        
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
    
    def find_article_containers(self, soup: BeautifulSoup) -> List[Tag]:
        """
        Поиск контейнеров статей с использованием множественных стратегий.
        
        Стратегия:
        1. Пробуем семантические теги (article)
        2. Ищем по классам с ключевыми словами
        3. Возвращаем наиболее релевантные результаты
        """
        containers = []
        
        for selector in self.article_container_selectors:
            try:
                elements = soup.select(selector)
                if elements:
                    logger.debug(f"Найдено {len(elements)} элементов по селектору '{selector}'")
                    containers.extend(elements)
            except Exception as e:
                logger.warning(f"Ошибка в селекторе '{selector}': {e}")
        
        # Удаляем дубликаты, сохраняя порядок
        unique_containers = []
        seen = set()
        for container in containers:
            container_id = id(container)
            if container_id not in seen:
                seen.add(container_id)
                unique_containers.append(container)
        
        logger.info(f"Найдено {len(unique_containers)} уникальных контейнеров статей")
        return unique_containers
    
    def extract_title(self, container: Tag) -> Optional[str]:
        """
        Извлечение заголовка с множественными fallback стратегиями.
        
        Покрывает:
        - lenta.ru: h3.card-mini__title
        - habr.com: .tm-title__link
        - Общие паттерны: h1-h4, div[class*="title"]
        """
        for selector in self.title_selectors:
            try:
                element = container.select_one(selector)
                if element:
                    title = self._clean_text(element.get_text())
                    if self._is_valid_title(title):
                        logger.debug(f"Заголовок найден селектором '{selector}': {title[:50]}...")
                        return title
            except Exception as e:
                logger.debug(f"Ошибка в селекторе заголовка '{selector}': {e}")
        
        # Fallback: ищем любой текст в ссылках
        try:
            link = container.find('a', href=True)
            if link:
                title = self._clean_text(link.get_text())
                if self._is_valid_title(title):
                    logger.debug(f"Заголовок из ссылки: {title[:50]}...")
                    return title
        except Exception as e:
            logger.debug(f"Ошибка в fallback поиске заголовка: {e}")
        
        return None
    
    def extract_url(self, container: Tag, base_url: str) -> Optional[str]:
        """
        Извлечение URL статьи с преобразованием в абсолютный.
        
        Покрывает:
        - lenta.ru: a.card-mini[href]
        - habr.com: .tm-title__link[href]
        - Общие паттерны: любые ссылки в контейнере
        """
        # Если сам контейнер - ссылка
        if container.name == 'a' and container.get('href'):
            href = container.get('href')
            url = urljoin(base_url, href)
            if self._is_valid_url(url):
                return url
        
        # Ищем ссылки в заголовках
        for selector in self.title_selectors:
            try:
                title_element = container.select_one(selector)
                if title_element:
                    # Если сам элемент заголовка - ссылка
                    if title_element.name == 'a' and title_element.get('href'):
                        href = title_element.get('href')
                        url = urljoin(base_url, href)
                        if self._is_valid_url(url):
                            return url
                    
                    # Ищем ссылку внутри заголовка
                    link = title_element.find('a', href=True)
                    if link:
                        href = link.get('href')
                        url = urljoin(base_url, href)
                        if self._is_valid_url(url):
                            return url
            except Exception as e:
                logger.debug(f"Ошибка поиска URL в заголовке '{selector}': {e}")
        
        # Fallback: первая найденная ссылка
        try:
            link = container.find('a', href=True)
            if link:
                href = link.get('href')
                url = urljoin(base_url, href)
                if self._is_valid_url(url):
                    return url
        except Exception as e:
            logger.debug(f"Ошибка в fallback поиске URL: {e}")
        
        return None
    
    def extract_content(self, container: Tag) -> Optional[str]:
        """
        Извлечение контента статьи (опционально).
        
        Стратегия:
        1. Ищем специфичные контейнеры контента
        2. Fallback на параграфы
        3. Ограничиваем длину для предварительного просмотра
        """
        for selector in self.content_selectors:
            try:
                element = container.select_one(selector)
                if element:
                    content = self._clean_text(element.get_text())
                    if len(content) > 20:  # Минимальная длина контента
                        # Ограничиваем для preview
                        preview = content[:500] + "..." if len(content) > 500 else content
                        logger.debug(f"Контент найден селектором '{selector}': {len(content)} символов")
                        return preview
            except Exception as e:
                logger.debug(f"Ошибка в селекторе контента '{selector}': {e}")
        
        return ""
    
    def extract_date(self, container: Tag, article_url: Optional[str] = None) -> Optional[str]:
        """
        Извлечение даты публикации с множественными стратегиями.
        
        Покрывает:
        - lenta.ru: дата из URL /YYYY/MM/DD/
        - habr.com: time[datetime], meta теги
        - meduza.io: data-publication-time
        - Общие паттерны: элементы с классами date/time
        """
        # Стратегия 1: Ищем в HTML элементах
        for selector in self.date_selectors:
            try:
                element = container.select_one(selector)
                if element:
                    # Пробуем атрибут datetime
                    datetime_attr = element.get('datetime')
                    if datetime_attr:
                        date = self._parse_date(datetime_attr)
                        if date:
                            logger.debug(f"Дата из datetime атрибута: {date}")
                            return date
                    
                    # Пробуем data-publication-time (meduza.io)
                    pub_time_attr = element.get('data-publication-time')
                    if pub_time_attr:
                        date = self._parse_date(pub_time_attr)
                        if date:
                            logger.debug(f"Дата из data-publication-time: {date}")
                            return date
                    
                    # Пробуем content атрибут для meta тегов
                    content_attr = element.get('content')
                    if content_attr:
                        date = self._parse_date(content_attr)
                        if date:
                            logger.debug(f"Дата из content атрибута: {date}")
                            return date
                    
                    # Пробуем текст элемента
                    text = self._clean_text(element.get_text())
                    if text:
                        date = self._parse_date(text)
                        if date:
                            logger.debug(f"Дата из текста элемента: {date}")
                            return date
            except Exception as e:
                logger.debug(f"Ошибка в селекторе даты '{selector}': {e}")
        
        # Стратегия 2: Извлечение из URL (как в lenta.ru)
        if article_url:
            date = self._extract_date_from_url(article_url)
            if date:
                logger.debug(f"Дата из URL: {date}")
                return date
        
        return None
    
    def _extract_date_from_url(self, url: str) -> Optional[str]:
        """
        Извлечение даты из URL (стратегия lenta.ru).
        
        Паттерны:
        - /YYYY/MM/DD/
        - /YYYY-MM-DD/
        - /YYYY/MM/
        """
        patterns = [
            r'/(\d{4})/(\d{2})/(\d{2})/',  # /2025/05/25/
            r'/(\d{4})-(\d{2})-(\d{2})/',  # /2025-05-25/
            r'/(\d{4})/(\d{2})/',          # /2025/05/
            r'/(\d{4})/',                  # /2025/
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                try:
                    groups = match.groups()
                    if len(groups) >= 3:
                        year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
                        date_obj = datetime(year, month, day)
                        return date_obj.isoformat()
                    elif len(groups) >= 2:
                        year, month = int(groups[0]), int(groups[1])
                        date_obj = datetime(year, month, 1)
                        return date_obj.isoformat()
                    elif len(groups) >= 1:
                        year = int(groups[0])
                        date_obj = datetime(year, 1, 1)
                        return date_obj.isoformat()
                except (ValueError, TypeError) as e:
                    logger.debug(f"Ошибка парсинга даты из URL {url}: {e}")
                    continue
        
        return None
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """
        Парсинг даты из различных форматов.
        """
        if not date_str:
            return None
        
        # Очищаем строку
        date_str = date_str.strip()
        
        # Форматы для парсинга
        formats = [
            "%Y-%m-%dT%H:%M:%S%z",     # ISO с timezone
            "%Y-%m-%dT%H:%M:%S",       # ISO без timezone
            "%Y-%m-%d %H:%M:%S",       # Стандартный
            "%Y-%m-%d",                # Только дата
            "%d.%m.%Y %H:%M",          # Русский формат
            "%d.%m.%Y",                # Русская дата
            "%B %d, %Y",               # English format
            "%d %B %Y",                # Русский текстовый
        ]
        
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.isoformat()
            except ValueError:
                continue
        
        # Если не удалось распарсить, логируем предупреждение
        logger.debug(f"Не удалось распарсить дату: {date_str}")
        return None
    
    def _clean_text(self, text: str) -> str:
        """Очистка текста от лишних пробелов и символов."""
        if not text:
            return ""
        return " ".join(text.strip().split())
    
    def _is_valid_title(self, title: str) -> bool:
        """Проверка валидности заголовка."""
        if not title or len(title.strip()) < 5:
            return False
        
        # Исключаем навигационные элементы
        excluded_keywords = [
            'menu', 'navigation', 'nav', 'search', 'login', 'signup',
            'footer', 'header', 'sidebar', 'advertisement', 'ads'
        ]
        
        title_lower = title.lower()
        return not any(keyword in title_lower for keyword in excluded_keywords)
    
    def _is_valid_url(self, url: str) -> bool:
        """Проверка валидности URL."""
        if not url:
            return False
        
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except Exception:
            return False


async def fetch_generic_articles(source: SourceProtocol) -> List[Dict[str, Any]]:
    """
    Универсальная функция для парсинга статей с любого новостного сайта.
    
    Эта функция предназначена для замены кастомных парсеров (habr.py, lenta.py)
    и автоматического извлечения статей с новостных сайтов.
    
    Args:
        source: Объект источника с URL и метаданными
    
    Returns:
        Список словарей с извлеченными статьями
    """
    logger.info(f"Начало универсального парсинга {source.name} ({source.url})")
    
    async with UniversalNewsParser() as parser:
        # Получаем HTML страницу
        html_content = await parser.fetch_page(source.url)
        if not html_content:
            logger.error(f"Не удалось получить содержимое {source.url}")
            return []
        
        # Парсим HTML
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
        except Exception as e:
            logger.error(f"Ошибка парсинга HTML {source.url}: {e}")
            return []
        
        # Находим контейнеры статей
        containers = parser.find_article_containers(soup)
        if not containers:
            logger.warning(f"Не найдено контейнеров статей на {source.url}")
            return []
        
        articles = []
        successful_extractions = 0
        
        for i, container in enumerate(containers):
            try:
                # Извлекаем заголовок
                title = parser.extract_title(container)
                if not title:
                    logger.debug(f"Контейнер {i+1}: заголовок не найден, пропускаем")
                    continue
                
                # Извлекаем URL
                article_url = parser.extract_url(container, source.url)
                if not article_url:
                    logger.debug(f"Контейнер {i+1}: URL не найден, пропускаем")
                    continue
                
                # Извлекаем контент (опционально)
                content = parser.extract_content(container)
                
                # Извлекаем дату
                published_at = parser.extract_date(container, article_url)
                
                # Формируем результат
                article = {
                    "title": title,
                    "url": article_url,
                    "content": content or "",
                    "published_at": published_at,
                    "source_name": source.name
                }
                
                articles.append(article)
                successful_extractions += 1
                
                logger.debug(f"Успешно извлечена статья {successful_extractions}: {title[:50]}...")
                
            except Exception as e:
                logger.warning(f"Ошибка обработки контейнера {i+1}: {e}")
                continue
        
        logger.info(f"Универсальный парсинг {source.name} завершен: "
                   f"{successful_extractions} статей из {len(containers)} контейнеров")
        
        return articles 