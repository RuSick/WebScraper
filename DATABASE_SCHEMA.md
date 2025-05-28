# Структура базы данных MediaScope

## Обзор

MediaScope использует PostgreSQL в качестве основной базы данных. Система построена на Django ORM и включает основные модели для новостей (`Source`, `Article`) и полноценную систему авторизации (`User`, `UserProfile`, `SubscriptionPlan`, `UserSubscription`, `FavoriteArticle`).

## Модели данных

### 1. Source (Источники новостей)

Модель для хранения информации об источниках новостей, с которых происходит парсинг статей.

#### Поля:

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| `id` | BigAutoField | Первичный ключ | AUTO_INCREMENT |
| `name` | CharField(255) | Название источника | NOT NULL |
| `url` | URLField | URL источника | UNIQUE, NOT NULL |
| `type` | CharField(10) | Тип источника | Choices: rss, html, spa, api, tg |
| `is_active` | BooleanField | Активен ли источник | DEFAULT: True |
| `description` | TextField | Описание источника | BLANK |
| `update_frequency` | PositiveIntegerField | Частота обновления (мин) | DEFAULT: 60 |
| `last_parsed` | DateTimeField | Время последнего парсинга | NULL, BLANK |
| `articles_count` | PositiveIntegerField | Количество статей | DEFAULT: 0 |
| `created_at` | DateTimeField | Дата создания | AUTO_NOW_ADD |
| `updated_at` | DateTimeField | Дата обновления | AUTO_NOW |

#### Типы источников:
- `rss` - RSS фиды
- `html` - HTML страницы
- `spa` - SPA приложения (JavaScript)
- `api` - API эндпоинты
- `tg` - Telegram каналы

#### Индексы:
- Первичный ключ на `id`
- Уникальный индекс на `url`
- Сортировка по умолчанию: `-created_at`

---

### 2. Article (Статьи)

Основная модель для хранения новостных статей с результатами NLP-анализа.

#### Поля:

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| `id` | BigAutoField | Первичный ключ | AUTO_INCREMENT |
| `title` | CharField(500) | Заголовок статьи | NOT NULL |
| `content` | TextField | Полный текст статьи | BLANK |
| `summary` | TextField | Краткое содержание | BLANK |
| `url` | URLField | Оригинальная ссылка | UNIQUE, NOT NULL |
| `source` | ForeignKey | Ссылка на источник | CASCADE |
| `published_at` | DateTimeField | Дата публикации | NOT NULL |
| `topic` | CharField(20) | Основная тема | Choices, DEFAULT: 'other' |
| `tags` | ArrayField | Ключевые слова | PostgreSQL Array |
| `locations` | ArrayField | Географические упоминания | PostgreSQL Array |
| `is_analyzed` | BooleanField | Проанализирована ли | DEFAULT: False |
| `read_count` | PositiveIntegerField | Количество просмотров | DEFAULT: 0 |
| `is_featured` | BooleanField | Рекомендуемая статья | DEFAULT: False |
| `is_active` | BooleanField | Активна ли статья | DEFAULT: True |
| `created_at` | DateTimeField | Дата создания | AUTO_NOW_ADD |
| `updated_at` | DateTimeField | Дата обновления | AUTO_NOW |

#### Темы статей (TOPIC_CHOICES):
- `politics` - Политика
- `economics` - Экономика
- `technology` - Технологии
- `science` - Наука
- `sports` - Спорт
- `culture` - Культура
- `health` - Здоровье
- `education` - Образование
- `environment` - Экология
- `society` - Общество
- `war` - Война и конфликты
- `international` - Международные отношения
- `business` - Бизнес
- `finance` - Финансы
- `entertainment` - Развлечения
- `travel` - Путешествия
- `food` - Еда
- `fashion` - Мода
- `auto` - Автомобили
- `real_estate` - Недвижимость
- `other` - Прочее

#### Индексы:
- Первичный ключ на `id`
- Уникальный индекс на `url`
- Индекс на `published_at`
- Индекс на `topic`
- Индекс на `source`
- Индекс на `is_analyzed`
- Сортировка по умолчанию: `-published_at`

---

## Система авторизации

### 3. User (Пользователи)

Кастомная модель пользователя, расширяющая AbstractUser Django.

