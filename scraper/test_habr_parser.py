import asyncio
import logging
from parsers.habr_parser import fetch_habr_articles

# Устанавливаем уровень DEBUG для более подробного вывода
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

async def test_basic_parsing():
    """Тестируем базовый парсинг без контента."""
    logger.info("=== Тест базового парсинга (без контента) ===")
    articles = await fetch_habr_articles(include_content=False, max_articles=3)
    
    if not articles:
        logger.warning("No articles found on Habr main page.")
        return
        
    logger.info(f"Found {len(articles)} articles.")
    for art in articles:
        logger.info("\n" + "="*50)
        logger.info(f"Title: {art['title']}")
        logger.info(f"URL: {art['url']}")
        logger.info(f"Published: {art['pub_date']}")
        logger.info(f"Snippet: {art['snippet'][:100]}..." if art['snippet'] else "Snippet: (нет)")

async def test_content_parsing():
    """Тестируем парсинг с получением полного контента."""
    logger.info("\n\n=== Тест парсинга с контентом (ограничение: 1 статья) ===")
    articles = await fetch_habr_articles(include_content=True, max_articles=1)
    
    if not articles:
        logger.warning("No articles found on Habr main page.")
        return
        
    logger.info(f"Found {len(articles)} articles with content.")
    for art in articles:
        logger.info("\n" + "="*70)
        logger.info(f"Title: {art['title']}")
        logger.info(f"URL: {art['url']}")
        logger.info(f"Published: {art['pub_date']}")
        logger.info(f"Snippet: {art['snippet'][:100]}..." if art['snippet'] else "Snippet: (нет)")
        logger.info(f"Content length: {len(art.get('content', ''))} characters")
        if art.get('content'):
            logger.info(f"Content preview: {art.get('content', '')[:300]}...")
        else:
            logger.warning("Контент не был извлечен!")

async def main():
    # Сначала тестируем базовый парсинг
    await test_basic_parsing()
    
    # Затем тестируем парсинг с контентом
    await test_content_parsing()

if __name__ == "__main__":
    asyncio.run(main()) 