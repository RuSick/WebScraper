# MediaScope - Инструкция для ИИ-ассистента

## Обзор проекта
MediaScope - это система агрегации и анализа новостей, построенная на Django с React фронтендом. Система автоматически собирает статьи из различных источников, анализирует их содержимое с помощью NLP и предоставляет удобный интерфейс для просмотра.

## Архитектура системы

### Backend (Django)
- **Django 4.2** - основной фреймворк
- **PostgreSQL** - база данных
- **Redis** - брокер сообщений для Celery
- **Celery** - система фоновых задач
- **Django REST Framework** - API

### Frontend (Django Templates)
- **Bootstrap 5** - UI фреймворк
- **Vanilla JavaScript** - интерактивность
- **Django Templates** - серверный рендеринг
- **Демо-интерфейс** - для тестирования и демонстрации

### Фоновые задачи (Celery)
- **Автоматическая цепочка**: парсинг → сохранение → анализ
- **8 воркеров** для параллельной обработки
- **Redis** как брокер сообщений

## Структура проекта

```
MediaScope/
├── backend/                 # Django настройки
│   ├── settings.py         # Основные настройки
│   ├── celery.py          # Конфигурация Celery
│   └── urls.py            # Главные URL маршруты
├── core/                   # Основные модели и логика
│   ├── models.py          # Модели данных (Source, Article)
│   ├── views.py           # Django views для демо-интерфейса
│   ├── text_analyzer.py   # NLP анализ текста
│   └── admin.py           # Django админка
├── api/                    # REST API
│   ├── views.py           # API эндпоинты
│   ├── serializers.py     # Сериализаторы данных
│   └── urls.py            # API маршруты
├── scraper/               # Система парсинга
│   ├── tasks.py           # Celery задачи
│   ├── parsers/           # Парсеры для разных источников
│   │   ├── universal_parser.py  # Универсальный парсер
│   │   ├── habr_parser.py      # Парсер для Habr
│   │   └── lenta_parser.py     # Парсер для Lenta.ru
│   └── utils.py           # Вспомогательные функции
├── templates/             # Django шаблоны
│   └── demo/
│       └── index.html     # Демо-интерфейс с Bootstrap
└── static/                # Статические файлы (CSS, JS, изображения)
```

## Модели данных

### Source (Источник новостей)
```python
class Source(models.Model):
    name = models.CharField(max_length=200)           # Название источника
    url = models.URLField()                           # URL источника
    type = models.CharField(max_length=50)            # Тип парсера
    is_active = models.BooleanField(default=True)     # Активен ли источник
    description = models.TextField(blank=True)        # Описание источника
    update_frequency = models.PositiveIntegerField(default=60) # Частота обновления (мин)
    articles_count = models.IntegerField(default=0)   # Количество статей
    last_parsed = models.DateTimeField(null=True)     # Последний парсинг
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Время обновления
```

### Article (Статья)
```python
class Article(models.Model):
    title = models.CharField(max_length=500)          # Заголовок
    content = models.TextField()                      # Полный текст
    summary = models.TextField()                      # Краткое содержание
    url = models.URLField(unique=True)                # Уникальный URL
    published_at = models.DateTimeField()             # Дата публикации
    source = models.ForeignKey(Source)                # Источник
    topic = models.CharField(max_length=100)          # Тема (NLP)
    tags = ArrayField(models.CharField(max_length=100), default=list) # Теги (NLP)
    locations = ArrayField(models.CharField(max_length=100), default=list) # Локации (NLP)
    read_count = models.PositiveIntegerField(default=0) # Просмотры
    is_featured = models.BooleanField(default=False)  # Рекомендуемая
    is_active = models.BooleanField(default=True)     # Активная
    is_analyzed = models.BooleanField(default=False)  # Проанализирована
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)   # Время обновления
```

## 🔄 ДЕТАЛЬНАЯ ЛОГИКА РАБОТЫ СИСТЕМЫ

### ⚠️ ВАЖНО: НЕ СОЗДАВАЙТЕ ДУБЛИКАТЫ!
Вся логика парсинга, сохранения и анализа УЖЕ РЕАЛИЗОВАНА. Используйте существующие функции!

### 🚀 Полная цепочка обработки новостей

#### 1. ЗАПУСК ПАРСИНГА (Точка входа)
**Когда пользователь говорит "запускай парсер" - используйте ТОЛЬКО эти методы:**

