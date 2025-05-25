#!/usr/bin/env python
"""
Скрипт для добавления IT-источников в MediaScope.

Добавляет русскоязычные и англоязычные технологические источники
с автоматическим определением типа парсинга.
"""

import os
import sys
import django
from urllib.parse import urlparse

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Source


# 🇷🇺 Русскоязычные IT-источники
RUSSIAN_IT_SOURCES = [
    {
        'name': 'Habr - Новости',
        'url': 'https://habr.com/ru/news/',
        'type': 'html',
        'description': 'Новости IT-индустрии от сообщества разработчиков',
        'update_frequency': 30,
    },
    {
        'name': 'VC.ru - Технологии',
        'url': 'https://vc.ru/tech',
        'type': 'spa',  # SPA с динамической загрузкой
        'description': 'Технологические новости и аналитика от VC.ru',
        'update_frequency': 60,
    },
    {
        'name': 'CNews',
        'url': 'https://cnews.ru/news/',
        'type': 'html',
        'description': 'Деловые новости IT-рынка России',
        'update_frequency': 45,
    },
    {
        'name': '3DNews',
        'url': 'https://3dnews.ru/news',
        'type': 'html',
        'description': 'Новости компьютерного железа и технологий',
        'update_frequency': 60,
    },
    {
        'name': 'iXBT',
        'url': 'https://ixbt.com/news/',
        'type': 'html',
        'description': 'Новости IT, обзоры техники и технологий',
        'update_frequency': 60,
    },
    {
        'name': 'Tproger',
        'url': 'https://tproger.ru/news',
        'type': 'html',
        'description': 'Новости программирования и разработки',
        'update_frequency': 120,
    },
    {
        'name': 'РосКомСвобода',
        'url': 'https://roskomsvoboda.org/news/',
        'type': 'html',
        'description': 'Новости цифровых прав и интернет-свободы',
        'update_frequency': 180,
    },
    {
        'name': 'Xakep',
        'url': 'https://xakep.ru/news/',
        'type': 'html',
        'description': 'Новости информационной безопасности',
        'update_frequency': 120,
    },
    {
        'name': 'SecurityLab',
        'url': 'https://www.securitylab.ru/news/',
        'type': 'html',
        'description': 'Новости кибербезопасности и защиты информации',
        'update_frequency': 120,
    },
    {
        'name': 'N+1',
        'url': 'https://nplus1.ru/news',
        'type': 'html',
        'description': 'Научно-популярные новости и технологии',
        'update_frequency': 180,
    },
    {
        'name': 'Neuronus',
        'url': 'https://neuronus.com/news',
        'type': 'html',
        'description': 'Новости нейротехнологий и искусственного интеллекта',
        'update_frequency': 240,
    },
    {
        'name': 'RB.ru',
        'url': 'https://rb.ru/news/',
        'type': 'html',
        'description': 'Новости российского бизнеса и технологий',
        'update_frequency': 120,
    },
    {
        'name': 'RusBase',
        'url': 'https://rusbase.ru/news/',
        'type': 'html',
        'description': 'Новости стартапов и технологического бизнеса',
        'update_frequency': 120,
    },
]

# 🌍 Англоязычные IT-источники
ENGLISH_IT_SOURCES = [
    {
        'name': 'TechCrunch',
        'url': 'https://techcrunch.com/',
        'type': 'spa',  # Сложная SPA структура
        'description': 'Leading technology media property, dedicated to obsessively profiling startups',
        'update_frequency': 30,
    },
    {
        'name': 'The Next Web',
        'url': 'https://thenextweb.com/news/',
        'type': 'spa',  # React-based SPA
        'description': 'International technology news, business & culture',
        'update_frequency': 60,
    },
    {
        'name': 'The Verge - Tech',
        'url': 'https://www.theverge.com/tech',
        'type': 'spa',  # Vox Media SPA
        'description': 'Technology news and reviews from The Verge',
        'update_frequency': 45,
    },
    {
        'name': 'Wired - Tech',
        'url': 'https://wired.com/category/tech',
        'type': 'html',
        'description': 'Technology news and analysis from Wired Magazine',
        'update_frequency': 60,
    },
    {
        'name': 'Ars Technica - IT',
        'url': 'https://arstechnica.com/information-technology/',
        'type': 'html',
        'description': 'In-depth technology news and analysis',
        'update_frequency': 90,
    },
    {
        'name': 'VentureBeat - AI',
        'url': 'https://venturebeat.com/category/ai/',
        'type': 'spa',  # WordPress + React components
        'description': 'AI and machine learning news from VentureBeat',
        'update_frequency': 120,
    },
    {
        'name': 'IEEE Spectrum - AI',
        'url': 'https://spectrum.ieee.org/artificial-intelligence',
        'type': 'html',
        'description': 'IEEE Spectrum artificial intelligence coverage',
        'update_frequency': 180,
    },
    {
        'name': 'Synced Review',
        'url': 'https://syncedreview.com/',
        'type': 'html',
        'description': 'AI research news and analysis',
        'update_frequency': 240,
    },
    {
        'name': 'Hugging Face Blog',
        'url': 'https://huggingface.co/blog',
        'type': 'spa',  # Next.js application
        'description': 'Machine learning and NLP research blog',
        'update_frequency': 360,
    },
    {
        'name': 'BleepingComputer',
        'url': 'https://www.bleepingcomputer.com/',
        'type': 'html',
        'description': 'Computer help and cybersecurity news',
        'update_frequency': 60,
    },
    {
        'name': 'CyberScoop',
        'url': 'https://www.cyberscoop.com/',
        'type': 'html',
        'description': 'Cybersecurity news and analysis',
        'update_frequency': 120,
    },
    {
        'name': 'Threatpost',
        'url': 'https://threatpost.com/',
        'type': 'html',
        'description': 'Cybersecurity news and threat intelligence',
        'update_frequency': 120,
    },
    {
        'name': 'Dev.to',
        'url': 'https://dev.to',
        'type': 'spa',  # Ruby on Rails + Preact
        'description': 'Community of software developers',
        'update_frequency': 180,
    },
    {
        'name': 'Python Insider',
        'url': 'https://pythoninsider.blogspot.com',
        'type': 'html',
        'description': 'Official Python development news',
        'update_frequency': 720,  # Обновляется редко
    },
    {
        'name': 'Go Blog',
        'url': 'https://go.dev/blog',
        'type': 'html',
        'description': 'Official Go programming language blog',
        'update_frequency': 720,
    },
    {
        'name': 'Node.js Blog',
        'url': 'https://nodejs.org/en/blog',
        'type': 'html',
        'description': 'Official Node.js news and updates',
        'update_frequency': 720,
    },
    {
        'name': 'React Blog',
        'url': 'https://reactjs.org/blog',
        'type': 'html',
        'description': 'Official React library news and updates',
        'update_frequency': 720,
    },
]


