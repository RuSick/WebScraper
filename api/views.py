from rest_framework import generics, filters, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from collections import Counter
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from core.models import Source, Article
from .serializers import (
    SourceListSerializer, SourceDetailSerializer, SourceCreateUpdateSerializer,
    ArticleListSerializer, ArticleDetailSerializer, ArticleCreateUpdateSerializer,
    ArticleStatsSerializer, SourceStatsSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    """Стандартная пагинация для API."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@extend_schema_view(
    list=extend_schema(
        tags=['articles'],
        summary="Получить список статей",
        description="""
        Возвращает список статей с поддержкой поиска, фильтрации и сортировки.
        
        **Поиск**: используйте параметр `search` для поиска по заголовку, контенту и краткому содержанию.
        
        **Фильтрация**: 
        - По теме: `topic=technology`
        - По источнику: `source=1` или `source_name=habr`
        - По тегам: `tags=python,javascript`
        - По локациям: `locations=москва,россия`
        - По дате: `published_at__gte=2025-01-01`
        - Рекомендуемые: `featured=true`
        - Проанализированные: `analyzed=true`
        - За сегодня: `today=true`
        - За неделю: `this_week=true`
        
        **Сортировка**: используйте параметр `ordering` с значениями `published_at`, `created_at`, `read_count`
        """,
        parameters=[
            OpenApiParameter(
                name='search',
                description='Поиск по заголовку, контенту и краткому содержанию',
                required=False,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name='topic',
                description='Фильтр по теме статьи',
                required=False,
                type=OpenApiTypes.STR,
                enum=['politics', 'economics', 'technology', 'science', 'sports', 'culture',
                      'health', 'education', 'environment', 'society', 'war', 'international',
                      'business', 'finance', 'entertainment', 'travel', 'food', 'fashion',
                      'auto', 'real_estate', 'other']
            ),
            OpenApiParameter(
                name='tags',
                description='Фильтр по тегам (через запятую)',
                required=False,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name='locations',
                description='Фильтр по локациям (через запятую)',
                required=False,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name='featured',
                description='Только рекомендуемые статьи',
                required=False,
                type=OpenApiTypes.BOOL,
            ),
            OpenApiParameter(
                name='analyzed',
                description='Только проанализированные статьи',
                required=False,
                type=OpenApiTypes.BOOL,
            ),
            OpenApiParameter(
                name='today',
                description='Статьи за сегодня',
                required=False,
                type=OpenApiTypes.BOOL,
            ),
            OpenApiParameter(
                name='this_week',
                description='Статьи за эту неделю',
                required=False,
                type=OpenApiTypes.BOOL,
            ),
        ],
        examples=[
            OpenApiExample(
                'Поиск по Python',
                value={'search': 'python'},
                request_only=True,
            ),
            OpenApiExample(
                'Технологические статьи из Москвы',
                value={'topic': 'technology', 'locations': 'москва'},
                request_only=True,
            ),
        ]
    ),
    create=extend_schema(
        tags=['articles'],
        summary="Создать новую статью",
        description="Создает новую статью с проверкой уникальности URL."
    )
)
class ArticleListCreateView(generics.ListCreateAPIView):
    """
    Список статей с поиском и фильтрацией + создание новых статей.
    
    Поиск по: title, content, summary, tags, locations
    Фильтры: topic, source, is_featured, is_analyzed, published_at
    Сортировка: published_at, created_at, read_count
    """
    queryset = Article.objects.filter(is_active=True).select_related('source')
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Поиск по полям
    search_fields = ['title', 'content', 'summary', 'tags', 'locations']
    
    # Фильтрация
    filterset_fields = {
        'topic': ['exact', 'in'],
        'source': ['exact'],
        'source__name': ['icontains'],
        'is_featured': ['exact'],
        'is_analyzed': ['exact'],
        'published_at': ['gte', 'lte', 'date'],
        'created_at': ['gte', 'lte', 'date'],
    }
    
    # Сортировка
    ordering_fields = ['published_at', 'created_at', 'read_count']
    ordering = ['-published_at']  # По умолчанию сортируем по дате публикации
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ArticleCreateUpdateSerializer
        return ArticleListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Дополнительные фильтры через query params
        today = timezone.now().date()
        
        # Фильтр "сегодня"
        if self.request.query_params.get('today'):
            queryset = queryset.filter(published_at__date=today)
        
        # Фильтр "эта неделя"  
        if self.request.query_params.get('this_week'):
            week_ago = today - timedelta(days=7)
            queryset = queryset.filter(published_at__date__gte=week_ago)
        
        # Фильтр "рекомендуемые"
        if self.request.query_params.get('featured'):
            queryset = queryset.filter(is_featured=True)
        
        # Фильтр "проанализированные"
        if self.request.query_params.get('analyzed'):
            queryset = queryset.filter(is_analyzed=True)
        
        # Фильтр по источнику (slug)
        source_name = self.request.query_params.get('source_name')
        if source_name:
            queryset = queryset.filter(source__name__icontains=source_name)
        
        # Фильтр по тегам
        tags = self.request.query_params.get('tags')
        if tags:
            tag_list = [tag.strip().lower() for tag in tags.split(',')]
            q_objects = Q()
            for tag in tag_list:
                q_objects |= Q(tags__icontains=tag)
            queryset = queryset.filter(q_objects)
        
        # Фильтр по локациям
        locations = self.request.query_params.get('locations')
        if locations:
            location_list = [loc.strip().lower() for loc in locations.split(',')]
            q_objects = Q()
            for location in location_list:
                q_objects |= Q(locations__icontains=location)
            queryset = queryset.filter(q_objects)
            
        return queryset


@extend_schema_view(
    retrieve=extend_schema(
        tags=['articles'],
        summary="Получить статью",
        description="Возвращает детальную информацию о статье и увеличивает счетчик просмотров."
    ),
    update=extend_schema(
        tags=['articles'],
        summary="Обновить статью",
        description="Полное обновление статьи."
    ),
    partial_update=extend_schema(
        tags=['articles'],
        summary="Частично обновить статью",
        description="Частичное обновление полей статьи."
    ),
    destroy=extend_schema(
        tags=['articles'],
        summary="Удалить статью",
        description="Удаляет статью из базы данных."
    )
)
class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Детальная информация о статье + редактирование + удаление.
    """
    queryset = Article.objects.filter(is_active=True).select_related('source')
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ArticleCreateUpdateSerializer
        return ArticleDetailSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """Получение статьи с увеличением счетчика просмотров."""
        instance = self.get_object()
        
        # Увеличиваем счетчик просмотров
        instance.read_count += 1
        instance.save(update_fields=['read_count'])
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        tags=['sources'],
        summary="Получить список источников",
        description="Возвращает список всех источников с поддержкой поиска и фильтрации."
    ),
    create=extend_schema(
        tags=['sources'],
        summary="Создать новый источник",
        description="Создает новый источник с проверкой уникальности URL."
    )
)
class SourceListCreateView(generics.ListCreateAPIView):
    """
    Список источников + создание новых источников.
    
    Поиск по: name, description
    Фильтры: type, is_active
    Сортировка: name, created_at, articles_count
    """
    queryset = Source.objects.all()
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Поиск
    search_fields = ['name', 'description']
    
    # Фильтрация
    filterset_fields = {
        'type': ['exact', 'in'],
        'is_active': ['exact'],
        'created_at': ['gte', 'lte', 'date'],
    }
    
    # Сортировка
    ordering_fields = ['name', 'created_at', 'articles_count']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SourceCreateUpdateSerializer
        return SourceListSerializer


