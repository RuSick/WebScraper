# 🚀 Быстрый запуск MediaScope

## Запуск из корневой папки проекта

### Все доступные команды:

```bash
# 🔥 Запуск фронтенда и бэкенда одновременно
npm start
# или
npm run dev

# 🎨 Только фронтенд (React)
npm run frontend

# 🐍 Только бэкенд (Django)
npm run backend

# 📦 Установка зависимостей фронтенда
npm run setup
# или
npm run install-frontend

# 🏗️ Сборка фронтенда для продакшена
npm run build-frontend

# 🧪 Тесты фронтенда
npm run test-frontend

# 🔍 Линтер фронтенда
npm run lint-frontend
```

### Быстрый старт:

1. **Первый запуск:**
   ```bash
   npm run setup  # Установка зависимостей фронтенда
   npm start      # Запуск всего проекта
   ```

2. **Обычный запуск:**
   ```bash
   npm start      # Фронтенд на :3000, бэкенд на :8000
   ```

3. **Раздельный запуск:**
   ```bash
   # В одном терминале
   npm run backend
   
   # В другом терминале  
   npm run frontend
   ```

### Порты:
- **Фронтенд (React):** http://localhost:3000
- **Бэкенд (Django):** http://localhost:8000
- **API:** http://localhost:8000/api/

### Остановка:
- `Ctrl+C` - остановит все процессы при использовании `npm start`
- Или остановите каждый процесс отдельно

---

**Примечание:** Убедитесь, что активирована виртуальная среда Python (`news-env`) перед запуском. 