#### Поля:

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| `id` | BigAutoField | Первичный ключ | AUTO_INCREMENT |
| `email` | EmailField | Email адрес | UNIQUE, NOT NULL |
| `username` | CharField(150) | Имя пользователя | UNIQUE, NOT NULL |
| `first_name` | CharField(150) | Имя | NOT NULL |
| `last_name` | CharField(150) | Фамилия | NOT NULL |
| `is_email_verified` | BooleanField | Подтвержден ли email | DEFAULT: False |
| `date_joined` | DateTimeField | Дата регистрации | AUTO_NOW_ADD |
| `last_login` | DateTimeField | Последний вход | NULL |
| `is_active` | BooleanField | Активен ли аккаунт | DEFAULT: True |
| `is_staff` | BooleanField | Доступ к админке | DEFAULT: False |
| `is_superuser` | BooleanField | Суперпользователь | DEFAULT: False |

#### Методы:
- `full_name` - Полное имя пользователя
- `get_absolute_url()` - URL профиля пользователя

#### Индексы:
- Первичный ключ на `id`
- Уникальный индекс на `email`
- Уникальный индекс на `username`

---

### 4. UserProfile (Профили пользователей)

Расширенная информация о пользователе и настройки.

#### Поля:

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| `id` | BigAutoField | Первичный ключ | AUTO_INCREMENT |
| `user` | OneToOneField | Ссылка на пользователя | CASCADE |
| `avatar` | ImageField | Аватар пользователя | NULL, BLANK |
| `bio` | TextField | Биография | BLANK |
| `language` | CharField(2) | Язык интерфейса | Choices: ru, en, DEFAULT: ru |
| `theme` | CharField(10) | Тема оформления | Choices: light, dark, auto, DEFAULT: auto |
| `timezone` | CharField(50) | Часовой пояс | DEFAULT: Europe/Moscow |
| `email_notifications` | BooleanField | Email уведомления | DEFAULT: True |
| `newsletter_subscription` | BooleanField | Подписка на рассылку | DEFAULT: True |
| `articles_read` | PositiveIntegerField | Прочитанных статей | DEFAULT: 0 |
| `last_activity` | DateTimeField | Последняя активность | AUTO_NOW |
| `created_at` | DateTimeField | Дата создания | AUTO_NOW_ADD |
| `updated_at` | DateTimeField | Дата обновления | AUTO_NOW |

#### Индексы:
- Первичный ключ на `id`
- Уникальный индекс на `user`
- Индекс на `last_activity`

---

### 5. SubscriptionPlan (Планы подписок)

Модель для управления планами подписок и их возможностями.

#### Поля:

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| `id` | BigAutoField | Первичный ключ | AUTO_INCREMENT |
| `name` | CharField(100) | Название плана | NOT NULL |
| `slug` | SlugField(100) | URL-slug плана | UNIQUE, NOT NULL |
| `plan_type` | CharField(20) | Тип плана | Choices, NOT NULL |
| `description` | TextField | Описание плана | BLANK |
| `price` | DecimalField(10,2) | Цена плана | NOT NULL |
| `billing_period` | CharField(20) | Период оплаты | Choices, NOT NULL |
| `features` | JSONField | Возможности плана | DEFAULT: list |
| `is_popular` | BooleanField | Популярный план | DEFAULT: False |
| `is_active` | BooleanField | Активен ли план | DEFAULT: True |
| `created_at` | DateTimeField | Дата создания | AUTO_NOW_ADD |
| `updated_at` | DateTimeField | Дата обновления | AUTO_NOW |

#### Типы планов:
- `free` - Бесплатный
- `basic` - Базовый
- `premium` - Премиум
- `enterprise` - Корпоративный

#### Периоды оплаты:
- `monthly` - Ежемесячно
- `yearly` - Ежегодно
- `lifetime` - Пожизненно

#### Индексы:
- Первичный ключ на `id`
- Уникальный индекс на `slug`
- Индекс на `plan_type`

---

### 6. UserSubscription (Подписки пользователей)

Модель для отслеживания активных подписок пользователей.

#### Поля:

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| `id` | BigAutoField | Первичный ключ | AUTO_INCREMENT |
| `user` | ForeignKey | Ссылка на пользователя | CASCADE |
| `plan` | ForeignKey | Ссылка на план | CASCADE |
| `status` | CharField(20) | Статус подписки | Choices, NOT NULL |
| `start_date` | DateTimeField | Дата начала | NOT NULL |
| `end_date` | DateTimeField | Дата окончания | NULL, BLANK |
| `auto_renewal` | BooleanField | Автопродление | DEFAULT: False |
| `created_at` | DateTimeField | Дата создания | AUTO_NOW_ADD |
| `updated_at` | DateTimeField | Дата обновления | AUTO_NOW |

