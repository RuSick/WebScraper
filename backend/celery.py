# backend/celery.py

import os
from celery import Celery
from celery.schedules import crontab

# Установка переменной окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Создание экземпляра Celery
app = Celery('backend')

# Загрузка конфигурации из настроек Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическая загрузка задач из всех приложений
app.autodiscover_tasks()

# Явный импорт задач для обеспечения их регистрации
app.autodiscover_tasks(['scraper'])

# Настройка периодических задач
app.conf.beat_schedule = {
    'parse-all-sources': {
        'task': 'scraper.tasks.parse_all_sources',
        'schedule': crontab(minute='*/30'),  # Каждые 30 минут
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')