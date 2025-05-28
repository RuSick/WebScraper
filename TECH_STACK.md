# MediaScope - Технологический стек

## 🚀 Обзор архитектуры

MediaScope построен на современном технологическом стеке с микросервисной архитектурой, обеспечивающей масштабируемость, производительность и надежность.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Workers       │
│   React + TC    │◄──►│   Django + DRF  │◄──►│   Celery        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Database      │    │   Message       │
                       │   PostgreSQL    │    │   Broker        │
                       └─────────────────┘    │   Redis         │
                                              └─────────────────┘
```

---

## 🔧 Backend Technologies

### Core Framework
- **Django 4.2** - Основной веб-фреймворк
  - **Версия**: 4.2 LTS
  - **Применение**: Веб-приложение, ORM, админ-панель
  - **Компоненты**: Models, Views, URL routing, Middleware
  - **Конфигурация**: Production-ready settings с разделением на dev/prod

### API Framework
- **Django REST Framework (DRF) 3.14+** - REST API
  - **Сериализация**: ModelSerializer, ListSerializer
  - **ViewSets**: ModelViewSet, ReadOnlyModelViewSet
  - **Пагинация**: PageNumberPagination (20 элементов)
  - **Фильтрация**: DjangoFilterBackend, SearchFilter, OrderingFilter
  - **Документация**: drf-spectacular для OpenAPI/Swagger

### База данных
- **PostgreSQL 12+** - Основная СУБД
  - **Расширения**: ArrayField для тегов и локаций
  - **Индексы**: Оптимизированные для поиска и фильтрации
  - **Транзакции**: ACID compliance
  - **Полнотекстовый поиск**: PostgreSQL FTS

### Система очередей
- **Celery 5.3+** - Распределенная система задач
  - **Воркеры**: 8 параллельных процессов
  - **Задачи**: parse_source, save_article, analyze_article_text
  - **Мониторинг**: Встроенное логирование и метрики
  - **Retry**: Автоматические повторы при ошибках

- **Redis 6+** - Брокер сообщений и кэш
  - **Применение**: Очередь Celery, кэширование API
  - **Конфигурация**: Persistence включен
  - **Производительность**: In-memory операции

---

## 🎨 Frontend Technologies

### Core Framework
- **React 18** - Основной UI фреймворк
  - **Hooks**: useState, useEffect, useContext, useCallback
  - **Context API**: Глобальное управление состоянием
  - **React Router**: Клиентский роутинг
  - **Компонентная архитектура**: Переиспользуемые UI компоненты

### Styling & UI
- **Tailwind CSS 3.3+** - Utility-first CSS фреймворк
  - **JIT компиляция**: Оптимизированная сборка
  - **Dark mode**: Поддержка темной темы
  - **Responsive design**: Mobile-first подход
  - **Custom components**: Собственные UI компоненты

### State Management & Data Fetching
- **React Query (TanStack Query)** - Управление серверным состоянием
  - **Кэширование**: Автоматическое кэширование API запросов
  - **Синхронизация**: Background refetching
  - **Оптимистичные обновления**: Instant UI updates
  - **Error handling**: Централизованная обработка ошибок

### Build Tools
- **Vite** - Современный build tool
  - **Hot Module Replacement**: Мгновенные обновления
  - **ES modules**: Нативная поддержка
  - **Tree shaking**: Оптимизация bundle размера
  - **TypeScript ready**: Готовность к миграции на TS

---

## 🕷️ Web Scraping & Data Processing

### HTTP Clients
- **aiohttp 3.9+** - Асинхронные HTTP запросы
  - **Async/await**: Неблокирующие операции
  - **Connection pooling**: Переиспользование соединений
  - **Timeout handling**: Контроль времени ожидания
  - **SSL verification**: Безопасные соединения

### HTML Parsing
- **BeautifulSoup4 4.12+** - HTML/XML парсер
  - **CSS selectors**: Гибкий поиск элементов
  - **Tree navigation**: Навигация по DOM
  - **Encoding detection**: Автоопределение кодировки
  - **Robust parsing**: Устойчивость к невалидному HTML

- **selectolax 0.3+** - Быстрый HTML парсер
  - **High performance**: Оптимизированная скорость
  - **Memory efficient**: Эффективное использование памяти
  - **CSS selectors**: Поддержка селекторов
  - **C extensions**: Нативные расширения

### Browser Automation
- **Playwright 1.42+** - Headless browser automation
  - **JavaScript rendering**: Обработка SPA сайтов
  - **Multiple browsers**: Chromium, Firefox, WebKit
  - **Network interception**: Контроль запросов
  - **Screenshot capabilities**: Снимки экрана

### RSS Processing
- **feedparser 6.0+** - RSS/Atom парсер
  - **Multiple formats**: RSS 1.0/2.0, Atom
  - **Encoding handling**: Автоматическая обработка кодировок
  - **Date parsing**: Парсинг различных форматов дат
  - **Sanitization**: Очистка контента

---

## 🧠 Natural Language Processing

### Current NLP Engine
- **spaCy 3.7.2** - Современный ML-анализатор
  - **Модель**: ru_core_news_sm для русского языка
  - **Named Entity Recognition**: Извлечение именованных сущностей
  - **Лемматизация**: Приведение к начальной форме
  - **Part-of-Speech tagging**: Морфологический анализ
  - **Векторные представления**: Word embeddings
  - **Производительность**: ~50ms на статью
  - **Точность**: ~85% для тематик (улучшение с ML)

### Hybrid Analysis Approach
- **Primary**: spaCy ML-модели для основного анализа
- **Fallback**: Словарный анализатор при ошибках spaCy
- **Тематическая классификация**: 21 категория
- **Извлечение ключевых слов**: Частотный + семантический анализ
- **Географические названия**: NER + база локаций

### Text Processing
- **spaCy Pipeline** - Полная обработка текста
  - **Токенизация**: Разбиение на токены
  - **Лемматизация**: Нормализация словоформ
  - **POS-теги**: Части речи
  - **Dependency parsing**: Синтаксический анализ
  - **NER**: Именованные сущности (PERSON, ORG, GPE, LOC)

### Language Detection
- **spaCy Language Detection** - Определение языка
  - **Статистический анализ**: Частота символов и n-грамм
  - **Fallback механизм**: Словарный подход
  - **Поддержка**: Русский/английский

---

## 🗄️ Database & Storage

### Primary Database
- **PostgreSQL 12+** - Реляционная СУБД
  - **ACID транзакции**: Надежность данных
  - **JSON поддержка**: Гибкие структуры
  - **Full-text search**: Встроенный поиск
  - **Extensions**: ArrayField, contrib modules

### Database Schema
```sql
-- Основные таблицы
sources (11 полей)     -- Источники новостей
articles (15 полей)    -- Статьи с метаданными
```

### Indexes & Performance
- **Primary keys**: Автоинкремент ID
- **Unique constraints**: URL уникальность
- **Foreign keys**: Связи с каскадным удалением
- **Composite indexes**: Оптимизация запросов
- **Array indexes**: PostgreSQL специфичные

---

## 🔄 DevOps & Infrastructure

### Process Management
- **Concurrently** - Параллельный запуск сервисов
  - **Frontend**: React dev server (port 3000)
  - **Backend**: Django runserver (port 8000)
  - **Unified commands**: npm start для всего стека

### Package Management
- **npm** - Frontend зависимости
  - **package.json**: Скрипты и зависимости
  - **Semantic versioning**: Контроль версий
  - **Lock files**: Детерминированные установки

- **pip** - Python зависимости
  - **requirements.txt**: Production зависимости
  - **Virtual environment**: Изоляция окружения
  - **Freeze versions**: Фиксированные версии

### Environment Management
- **Python venv** - Виртуальное окружение
  - **Изоляция**: Отдельные зависимости
  - **Версионирование**: Python 3.10+
  - **Активация**: Source-based activation

---

## 📊 Monitoring & Logging

### Application Logging
- **Python logging** - Встроенное логирование
  - **Уровни**: DEBUG, INFO, WARNING, ERROR
  - **Форматирование**: Структурированные сообщения
  - **Ротация**: По размеру и времени
  - **Handlers**: Console и file output

### Performance Monitoring
- **Django Debug Toolbar** - Development профилирование
  - **SQL queries**: Анализ запросов к БД
  - **Template rendering**: Время рендеринга
  - **Cache hits**: Статистика кэширования
  - **Memory usage**: Использование памяти

### Task Monitoring
- **Celery logging** - Мониторинг задач
  - **Task status**: Статус выполнения
  - **Error tracking**: Отслеживание ошибок
  - **Performance metrics**: Время выполнения
  - **Worker health**: Состояние воркеров

---

## 🔒 Security & Authentication

### Django Security
- **CSRF Protection** - Защита от CSRF атак
- **XSS Prevention** - Автоэкранирование шаблонов
- **SQL Injection Protection** - Django ORM
- **Secure Headers** - Security middleware
- **Input Validation** - Serializer validation

### API Security
- **CORS Configuration** - Cross-origin requests
- **Rate Limiting** - Защита от злоупотреблений
- **Input Sanitization** - Очистка входных данных
- **Error Handling** - Безопасные сообщения об ошибках

---

## 📦 Dependencies & Versions

### Backend Dependencies (requirements.txt)
```txt
Django==4.2
djangorestframework==3.14.0
django-filter==23.5
django-cors-headers==4.3.1
drf-spectacular==0.27.1
celery==5.3.6
redis==5.0.1
psycopg2-binary==2.9.9
aiohttp==3.9.3
beautifulsoup4==4.12.3
selectolax==0.3.16
spacy==3.7.2
playwright==1.42.0
python-dateutil==2.8.2
Brotli==1.1.0
```

### Frontend Dependencies (package.json)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "@tanstack/react-query": "^4.24.0",
    "axios": "^1.3.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^3.1.0",
    "vite": "^4.1.0",
    "tailwindcss": "^3.2.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
```