#### Статусы подписки:
- `active` - Активна
- `expired` - Истекла
- `cancelled` - Отменена
- `pending` - Ожидает оплаты

#### Методы:
- `is_active` - Проверка активности подписки
- `days_remaining` - Количество дней до окончания

#### Индексы:
- Первичный ключ на `id`
- Индекс на `user`
- Индекс на `status`
- Индекс на `end_date`

---

### 7. FavoriteArticle (Избранные статьи)

Модель для хранения избранных статей пользователей.

#### Поля:

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| `id` | BigAutoField | Первичный ключ | AUTO_INCREMENT |
| `user` | ForeignKey | Ссылка на пользователя | CASCADE |
| `article` | ForeignKey | Ссылка на статью | CASCADE |
| `notes` | TextField | Заметки пользователя | BLANK |
| `created_at` | DateTimeField | Дата добавления | AUTO_NOW_ADD |

#### Индексы:
- Первичный ключ на `id`
- Уникальный составной индекс на `(user, article)`
- Индекс на `user`
- Индекс на `created_at`

---

## Связи между таблицами

### Source → Article (One-to-Many)
- Один источник может содержать множество статей
- Связь через `Article.source` → `Source.id`
- При удалении источника все его статьи удаляются (CASCADE)
- Обратная связь: `source.articles.all()`

### User → UserProfile (One-to-One)
- Каждый пользователь имеет один профиль
- Связь через `UserProfile.user` → `User.id`
- При удалении пользователя профиль удаляется (CASCADE)
- Обратная связь: `user.profile`

### User → UserSubscription (One-to-Many)
- Пользователь может иметь несколько подписок (история)
- Связь через `UserSubscription.user` → `User.id`
- При удалении пользователя подписки удаляются (CASCADE)
- Обратная связь: `user.subscriptions.all()`

### SubscriptionPlan → UserSubscription (One-to-Many)
- План может быть у множества пользователей
- Связь через `UserSubscription.plan` → `SubscriptionPlan.id`
- При удалении плана подписки сохраняются (PROTECT)
- Обратная связь: `plan.subscriptions.all()`

### User → FavoriteArticle (One-to-Many)
- Пользователь может иметь множество избранных статей
- Связь через `FavoriteArticle.user` → `User.id`
- При удалении пользователя избранное удаляется (CASCADE)
- Обратная связь: `user.favorite_articles.all()`

### Article → FavoriteArticle (One-to-Many)
- Статья может быть в избранном у множества пользователей
- Связь через `FavoriteArticle.article` → `Article.id`
- При удалении статьи записи избранного удаляются (CASCADE)
- Обратная связь: `article.favorited_by.all()`

---

## PostgreSQL специфичные поля

### ArrayField
Используется для хранения массивов строк в полях:
- `Article.tags` - массив ключевых слов
- `Article.locations` - массив географических названий

Пример данных:
```json
{
  "tags": ["технологии", "искусственный интеллект", "машинное обучение"],
  "locations": ["Москва", "Россия", "США"]
}
```

---

## Миграции

### Основные миграции:

#### Core приложение:
1. **0001_initial.py** - Создание базовых таблиц (Source, Article)
2. **0002_alter_article_options_alter_source_options_and_more.py** - Добавление полей аналитики и метаданных
3. **0003_update_article_analysis.py** - Обновление системы анализа и расширение тем

#### Accounts приложение:
1. **accounts/0001_initial.py** - Создание системы авторизации:
   - Кастомная модель User
   - UserProfile с настройками пользователя
   - SubscriptionPlan для планов подписок
   - UserSubscription для отслеживания подписок
   - FavoriteArticle для избранных статей

### Порядок применения миграций:

```bash
# Применение всех миграций
python manage.py migrate

# Применение миграций по приложениям
python manage.py migrate core
python manage.py migrate accounts

# Создание новых миграций при изменении моделей
python manage.py makemigrations
python manage.py makemigrations accounts
```

### Зависимости миграций:
- `accounts.0001_initial` зависит от `core.0001_initial` (для связи FavoriteArticle → Article)
- Все auth миграции должны применяться после создания базовых таблиц

