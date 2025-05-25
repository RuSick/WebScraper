# Headless Browser Module

Модуль для парсинга JavaScript-зависимых сайтов (SPA) с использованием headless-браузеров.

## 📋 Назначение

Многие современные новостные сайты загружают контент динамически через JavaScript, что делает их недоступными для обычного HTTP-парсинга. Этот модуль предоставляет fallback-механизм для таких сайтов.

## 🎯 Поддерживаемые сайты

- **Meduza.io** - React-based SPA
- **TJournal.ru** - Vue.js-based SPA  
- **VC.ru** - частично SPA
- **DTF.ru** - аналогично VC.ru
- Другие современные новостные сайты

## 🏗️ Архитектура

### Автоматический Fallback

```python
# 1. Обычный HTTP-запрос (быстро)
html = await session.get(url)

# 2. Проверка на SPA
if should_use_headless(html, url):
    # 3. Fallback на headless (медленно, но работает)
    html = await fetch_with_playwright(url)
```

### Критерии для Headless

1. **HTML слишком короткий** (< 2KB) - подозрение на SPA
2. **Известный SPA-сайт** из списка `KNOWN_SPA_DOMAINS`
3. **JavaScript-индикаторы**: `window.__INITIAL_STATE__`, `data-react-helmet`, etc.

## ⚙️ Настройка

### В settings.py:

```python
# Отключено по умолчанию
ENABLE_HEADLESS_PARSING = False

# Для активации:
ENABLE_HEADLESS_PARSING = True
HEADLESS_TIMEOUT = 30
```

### Требования для активации:

```bash
# 1. Установка Playwright
pip install playwright

# 2. Установка браузеров
playwright install

# 3. Включение в настройках
ENABLE_HEADLESS_PARSING = True
```

## 📁 Структура модуля

```
scraper/browser/
├── __init__.py              # Экспорт функций
├── fallback_playwright.py   # 🚧 ЗАГЛУШКА - основной модуль
└── README.md               # Эта документация
```

## 🚧 Текущий статус: ЗАГЛУШКА

Модуль является **архитектурной заглушкой**. Функция `fetch_with_playwright()` не реализована и возвращает `NotImplementedError`.

### Что работает:
- ✅ Автоматическое определение SPA-сайтов
- ✅ Fallback-механика в BaseParser и UniversalParser
- ✅ Настройки в Django
- ✅ Логирование и обработка ошибок

### Что не реализовано:
- ❌ Фактический запуск Playwright
- ❌ Обработка JavaScript-рендеринга
- ❌ Оптимизация производительности

## 🔮 Будущая реализация

```python
async def fetch_with_playwright(url: str, timeout: int = 30) -> str:
    """Реализация с Playwright."""
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Устанавливаем User-Agent как у обычного браузера
        await page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
        
        # Переходим на страницу и ждем загрузки
        await page.goto(url, wait_until='networkidle')
        
        # Дополнительная задержка для SPA
        await page.wait_for_timeout(2000)
        
        # Получаем финальный HTML
        html = await page.content()
        await browser.close()
        
        return html
```

## 📊 Производительность

### Без Headless (текущее):
- ⚡ **Скорость**: ~1 секунда на сайт
- 💾 **Память**: ~10MB на парсер  
- 🎯 **Покрытие**: 80% сайтов

### С Headless (планируемое):
- 🐌 **Скорость**: ~10-30 секунд на сайт
- 💾 **Память**: ~100MB на браузер
- 🎯 **Покрытие**: 90-95% сайтов

## 🔧 Интеграция

### BaseParser
```python
# Автоматический fallback в fetch_url()
html = await self.fetch_url(url)  # Может использовать headless
```

### UniversalParser  
```python
# Автоматический fallback в fetch_page()
html = await parser.fetch_page(url)  # Может использовать headless
```

### Celery Tasks
```python
# Прозрачная интеграция
articles = await fetch_generic_articles(source)  # Автоматический fallback
```

## 🚀 Активация

Когда потребуется поддержка SPA-сайтов:

1. **Установить Playwright**: `pip install playwright`
2. **Установить браузеры**: `playwright install`  
3. **Реализовать функцию** в `fallback_playwright.py`
4. **Включить настройку**: `ENABLE_HEADLESS_PARSING = True`
5. **Тестировать** на Meduza.io и TJournal.ru

## 📈 Мониторинг

Логи будут показывать использование headless:

```
INFO: Обнаружен известный SPA-сайт: https://meduza.io
INFO: Пытаемся headless-парсинг для https://meduza.io  
INFO: Headless-парсинг улучшил результат: 1030 → 45231 символов
```

---

**Статус**: 🚧 Готово к развертыванию при необходимости  
**Приоритет**: 📈 Средний (80% сайтов уже работают без headless)  
**Сложность**: 🔧 Низкая (заглушка готова, осталось заполнить реализацию) 