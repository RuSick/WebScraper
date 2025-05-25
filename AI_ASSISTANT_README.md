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

### Frontend (React)
- **React 18** - пользовательский интерфейс
- **Axios** - HTTP клиент
- **CSS Modules** - стилизация

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
└── frontend/              # React приложение
    ├── src/
    │   ├── components/    # React компоненты
    │   ├── services/      # API сервисы
    │   └── styles/        # CSS стили
    └── public/
```

## Модели данных

### Source (Источник новостей)
```python
class Source(models.Model):
    name = models.CharField(max_length=200)           # Название источника
    url = models.URLField()                           # URL источника
    type = models.CharField(max_length=50)            # Тип парсера
    is_active = models.BooleanField(default=True)     # Активен ли источник
    articles_count = models.IntegerField(default=0)   # Количество статей
    last_parsed = models.DateTimeField(null=True)     # Последний парсинг
    created_at = models.DateTimeField(auto_now_add=True)
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
    tags = models.JSONField(default=list)             # Теги (NLP)
    locations = models.JSONField(default=list)        # Локации (NLP)
    is_featured = models.BooleanField(default=False)  # Рекомендуемая
    is_active = models.BooleanField(default=True)     # Активная
    is_analyzed = models.BooleanField(default=False)  # Проанализирована
    created_at = models.DateTimeField(auto_now_add=True)
```

## Цепочка фоновых задач Celery

### 🔄 Архитектура цепочки
Система реализует автоматическую цепочку задач без использования `chain()`:

1. **`parse_source(source_id)`** - парсит источник и находит статьи
2. **`save_article(data)`** - сохраняет каждую статью в БД (только новые)
3. **`analyze_article_text(article_id)`** - анализирует текст статьи (NLP)

### 🚀 Принцип работы
- Пользователь запускает только `parse_source(source_id)` через API
- Парсер находит статьи и **автоматически** отправляет каждую в `save_article.delay()`
- При сохранении новой статьи **автоматически** запускается `analyze_article_text.delay()`
- Дубликаты отфильтровываются автоматически (по URL)
- Анализ запускается только для новых статей

### 📋 Celery задачи

#### `parse_source(source_id: int)`
- Получает источник из БД
- Использует универсальный парсер для сбора статей
- Отправляет каждую найденную статью в `save_article.delay()`
- Обновляет время последнего парсинга источника

#### `save_article(article_data: Dict)`
- Проверяет уникальность статьи по URL
- Сохраняет новую статью в БД
- Обновляет счетчик статей в источнике
- **Автоматически** запускает `analyze_article_text.delay(article_id)`

#### `analyze_article_text(article_id: int)`
- Получает статью из БД
- Выполняет NLP-анализ (тема, теги, локации)
- Сохраняет результаты анализа
- Устанавливает `is_analyzed=True`

#### `analyze_unanalyzed_articles(batch_size=50)`
- Находит непроанализированные статьи
- Запускает анализ батчами по 50 статей
- Используется для массового анализа существующих статей

#### `parse_all_sources()`
- Запускает парсинг всех активных источников
- Каждый источник обрабатывается отдельной задачей

## API эндпоинты

### Источники
- `GET /api/sources/` - список всех источников
- `GET /api/sources/{id}/` - детали источника
- `POST /api/sources/{id}/parse/` - **запуск парсинга конкретного источника**
- `POST /api/sources/parse-all/` - **запуск парсинга всех активных источников**

### Статьи
- `GET /api/articles/` - список статей с пагинацией
- `GET /api/articles/{id}/` - детали статьи
- `POST /api/articles/analyze/` - **анализ непроанализированных статей**

### Задачи Celery
- `GET /api/tasks/{task_id}/status/` - **статус выполнения задачи**

### Статистика
- `GET /api/stats/articles/` - общая статистика по статьям

## Система парсинга

### Универсальный парсер
Основной парсер (`scraper/parsers/universal_parser.py`) работает с любыми новостными сайтами:

#### Возможности:
- Автоматическое определение контейнеров статей
- Извлечение заголовков, ссылок, дат публикации
- Получение полного контента статей
- Строгая фильтрация нежелательных URL
- Валидация контента статей

#### Фильтрация URL:
Исключаются служебные страницы:
- `/comments`, `/users`, `/sandbox`, `/company`, `/promo`
- `/login`, `/signup`, `/search`, `/tags`, `/archive`
- `/about`, `/contact`, `/privacy`, `/terms`, `/help`
- Статические файлы (CSS, JS, изображения)
- API endpoints, админка

#### Валидация контента:
- Минимальная длина заголовка: 5 символов
- Минимальная длина контента или summary: 20 символов
- Исключение служебных заголовков: "комментарии", "войти", "регистрация"

### Специализированные парсеры
- **HabrParser** - для Habr.com
- **LentaParser** - для Lenta.ru

## NLP анализ текста

Система анализа (`core/text_analyzer.py`) определяет:

### Темы статей:
- `technology` - технологии, IT, наука
- `politics` - политика, государство
- `economics` - экономика, бизнес, финансы
- `sports` - спорт
- `culture` - культура, искусство
- `health` - здоровье, медицина
- `other` - прочие темы

### Извлечение данных:
- **Теги** - ключевые слова из текста
- **Локации** - географические названия
- **Тональность** - позитивная/негативная/нейтральная

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
- Node.js (для фронтенда)

### Команды запуска:
```bash
# Backend
python manage.py runserver 8000

# Celery worker
celery -A backend worker --loglevel=info

# Frontend (в отдельном терминале)
cd frontend && npm start
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
- Django админка: http://localhost:8000/admin/
- API документация: http://localhost:8000/api/

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

Система полностью готова к продуктивному использованию и дальнейшему развитию! 