---

## API Endpoints

### Sources API:
- `GET /api/sources/` - Список источников
- `POST /api/sources/` - Создание источника
- `GET /api/sources/{id}/` - Детали источника
- `PUT/PATCH /api/sources/{id}/` - Обновление источника
- `DELETE /api/sources/{id}/` - Удаление источника

### Articles API:
- `GET /api/articles/` - Список статей с фильтрацией
- `POST /api/articles/` - Создание статьи
- `GET /api/articles/{id}/` - Детали статьи
- `PUT/PATCH /api/articles/{id}/` - Обновление статьи
- `DELETE /api/articles/{id}/` - Удаление статьи

### Authentication API:
- `POST /api/auth/register/` - Регистрация пользователя
- `POST /api/auth/login/` - Вход в систему (получение JWT токена)
- `POST /api/auth/logout/` - Выход из системы
- `GET /api/auth/profile/` - Получение профиля пользователя
- `PATCH /api/auth/profile/update/` - Обновление профиля
- `POST /api/auth/change-password/` - Смена пароля
- `GET /api/auth/stats/` - Статистика пользователя
- `GET /api/auth/dashboard/` - Данные для дашборда

### Subscription API:
- `GET /api/auth/subscription-plans/` - Список планов подписок
- `GET /api/auth/subscriptions/` - Подписки пользователя
- `POST /api/auth/subscriptions/` - Создание подписки

### Favorites API:
- `GET /api/auth/favorites/` - Избранные статьи пользователя
- `POST /api/auth/favorites/` - Добавление в избранное
- `DELETE /api/auth/favorites/{id}/` - Удаление из избранного
- `PATCH /api/auth/favorites/{id}/` - Обновление заметок
- `POST /api/auth/articles/{id}/toggle-favorite/` - Переключение избранного
- `GET /api/auth/articles/{id}/check-favorite/` - Проверка избранного

### Фильтрация и поиск:
- **Поиск**: по title, content, summary, tags, locations
- **Фильтры**: topic, source, is_featured, is_analyzed, published_at
- **Сортировка**: published_at, created_at, read_count

### Аутентификация:
- **JWT токены** для авторизации API запросов
- **Token-based authentication** с автоматическим обновлением
- **Защищенные endpoints** требуют заголовок `Authorization: Token <jwt_token>`

---

## Производительность

### Оптимизации:
1. **Индексы** на часто используемых полях
2. **select_related('source')** для избежания N+1 запросов
3. **Пагинация** для больших списков (20 элементов по умолчанию)
4. **Кэширование** счетчиков в Source.articles_count

### Рекомендации:
- Регулярная очистка старых статей
- Мониторинг размера ArrayField полей
- Использование индексов для PostgreSQL Array полей при необходимости

---

## Безопасность

### Валидация:
- Уникальность URL статей и источников
- Валидация URL через URLValidator
- Проверка типов источников через choices
- Санитизация входных данных

### Права доступа:
- Только активные статьи (`is_active=True`) доступны через API
- Административный интерфейс для управления источниками
- Логирование всех операций парсинга

### Аутентификация и авторизация:
- **JWT токены** для безопасной аутентификации
- **Хеширование паролей** с использованием Django PBKDF2
- **Валидация email** при регистрации
- **Уникальность username и email** на уровне базы данных
- **Автоматическое истечение токенов** при неактивности
- **Защита от CSRF** для всех форм
- **Rate limiting** для API endpoints (планируется)

### Защита данных пользователей:
- **Шифрование паролей** в базе данных
- **Валидация сложности паролей** на клиенте и сервере
- **Безопасное хранение JWT токенов** в localStorage (с автоочисткой)
- **Логирование попыток входа** для мониторинга безопасности
- **Автоматический logout** при обнаружении 401 ошибок

### Приватность:
- **Изоляция данных пользователей** - каждый видит только свои избранные и статистику
- **Опциональные уведомления** - пользователь контролирует email рассылки
- **Удаление данных** при деактивации аккаунта (CASCADE)

---

## Мониторинг

### Метрики:
- Количество статей по источникам
- Статистика по темам
- Производительность парсинга
- Ошибки анализа текста

