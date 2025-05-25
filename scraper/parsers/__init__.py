from .base import BaseParser
from .rss import RSSParser
from .universal_parser import UniversalNewsParser, fetch_generic_articles

__all__ = ['BaseParser', 'RSSParser', 'UniversalNewsParser', 'fetch_generic_articles'] 