def add_sources(sources_list, category_name):
    """Добавляет источники в базу данных."""
    print(f"\n📰 Добавление {category_name} источников...")
    
    added_count = 0
    updated_count = 0
    skipped_count = 0
    
    for source_data in sources_list:
        try:
            # Проверяем, существует ли источник
            source, created = Source.objects.get_or_create(
                url=source_data['url'],
                defaults=source_data
            )
            
            if created:
                print(f"✅ Добавлен: {source.name}")
                added_count += 1
            else:
                # Обновляем существующий источник
                for key, value in source_data.items():
                    if key != 'url':  # URL не обновляем
                        setattr(source, key, value)
                source.save()
                print(f"🔄 Обновлен: {source.name}")
                updated_count += 1
                
        except Exception as e:
            print(f"❌ Ошибка при добавлении {source_data['name']}: {e}")
            skipped_count += 1
    
    print(f"\n📊 {category_name} - Итого:")
    print(f"   ✅ Добавлено: {added_count}")
    print(f"   🔄 Обновлено: {updated_count}")
    print(f"   ❌ Пропущено: {skipped_count}")
    
    return added_count, updated_count, skipped_count


def show_parsing_notes():
    """Показывает заметки о парсинге различных типов источников."""
    print("\n" + "="*60)
    print("📝 ЗАМЕТКИ О ПАРСИНГЕ ИСТОЧНИКОВ")
    print("="*60)
    
    print("\n🟢 HTML источники (готовы к парсингу):")
    html_sources = [s for s in RUSSIAN_IT_SOURCES + ENGLISH_IT_SOURCES if s['type'] == 'html']
    for source in html_sources:
        print(f"   • {source['name']}")
    
    print(f"\n🟡 SPA источники (требуют headless парсер):")
    spa_sources = [s for s in RUSSIAN_IT_SOURCES + ENGLISH_IT_SOURCES if s['type'] == 'spa']
    for source in spa_sources:
        print(f"   • {source['name']} - {source['url']}")
    
    print("\n💡 Рекомендации для SPA источников:")
    print("   1. Используйте Playwright или Selenium для рендеринга JavaScript")
    print("   2. Добавьте задержки для загрузки динамического контента")
    print("   3. Рассмотрите возможность использования API, если доступно")
    print("   4. Настройте User-Agent для избежания блокировок")
    
    print("\n🔧 Следующие шаги:")
    print("   1. Создать специализированные парсеры для каждого типа источника")
    print("   2. Настроить расписание парсинга в зависимости от частоты обновления")
    print("   3. Добавить мониторинг успешности парсинга")
    print("   4. Реализовать обработку ошибок и повторные попытки")


def main():
    """Основная функция скрипта."""
    print("🚀 Добавление IT-источников в MediaScope")
    print("="*50)
    
    # Показываем текущее количество источников
    current_count = Source.objects.count()
    print(f"📊 Текущее количество источников: {current_count}")
    
    # Добавляем русскоязычные источники
    ru_added, ru_updated, ru_skipped = add_sources(RUSSIAN_IT_SOURCES, "русскоязычных")
    
    # Добавляем англоязычные источники
    en_added, en_updated, en_skipped = add_sources(ENGLISH_IT_SOURCES, "англоязычных")
    
    # Показываем общую статистику
    total_added = ru_added + en_added
    total_updated = ru_updated + en_updated
    total_skipped = ru_skipped + en_skipped
    new_count = Source.objects.count()
    
    print("\n" + "="*50)
    print("📈 ОБЩАЯ СТАТИСТИКА")
    print("="*50)
    print(f"📊 Источников было: {current_count}")
    print(f"📊 Источников стало: {new_count}")
    print(f"✅ Всего добавлено: {total_added}")
    print(f"🔄 Всего обновлено: {total_updated}")
    print(f"❌ Всего пропущено: {total_skipped}")
    
    # Показываем заметки о парсинге
    show_parsing_notes()
    
    print(f"\n🎉 Готово! Добавлено {total_added} новых IT-источников")


if __name__ == '__main__':
    main() 