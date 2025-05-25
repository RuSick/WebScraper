import asyncio
import logging
from parsers.playwright_parser import PlaywrightParser

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_parser():
    """Тестирование парсера на примере habr.com."""
    url = "https://habr.com/ru/all/"
    source_name = "Habr"
    
    try:
        async with PlaywrightParser(url, source_name) as parser:
            articles = await parser.fetch_articles()
            
            if not articles:
                logger.warning(f"No articles found on {url}")
                return
                
            logger.info(f"Found {len(articles)} articles")
            
            for article in articles:
                logger.info("\n" + "="*50)
                logger.info(f"Title: {article['title']}")
                logger.info(f"URL: {article['url']}")
                logger.info(f"Published: {article['published_at']}")
                logger.info(f"Content snippet: {article['content'][:200]}...")
                
    except Exception as e:
        logger.error(f"Error testing parser: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_parser()) 