```python
# Через API (рекомендуемый способ)
curl -X POST http://localhost:8000/api/sources/11/parse/  # Один источник
curl -X POST http://localhost:8000/api/sources/parse-all/ # Все источники

# Через Celery задачи напрямую
from scraper.tasks import parse_source, parse_all_sources
parse_source.delay(source_id)      # Один источник
parse_all_sources.delay()          # Все источники

# Через скрипт
python parse_sources.py           # Простой скрипт запуска
```

#### 2. ЭТАП 1: ПАРСИНГ ИСТОЧНИКА
**Файл: `scraper/tasks.py` → функция `parse_source(source_id)`**

```python
@shared_task
def parse_source(source_id: int) -> Dict[str, Any]:
    """
    ГЛАВНАЯ ЗАДАЧА ПАРСИНГА
    
    Что делает:
    1. Получает источник из БД по ID
    2. Проверяет активность источника
    3. Использует универсальный парсер для сбора статей
    4. Автоматически отправляет КАЖДУЮ найденную статью в save_article.delay()
    5. Обновляет время последнего парсинга
    
    ВАЖНО: НЕ сохраняет статьи напрямую! Только планирует задачи сохранения!
    """
```

**Логика парсинга:**
- Использует `fetch_generic_articles(source)` из `universal_parser.py`
- Находит контейнеры статей на странице
- Извлекает заголовки, URL, контент, даты
- Фильтрует служебные страницы и дубликаты
- Возвращает список словарей с данными статей

#### 3. ЭТАП 2: СОХРАНЕНИЕ СТАТЕЙ
**Файл: `scraper/tasks.py` → функция `save_article(article_data)`**

```python
@shared_task
def save_article(article_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    ЗАДАЧА СОХРАНЕНИЯ ОДНОЙ СТАТЬИ
    
    Что делает:
    1. Проверяет уникальность по URL (НЕ создает дубликаты!)
    2. Если статья новая - сохраняет в БД
    3. Обновляет счетчик статей в источнике
    4. Автоматически запускает analyze_article_text.delay(article_id)
    
    ВАЖНО: Запускается автоматически из parse_source для каждой статьи!
    """
```

**Структура article_data:**
```python
{
    'title': 'Заголовок статьи',
    'content': 'Полный текст статьи',
    'summary': 'Краткое содержание',
    'url': 'https://example.com/article',
    'published_at': '2025-01-01T12:00:00Z',  # или None
    'source_id': 11,
    'topic': 'technology'  # или 'other'
}
```

#### 4. ЭТАП 3: АНАЛИЗ ТЕКСТА
**Файл: `scraper/tasks.py` → функция `analyze_article_text(article_id)`**

```python
@shared_task
def analyze_article_text(article_id: int) -> Dict[str, Any]:
    """
    ЗАДАЧА АНАЛИЗА ОДНОЙ СТАТЬИ
    
    Что делает:
    1. Получает статью из БД по ID
    2. Проверяет, не анализировалась ли уже
    3. Вызывает analyze_article_content() из core/text_analyzer.py
    4. Сохраняет результаты: topic, tags, locations
    5. Устанавливает is_analyzed=True
    
    ВАЖНО: Запускается автоматически из save_article для новых статей!
    """
```

**NLP анализ выполняется в `core/text_analyzer.py`:**
```python
def analyze_article_content(article) -> Dict[str, Any]:
    """
    Анализирует текст статьи и возвращает:
    {
        'topic': 'technology',           # Определенная тема
        'tags': ['python', 'django'],   # Ключевые слова
        'locations': ['москва', 'россия'] # Географические названия
    }
    """
```

### 🔧 Универсальный парсер (НЕ ИЗМЕНЯЙТЕ!)

**Файл: `scraper/parsers/universal_parser.py`**

Это ОСНОВНОЙ парсер системы, который работает с любыми новостными сайтами:

```python
async def fetch_generic_articles(source: SourceProtocol) -> List[Dict[str, Any]]:
    """
    ГЛАВНАЯ ФУНКЦИЯ ПАРСИНГА
    
    Алгоритм работы:
    1. Получает HTML страницы источника
    2. Ищет контейнеры статей (article, div.post, div.news и т.д.)
    3. Извлекает из каждого контейнера:
       - Заголовок (h1-h4, .title, .headline)
       - URL статьи (ссылки в заголовках)
       - Контент (article, .content, .body)
       - Дату публикации (time, .date, meta теги)
    4. Фильтрует нежелательные URL и контент
    5. Возвращает список валидных статей
    """
```

