"""
Модуль headless-браузера для парсинга JavaScript-зависимых сайтов.

Этот модуль предоставляет fallback-механизм для сайтов, которые 
загружают контент динамически через JavaScript (SPA).

Поддерживаемые браузеры:
- Playwright (заглушка)
- Selenium (планируется)

Использование:
    from scraper.browser.fallback_playwright import fetch_with_playwright
    
    html = await fetch_with_playwright(url)
"""

from .fallback_playwright import fetch_with_playwright

__all__ = ['fetch_with_playwright'] 