# MediaScope Design System 2024-2025

## 🎨 Обзор дизайн-системы

MediaScope использует современную дизайн-систему, вдохновленную принципами минимализма и удобства использования 2024-2025 годов. Дизайн основан на CSS-переменных для поддержки светлой и темной тем.

## 🌈 Цветовая палитра

### Основные цвета
```css
--primary-hue: 240;
--primary-saturation: 100%;
--primary-lightness: 58%;
```

### Светлая тема
```css
--bg-primary: #ffffff;      /* Основной фон */
--bg-secondary: #f8fafc;    /* Вторичный фон */
--bg-tertiary: #f1f5f9;     /* Третичный фон */
--bg-accent: #e2e8f0;       /* Акцентный фон */

--text-primary: #0f172a;    /* Основной текст */
--text-secondary: #475569;  /* Вторичный текст */
--text-tertiary: #64748b;   /* Третичный текст */
--text-muted: #94a3b8;      /* Приглушенный текст */
```

### Темная тема
```css
--bg-primary: #0f172a;      /* Основной фон */
--bg-secondary: #1e293b;    /* Вторичный фон */
--bg-tertiary: #334155;     /* Третичный фон */
--bg-accent: #475569;       /* Акцентный фон */

--text-primary: #f8fafc;    /* Основной текст */
--text-secondary: #e2e8f0;  /* Вторичный текст */
--text-tertiary: #cbd5e1;   /* Третичный текст */
--text-muted: #94a3b8;      /* Приглушенный текст */
```

## 🔤 Типографика

### Шрифт
- **Основной**: Inter (Google Fonts)
- **Fallback**: -apple-system, BlinkMacSystemFont, sans-serif

### Размеры заголовков
- **H1 (app-title)**: 1.75rem, font-weight: 700
- **H2-H6**: Пропорциональные размеры
- **Body**: 1rem, line-height: 1.6

## 📐 Компоненты

### 1. Карточки статей (Article Cards)
```css
.article-card {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 1.5rem;
    transition: all 0.3s ease;
    box-shadow: var(--shadow-sm);
}

.article-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
}
```

**Особенности:**
- Современные скругленные углы (16px)
- Плавные hover-эффекты
- Тени для глубины
- Адаптивная сетка

### 2. Бейджи тем (Topic Badges)
```css
.topic-badge {
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.375rem 0.75rem;
    border-radius: 20px;
    text-transform: uppercase;
    letter-spacing: 0.025em;
}
```

**Цветовая схема:**
- Политика: #dc2626
- Экономика: #059669
- Технологии: #2563eb
- Наука: #7c3aed
- И другие (всего 21 категория)

### 3. Теги и локации
```css
.tag {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
    border-radius: 8px;
    background: var(--bg-secondary);
    color: var(--text-secondary);
    transition: all 0.3s ease;
}

.tag:hover {
    background: hsl(var(--primary-hue), var(--primary-saturation), var(--primary-lightness));
    color: white;
    transform: translateY(-1px);
}
```

### 4. Статистические карточки
```css
.stat-card {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 1.5rem;
    position: relative;
    overflow: hidden;
}

.stat-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 4px;
    background: var(--gradient-primary);
}
```

### 5. Формы и инпуты
```css
.form-control, .form-select {
    background: var(--bg-primary);
    border: 2px solid var(--border-color);
    border-radius: 12px;
    padding: 0.75rem 1rem;
    transition: all 0.3s ease;
}

.form-control:focus {
    border-color: hsl(var(--primary-hue), var(--primary-saturation), var(--primary-lightness));
    box-shadow: 0 0 0 3px hsla(var(--primary-hue), var(--primary-saturation), var(--primary-lightness), 0.1);
}
```

## 🌟 UX Улучшения

### 1. Переключатель темы
- Фиксированная позиция в правом верхнем углу
- Сохранение выбора в localStorage
- Плавные переходы между темами

### 2. Активные фильтры
- Визуальное отображение применяемых фильтров
- Возможность удаления отдельных фильтров
- Кнопка "Очистить все"

### 3. Поиск с дебаунсингом
- Автоматический поиск при вводе (>= 3 символа)
- Поиск по Enter
- Таймаут 500ms для оптимизации

### 4. Загрузка и состояния
- Современные спиннеры
- Плавные переходы
- Состояние "пусто" для отсутствующих данных

### 5. Пагинация
- Современный дизайн кнопок
- Умное отображение номеров страниц
- Навигация стрелками

## 📱 Адаптивность

### Брейкпоинты
- **Desktop**: 1200px+
- **Tablet**: 768px - 1199px
- **Mobile**: < 768px

### Сетки
```css
/* Desktop */
.search-grid {
    grid-template-columns: 2fr 1fr 1fr 1fr 1fr auto;
}

/* Tablet */
@media (max-width: 1200px) {
    .search-grid {
        grid-template-columns: 1fr 1fr;
    }
}

/* Mobile */
@media (max-width: 768px) {
    .search-grid {
        grid-template-columns: 1fr;
    }
}
```

## 🎭 Анимации и переходы

### Основные переходы
```css
/* Глобальные переходы */
* {
    transition: color 0.3s ease, background-color 0.3s ease, border-color 0.3s ease;
}

/* Hover эффекты */
.article-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
}

.tag:hover {
    transform: translateY(-1px);
}
```

### Загрузочные анимации
```css
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.spinner {
    animation: spin 1s linear infinite;
}
```

## 🛠️ Реализация

### CSS переменные
Система основана на CSS-переменных для:
- Легкого переключения тем
- Консистентности цветов
- Простоты обслуживания

### JavaScript функции
- `toggleTheme()` - переключение темы
- `updateActiveFilters()` - управление фильтрами
- `setLoading()` - состояния загрузки

### Современные CSS функции
- CSS Grid для макетов
- Flexbox для выравнивания
- CSS-in-JS для динамических стилей
- Custom properties для переменных

## 🚀 Производительность

### Оптимизации
- Дебаунсинг поиска (500ms)
- Ленивая загрузка изображений
- Минимальные DOM манипуляции
- Кеширование темы в localStorage

### Размер бандла
- Inter font: ~15KB
- Bootstrap Icons: ~50KB
- Custom CSS: ~20KB
- JavaScript: ~25KB

## 📋 Чеклист соответствия

- ✅ Поддержка светлой и темной тем
- ✅ Современные UI-паттерны
- ✅ Адаптивный дизайн
- ✅ Доступность (ARIA)
- ✅ Плавные анимации
- ✅ Консистентная типографика
- ✅ Семантический HTML
- ✅ Оптимизированная производительность

## 🔮 Будущие улучшения

1. **Системные предпочтения темы**
   ```javascript
   const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
   ```

2. **Дополнительные темы**
   - Высококонтрастная тема
   - Кастомные цветовые схемы

3. **Микроанимации**
   - Плавные появления элементов
   - Параллакс эффекты

4. **PWA функции**
   - Оффлайн поддержка
   - Пуш-уведомления

---

*Дизайн-система MediaScope создана с учетом современных трендов UX/UI 2024-2025 годов и лучших практик веб-разработки.* 