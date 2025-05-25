from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Source, Article


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    """Админка для источников новостей."""
    
    list_display = [
        'name', 'type_badge', 'is_active_badge', 'articles_count', 
        'last_parsed_display', 'created_at'
    ]
    list_filter = ['type', 'is_active', 'created_at']
    search_fields = ['name', 'url', 'description']
    readonly_fields = ['created_at', 'updated_at', 'articles_count']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'url', 'type', 'is_active')
        }),
        ('Настройки парсинга', {
            'fields': ('description', 'update_frequency')
        }),
        ('Статистика', {
            'fields': ('articles_count', 'last_parsed'),
            'classes': ('collapse',)
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_sources', 'deactivate_sources']

    def type_badge(self, obj):
        """Цветной бейдж типа источника."""
        colors = {
            'rss': '#28a745',      # зеленый
            'html': '#007bff',     # синий
            'spa': '#ffc107',      # желтый
            'api': '#6f42c1',      # фиолетовый
            'tg': '#17a2b8',       # голубой
        }
        color = colors.get(obj.type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 3px; font-size: 12px;">{}</span>',
            color, obj.get_type_display()
        )
    type_badge.short_description = 'Тип'

    def is_active_badge(self, obj):
        """Бейдж активности источника."""
        if obj.is_active:
            return format_html(
                '<span style="color: #28a745;">✓ Активен</span>'
            )
        else:
            return format_html(
                '<span style="color: #dc3545;">✗ Неактивен</span>'
            )
    is_active_badge.short_description = 'Статус'

    def last_parsed_display(self, obj):
        """Отображение времени последнего парсинга."""
        if obj.last_parsed:
            now = timezone.now()
            diff = now - obj.last_parsed
            if diff.days > 0:
                return f"{diff.days} дн. назад"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} ч. назад"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} мин. назад"
            else:
                return "Только что"
        return "Никогда"
    last_parsed_display.short_description = 'Последний парсинг'

    def activate_sources(self, request, queryset):
        """Активировать выбранные источники."""
        count = queryset.update(is_active=True)
        self.message_user(request, f"Активировано {count} источников.")
    activate_sources.short_description = "Активировать выбранные источники"

    def deactivate_sources(self, request, queryset):
        """Деактивировать выбранные источники."""
        count = queryset.update(is_active=False)
        self.message_user(request, f"Деактивировано {count} источников.")
    deactivate_sources.short_description = "Деактивировать выбранные источники"


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Админка для статей."""
    
    list_display = [
        'title_short', 'source', 'topic_badge', 'tone_badge', 
        'published_at', 'read_count', 'is_featured_badge'
    ]
    list_filter = [
        'topic', 'tone', 'is_featured', 'is_active', 
        'source', 'published_at', 'created_at'
    ]
    search_fields = ['title', 'content', 'summary']
    readonly_fields = ['created_at', 'updated_at', 'read_count']
    date_hierarchy = 'published_at'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'url', 'source', 'published_at')
        }),
        ('Контент', {
            'fields': ('summary', 'content'),
        }),
        ('Категоризация', {
            'fields': ('topic', 'tone', 'is_featured', 'is_active')
        }),
        ('Статистика', {
            'fields': ('read_count',),
            'classes': ('collapse',)
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_featured', 'unmark_as_featured', 'activate_articles', 'deactivate_articles']

    def title_short(self, obj):
        """Сокращенный заголовок."""
        return obj.title[:60] + "..." if len(obj.title) > 60 else obj.title
    title_short.short_description = 'Заголовок'

    def topic_badge(self, obj):
        """Цветной бейдж темы."""
        colors = {
            'politics': '#dc3545',      # красный
            'business': '#28a745',      # зеленый
            'technology': '#007bff',    # синий
            'sports': '#fd7e14',        # оранжевый
            'entertainment': '#e83e8c', # розовый
            'science': '#6f42c1',       # фиолетовый
            'health': '#20c997',        # бирюзовый
            'world': '#ffc107',         # желтый
            'society': '#6c757d',       # серый
            'culture': '#17a2b8',       # голубой
            'other': '#343a40',         # темно-серый
        }
        color = colors.get(obj.topic, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_topic_display()
        )
    topic_badge.short_description = 'Тема'

    def tone_badge(self, obj):
        """Бейдж тональности."""
        colors = {
            'positive': '#28a745',   # зеленый
            'neutral': '#6c757d',    # серый
            'negative': '#dc3545',   # красный
        }
        color = colors.get(obj.tone, '#6c757d')
        icons = {
            'positive': '😊',
            'neutral': '😐',
            'negative': '😞',
        }
        icon = icons.get(obj.tone, '😐')
        return format_html(
            '<span style="color: {};">{} {}</span>',
            color, icon, obj.get_tone_display()
        )
    tone_badge.short_description = 'Тональность'

    def is_featured_badge(self, obj):
        """Бейдж рекомендуемой статьи."""
        if obj.is_featured:
            return format_html('<span style="color: #ffc107;">⭐ Рекомендуемая</span>')
        return ""
    is_featured_badge.short_description = 'Рекомендуемая'

    def mark_as_featured(self, request, queryset):
        """Отметить как рекомендуемые."""
        count = queryset.update(is_featured=True)
        self.message_user(request, f"Отмечено как рекомендуемые {count} статей.")
    mark_as_featured.short_description = "Отметить как рекомендуемые"

    def unmark_as_featured(self, request, queryset):
        """Убрать из рекомендуемых."""
        count = queryset.update(is_featured=False)
        self.message_user(request, f"Убрано из рекомендуемых {count} статей.")
    unmark_as_featured.short_description = "Убрать из рекомендуемых"

    def activate_articles(self, request, queryset):
        """Активировать статьи."""
        count = queryset.update(is_active=True)
        self.message_user(request, f"Активировано {count} статей.")
    activate_articles.short_description = "Активировать выбранные статьи"

    def deactivate_articles(self, request, queryset):
        """Деактивировать статьи."""
        count = queryset.update(is_active=False)
        self.message_user(request, f"Деактивировано {count} статей.")
    deactivate_articles.short_description = "Деактивировать выбранные статьи"


# Кастомизация заголовков админки
admin.site.site_header = "MediaScope - Админ-панель"
admin.site.site_title = "MediaScope"
admin.site.index_title = "Управление новостной платформой"
