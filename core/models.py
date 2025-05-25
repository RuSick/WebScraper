from django.db import models
from django.core.validators import URLValidator


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
    
    TONE_CHOICES = [
        ('positive', 'Позитивная'),
        ('neutral', 'Нейтральная'),
        ('negative', 'Негативная'),
    ]

    TOPIC_CHOICES = [
        ('politics', 'Политика'),
        ('business', 'Бизнес'),
        ('technology', 'Технологии'),
        ('sports', 'Спорт'),
        ('entertainment', 'Развлечения'),
        ('science', 'Наука'),
        ('health', 'Здоровье'),
        ('world', 'Мир'),
        ('society', 'Общество'),
        ('culture', 'Культура'),
        ('other', 'Другое'),
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
    tone = models.CharField(
        max_length=10, 
        choices=TONE_CHOICES, 
        default='neutral',
        verbose_name="Тональность",
        help_text="Эмоциональная тональность статьи"
    )
    topic = models.CharField(
        max_length=20,
        choices=TOPIC_CHOICES,
        default='other',
        verbose_name="Тема",
        help_text="Основная тема статьи"
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
            models.Index(fields=['tone']),
            models.Index(fields=['source']),
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
