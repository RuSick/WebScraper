#!/usr/bin/env python
"""
Тестовый скрипт для проверки Celery-задачи сбора статей с Хабра.
Запускает задачу синхронно без Celery worker'а для тестирования.
"""

import os
import sys
import django

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from scraper.tasks import collect_habr_articles
import logging

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_habr_collection():
    """Тестирует сбор статей с Хабра."""
    logger.info("Начинаем тест сбора статей с Хабра...")
    
    # Запускаем задачу синхронно (без Celery)
    result = collect_habr_articles(include_content=True, max_articles=5)
    
    logger.info("Результат сбора:")
    logger.info(f"Статус: {result.get('status')}")
    logger.info(f"Новых статей: {result.get('new_articles', 0)}")
    logger.info(f"Обновлено статей: {result.get('updated_articles', 0)}")
    logger.info(f"Всего обработано: {result.get('total_processed', 0)}")
    
    if result.get('status') == 'error':
        logger.error(f"Ошибка: {result.get('error')}")
    else:
        logger.info(f"Сообщение: {result.get('message')}")

if __name__ == "__main__":
    test_habr_collection() 