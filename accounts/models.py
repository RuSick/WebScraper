from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


class User(AbstractUser):
    """Расширенная модель пользователя."""
    
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        help_text="Email адрес пользователя"
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name="Имя"
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name="Фамилия"
    )
    is_email_verified = models.BooleanField(
        default=False,
        verbose_name="Email подтвержден",
        help_text="Подтвердил ли пользователь свой email"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        """Возвращает полное имя пользователя."""
        return f"{self.first_name} {self.last_name}".strip()


class UserProfile(models.Model):
    """Профиль пользователя с дополнительной информацией."""
    
    LANGUAGE_CHOICES = [
        ('ru', 'Русский'),
        ('en', 'English'),
    ]
    
    THEME_CHOICES = [
        ('light', 'Светлая'),
        ('dark', 'Темная'),
        ('auto', 'Автоматически'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="Пользователь"
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name="Аватар"
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        verbose_name="О себе",
        help_text="Краткая информация о пользователе"
    )
    language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default='ru',
        verbose_name="Язык интерфейса"
    )
    theme = models.CharField(
        max_length=5,
        choices=THEME_CHOICES,
        default='auto',
        verbose_name="Тема оформления"
    )
    timezone = models.CharField(
        max_length=50,
        default='Europe/Minsk',
        verbose_name="Часовой пояс"
    )
    
    # Настройки уведомлений
    email_notifications = models.BooleanField(
        default=True,
        verbose_name="Email уведомления",
        help_text="Получать уведомления на email"
    )
    newsletter_subscription = models.BooleanField(
        default=False,
        verbose_name="Подписка на рассылку",
        help_text="Получать еженедельную рассылку с топ новостями"
    )
    
    # Статистика
    articles_read = models.PositiveIntegerField(
        default=0,
        verbose_name="Прочитано статей"
    )
    last_activity = models.DateTimeField(
        auto_now=True,
        verbose_name="Последняя активность"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"Профиль {self.user.get_full_name()}"


class SubscriptionPlan(models.Model):
    """Планы подписки для различных функций."""
    
    PLAN_TYPE_CHOICES = [
        ('free', 'Бесплатный'),
        ('basic', 'Базовый'),
        ('premium', 'Премиум'),
        ('enterprise', 'Корпоративный'),
    ]
    
    BILLING_PERIOD_CHOICES = [
        ('monthly', 'Ежемесячно'),
        ('yearly', 'Ежегодно'),
        ('lifetime', 'Пожизненно'),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name="Название плана"
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="Slug",
        help_text="Уникальный идентификатор плана"
    )
    plan_type = models.CharField(
        max_length=20,
        choices=PLAN_TYPE_CHOICES,
        verbose_name="Тип плана"
    )
    description = models.TextField(
        verbose_name="Описание",
        help_text="Подробное описание возможностей плана"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Цена"
    )
    billing_period = models.CharField(
        max_length=20,
        choices=BILLING_PERIOD_CHOICES,
        default='monthly',
        verbose_name="Период оплаты"
    )
    
    # Лимиты и возможности
    max_api_requests_per_day = models.PositiveIntegerField(
        default=100,
        verbose_name="Лимит API запросов в день"
    )
    max_saved_articles = models.PositiveIntegerField(
        default=50,
        verbose_name="Лимит сохраненных статей"
    )
    max_custom_sources = models.PositiveIntegerField(
        default=0,
        verbose_name="Лимит пользовательских источников"
    )
    
    # Премиум функции
    headless_parsing_enabled = models.BooleanField(
        default=False,
        verbose_name="Headless парсинг",
        help_text="Доступ к парсингу SPA сайтов через Playwright"
    )
    advanced_analytics = models.BooleanField(
        default=False,
        verbose_name="Расширенная аналитика",
        help_text="Доступ к детальной аналитике и экспорту данных"
    )
    priority_support = models.BooleanField(
        default=False,
        verbose_name="Приоритетная поддержка"
    )
    api_access = models.BooleanField(
        default=False,
        verbose_name="API доступ",
        help_text="Доступ к REST API для интеграций"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
        help_text="Доступен ли план для покупки"
    )
    is_popular = models.BooleanField(
        default=False,
        verbose_name="Популярный",
        help_text="Отображать как рекомендуемый план"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

    class Meta:
        verbose_name = "План подписки"
        verbose_name_plural = "Планы подписки"
        ordering = ['price']

    def __str__(self):
        return f"{self.name} ({self.get_billing_period_display()})"


class UserSubscription(models.Model):
    """Подписка пользователя на определенный план."""
    
    STATUS_CHOICES = [
        ('active', 'Активна'),
        ('expired', 'Истекла'),
        ('cancelled', 'Отменена'),
        ('pending', 'Ожидает оплаты'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name="Пользователь"
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name="План подписки"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус"
    )
    
    # Даты
    start_date = models.DateTimeField(
        verbose_name="Дата начала"
    )
    end_date = models.DateTimeField(
        verbose_name="Дата окончания"
    )
    
    # Оплата
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма оплаты"
    )
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Способ оплаты"
    )
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="ID транзакции"
    )
    
    # Автопродление
    auto_renewal = models.BooleanField(
        default=False,
        verbose_name="Автопродление"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлена")

    class Meta:
        verbose_name = "Подписка пользователя"
        verbose_name_plural = "Подписки пользователей"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['end_date']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.plan.name}"

    @property
    def is_active(self):
        """Проверяет, активна ли подписка."""
        return (
            self.status == 'active' and 
            self.end_date > timezone.now()
        )

    @property
    def days_remaining(self):
        """Количество дней до окончания подписки."""
        if self.is_active:
            return (self.end_date - timezone.now()).days
        return 0

    def extend_subscription(self, days=30):
        """Продлевает подписку на указанное количество дней."""
        if self.is_active:
            self.end_date += timedelta(days=days)
        else:
            self.start_date = timezone.now()
            self.end_date = timezone.now() + timedelta(days=days)
            self.status = 'active'
        self.save()


class UserFavoriteArticle(models.Model):
    """Избранные статьи пользователя."""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_articles',
        verbose_name="Пользователь"
    )
    article = models.ForeignKey(
        'core.Article',
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name="Статья"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Заметки",
        help_text="Личные заметки пользователя к статье"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлена")

    class Meta:
        verbose_name = "Избранная статья"
        verbose_name_plural = "Избранные статьи"
        unique_together = ['user', 'article']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.article.title[:50]}"


