#!/usr/bin/env python
"""
Скрипт для мониторинга прогресса анализа статей
"""

import os
import sys
import django
import time
from datetime import datetime

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Article


def monitor_analysis_progress():
    """Мониторит прогресс анализа статей."""
    
    print("📊 Мониторинг анализа статей")
    print("=" * 40)
    
    start_time = time.time()
    
    while True:
        # Получаем статистику
        total = Article.objects.count()
        analyzed = Article.objects.filter(is_analyzed=True).count()
        unanalyzed = total - analyzed
        progress = (analyzed / total * 100) if total > 0 else 0
        
        # Вычисляем скорость
        elapsed = time.time() - start_time
        if elapsed > 0 and analyzed > 0:
            rate = analyzed / elapsed * 60  # статей в минуту
            eta_minutes = unanalyzed / (rate / 60) if rate > 0 else 0
        else:
            rate = 0
            eta_minutes = 0
        
        # Выводим статистику
        current_time = datetime.now().strftime("%H:%M:%S")
        print(f"\r[{current_time}] 📈 {analyzed}/{total} ({progress:.1f}%) | "
              f"⏳ Осталось: {unanalyzed} | 🚀 Скорость: {rate:.1f}/мин | "
              f"⏱️ ETA: {eta_minutes:.0f}мин", end="", flush=True)
        
        # Если все проанализировано - завершаем
        if unanalyzed == 0:
            print(f"\n\n🎉 Анализ завершен! Все {total} статей проанализированы!")
            break
        
        time.sleep(5)  # Обновляем каждые 5 секунд


if __name__ == "__main__":
    try:
        monitor_analysis_progress()
    except KeyboardInterrupt:
        print("\n\n⏹️ Мониторинг остановлен пользователем")
    except Exception as e:
        print(f"\n\n❌ Ошибка: {e}") 