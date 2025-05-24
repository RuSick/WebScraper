
from django.db import models


class Source(models.Model):
    TYPE_CHOICES = [
        ('rss', 'RSS'),
        ('html', 'HTML'),
        ('api', 'API'),
        ('tg', 'Telegram'),
    ]

    name = models.CharField(max_length=255)
    url = models.URLField(unique=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    TONE_CHOICES = [
        ('positive', 'Позитивная'),
        ('neutral', 'Нейтральная'),
        ('negative', 'Негативная'),
    ]

    title = models.CharField(max_length=500)
    content = models.TextField()
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='articles')
    url = models.URLField(unique=True)
    published_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    tone = models.CharField(max_length=10, choices=TONE_CHOICES, default='neutral')
    topic = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.title[:50]} ({self.source.name})"