**Фильтрация URL (СТРОГАЯ!):**
- Исключает: `/comments`, `/users`, `/login`, `/search`, `/admin`
- Исключает: статические файлы (CSS, JS, изображения)
- Исключает: служебные страницы (/about, /contact, /privacy)
- Проверяет домен (только тот же сайт)

**Валидация контента:**
- Минимум 5 символов в заголовке
- Минимум 20 символов в контенте или summary
- Исключает служебные заголовки ("комментарии", "войти")
- Проверяет качество текста (соотношение букв к символам)

### 📋 Дополнительные задачи

#### Массовый анализ существующих статей
```python
@shared_task
def analyze_unanalyzed_articles(batch_size: int = 50):
    """
    Анализирует все непроанализированные статьи батчами
    
    Использование:
    - Через API: POST /api/articles/analyze/
    - Напрямую: analyze_unanalyzed_articles.delay()
    """
```

#### Парсинг всех источников
```python
@shared_task
def parse_all_sources():
    """
    Запускает парсинг всех активных источников
    
    Использование:
    - Через API: POST /api/sources/parse-all/
    - Напрямую: parse_all_sources.delay()
    """
```

## API эндпоинты

### 🚀 Управление парсингом
```bash
# Запуск парсинга одного источника
POST /api/sources/{id}/parse/
# Ответ: {"message": "Парсинг запущен", "task_id": "abc123", "status": "started"}

# Запуск парсинга всех источников  
POST /api/sources/parse-all/
# Ответ: {"message": "Запущен парсинг 38 источников", "task_ids": [...]}

# Запуск анализа непроанализированных статей
POST /api/articles/analyze/
# Ответ: {"message": "Анализ запущен", "task_id": "def456"}

# Проверка статуса задачи
GET /api/tasks/{task_id}/status/
# Ответ: {"task_id": "abc123", "status": "SUCCESS", "result": {...}}
```

### 📊 Получение данных
```bash
# Список статей с фильтрацией
GET /api/articles/?page=1&page_size=12&topic=technology&analyzed=true

# Список источников
GET /api/sources/

# Статистика
GET /api/stats/articles/
GET /api/stats/sources/
```

## 🎯 КОМАНДЫ ДЛЯ ИИ-АССИСТЕНТА

### Когда пользователь говорит "запускай парсер":
```python
# ИСПОЛЬЗУЙТЕ ТОЛЬКО ЭТО:
curl -X POST http://localhost:8000/api/sources/parse-all/
# ИЛИ для конкретного источника:
curl -X POST http://localhost:8000/api/sources/11/parse/
```

### Когда нужен только анализ:
```python
# Анализ всех непроанализированных статей:
curl -X POST http://localhost:8000/api/articles/analyze/
```

### Когда нужна проверка статуса:
```python
# Проверка статуса задачи:
curl http://localhost:8000/api/tasks/{task_id}/status/
```

### Когда нужна статистика:
```python
# Общая статистика:
curl http://localhost:8000/api/stats/articles/
```

## 🚨 ЧТО НЕ НУЖНО ДЕЛАТЬ

### ❌ НЕ создавайте новые функции парсинга:
- Универсальный парсер уже работает с любыми сайтами
- Есть специализированные парсеры для Habr и Lenta.ru
- Логика фильтрации и валидации уже реализована

### ❌ НЕ создавайте новые функции сохранения:
- `save_article()` уже обрабатывает все случаи
- Проверка дубликатов по URL уже есть
- Обновление счетчиков уже реализовано

### ❌ НЕ создавайте новые функции анализа:
- `analyze_article_text()` уже анализирует все аспекты
- NLP анализ в `core/text_analyzer.py` уже настроен
- Определение тем, тегов и локаций уже работает

### ❌ НЕ вызывайте функции напрямую:
- Используйте API эндпоинты или Celery задачи
- Не импортируйте парсеры напрямую в коде
- Не обходите систему задач

## 🔍 Отладка и мониторинг

### Проверка работы системы:
```bash
# Статус Celery worker
celery -A backend inspect active

# Логи Django
tail -f /var/log/django.log

# Статистика базы данных
python manage.py shell -c "from core.models import Article; print(f'Всего статей: {Article.objects.count()}')"
```

