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
        Улучшенное извлечение контента статьи с продвинутой обработкой.
        
        Стратегия:
        1. Ищем семантические контейнеры контента (article, section, main)
        2. Фильтруем нежелательные элементы (nav, footer, aside, ads)
        3. Извлекаем и очищаем текст с сохранением структуры
        4. Валидируем качество контента
        5. Возвращаем только релевантный контент
        """
        
        # Приоритетные селекторы для основного контента
        priority_selectors = [
            'article[itemprop="articleBody"]',  # Schema.org разметка
            'div[itemprop="articleBody"]',
            'section[itemprop="articleBody"]',
            'div[class*="article-body"]',
            'div[class*="article-content"]',
            'div[class*="post-content"]',
            'div[class*="entry-content"]',
            'div[class*="content-body"]',
            'main article',
            'article',
            'main section',
            'div[role="main"]',
        ]
        
        # Стандартные селекторы контента
        standard_selectors = [
            'div[class*="body"]', 'div[class*="text"]', 'div[class*="content"]',
            'div[class*="description"]', 'div[class*="excerpt"]',
            'div[class*="summary"]', 'div[class*="intro"]',
            'section', 'main'
        ]
        
        # Сначала пробуем приоритетные селекторы
        for selector in priority_selectors:
            content = self._extract_and_validate_content(container, selector)
            if content:
                logger.debug(f"Контент найден приоритетным селектором '{selector}': {len(content)} символов")
                return content
        
        # Затем стандартные селекторы
        for selector in standard_selectors:
            content = self._extract_and_validate_content(container, selector)
            if content:
                logger.debug(f"Контент найден стандартным селектором '{selector}': {len(content)} символов")
                return content
        
        # Fallback: извлекаем из параграфов
        content = self._extract_from_paragraphs(container)
        if content:
            logger.debug(f"Контент извлечён из параграфов: {len(content)} символов")
            return content
        
        return ""
    
    def _extract_and_validate_content(self, container: Tag, selector: str) -> Optional[str]:
        """Извлечение и валидация контента по селектору."""
        try:
            element = container.select_one(selector)
            if not element:
                return None
            
            # Удаляем нежелательные элементы
            cleaned_element = self._remove_unwanted_elements(element)
            
            # Извлекаем и очищаем текст
            raw_text = cleaned_element.get_text(separator=' ', strip=True)
            cleaned_text = self._advanced_text_cleaning(raw_text)
            
            # Валидируем качество контента
            if self._is_valid_content(cleaned_text):
                return cleaned_text
            
        except Exception as e:
            logger.debug(f"Ошибка в селекторе контента '{selector}': {e}")
        
        return None
    
    def _extract_from_paragraphs(self, container: Tag) -> Optional[str]:
        """Fallback: извлечение контента из параграфов."""
        try:
            paragraphs = container.find_all('p')
            if not paragraphs:
                return None
            
            # Собираем текст из всех параграфов
            texts = []
            for p in paragraphs:
                # Пропускаем параграфы в нежелательных контейнерах
                if self._is_in_unwanted_container(p):
                    continue
                
                text = p.get_text(strip=True)
                if text and len(text) > 10:  # Минимальная длина параграфа
                    texts.append(text)
            
            if texts:
                combined_text = ' '.join(texts)
                cleaned_text = self._advanced_text_cleaning(combined_text)
                
                if self._is_valid_content(cleaned_text):
                    return cleaned_text
            
        except Exception as e:
            logger.debug(f"Ошибка извлечения из параграфов: {e}")
        
        return None
    
    def _remove_unwanted_elements(self, element: Tag) -> Tag:
        """Удаление нежелательных элементов из контента."""
        # Создаём копию элемента для безопасного изменения
        element_copy = element.__copy__()
        
        # Селекторы нежелательных элементов
        unwanted_selectors = [
            'nav', 'footer', 'header', 'aside',
            'div[class*="sidebar"]', 'div[class*="widget"]',
            'div[class*="advertisement"]', 'div[class*="ads"]',
            'div[class*="banner"]', 'div[class*="promo"]',
            'div[class*="social"]', 'div[class*="share"]',
            'div[class*="comment"]', 'div[class*="related"]',
            'div[class*="navigation"]', 'div[class*="menu"]',
            'script', 'style', 'noscript',
            'form', 'input', 'button',
            '[class*="hidden"]', '[style*="display:none"]',
            '[class*="ad-"]', '[id*="ad-"]',
            '.advertisement', '.ads', '.banner',
        ]
        
        # Удаляем нежелательные элементы
        for selector in unwanted_selectors:
            try:
                for unwanted in element_copy.select(selector):
                    unwanted.decompose()
            except Exception as e:
                logger.debug(f"Ошибка удаления элементов '{selector}': {e}")
        
        return element_copy
    
    def _is_in_unwanted_container(self, element: Tag) -> bool:
        """Проверка, находится ли элемент в нежелательном контейнере."""
        unwanted_classes = [
            'sidebar', 'widget', 'advertisement', 'ads', 'banner',
            'social', 'share', 'comment', 'related', 'navigation',
            'menu', 'footer', 'header'
        ]
        
        # Проверяем родительские элементы
        parent = element.parent
        while parent and parent.name != 'body':
            if parent.get('class'):
                classes = ' '.join(parent.get('class')).lower()
                if any(unwanted in classes for unwanted in unwanted_classes):
                    return True
            parent = parent.parent
        
        return False
    
    def _advanced_text_cleaning(self, text: str) -> str:
        """Продвинутая очистка текста с сохранением структуры."""
        if not text:
            return ""
        
        # Базовая очистка
        text = text.strip()
        
        # Удаляем лишние пробелы и переносы строк
        text = re.sub(r'\s+', ' ', text)
        
        # Удаляем повторяющиеся знаки препинания
        text = re.sub(r'[.]{3,}', '...', text)
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        
        # Исправляем пробелы вокруг знаков препинания
        text = re.sub(r'\s+([,.!?;:])', r'\1', text)
        text = re.sub(r'([.!?])\s*([А-ЯA-Z])', r'\1 \2', text)
        
        # Удаляем служебные фразы
        service_phrases = [
            r'читать далее\.?\.?\.?',
            r'подробнее\.?\.?\.?',
            r'смотреть также\.?\.?\.?',
            r'источник:?\s*\S+',
            r'фото:?\s*\S+',
            r'видео:?\s*\S+',
            r'реклама\.?',
            r'advertisement\.?',
            r'sponsored\.?',
        ]
        
        for pattern in service_phrases:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Финальная очистка
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _is_valid_content(self, content: str) -> bool:
        """Валидация качества контента."""
        if not content:
            return False
        
        # Увеличенная минимальная длина для более качественного контента
        if len(content) < 100:
            return False
        
        # Проверяем наличие нормальных предложений (минимум 2)
        sentences = re.split(r'[.!?]+', content)
        valid_sentences = [s.strip() for s in sentences if len(s.strip()) > 15]
        
        if len(valid_sentences) < 2:
            return False
        
        # Проверяем соотношение букв к цифрам/символам
        letters = len(re.findall(r'[а-яёА-ЯЁa-zA-Z]', content))
        total_chars = len(content.replace(' ', ''))
        
        if total_chars > 0 and letters / total_chars < 0.6:
            return False
        
        # Расширенный список подозрительных паттернов
        suspicious_patterns = [
            # Навигация и меню
            r'^(меню|навигация|поиск|войти|регистрация)',
            r'(главное меню|основное меню|навигация по сайту)',
            
            # Технические сообщения
            r'(cookie|privacy policy|terms of service|политика конфиденциальности)',
            r'^(404|error|ошибка|страница не найдена)',
            r'(javascript|enable|включите|отключен)',
            r'^(loading|загрузка|подождите)',
            r'(maintenance|обслуживание|технические работы)',
            
            # Формы и регистрация
            r'(заполните форму|введите данные|обязательные поля)',
            r'(регистрация|авторизация|войти в систему)',
            r'(забыли пароль|восстановление пароля)',
            r'(подтвердите email|активация аккаунта)',
            
            # Социальные сети и подписки
            r'(подписывайтесь|следите за нами|присоединяйтесь)',
            r'(вконтакте|facebook|twitter|instagram|youtube|telegram)',
            r'(поделиться|share|лайк|like)',
            r'(подписка|newsletter|рассылка)',
            
            # Реклама и коммерция
            r'(реклама|advertisement|sponsored|спонсор)',
            r'(купить|заказать|скидка|акция|распродажа)',
            r'(цена|стоимость|руб\.|₽|\$|€)',
            
            # Комментарии и форумы
            r'(оставить комментарий|написать комментарий)',
            r'(ответить|цитировать|процитировать)',
            r'(модерация|администрация)',
            
            # Служебная информация
            r'(все права защищены|copyright|копирайт)',
            r'(обратная связь|связаться с нами|контакты)',
            r'(помощь|поддержка|техподдержка)',
            r'(правила|условия использования)',
            
            # Пустой или технический контент
            r'^(нет данных|no data|empty|пусто)$',
            r'^(undefined|null|none)$',
            r'^(test|тест|demo|демо)$',
            
            # Короткие фразы без смысла
            r'^(да|нет|ok|хорошо|плохо|отлично)$',
            r'^[0-9\s\-_.,!?]+$',  # Только цифры и знаки
        ]
        
        content_lower = content.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, content_lower):
                logger.debug(f"Контент исключён по паттерну '{pattern}': {content[:50]}...")
                return False
        
        # Проверяем на повторяющийся контент (возможно, меню или навигация)
        words = content.split()
        if len(words) > 10:
            unique_words = set(words)
            if len(unique_words) / len(words) < 0.4:  # Слишком много повторов
                logger.debug(f"Контент исключён из-за повторов: {content[:50]}...")
                return False
        
        # Проверяем наличие содержательных слов
        meaningful_words = [w for w in words if len(w) > 3 and not w.lower() in [
            'это', 'что', 'как', 'где', 'когда', 'почему', 'зачем',
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'man', 'men', 'put', 'say', 'she', 'too', 'use'
        ]]
        
        if len(meaningful_words) < len(words) * 0.3:  # Минимум 30% содержательных слов
            logger.debug(f"Контент исключён из-за недостатка содержательных слов: {content[:50]}...")
            return False
        
        # Проверяем структуру текста - должны быть знаки препинания
        punctuation_count = len(re.findall(r'[.!?,:;]', content))
        if punctuation_count < len(sentences):  # Минимум один знак препинания на предложение
            logger.debug(f"Контент исключён из-за отсутствия пунктуации: {content[:50]}...")
            return False
        
        return True
    
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
    
    def _is_valid_article_url(self, url: str, base_url: str) -> bool:
        """Расширенная проверка валидности URL статьи."""
        if not self._is_valid_url(url):
            return False
        
        # Расширенный список исключаемых служебных страниц
        excluded_patterns = [
            # Основные служебные страницы
            r'/search[/?]',
            r'/login[/?]',
            r'/register[/?]',
            r'/signup[/?]',
            r'/contact[/?]',
            r'/contacts[/?]',
            r'/about[/?]',
            r'/privacy[/?]',
            r'/terms[/?]',
            r'/policy[/?]',
            r'/sitemap[/?]',
            r'/rss[/?]',
            r'/feed[/?]',
            r'/archive[/?]',
            r'/category[/?]',
            r'/tag[/?]',
            r'/author[/?]',
            r'/user[/?]',
            r'/profile[/?]',
            r'/admin[/?]',
            r'/api[/?]',
            r'/ajax[/?]',
            r'/json[/?]',
            r'/xml[/?]',
            
            # Дополнительные служебные страницы
            r'/help[/?]',
            r'/support[/?]',
            r'/faq[/?]',
            r'/feedback[/?]',
            r'/subscribe[/?]',
            r'/unsubscribe[/?]',
            r'/newsletter[/?]',
            r'/advertising[/?]',
            r'/ads[/?]',
            r'/careers[/?]',
            r'/jobs[/?]',
            r'/press[/?]',
            r'/media[/?]',
            r'/partners[/?]',
            r'/legal[/?]',
            r'/disclaimer[/?]',
            r'/copyright[/?]',
            r'/dmca[/?]',
            r'/cookies[/?]',
            r'/gdpr[/?]',
            r'/404[/?]',
            r'/error[/?]',
            r'/maintenance[/?]',
            
            # Социальные сети и внешние ссылки
            r'facebook\.com',
            r'twitter\.com',
            r'instagram\.com',
            r'youtube\.com',
            r'vk\.com',
            r'telegram\.me',
            r't\.me',
            r'linkedin\.com',
            r'tiktok\.com',
            
            # Файлы
            r'\.pdf$',
            r'\.doc$',
            r'\.docx$',
            r'\.xls$',
            r'\.xlsx$',
            r'\.ppt$',
            r'\.pptx$',
            r'\.zip$',
            r'\.rar$',
            r'\.tar$',
            r'\.gz$',
            r'\.jpg$',
            r'\.jpeg$',
            r'\.png$',
            r'\.gif$',
            r'\.svg$',
            r'\.webp$',
            r'\.mp4$',
            r'\.avi$',
            r'\.mov$',
            r'\.wmv$',
            r'\.mp3$',
            r'\.wav$',
            r'\.flac$',
            
            # Якорные ссылки и фрагменты
            r'#',
            r'javascript:',
            r'mailto:',
            r'tel:',
            
            # Специфичные паттерны для новостных сайтов
            r'/docs/',
            r'/static/',
            r'/assets/',
            r'/images/',
            r'/css/',
            r'/js/',
            r'/fonts/',
            r'/uploads/',
            r'/download/',
            r'/redirect/',
            r'/go/',
            r'/out/',
            r'/exit/',
            
            # Комментарии и форумы
            r'/comment',
            r'/reply',
            r'/forum',
            r'/discussion',
            r'/thread',
            
            # Разделы без контента
            r'/main[/?]$',
            r'/index[/?]$',
            r'/home[/?]$',
            r'/$',  # Только главная страница
        ]
        
        url_lower = url.lower()
        for pattern in excluded_patterns:
            if re.search(pattern, url_lower):
                logger.debug(f"URL исключён по паттерну '{pattern}': {url}")
                return False
        
        # Проверяем, что URL ведёт на тот же домен или поддомен
        try:
            base_domain = urlparse(base_url).netloc.lower()
            url_domain = urlparse(url).netloc.lower()
            
            # Разрешаем только тот же домен (исключаем поддомены соцсетей)
            if url_domain != base_domain:
                # Разрешаем только новостные поддомены
                allowed_subdomains = ['www', 'news', 'sport', 'rsport', 'ria', 'russian']
                subdomain = url_domain.split('.')[0] if '.' in url_domain else ''
                
                if not (url_domain.endswith('.' + base_domain) and subdomain in allowed_subdomains):
                    logger.debug(f"URL исключён как внешний домен: {url}")
                    return False
        except Exception:
            return False
        
        return True
    
    def _is_valid_article(self, title: str, content: str, url: str) -> bool:
        """Комплексная валидация качества статьи."""
        
        # Проверяем заголовок
        if not self._is_valid_title(title):
            return False
        
        # Проверяем минимальную длину заголовка для статьи
        if len(title) < 10:
            return False
        
        # Расширенная проверка подозрительных паттернов в заголовке
        title_lower = title.lower()
        suspicious_title_patterns = [
            # Служебные страницы (русский)
            r'^(главная|home|index)$',
            r'^(меню|menu|навигация|navigation)$',
            r'^(поиск|search)$',
            r'^(войти|login|вход|авторизация)$',
            r'^(регистрация|register|signup|зарегистрироваться)$',
            r'(регистрация на сайте|регистрация пользователей)',
            r'^(контакты|contact|связаться|обратная связь)$',
            r'(связаться с нами|обратная связь|контактная информация)',
            r'^(о нас|about|о сайте|о компании)$',
            r'^(правила|rules|terms|условия)$',
            r'(правила сайта|пользовательское соглашение)',
            r'^(политика|privacy|policy|конфиденциальность)$',
            r'^(реклама|advertisement|ads|размещение рекламы)$',
            r'^(помощь|help|support|поддержка)$',
            r'^(faq|часто задаваемые|вопросы и ответы)$',
            r'^(подписка|subscribe|newsletter|рассылка)$',
            r'^(карьера|careers|jobs|вакансии|работа)$',
            r'^(партнёры|partners|сотрудничество)$',
            r'^(пресс-центр|press|media|для прессы)$',
            
            # Ошибки и технические страницы
            r'^(404|error|ошибка|страница не найдена)$',
            r'^(loading|загрузка|подождите)$',
            r'^(maintenance|обслуживание|технические работы)$',
            
            # Социальные сети
            r'(вконтакте|vk|facebook|twitter|instagram|youtube|telegram)',
            r'(подписывайтесь|следите|смотрите)',
            r'^(подписывайтесь на нас|следите за нами)$',
            
            # Куки и GDPR
            r'(cookie|куки|согласие|gdpr)',
            
            # Комментарии и форумы
            r'^(комментарий|comment|ответ|reply)$',
            r'^(обсуждение|discussion|форум|forum)$',
            
            # Короткие бессмысленные заголовки
            r'^[0-9\s\-_.,!?]+$',  # Только цифры и знаки
            r'^[a-zA-Z\s\-_.,!?]{1,3}$',  # Очень короткие латинские
            r'^[а-яё\s\-_.,!?]{1,3}$',  # Очень короткие русские
            
            # Технические заголовки
            r'^(undefined|null|none|empty|blank)$',
            r'^(test|тест|demo|демо)$',
            r'^(placeholder|заглушка)$',
        ]
        
        for pattern in suspicious_title_patterns:
            if re.search(pattern, title_lower):
                logger.debug(f"Заголовок исключён по паттерну '{pattern}': {title}")
                return False
        
        # Проверяем контент (если есть)
        if content:
            if not self._is_valid_content(content):
                return False
        else:
            # Если контента нет, проверяем заголовок более строго
            if not self._is_substantial_title(title):
                logger.debug(f"Заголовок без контента не прошёл проверку: {title}")
                return False
        
        # Проверяем соотношение букв в заголовке
        letters = len(re.findall(r'[а-яёА-ЯЁa-zA-Z]', title))
        if letters < len(title) * 0.5:  # Минимум 50% букв
            logger.debug(f"Заголовок содержит слишком мало букв: {title}")
            return False
        
        return True
    
    def _is_substantial_title(self, title: str) -> bool:
        """Проверка, является ли заголовок содержательным (для статей без контента)."""
        if len(title) < 15:  # Минимум 15 символов для статьи без контента
            return False
        
        # Должно быть минимум 3 слова
        words = title.split()
        if len(words) < 3:
            return False
        
        # Проверяем наличие содержательных слов (не только предлоги/союзы)
        meaningful_words = [w for w in words if len(w) > 2]
        if len(meaningful_words) < 2:
            return False
        
        # Исключаем заголовки, состоящие только из названий разделов
        section_words = [
            'новости', 'news', 'главное', 'главная', 'сегодня', 'сейчас',
            'лента', 'feed', 'все', 'all', 'последние', 'latest',
            'архив', 'archive', 'категория', 'category', 'раздел', 'section'
        ]
        
        title_words_lower = [w.lower() for w in words]
        if all(w in section_words for w in title_words_lower if len(w) > 2):
            return False
        
        return True


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
        skipped_stats = {
            'no_title': 0,
            'no_url': 0,
            'invalid_url': 0,
            'no_content': 0,
            'low_quality': 0,
            'duplicate_url': 0
        }
        processed_urls = set()
        
        for i, container in enumerate(containers):
            try:
                # Извлекаем заголовок
                title = parser.extract_title(container)
                if not title:
                    skipped_stats['no_title'] += 1
                    logger.debug(f"Контейнер {i+1}: заголовок не найден, пропускаем")
                    continue
                
                # Извлекаем URL
                article_url = parser.extract_url(container, source.url)
                if not article_url:
                    skipped_stats['no_url'] += 1
                    logger.debug(f"Контейнер {i+1}: URL не найден, пропускаем")
                    continue
                
                # Проверяем валидность URL
                if not parser._is_valid_article_url(article_url, source.url):
                    skipped_stats['invalid_url'] += 1
                    logger.debug(f"Контейнер {i+1}: невалидный URL {article_url}, пропускаем")
                    continue
                
                # Проверяем на дубликаты URL в текущей сессии
                if article_url in processed_urls:
                    skipped_stats['duplicate_url'] += 1
                    logger.debug(f"Контейнер {i+1}: дублирующийся URL {article_url}, пропускаем")
                    continue
                
                processed_urls.add(article_url)
                
                # Извлекаем контент
                content = parser.extract_content(container)
                
                # Проверяем качество статьи
                if not parser._is_valid_article(title, content, article_url):
                    if not content:
                        skipped_stats['no_content'] += 1
                    else:
                        skipped_stats['low_quality'] += 1
                    logger.debug(f"Контейнер {i+1}: статья не прошла валидацию качества, пропускаем")
                    continue
                
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
        
        # Логируем детальную статистику
        total_containers = len(containers)
        logger.info(f"Универсальный парсинг {source.name} завершен:")
        logger.info(f"  Обработано контейнеров: {total_containers}")
        logger.info(f"  Успешно извлечено статей: {successful_extractions}")
        logger.info(f"  Пропущено - нет заголовка: {skipped_stats['no_title']}")
        logger.info(f"  Пропущено - нет URL: {skipped_stats['no_url']}")
        logger.info(f"  Пропущено - невалидный URL: {skipped_stats['invalid_url']}")
        logger.info(f"  Пропущено - нет контента: {skipped_stats['no_content']}")
        logger.info(f"  Пропущено - низкое качество: {skipped_stats['low_quality']}")
        logger.info(f"  Пропущено - дубликаты: {skipped_stats['duplicate_url']}")
        
        return articles 