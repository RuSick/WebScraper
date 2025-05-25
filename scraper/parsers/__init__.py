from .base import BaseParser
from .rss import RSSParser
from .html import HTMLParser
from .lenta import LentaParser
from .universal_parser import UniversalNewsParser, fetch_generic_articles

__all__ = ['BaseParser', 'RSSParser', 'HTMLParser', 'LentaParser', 'UniversalNewsParser', 'fetch_generic_articles'] 