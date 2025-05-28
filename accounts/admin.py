from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    User, UserProfile, SubscriptionPlan, UserSubscription,
    UserFavoriteArticle, UserCustomSource, APIUsageLog
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админка для пользователей."""
    
    list_display = [
        'email', 'get_full_name', 'is_email_verified', 
        'is_active', 'is_staff', 'created_at'
    ]
    list_filter = [
        'is_active', 'is_staff', 'is_superuser', 
        'is_email_verified', 'created_at'
    ]
    search_fields = ['email', 'first_name', 'last_name', 'username']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Личная информация', {
            'fields': ('first_name', 'last_name', 'email', 'is_email_verified')
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Важные даты', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username
    get_full_name.short_description = 'Полное имя'


class UserProfileInline(admin.StackedInline):
    """Инлайн для профиля пользователя."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Админка для профилей пользователей."""
    
    list_display = [
        'user', 'language', 'theme', 'articles_read', 
        'email_notifications', 'last_activity'
    ]
    list_filter = [
        'language', 'theme', 'email_notifications', 
        'newsletter_subscription', 'created_at'
    ]
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'bio']
    readonly_fields = ['articles_read', 'last_activity', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'avatar', 'bio')
        }),
        ('Настройки интерфейса', {
            'fields': ('language', 'theme', 'timezone')
        }),
        ('Уведомления', {
            'fields': ('email_notifications', 'newsletter_subscription')
        }),
        ('Статистика', {
            'fields': ('articles_read', 'last_activity'),
            'classes': ('collapse',)
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    """Админка для планов подписки."""
    
    list_display = [
        'name', 'plan_type', 'price', 'billing_period', 
        'headless_parsing_enabled', 'is_active', 'is_popular'
    ]
    list_filter = [
        'plan_type', 'billing_period', 'headless_parsing_enabled',
        'advanced_analytics', 'api_access', 'is_active', 'is_popular'
    ]
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'plan_type', 'description')
        }),
        ('Цена и биллинг', {
            'fields': ('price', 'billing_period')
        }),
        ('Лимиты', {
            'fields': (
                'max_api_requests_per_day', 'max_saved_articles', 
                'max_custom_sources'
            )
        }),
        ('Премиум функции', {
            'fields': (
                'headless_parsing_enabled', 'advanced_analytics',
                'priority_support', 'api_access'
            )
        }),
        ('Настройки отображения', {
            'fields': ('is_active', 'is_popular')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    """Админка для подписок пользователей."""
    
    list_display = [
        'user', 'plan', 'status', 'start_date', 'end_date',
        'days_remaining_display', 'amount_paid', 'auto_renewal'
    ]
    list_filter = [
        'status', 'plan', 'auto_renewal', 'start_date', 'end_date'
    ]
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'plan__name', 'transaction_id'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Подписка', {
            'fields': ('user', 'plan', 'status')
        }),
        ('Период действия', {
            'fields': ('start_date', 'end_date', 'auto_renewal')
        }),
        ('Оплата', {
            'fields': ('amount_paid', 'payment_method', 'transaction_id')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def days_remaining_display(self, obj):
        if obj.is_active:
            days = obj.days_remaining
            if days > 7:
                color = 'green'
            elif days > 3:
                color = 'orange'
            else:
                color = 'red'
            return format_html(
                '<span style="color: {};">{} дней</span>',
                color, days
            )
        return format_html('<span style="color: red;">Неактивна</span>')
    days_remaining_display.short_description = 'Осталось дней'


@admin.register(UserFavoriteArticle)
class UserFavoriteArticleAdmin(admin.ModelAdmin):
    """Админка для избранных статей."""
    
    list_display = ['user', 'article_title', 'created_at']
    list_filter = ['created_at']
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'article__title'
    ]
    date_hierarchy = 'created_at'
    
    def article_title(self, obj):
        return obj.article.title[:50] + "..." if len(obj.article.title) > 50 else obj.article.title
    article_title.short_description = 'Статья'


@admin.register(UserCustomSource)
class UserCustomSourceAdmin(admin.ModelAdmin):
    """Админка для пользовательских источников."""
    
    list_display = [
        'name', 'user', 'status', 'requires_headless',
        'approved_by', 'created_at'
    ]
    list_filter = [
        'status', 'requires_headless', 'approved_at', 'created_at'
    ]
    search_fields = [
        'name', 'url', 'description',
        'user__email', 'user__first_name', 'user__last_name'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'name', 'url', 'description')
        }),
        ('Настройки парсинга', {
            'fields': ('requires_headless', 'parsing_frequency')
        }),
        ('Модерация', {
            'fields': ('status', 'admin_notes', 'approved_by', 'approved_at')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['approve_sources', 'reject_sources']
    
    def approve_sources(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='approved',
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'Одобрено {updated} источников.')
    approve_sources.short_description = 'Одобрить выбранные источники'
    
    def reject_sources(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'Отклонено {updated} источников.')
    reject_sources.short_description = 'Отклонить выбранные источники'


@admin.register(APIUsageLog)
class APIUsageLogAdmin(admin.ModelAdmin):
    """Админка для логов API."""
    
    list_display = [
        'user', 'method', 'endpoint', 'status_code',
        'response_time', 'created_at'
    ]
    list_filter = [
        'method', 'status_code', 'created_at'
    ]
    search_fields = [
        'user__email', 'endpoint', 'ip_address'
    ]
    date_hierarchy = 'created_at'
    readonly_fields = [
        'user', 'endpoint', 'method', 'status_code',
        'response_time', 'ip_address', 'user_agent', 'created_at'
    ]
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
