import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Dict
import logging
import asyncio

logger = logging.getLogger(__name__)

HABR_URL = "https://habr.com/ru/all/"

async def fetch_article_content(session: aiohttp.ClientSession, article_url: str) -> str:
    """Получает полный контент статьи по её URL."""
    try:
        async with session.get(article_url) as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Список возможных селекторов для контента статьи
            content_selectors = [
                'div.tm-article-body__content',
                'div.article-formatted-body',
                'div.tm-article-body',
                'article .post__text',
                '.post-content-body'
            ]
            
            for selector in content_selectors:
                content_div = soup.select_one(selector)
                if content_div:
                    # Удаляем ненужные элементы
                    for unwanted in content_div.find_all(['script', 'style', 'button', 'nav', 'aside']):
                        unwanted.decompose()
                    
                    content = content_div.get_text(strip=True, separator=' ')
                    if content:  # Если нашли непустой контент
                        logger.debug(f"Контент найден с селектором: {selector}")
                        return content
            
            # Если ничего не нашли, попробуем найти основной контент по тегам
            main_content = soup.find('main') or soup.find('article')
            if main_content:
                # Удаляем заголовки, навигацию и прочее
                for unwanted in main_content.find_all(['nav', 'aside', 'footer', 'header', 'script', 'style']):
                    unwanted.decompose()
                
                content = main_content.get_text(strip=True, separator=' ')
                if len(content) > 200:  # Если контент достаточно длинный
                    logger.debug("Контент найден через main/article тег")
                    return content
            
            logger.warning(f"Не удалось найти контент для {article_url}")
            return ""
            
    except Exception as e:
        logger.warning(f"Ошибка при получении контента статьи {article_url}: {e}")
        return ""

async def fetch_habr_articles(include_content: bool = False, max_articles: int = None) -> List[Dict]:
    """
    Получает статьи с главной страницы Хабра.
    
    Args:
        include_content: Если True, получает полный контент каждой статьи
        max_articles: Максимальное количество статей для обработки
    """
    articles = []
    async with aiohttp.ClientSession() as session:
        async with session.get(HABR_URL) as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            article_elements = soup.find_all('article', class_='tm-articles-list__item')
            if max_articles:
                article_elements = article_elements[:max_articles]
                
            for article in article_elements:
                try:
                    # Заголовок и ссылка
                    h2 = article.find('h2', class_='tm-title tm-title_h2')
                    a = h2.find('a') if h2 else None
                    title = a.get_text(strip=True) if a else None
                    url = urljoin(HABR_URL, a['href']) if a else None
                    
                    # Дата публикации
                    time_tag = article.find('time')
                    pub_date = time_tag['datetime'] if time_tag and time_tag.has_attr('datetime') else None
                    
                    # Краткое описание (если есть)
                    snippet_div = article.find('div', class_='tm-article-snippet__lead')
                    snippet = snippet_div.get_text(strip=True) if snippet_div else ""
                    
                    if title and url:
                        article_data = {
                            'title': title,
                            'url': url,
                            'pub_date': pub_date,
                            'snippet': snippet
                        }
                        
                        # Получаем полный контент, если запрошено
                        if include_content:
                            content = await fetch_article_content(session, url)
                            article_data['content'] = content
                            
                        articles.append(article_data)
                        
                except Exception as e:
                    logger.warning(f"Ошибка при парсинге статьи: {e}")
    
    return articles 