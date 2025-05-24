from rest_framework import viewsets, filters
from core.models import Article, Source
from api.serializers import ArticleSerializer, SourceSerializer


class SourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Source.objects.filter(is_active=True)
    serializer_class = SourceSerializer


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.all().order_by('-published_at')
    serializer_class = ArticleSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'topic', 'tone']
    ordering_fields = ['published_at', 'tone']