from django.db import models
from django.core.validators import URLValidator
from django.contrib.postgres.fields import ArrayField


class Source(models.Model):
    """Модель источника новостей."""
    
    TYPE_CHOICES = [
        ('rss', 'RSS'),
        ('html', 'HTML'),
        ('spa', 'SPA (JavaScript)'),
        ('api', 'API'),
        ('tg', 'Telegram'),
    ]

    name = models.CharField(
        max_length=255, 
        verbose_name="Название",
        help_text="Название источника новостей"
    )
    url = models.URLField(
        unique=True,
        verbose_name="URL",
        help_text="Ссылка на источник"
    )
    type = models.CharField(
        max_length=10, 
        choices=TYPE_CHOICES,
        verbose_name="Тип источника",
        help_text="Способ парсинга источника"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
        help_text="Включен ли парсинг этого источника"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
        help_text="Краткое описание источника"
    )
    update_frequency = models.PositiveIntegerField(
        default=60,
        verbose_name="Частота обновления (мин)",
        help_text="Как часто парсить источник в минутах"
    )
    last_parsed = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Последний парсинг",
        help_text="Когда последний раз парсился источник"
    )
    articles_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Количество статей",
        help_text="Общее количество статей с этого источника"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

    class Meta:
        verbose_name = "Источник новостей"
        verbose_name_plural = "Источники новостей"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class Article(models.Model):
    """Модель новостной статьи."""

    TOPIC_CHOICES = [
        ('politics', 'Политика'),
        ('economics', 'Экономика'),
        ('technology', 'Технологии'),
        ('science', 'Наука'),
        ('sports', 'Спорт'),
        ('culture', 'Культура'),
        ('health', 'Здоровье'),
        ('education', 'Образование'),
        ('environment', 'Экология'),
        ('society', 'Общество'),
        ('war', 'Война и конфликты'),
        ('international', 'Международные отношения'),
        ('business', 'Бизнес'),
        ('finance', 'Финансы'),
        ('entertainment', 'Развлечения'),
        ('travel', 'Путешествия'),
        ('food', 'Еда'),
        ('fashion', 'Мода'),
        ('auto', 'Автомобили'),
        ('real_estate', 'Недвижимость'),
        ('other', 'Прочее'),
    ]

    title = models.CharField(
        max_length=500,
        verbose_name="Заголовок",
        help_text="Заголовок статьи"
    )
    content = models.TextField(
        blank=True,
        verbose_name="Контент",
        help_text="Полный текст статьи"
    )
    summary = models.TextField(
        blank=True,
        verbose_name="Краткое содержание",
        help_text="Краткое содержание статьи (автоматически или из источника)"
    )
    source = models.ForeignKey(
        Source, 
        on_delete=models.CASCADE, 
        related_name='articles',
        verbose_name="Источник"
    )
    url = models.URLField(
        unique=True,
        verbose_name="Ссылка",
        help_text="Оригинальная ссылка на статью"
    )
    published_at = models.DateTimeField(
        verbose_name="Дата публикации",
        help_text="Когда статья была опубликована"
    )
    
    # Аналитические поля
    topic = models.CharField(
        max_length=20,
        choices=TOPIC_CHOICES,
        default='other',
        verbose_name="Тема",
        help_text="Основная тема статьи (определяется автоматически)"
    )
    tags = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True,
        verbose_name="Теги",
        help_text="Ключевые слова и фразы (определяются автоматически)"
    )
    locations = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True,
        verbose_name="Локации",
        help_text="Географические упоминания (определяются автоматически)"
    )
    
    # Флаги обработки
    is_analyzed = models.BooleanField(
        default=False,
        verbose_name="Проанализирована",
        help_text="Был ли проведен автоматический анализ текста"
    )
    
    # Технические поля
    read_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Количество просмотров"
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name="Рекомендуемая",
        help_text="Отображать в рекомендуемых статьях"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна",
        help_text="Отображать ли статью пользователям"
    )
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлена")

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['published_at']),
            models.Index(fields=['topic']),
            models.Index(fields=['source']),
            models.Index(fields=['is_analyzed']),
        ]

    def __str__(self):
        return f"{self.title[:50]}... ({self.source.name})"

    @property
    def short_content(self):
        """Краткое содержание для превью."""
        if self.summary:
            return self.summary
        elif self.content:
            return self.content[:200] + "..." if len(self.content) > 200 else self.content
        return ""