### System Dependencies
```bash
# Python
Python 3.10+
pip 23+

# Node.js
Node.js 18+
npm 9+

# Databases
PostgreSQL 12+
Redis 6+

# spaCy Model
python -m spacy download ru_core_news_sm

# System
Linux/macOS/Windows
4GB+ RAM
SSD storage
```

---

## 🚀 Performance Characteristics

### Current Metrics
- **850+ статей** в базе данных
- **38 активных источников** новостей
- **100% покрытие анализом** всех статей
- **8 параллельных воркеров** Celery
- **~50ms** время анализа одной статьи (spaCy)
- **20 статей/страница** пагинация API
- **85% точность** тематической классификации

### Scalability Features
- **Асинхронная обработка** - Неблокирующие операции
- **Горизонтальное масштабирование** - Добавление воркеров
- **Кэширование** - Redis для быстрого доступа
- **Индексы БД** - Оптимизированные запросы
- **Батчевая обработка** - Групповые операции
- **ML-анализ** - spaCy для точности и скорости

---

## 🔄 Development Workflow

### Local Development
```bash
# Запуск всего стека
npm start

# Отдельные сервисы
npm run backend    # Django на :8000
npm run frontend   # React на :3000
npm run celery     # Celery workers
```

### Code Quality
- **ESLint** - JavaScript/React линтинг
- **Prettier** - Форматирование кода
- **Black** - Python форматирование
- **isort** - Сортировка импортов

