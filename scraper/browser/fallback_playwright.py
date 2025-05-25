"""
Headless-парсер на основе Playwright для JavaScript-зависимых сайтов.

Этот модуль предназначен для парсинга Single Page Applications (SPA)
и сайтов, которые загружают контент динамически через JavaScript.

Примеры использования:
- Meduza.io (React-based SPA)
- TJournal.ru (Vue.js-based SPA) 
- Другие современные новостные сайты

ВНИМАНИЕ: Данный модуль является архитектурной заглушкой.
Для активации требуется:
1. Установка Playwright: pip install playwright
2. Установка браузеров: playwright install
3. Включение флага ENABLE_HEADLESS_PARSING = True в settings.py
4. Реализация функции fetch_with_playwright()
"""

import logging
from typing import Optional
from django.conf import settings

logger = logging.getLogger(__name__)


async def fetch_with_playwright(url: str, timeout: int = 30) -> str:
    """
    Потенциальный headless-парсер на основе Playwright.
    
    Возвращает HTML после полной отрисовки страницы JavaScript'ом.
    Подходит для парсинга SPA (Single Page Applications).
    
    Args:
        url: URL для загрузки
        timeout: Таймаут в секундах
    
    Returns:
        str: HTML-контент после полной загрузки JavaScript
    
    Raises:
        NotImplementedError: Модуль не активирован в данной сборке
        
    Пример будущей реализации:
        ```python
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url)
            await page.wait_for_load_state('networkidle')
            html = await page.content()
            await browser.close()
            return html
        ```
    """
    # Проверяем, включен ли headless-парсинг в настройках
    if not getattr(settings, 'ENABLE_HEADLESS_PARSING', False):
        logger.warning(f"Headless-парсинг отключен в настройках для {url}")
        raise NotImplementedError(
            "Headless-парсинг не активирован в данной сборке. "
            "Установите ENABLE_HEADLESS_PARSING = True в settings.py"
        )
    
    # TODO: Реализовать Playwright-парсинг когда потребуется
    logger.error(f"Запрошен headless-парсинг {url}, но модуль не реализован")
    raise NotImplementedError(
        "Headless-парсинг не реализован. "
        "Требуется установка Playwright и реализация функции."
    )


def is_headless_available() -> bool:
    """
    Проверяет доступность headless-парсинга.
    
    Returns:
        bool: True если headless-парсинг доступен и включен
    """
    # Проверяем настройку
    if not getattr(settings, 'ENABLE_HEADLESS_PARSING', False):
        return False
    
    # Проверяем наличие Playwright (когда будет реализован)
    try:
        import playwright
        return True
    except ImportError:
        logger.debug("Playwright не установлен")
        return False


def should_use_headless(html_content: str, url: str) -> bool:
    """
    Определяет, нужно ли использовать headless-парсинг.
    
    Критерии для использования headless:
    1. HTML слишком короткий (подозрение на SPA)
    2. Найдены признаки JavaScript-генерируемого контента
    3. Отсутствуют ожидаемые HTML-элементы
    
    Args:
        html_content: Полученный HTML-контент
        url: URL сайта
    
    Returns:
        bool: True если рекомендуется headless-парсинг
    """
    # Слишком короткий HTML - подозрение на SPA
    if len(html_content) < 2000:
        logger.info(f"Короткий HTML ({len(html_content)} символов) для {url}")
        return True
    
    # Признаки SPA-приложений
    spa_indicators = [
        'window.__INITIAL_STATE__',
        'window.__REDUX_STATE__', 
        'data-react-helmet',
        'ng-app',  # Angular
        'data-v-',  # Vue.js
        'id="root"',  # React root
        'id="app"'   # Vue/общий app root
    ]
    
    html_lower = html_content.lower()
    for indicator in spa_indicators:
        if indicator.lower() in html_lower:
            logger.info(f"Найден SPA-индикатор '{indicator}' для {url}")
            return True
    
    # Проверяем отношение JavaScript к контенту
    js_script_count = html_content.count('<script')
    content_size = len(html_content)
    
    # Если много JavaScript относительно контента
    if js_script_count > 10 and content_size < 5000:
        logger.info(f"Много JavaScript ({js_script_count} скриптов) для {url}")
        return True
    
    return False


# Список известных SPA-сайтов для приоритетного headless-парсинга
KNOWN_SPA_DOMAINS = [
    # Существующие SPA-сайты
    'meduza.io',
    'tjournal.ru', 
    'vc.ru',
    'dtf.ru',
    
    # 🇷🇺 Русскоязычные IT SPA-источники
    'vc.ru',  # VC.ru - Технологии (уже есть выше)
    
    # 🌍 Англоязычные IT SPA-источники  
    'techcrunch.com',           # TechCrunch - сложная SPA структура
    'thenextweb.com',           # The Next Web - React-based SPA
    'theverge.com',             # The Verge - Vox Media SPA
    'venturebeat.com',          # VentureBeat - WordPress + React components
    'huggingface.co',           # Hugging Face Blog - Next.js application
    'dev.to',                   # Dev.to - Ruby on Rails + Preact
    
    # Добавлять по мере обнаружения других SPA-сайтов
]


def is_known_spa_site(url: str) -> bool:
    """
    Проверяет, является ли сайт известным SPA.
    
    Args:
        url: URL для проверки
    
    Returns:
        bool: True если сайт в списке известных SPA
    """
    from urllib.parse import urlparse
    
    try:
        domain = urlparse(url).netloc.lower()
        # Удаляем www. префикс для сравнения
        domain = domain.replace('www.', '')
        
        return domain in KNOWN_SPA_DOMAINS
    except Exception:
        return False 