### Метрики пользователей:
- **Регистрации** - количество новых пользователей по дням/неделям
- **Активность** - количество активных пользователей (DAU/MAU)
- **Избранные статьи** - популярность контента
- **Подписки** - конверсия в платные планы
- **API запросы** - нагрузка на систему по пользователям
- **Время сессий** - продолжительность использования

### Логирование:
- Все операции парсинга
- Ошибки сохранения статей
- Результаты NLP анализа
- **Попытки входа** (успешные и неуспешные)
- **Регистрации пользователей**
- **Смены паролей**
- **API запросы** с метаданными пользователя
- **Ошибки аутентификации** (401, 403)

---

## Планируемые изменения структуры БД

### Долгосрочные планы нормализации

#### 1. Вынос тегов в отдельную таблицу

**Проблема текущего подхода:**
- ArrayField создает дублирование данных
- Сложность поиска и фильтрации по тегам
- Невозможность добавления метаданных к тегам
- Ограничения PostgreSQL ArrayField при больших объемах

**Планируемая структура:**

```sql
-- Таблица тегов
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50),  -- 'person', 'organization', 'technology', 'location'
    usage_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Связующая таблица многие-ко-многим
CREATE TABLE article_tags (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    relevance_score FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(article_id, tag_id)
);
```

**Преимущества:**
- Устранение дублирования данных
- Быстрые запросы с индексами
- Метаданные тегов (категории, счетчики)
- Гибкая фильтрация и аналитика
- Масштабируемость до миллионов тегов

#### 2. Вынос локаций в отдельную таблицу

```sql
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    country VARCHAR(100),
    region VARCHAR(100),
    coordinates POINT,  -- для карт
    location_type VARCHAR(50),  -- 'city', 'country', 'region'
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE article_locations (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    location_id INTEGER REFERENCES locations(id) ON DELETE CASCADE,
    mention_count INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(article_id, location_id)
);
```

#### 3. Разделение контента статей

**Цель:** Оптимизация запросов списков статей

```sql
-- Основная таблица (только метаданные)
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    url VARCHAR(500) UNIQUE NOT NULL,
    source_id INTEGER REFERENCES sources(id),
    published_at TIMESTAMP NOT NULL,
    topic VARCHAR(20),
    is_analyzed BOOLEAN DEFAULT FALSE,
    read_count INTEGER DEFAULT 0,
    is_featured BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Отдельная таблица для полного контента
CREATE TABLE article_content (
    article_id INTEGER PRIMARY KEY REFERENCES articles(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    content_length INTEGER,
    language VARCHAR(10) DEFAULT 'ru',
    encoding VARCHAR(20) DEFAULT 'utf-8',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 4. Система версионирования

```sql
CREATE TABLE article_versions (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    title VARCHAR(500),
    content TEXT,
    summary TEXT,
    version_number INTEGER,
    change_type VARCHAR(20),  -- 'created', 'updated', 'title_changed'
    changes_summary TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 5. Система пользователей

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    password_hash VARCHAR(128),
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    is_active BOOLEAN DEFAULT TRUE,
    date_joined TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

CREATE TABLE user_bookmarks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, article_id)
);

CREATE TABLE user_reading_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    read_at TIMESTAMP DEFAULT NOW(),
    reading_time INTEGER,
    read_percentage INTEGER DEFAULT 100
);
```

### Ожидаемые улучшения производительности

- **Запросы списков статей**: ускорение в 3-5 раз
- **Поиск по тегам**: ускорение в 10-20 раз
- **Аналитические запросы**: ускорение в 5-10 раз
- **Масштабируемость**: поддержка 10M+ статей

### Миграционная стратегия

1. **Этап 1** (2-3 недели): Создание новых таблиц параллельно
2. **Этап 2** (1-2 недели): Миграция данных и тестирование
3. **Этап 3** (1 неделя): Обновление API и фронтенда
4. **Этап 4** (1 неделя): Удаление старых полей

**Общее время реализации**: 5-7 недель

### Новые API endpoints

- `GET /api/tags/` - Список всех тегов
- `GET /api/tags/popular/` - Популярные теги
- `GET /api/tags/categories/` - Категории тегов
- `GET /api/locations/` - Список локаций
- `GET /api/articles/?tags=python,django` - Фильтрация по тегам
- `GET /api/articles/?locations=moscow` - Фильтрация по локациям
- `GET /api/users/{id}/bookmarks/` - Закладки пользователя
- `GET /api/users/{id}/history/` - История чтения 