@extend_schema_view(
    retrieve=extend_schema(
        tags=['sources'],
        summary="Получить источник",
        description="Возвращает детальную информацию об источнике с последними статьями."
    ),
    update=extend_schema(
        tags=['sources'],
        summary="Обновить источник",
        description="Полное обновление источника."
    ),
    partial_update=extend_schema(
        tags=['sources'],
        summary="Частично обновить источник",
        description="Частичное обновление полей источника."
    ),
    destroy=extend_schema(
        tags=['sources'],
        summary="Удалить источник",
        description="Удаляет источник из базы данных."
    )
)
class SourceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Детальная информация об источнике + редактирование + удаление.
    """
    queryset = Source.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return SourceCreateUpdateSerializer
        return SourceDetailSerializer


@extend_schema(
    tags=['stats'],
    summary="Статистика по статьям",
    description="""
    Возвращает подробную статистику по статьям:
    - Общее количество статей
    - Количество рекомендуемых статей
    - Количество проанализированных статей  
    - Распределение по темам
    - Топ-10 источников по количеству статей
    - Топ тегов и локаций
    - Количество статей за последние 24 часа
    """,
    responses=ArticleStatsSerializer
)
@api_view(['GET'])
def articles_stats(request):
    """Статистика по статьям."""
    
    # Основные счетчики
    total_articles = Article.objects.filter(is_active=True).count()
    featured_articles = Article.objects.filter(is_active=True, is_featured=True).count()
    analyzed_articles = Article.objects.filter(is_active=True, is_analyzed=True).count()
    total_sources = Source.objects.filter(is_active=True).count()
    
    # Статьи за последние 24 часа
    yesterday = timezone.now() - timedelta(hours=24)
    recent_articles_count = Article.objects.filter(
        is_active=True,
        created_at__gte=yesterday
    ).count()
    
    # Распределение по темам
    topics = Article.objects.filter(is_active=True).values('topic').annotate(
        count=Count('id')
    ).order_by('-count')
    
    articles_by_topic = {}
    for topic in topics:
        topic_label = dict(Article.TOPIC_CHOICES).get(topic['topic'], topic['topic'])
        articles_by_topic[topic_label] = topic['count']
    
    # Топ источников
    sources = Article.objects.filter(is_active=True).values(
        'source__name'
    ).annotate(count=Count('id')).order_by('-count')[:10]
    
    articles_by_source = {}
    for source in sources:
        articles_by_source[source['source__name']] = source['count']
    
    # Топ тегов
    all_tags = []
    articles_with_tags = Article.objects.filter(is_active=True, is_analyzed=True).exclude(tags=[])
    for article in articles_with_tags:
        if article.tags:
            all_tags.extend(article.tags)
    
    tag_counter = Counter(all_tags)
    top_tags = [{'tag': tag, 'count': count} for tag, count in tag_counter.most_common(15)]
    
    # Топ локаций
    all_locations = []
    articles_with_locations = Article.objects.filter(is_active=True, is_analyzed=True).exclude(locations=[])
    for article in articles_with_locations:
        if article.locations:
            all_locations.extend(article.locations)
    
    location_counter = Counter(all_locations)
    top_locations = [{'location': loc, 'count': count} for loc, count in location_counter.most_common(15)]
    
    return Response({
        'total_articles': total_articles,
        'total_sources': total_sources,
        'featured_articles': featured_articles,
        'analyzed_articles': analyzed_articles,
        'articles_by_topic': articles_by_topic,
        'articles_by_source': articles_by_source,
        'recent_articles_count': recent_articles_count,
        'top_tags': top_tags,
        'top_locations': top_locations,
    })


@extend_schema(
    tags=['stats'],
    summary="Статистика по источникам",
    description="""
    Возвращает подробную статистику по источникам:
    - Общее количество источников
    - Количество активных источников
    - Распределение по типам источников
    - Топ-10 источников по количеству статей
    """,
    responses=SourceStatsSerializer
)
@api_view(['GET'])
def sources_stats(request):
    """Статистика по источникам."""
    
    # Основные счетчики
    total_sources = Source.objects.count()
    active_sources = Source.objects.filter(is_active=True).count()
    
    # Распределение по типам
    types = Source.objects.values('type').annotate(count=Count('id')).order_by('-count')
    
    sources_by_type = {}
    for source_type in types:
        type_label = dict(Source.TYPE_CHOICES).get(source_type['type'], source_type['type'])
        sources_by_type[type_label] = source_type['count']
    
    # Топ источников по количеству статей
    top_sources_data = Source.objects.annotate(
        real_articles_count=Count('articles', filter=Q(articles__is_active=True))
    ).order_by('-real_articles_count')[:10]
    
    top_sources = []
    for source in top_sources_data:
        top_sources.append({
            'name': source.name,
            'articles_count': source.real_articles_count,
            'type': source.get_type_display(),
            'is_active': source.is_active
        })
    
    return Response({
        'total_sources': total_sources,
        'active_sources': active_sources,
        'sources_by_type': sources_by_type,
        'top_sources': top_sources,
    })


@extend_schema(
    tags=['search'],
    summary="Универсальный поиск",
    description="""
    Выполняет поиск по статьям и источникам одновременно.
    
    Поиск осуществляется по:
    - Заголовкам, контенту и краткому содержанию статей
    - Тегам и локациям статей
    - Названиям и описаниям источников
    
    Возвращает до 20 статей и 10 источников.
    """,
    parameters=[
        OpenApiParameter(
            name='q',
            description='Поисковый запрос',
            required=True,
            type=OpenApiTypes.STR,
        ),
    ],
    examples=[
        OpenApiExample(
            'Поиск Python',
            value={'q': 'python'},
            request_only=True,
        ),
        OpenApiExample(
            'Поиск Москва',
            value={'q': 'москва'},
            request_only=True,
        ),
    ]
)
@api_view(['GET'])
def search_everything(request):
    """Универсальный поиск по статьям и источникам."""
    
    query = request.GET.get('q', '').strip()
    
    if not query:
        return Response({
            'error': 'Параметр "q" обязателен'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Поиск по статьям
    articles_queryset = Article.objects.filter(is_active=True).select_related('source')
    articles_q = Q(title__icontains=query) | Q(content__icontains=query) | Q(summary__icontains=query)
    
    # Добавляем поиск по тегам и локациям
    articles_q |= Q(tags__icontains=query) | Q(locations__icontains=query)
    
    articles = articles_queryset.filter(articles_q)[:20]
    articles_data = ArticleListSerializer(articles, many=True).data
    
    # Поиск по источникам
    sources_queryset = Source.objects.all()
    sources_q = Q(name__icontains=query) | Q(description__icontains=query)
    sources = sources_queryset.filter(sources_q)[:10]
    sources_data = SourceListSerializer(sources, many=True).data
    
    return Response({
        'query': query,
        'articles': {
            'count': len(articles_data),
            'results': articles_data
        },
        'sources': {
            'count': len(sources_data),
            'results': sources_data
        }
    })


@extend_schema(
    tags=['search'],
    summary="Популярные статьи",
    description="""
    Возвращает список популярных статей за последнюю неделю,
    отсортированных по количеству просмотров.
    
    Ограничено 20 статьями.
    """,
)
@api_view(['GET'])
def trending_articles(request):
    """Популярные статьи за последнюю неделю."""
    
    week_ago = timezone.now() - timedelta(days=7)
    
    articles = Article.objects.filter(
        is_active=True,
        published_at__gte=week_ago
    ).select_related('source').order_by('-read_count')[:20]
    
    serializer = ArticleListSerializer(articles, many=True)
    
    return Response({
        'count': len(serializer.data),
        'results': serializer.data
    })