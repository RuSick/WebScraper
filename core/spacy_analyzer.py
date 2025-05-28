"""
Модуль для анализа текста с использованием spaCy.
Предоставляет улучшенный NLP-анализ с машинным обучением.
"""

import spacy
import logging
from typing import List, Tuple, Dict, Any, Optional
from collections import Counter
from django.conf import settings

logger = logging.getLogger(__name__)


class SpacyTextAnalyzer:
    """
    Анализатор текста на основе spaCy для определения тематики, тегов и локаций.
    
    Использует предобученные модели машинного обучения для:
    - Named Entity Recognition (NER)
    - Лемматизация и морфологический анализ
    - Part-of-Speech tagging
    - Векторные представления слов
    """
    
    def __init__(self, model_name: str = 'ru_core_news_sm'):
        """
        Инициализация анализатора.
        
        Args:
            model_name: Название spaCy модели для загрузки
        """
        self.model_name = model_name
        self.nlp = None
        self._load_model()
        
        # Словари тематик для гибридного подхода (fallback)
        self.topic_keywords = {
            'politics': [
                'политик', 'выборы', 'президент', 'министр', 'правительство', 
                'парламент', 'депутат', 'власть', 'оппозиция', 'партия',
                'голосование', 'референдум', 'законопроект', 'дума', 'совет',
                'мэр', 'губернатор', 'администрация', 'кандидат', 'кампания'
            ],
            'economics': [
                'экономика', 'бюджет', 'налог', 'ввп', 'инфляция', 'банк',
                'кредит', 'инвестиции', 'рынок', 'торговля', 'экспорт',
                'импорт', 'валюта', 'рубль', 'доллар', 'евро', 'цена',
                'стоимость', 'тариф', 'пошлина', 'санкции'
            ],
            'technology': [
                'технология', 'компьютер', 'интернет', 'программа', 'софт',
                'приложение', 'сайт', 'платформа', 'алгоритм', 'данные',
                'цифровой', 'искусственный интеллект', 'роботы', 'автоматизация',
                'стартап', 'it', 'разработка', 'программирование', 'код'
            ],
            'war': [
                'война', 'конфликт', 'военный', 'армия', 'солдат', 'боевые',
                'атака', 'операция', 'фронт', 'обстрел', 'ракета', 'танк',
                'авиация', 'флот', 'оружие', 'защита', 'наступление', 'оборона',
                'мир', 'перемирие', 'украина', 'россия', 'спецоперация'
            ],
            'science': [
                'исследование', 'ученые', 'открытие', 'эксперимент', 'наука',
                'научный', 'лаборатория', 'институт', 'университет', 'диссертация',
                'публикация', 'журнал', 'конференция', 'симпозиум', 'академия'
            ],
            'health': [
                'здоровье', 'медицина', 'врач', 'больница', 'лечение', 'болезнь',
                'вирус', 'вакцина', 'эпидемия', 'пандемия', 'коронавирус',
                'ковид', 'пациент', 'диагноз', 'терапия', 'операция'
            ],
            'sports': [
                'спорт', 'футбол', 'хоккей', 'баскетбол', 'теннис', 'бокс',
                'олимпиада', 'чемпионат', 'турнир', 'матч', 'игра', 'команда',
                'спортсмен', 'тренер', 'стадион', 'соревнование', 'победа'
            ],
            'business': [
                'бизнес', 'компания', 'корпорация', 'предприятие', 'фирма',
                'организация', 'директор', 'менеджер', 'сделка', 'контракт',
                'партнерство', 'слияние', 'поглощение', 'ipo', 'акции'
            ],
            'entertainment': [
                'кино', 'фильм', 'актер', 'режиссер', 'музыка', 'концерт',
                'альбом', 'песня', 'артист', 'театр', 'спектакль', 'шоу',
                'телевидение', 'сериал', 'премьера', 'фестиваль'
            ],
            'culture': [
                'культура', 'искусство', 'музей', 'выставка', 'картина',
                'художник', 'скульптура', 'галерея', 'литература', 'книга',
                'автор', 'писатель', 'поэт', 'библиотека', 'памятник'
            ]
        }
        
        # Стоп-слова для фильтрации
        self.stop_words = {
            'это', 'как', 'его', 'что', 'или', 'для', 'при', 'все', 'так',
            'был', 'есть', 'уже', 'еще', 'чем', 'где', 'кто', 'они', 'она',
            'и', 'в', 'на', 'с', 'по', 'к', 'о', 'от', 'до', 'за', 'под',
            'над', 'между', 'через', 'из', 'у', 'а', 'но', 'да', 'же', 'ли',
            'не', 'ни', 'бы', 'вы', 'мы', 'ты', 'он', 'то', 'тот', 'эта',
            'быть', 'мочь', 'стать', 'сказать', 'говорить', 'знать', 'видеть'
        }
    
    def _load_model(self):
        """Загружает spaCy модель с обработкой ошибок."""
        try:
            self.nlp = spacy.load(self.model_name)
            logger.info(f"spaCy модель '{self.model_name}' успешно загружена")
        except OSError as e:
            logger.error(f"Не удалось загрузить spaCy модель '{self.model_name}': {e}")
            logger.error("Убедитесь, что модель установлена: python -m spacy download ru_core_news_sm")
            raise
        except Exception as e:
            logger.error(f"Ошибка загрузки spaCy модели: {e}")
            raise
    
    def analyze_text(self, title: str, content: str = "", summary: str = "") -> Dict[str, Any]:
        """
        Полный анализ текста статьи с использованием spaCy.
        
        Args:
            title: Заголовок статьи
            content: Полный текст статьи  
            summary: Краткое содержание
            
        Returns:
            Dict с результатами анализа: topic, tags, locations, entities
        """
        if not self.nlp:
            logger.error("spaCy модель не загружена")
            return self._fallback_analysis(title, content, summary)
        
        try:
            # Объединяем весь доступный текст
            full_text = f"{title} {summary} {content}".strip()
            
            if not full_text:
                logger.warning("Пустой текст для анализа")
                return {'topic': 'other', 'tags': [], 'locations': [], 'entities': []}
            
            # Обрабатываем текст через spaCy
            doc = self.nlp(full_text)
            
            # Извлекаем различные типы информации
            topic = self._determine_topic_spacy(doc, full_text.lower())
            tags = self._extract_keywords_spacy(doc, title)
            locations = self._extract_locations_spacy(doc)
            entities = self._extract_entities_spacy(doc)
            
            logger.info(f"spaCy анализ завершен: тема={topic}, тегов={len(tags)}, "
                       f"локаций={len(locations)}, сущностей={len(entities)}")
            
            return {
                'topic': topic,
                'tags': tags,
                'locations': locations,
                'entities': entities
            }
            
        except Exception as e:
            logger.error(f"Ошибка spaCy анализа: {e}")
            logger.info("Переключаемся на fallback анализ")
            return self._fallback_analysis(title, content, summary)
    
    def _determine_topic_spacy(self, doc, text_lower: str) -> str:
        """
        Определяет тематику с использованием spaCy + словарный fallback.
        
        Использует комбинацию:
        1. Лемматизированные токены из spaCy
        2. Именованные сущности
        3. Словарный подход как fallback
        """
        topic_scores = {}
        
        # Получаем лемматизированные токены
        lemmas = [token.lemma_.lower() for token in doc 
                 if not token.is_stop and not token.is_punct and len(token.lemma_) > 2]
        
        # Получаем именованные сущности
        entities = [ent.text.lower() for ent in doc.ents]
        
        # Объединяем для анализа
        analysis_tokens = lemmas + entities
        
        # Подсчитываем совпадения с тематическими словарями
        for topic, keywords in self.topic_keywords.items():
            score = 0
            
            # Проверяем лемматизированные токены
            for token in analysis_tokens:
                for keyword in keywords:
                    if keyword in token or token in keyword:
                        score += 2  # Больший вес для точных совпадений
            
            # Дополнительная проверка по исходному тексту (fallback)
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            
            if score > 0:
                topic_scores[topic] = score
        
        if topic_scores:
            best_topic = max(topic_scores, key=topic_scores.get)
            logger.debug(f"Определена тематика: {best_topic} (счет: {topic_scores[best_topic]})")
            return best_topic
        
        return 'other'
    
    def _extract_keywords_spacy(self, doc, title: str) -> List[str]:
        """Извлекает ключевые слова используя spaCy лемматизацию."""
        keywords = set()
        
        # Получаем значимые токены
        significant_tokens = [
            token.lemma_.lower() for token in doc
            if (not token.is_stop and 
                not token.is_punct and 
                not token.is_space and
                len(token.lemma_) > 3 and
                token.pos_ in ['NOUN', 'PROPN', 'ADJ', 'VERB'] and
                token.lemma_.lower() not in self.stop_words)
        ]
        
        # Подсчитываем частоту
        token_freq = Counter(significant_tokens)
        
        # Берем наиболее частые
        for token, freq in token_freq.most_common(15):
            if freq > 1 or token in title.lower():  # Частые слова или из заголовка
                keywords.add(token)
        
        # Добавляем именованные сущности как ключевые слова
        for ent in doc.ents:
            if ent.label_ in ['PER', 'ORG', 'EVENT']:  # Персоны, организации, события
                clean_ent = ent.text.strip().lower()
                if len(clean_ent) > 2:
                    keywords.add(clean_ent)
        
        return list(keywords)[:15]
    
    def _extract_locations_spacy(self, doc) -> List[str]:
        """Извлекает географические названия используя spaCy NER."""
        locations = set()
        
        # Извлекаем локации через NER
        for ent in doc.ents:
            if ent.label_ in ['LOC', 'GPE']:  # Locations, Geopolitical entities
                clean_location = ent.text.strip()
                if len(clean_location) > 2:
                    locations.add(clean_location.title())
        
        return list(locations)[:10]
    
    def _extract_entities_spacy(self, doc) -> List[Dict[str, str]]:
        """Извлекает все именованные сущности."""
        entities = []
        
        for ent in doc.ents:
            entities.append({
                'text': ent.text.strip(),
                'label': ent.label_,
                'description': spacy.explain(ent.label_) or ent.label_
            })
        
        return entities[:20]  # Ограничиваем количество
    
    def _fallback_analysis(self, title: str, content: str, summary: str) -> Dict[str, Any]:
        """
        Fallback анализ без spaCy (использует словарный подход).
        Вызывается при ошибках spaCy или отсутствии модели.
        """
        logger.info("Используется fallback анализ (словарный подход)")
        
        # Импортируем старый анализатор
        from core.text_analyzer import TextAnalyzer
        
        old_analyzer = TextAnalyzer()
        result = old_analyzer.analyze_text(title, content, summary)
        
        # Добавляем пустое поле entities для совместимости
        result['entities'] = []
        
        return result


def analyze_article_content_spacy(article) -> Dict[str, Any]:
    """
    Функция для анализа конкретной статьи с использованием spaCy.
    
    Args:
        article: Экземпляр модели Article
        
    Returns:
        Dict с результатами анализа
    """
    analyzer = SpacyTextAnalyzer()
    
    try:
        result = analyzer.analyze_text(
            title=article.title,
            content=article.content,
            summary=article.summary
        )
        
        logger.info(f"spaCy анализ статьи '{article.title[:50]}...' завершен")
        return result
        
    except Exception as e:
        logger.error(f"Ошибка spaCy анализа статьи {article.id}: {e}")
        # Возвращаем базовый результат
        return {
            'topic': 'other',
            'tags': [],
            'locations': [],
            'entities': []
        } 