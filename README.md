# MediaScope 📰

**MediaScope** — современная новостная платформа для сбора, анализа и мониторинга медиаконтента из различных источников с поддержкой анализа тональности и автоматической категоризации.

## 🚀 Возможности

- **Многоисточниковый сбор**: RSS, HTML сайты, API, Telegram каналы
- **Анализ тональности**: Автоматическое определение эмоциональной окраски статей
- **Тематическая классификация**: Выделение тем с помощью NLP (spaCy)
- **RESTful API**: Полнофункциональный API для доступа к данным
- **Асинхронная обработка**: Celery + Redis для фоновых задач
- **Административная панель**: Django Admin для управления источниками

## 🛠️ Технологический стек

### Backend
- **Django 4.2** - Основной веб-фреймворк
- **Django REST Framework 3.14** - API
- **PostgreSQL** - Основная база данных
- **Celery 5.3** - Асинхронные задачи
- **Redis 5.0** - Брокер сообщений и кэш

### Парсинг и анализ
- **BeautifulSoup4 4.12** - Парсинг HTML
- **selectolax 0.3** - Быстрый HTML парсер
- **aiohttp 3.9** - Асинхронные HTTP запросы
- **spaCy 3.7** - Обработка естественного языка

## 📋 Требования

- Python 3.8+
- PostgreSQL 12+
- Redis 6+

## ⚙️ Установка и настройка

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd MediaScope
```

### 2. Создание виртуального окружения
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Настройка базы данных PostgreSQL
```sql
CREATE DATABASE news_platform;
CREATE USER rusick WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE news_platform TO rusick;
```

### 5. Настройка переменных окружения
Создайте файл `.env` в корне проекта:
```env
DEBUG=True
SECRET_KEY=your-secret-key
DB_NAME=news_platform
DB_USER=rusick
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
```

### 6. Применение миграций
```bash
python manage.py migrate
```

### 7. Создание суперпользователя
```bash
python manage.py createsuperuser
```

### 8. Загрузка модели spaCy
```bash
python -m spacy download ru_core_news_sm
```

## 🏃‍♂️ Запуск проекта

### Запуск сервера разработки
```bash
python manage.py runserver
```

### Запуск Celery Worker
```bash
celery -A backend worker --loglevel=info
```

### Запуск Celery Beat (планировщик)
```bash
celery -A backend beat --loglevel=info
```

### Запуск Redis
```bash
redis-server
```

## 📁 Структура проекта

```
MediaScope/
├── backend/                 # Настройки Django проекта
│   ├── settings.py         # Основные настройки
│   ├── urls.py            # URL роутинг
│   ├── wsgi.py            # WSGI конфигурация
│   └── asgi.py            # ASGI конфигурация
├── core/                   # Основное приложение
│   ├── models.py          # Модели данных
│   ├── admin.py           # Административная панель
│   └── migrations/        # Миграции БД
├── api/                    # REST API приложение
│   ├── views.py           # API представления
│   ├── serializers.py     # Сериализаторы
│   └── urls.py            # API маршруты
├── manage.py              # Django управляющий скрипт
├── requirements.txt       # Зависимости Python
└── .python-version        # Версия Python
```

## 🗄️ Модели данных

### Source (Источники)
```python
class Source(models.Model):
    name = models.CharField(max_length=255)           # Название источника
    url = models.URLField(unique=True)                # URL источника
    type = models.CharField(max_length=10, choices=[  # Тип источника
        ('rss', 'RSS'),
        ('html', 'HTML'), 
        ('api', 'API'),
        ('tg', 'Telegram')
    ])
    is_active = models.BooleanField(default=True)     # Активность
    created_at = models.DateTimeField(auto_now_add=True)
```

### Article (Статьи)
```python
class Article(models.Model):
    title = models.CharField(max_length=500)          # Заголовок
    content = models.TextField()                      # Содержимое
    source = models.ForeignKey(Source)                # Источник
    url = models.URLField(unique=True)                # URL статьи
    published_at = models.DateTimeField()             # Дата публикации
    created_at = models.DateTimeField(auto_now_add=True)
    tone = models.CharField(max_length=10, choices=[  # Тональность
        ('positive', 'Позитивная'),
        ('neutral', 'Нейтральная'),
        ('negative', 'Негативная')
    ])
    topic = models.CharField(max_length=255)          # Тема
```

## 🔌 API Документация

### Базовый URL
```
http://localhost:8000/api/
```

### Источники
- **GET** `/api/sources/` - Список всех активных источников
- **GET** `/api/sources/{id}/` - Детали конкретного источника

### Статьи
- **GET** `/api/articles/` - Список всех статей
- **GET** `/api/articles/{id}/` - Детали конкретной статьи

#### Параметры фильтрации и поиска:
- `search` - Поиск по заголовку, теме и тональности
- `ordering` - Сортировка по `published_at`, `tone`

#### Примеры запросов:
```bash
# Все статьи
GET /api/articles/

# Поиск статей
GET /api/articles/?search=технологии

# Сортировка по дате
GET /api/articles/?ordering=-published_at

# Позитивные статьи
GET /api/articles/?search=positive
```

### Пример ответа API:
```json
{
    "count": 150,
    "next": "http://localhost:8000/api/articles/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Новая технология в ИИ",
            "content": "Содержимое статьи...",
            "url": "https://example.com/article/1",
            "published_at": "2024-01-15T10:30:00Z",
            "created_at": "2024-01-15T11:00:00Z",
            "tone": "positive",
            "topic": "технологии",
            "source": {
                "id": 1,
                "name": "Tech News",
                "url": "https://technews.com/rss",
                "type": "rss",
                "is_active": true
            }
        }
    ]
}
```

## 🔧 Административная панель

Доступ к Django Admin: `http://localhost:8000/admin/`

Здесь можно:
- Управлять источниками новостей
- Просматривать и редактировать статьи
- Мониторить процесс сбора данных

## 🚧 Разработка

### Добавление нового парсера
1. Создайте файл `tasks.py` в приложении `core`
2. Реализуйте Celery задачи для парсинга
3. Добавьте периодические задачи в настройки

### Добавление анализа тональности
1. Интегрируйте spaCy в обработку статей
2. Создайте функции анализа в `core/utils.py`
3. Добавьте вызов анализа в задачи парсинга

### Расширение API
1. Добавьте новые эндпоинты в `api/views.py`
2. Создайте соответствующие сериализаторы
3. Обновите URL конфигурацию

## 📊 Мониторинг

### Celery Flower (опционально)
```bash
pip install flower
celery -A backend flower
```
Доступ: `http://localhost:5555`

### Логирование
Логи доступны в консоли при запуске сервисов

## 🐛 Устранение неполадок

### Проблемы с подключением к БД
- Проверьте настройки в `backend/settings.py`
- Убедитесь, что PostgreSQL запущен
- Проверьте права доступа пользователя

### Проблемы с Celery
- Убедитесь, что Redis запущен
- Проверьте конфигурацию брокера
- Перезапустите воркеры

### Проблемы с зависимостями
- Обновите pip: `pip install --upgrade pip`
- Переустановите зависимости: `pip install -r requirements.txt --force-reinstall`

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📝 Лицензия

Этот проект распространяется под лицензией MIT.

## 📞 Контакты

- **Автор**: Rusick
- **Проект**: MediaScope
- **Цель**: Мониторинг и анализ медиаконтента

---

*Создано с ❤️ для эффективного мониторинга новостного контента* 