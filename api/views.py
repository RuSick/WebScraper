from rest_framework import generics, filters, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

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


class ArticleListCreateView(generics.ListCreateAPIView):
    """
    Список статей с поиском и фильтрацией + создание новых статей.
    
    Поиск по: title, content, summary
    Фильтры: topic, tone, source, is_featured, published_at
    Сортировка: published_at, created_at, read_count
    """
    queryset = Article.objects.filter(is_active=True).select_related('source')
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Поиск по полям
    search_fields = ['title', 'content', 'summary']
    
    # Фильтрация
    filterset_fields = {
        'topic': ['exact', 'in'],
        'tone': ['exact', 'in'],
        'source': ['exact'],
        'source__name': ['icontains'],
        'is_featured': ['exact'],
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
        
        # Фильтр по источнику (slug)
        source_name = self.request.query_params.get('source_name')
        if source_name:
            queryset = queryset.filter(source__name__icontains=source_name)
            
        return queryset


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
        """При получении статьи увеличиваем счетчик просмотров."""
        instance = self.get_object()
        # Увеличиваем счетчик просмотров
        Article.objects.filter(pk=instance.pk).update(read_count=instance.read_count + 1)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


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


class SourceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Детальная информация об источнике + редактирование + удаление.
    """
    queryset = Source.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return SourceCreateUpdateSerializer
        return SourceDetailSerializer


@api_view(['GET'])
def articles_stats(request):
    """
    Статистика по статьям.
    
    GET /api/stats/articles/
    """
    # Основная статистика
    total_articles = Article.objects.filter(is_active=True).count()
    featured_articles = Article.objects.filter(is_active=True, is_featured=True).count()
    
    # Статистика по темам
    topics_stats = Article.objects.filter(is_active=True).values('topic').annotate(
        count=Count('id')
    ).order_by('-count')
    articles_by_topic = {item['topic']: item['count'] for item in topics_stats}
    
    # Статистика по тональности
    tone_stats = Article.objects.filter(is_active=True).values('tone').annotate(
        count=Count('id')
    ).order_by('-count')
    articles_by_tone = {item['tone']: item['count'] for item in tone_stats}
    
    # Статистика по источникам (топ-10)
    source_stats = Article.objects.filter(is_active=True).values('source__name').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    articles_by_source = {item['source__name']: item['count'] for item in source_stats}
    
    # Статьи за последние 24 часа
    yesterday = timezone.now() - timedelta(days=1)
    recent_articles_count = Article.objects.filter(
        is_active=True, 
        created_at__gte=yesterday
    ).count()
    
    stats_data = {
        'total_articles': total_articles,
        'featured_articles': featured_articles,
        'articles_by_topic': articles_by_topic,
        'articles_by_tone': articles_by_tone,
        'articles_by_source': articles_by_source,
        'recent_articles_count': recent_articles_count,
    }
    
    serializer = ArticleStatsSerializer(stats_data)
    return Response(serializer.data)


@api_view(['GET'])
def sources_stats(request):
    """
    Статистика по источникам.
    
    GET /api/stats/sources/
    """
    # Основная статистика
    total_sources = Source.objects.count()
    active_sources = Source.objects.filter(is_active=True).count()
    
    # Статистика по типам
    type_stats = Source.objects.values('type').annotate(
        count=Count('id')
    ).order_by('-count')
    sources_by_type = {item['type']: item['count'] for item in type_stats}
    
    # Топ источников по количеству статей
    top_sources = Source.objects.filter(is_active=True).order_by('-articles_count')[:10]
    top_sources_data = [
        {'name': source.name, 'articles_count': source.articles_count}
        for source in top_sources
    ]
    
    stats_data = {
        'total_sources': total_sources,
        'active_sources': active_sources,
        'sources_by_type': sources_by_type,
        'top_sources': top_sources_data,
    }
    
    serializer = SourceStatsSerializer(stats_data)
    return Response(serializer.data)


@api_view(['GET'])
def search_everything(request):
    """
    Универсальный поиск по статьям и источникам.
    
    GET /api/search/?q=запрос
    """
    query = request.query_params.get('q', '').strip()
    
    if not query:
        return Response({
            'articles': [],
            'sources': [],
            'total_found': 0
        })
    
    # Поиск по статьям
    articles = Article.objects.filter(
        is_active=True
    ).filter(
        Q(title__icontains=query) | 
        Q(content__icontains=query) |
        Q(summary__icontains=query)
    ).select_related('source')[:20]
    
    # Поиск по источникам
    sources = Source.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query)
    )[:10]
    
    return Response({
        'articles': ArticleListSerializer(articles, many=True).data,
        'sources': SourceListSerializer(sources, many=True).data,
        'total_found': len(articles) + len(sources)
    })


@api_view(['GET'])
def trending_articles(request):
    """
    Популярные статьи (по количеству просмотров за последнюю неделю).
    
    GET /api/trending/
    """
    week_ago = timezone.now() - timedelta(days=7)
    
    trending = Article.objects.filter(
        is_active=True,
        published_at__gte=week_ago
    ).order_by('-read_count')[:20]
    
    serializer = ArticleListSerializer(trending, many=True)
    return Response(serializer.data)