### Testing Strategy
- **Jest** - Frontend тестирование
- **React Testing Library** - Component тесты
- **pytest** - Backend тестирование
- **Factory Boy** - Тестовые данные

---

## 📈 Future Technology Plans

### Planned Upgrades
- **Docker** - Контейнеризация приложения
- **TypeScript** - Полная типизация frontend
- **Next.js** - SSR возможности
- **Kubernetes** - Оркестрация контейнеров
- **Prometheus/Grafana** - Расширенный мониторинг
- **Elasticsearch** - Полнотекстовый поиск

### Database Evolution
- **Нормализация** - Вынос тегов в отдельные таблицы
- **Партиционирование** - Разделение по датам
- **Материализованные представления** - Кэширование аналитики
- **Vector search** - Семантический поиск через embeddings

### NLP Improvements
- **Расширенные модели** - Переход на ru_core_news_lg
- **Sentiment Analysis** - Анализ тональности
- **Topic Modeling** - Автоматическое выявление тем
- **Summarization** - Автоматическое реферирование

---

## 🏗️ Architecture Principles

### Design Patterns
- **MVC/MVT** - Django архитектура
- **Component-based** - React компоненты
- **Repository Pattern** - Абстракция данных
- **Observer Pattern** - Event-driven обновления
- **Factory Pattern** - Создание объектов

### Best Practices
- **DRY** - Don't Repeat Yourself
- **SOLID** - Принципы ООП
- **RESTful API** - Стандартизированные эндпоинты
- **Responsive Design** - Адаптивный интерфейс
- **Error Handling** - Graceful degradation

---

**Версия документа**: 1.1  
**Дата обновления**: Декабрь 2024  
**Статус**: Production Ready 