### Скрипты для мониторинга:
- `monitor_analysis.py` - отслеживание прогресса анализа
- `test_celery_chain.py` - тестирование цепочки задач

## Текущее состояние системы

### 📊 Статистика:
- **850 статей** в базе данных
- **Все статьи проанализированы** (100% покрытие)
- **38 активных источников** новостей
- **Дубликаты автоматически отфильтровываются**

### 🔧 Компоненты:
- ✅ Django сервер запущен на порту 8000
- ✅ Celery worker активен (8 воркеров)
- ✅ Redis брокер работает
- ✅ PostgreSQL база данных подключена
- ✅ Цепочка задач полностью функциональна

### 🚀 Производительность:
- **Параллельная обработка** - 8 воркеров Celery
- **Быстрый анализ** - ~50ms на статью
- **Масштабируемость** - батчи по 50 статей
- **Надежность** - каждая задача независима

## Запуск системы

### Требования:
- Python 3.10+
- PostgreSQL
- Redis

### Команды запуска:
```bash
# Backend (Django сервер)
python manage.py runserver 8000

# Celery worker
celery -A backend worker --loglevel=info

# Демо-интерфейс доступен по адресу:
# http://localhost:8000/ или http://localhost:8000/demo/
```

### Переменные окружения:
```bash
DATABASE_URL=postgresql://user:password@localhost/mediascope
REDIS_URL=redis://localhost:6379/0
DEBUG=True
SECRET_KEY=your-secret-key
```

## Примеры использования API

### Запуск парсинга источника:
```bash
curl -X POST http://localhost:8000/api/sources/11/parse/ \
  -H "Content-Type: application/json"
```

### Проверка статуса задачи:
```bash
curl http://localhost:8000/api/tasks/{task_id}/status/
```

### Массовый анализ статей:
```bash
curl -X POST http://localhost:8000/api/articles/analyze/ \
  -H "Content-Type: application/json"
```

### Получение статей:
```bash
curl "http://localhost:8000/api/articles/?page=1&page_size=12"
```

## Мониторинг и отладка

### Логи Celery:
Все задачи логируются с подробной информацией о выполнении.

### Скрипты для мониторинга:
- `monitor_analysis.py` - отслеживание прогресса анализа
- `test_celery_chain.py` - тестирование цепочки задач

### Веб-интерфейс:
- Главная страница: http://localhost:8000/
- Демо-интерфейс: http://localhost:8000/demo/
- Django админка: http://localhost:8000/admin/
- API документация: http://localhost:8000/api/docs/ (Swagger)
- API документация: http://localhost:8000/api/redoc/ (ReDoc)

## Решенные проблемы

### ✅ Фильтрация некорректных статей
- Исключены служебные страницы (/comments, /users и т.д.)
- Валидация контента и заголовков
- Проверка минимальной длины текста

### ✅ Цепочка фоновых задач
- Автоматическое выполнение: парсинг → сохранение → анализ
- Обработка дубликатов
- Параллельная обработка

### ✅ Масштабируемость
- Батчевая обработка статей
- Независимые задачи
- Мониторинг прогресса

## Рекомендации для разработки

### При добавлении новых источников:
1. Создать запись в модели `Source`
2. При необходимости создать специализированный парсер
3. Универсальный парсер работает с большинством сайтов

### При изменении логики анализа:
1. Обновить `core/text_analyzer.py`
2. Запустить повторный анализ через API
3. Проверить результаты в админке

### При масштабировании:
1. Увеличить количество Celery воркеров
2. Настроить Redis кластер
3. Оптимизировать размер батчей

## 🎯 ИТОГОВЫЕ ПРАВИЛА ДЛЯ ИИ-АССИСТЕНТА:

1. **Парсинг**: ВСЕГДА используйте `POST /api/sources/parse-all/` или `parse_source.delay()`
2. **Анализ**: ВСЕГДА используйте `POST /api/articles/analyze/` или `analyze_unanalyzed_articles.delay()`
3. **Статистика**: ВСЕГДА используйте `GET /api/stats/articles/`
4. **НЕ создавайте** новые функции парсинга/сохранения/анализа
5. **НЕ импортируйте** парсеры напрямую
6. **ИСПОЛЬЗУЙТЕ** существующую цепочку задач
7. **ПРОВЕРЯЙТЕ** статус через API `/api/tasks/{task_id}/status/`

Система полностью готова к продуктивному использованию и дальнейшему развитию! 