class UserCustomSource(models.Model):
    """Пользовательские источники новостей."""
    
    STATUS_CHOICES = [
        ('pending', 'Ожидает проверки'),
        ('approved', 'Одобрен'),
        ('rejected', 'Отклонен'),
        ('active', 'Активен'),
        ('inactive', 'Неактивен'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='custom_sources',
        verbose_name="Пользователь"
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Название источника"
    )
    url = models.URLField(
        verbose_name="URL источника"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус"
    )
    
    # Настройки парсинга
    requires_headless = models.BooleanField(
        default=False,
        verbose_name="Требует headless парсинг",
        help_text="Нужен ли Playwright для парсинга этого источника"
    )
    parsing_frequency = models.PositiveIntegerField(
        default=60,
        verbose_name="Частота парсинга (мин)"
    )
    
    # Модерация
    admin_notes = models.TextField(
        blank=True,
        verbose_name="Заметки администратора"
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_sources',
        verbose_name="Одобрен администратором"
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата одобрения"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

    class Meta:
        verbose_name = "Пользовательский источник"
        verbose_name_plural = "Пользовательские источники"
        unique_together = ['user', 'url']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.user.get_full_name()})"


class APIUsageLog(models.Model):
    """Лог использования API пользователями."""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='api_usage',
        verbose_name="Пользователь"
    )
    endpoint = models.CharField(
        max_length=200,
        verbose_name="Эндпоинт"
    )
    method = models.CharField(
        max_length=10,
        verbose_name="HTTP метод"
    )
    status_code = models.PositiveIntegerField(
        verbose_name="Код ответа"
    )
    response_time = models.FloatField(
        verbose_name="Время ответа (сек)"
    )
    ip_address = models.GenericIPAddressField(
        verbose_name="IP адрес"
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name="User Agent"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время запроса")

    class Meta:
        verbose_name = "Лог API"
        verbose_name_plural = "Логи API"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.method} {self.endpoint}"
