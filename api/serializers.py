from rest_framework import serializers
from core.models import Source, Article


class SourceListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка источников."""
    
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Source
        fields = [
            'id', 'name', 'url', 'type', 'type_display', 
            'is_active', 'articles_count', 'last_parsed'
        ]


class SourceDetailSerializer(serializers.ModelSerializer):
    """Детальный сериализатор источника."""
    
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    recent_articles = serializers.SerializerMethodField()
    
    class Meta:
        model = Source
        fields = [
            'id', 'name', 'url', 'type', 'type_display', 'is_active',
            'description', 'update_frequency', 'articles_count', 
            'last_parsed', 'created_at', 'recent_articles'
        ]
    
    def get_recent_articles(self, obj):
        """Получить последние 5 статей из источника."""
        recent = obj.articles.filter(is_active=True)[:5]
        return ArticleListSerializer(recent, many=True).data


class ArticleListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка статей."""
    
    source = SourceListSerializer(read_only=True)
    topic_display = serializers.CharField(source='get_topic_display', read_only=True)
    short_content = serializers.ReadOnlyField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'url', 'source', 'published_at',
            'topic', 'topic_display', 'tags', 'locations',
            'short_content', 'summary', 'content', 'is_featured', 'read_count', 'is_analyzed'
        ]


class ArticleDetailSerializer(serializers.ModelSerializer):
    """Детальный сериализатор статьи."""
    
    source = SourceListSerializer(read_only=True)
    topic_display = serializers.CharField(source='get_topic_display', read_only=True)
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'summary', 'url', 'source',
            'published_at', 'topic', 'topic_display', 'tags', 'locations',
            'is_featured', 'read_count', 'is_analyzed', 'created_at', 'updated_at'
        ]
    
    def to_representation(self, instance):
        """Увеличиваем счетчик просмотров при получении детальной информации."""
        representation = super().to_representation(instance)
        # Увеличиваем счетчик только при GET запросах, но не при каждом обращении к сериализатору
        if hasattr(self.context.get('request'), 'method') and self.context['request'].method == 'GET':
            # Можно добавить логику увеличения счетчика здесь
            pass
        return representation


class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления статей."""
    
    class Meta:
        model = Article
        fields = [
            'title', 'content', 'summary', 'url', 'source',
            'published_at', 'topic', 'tags', 'locations', 'is_featured', 'is_active'
        ]
    
    def validate_url(self, value):
        """Проверка уникальности URL."""
        if Article.objects.filter(url=value).exists():
            raise serializers.ValidationError("Статья с таким URL уже существует.")
        return value


class SourceCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления источников."""
    
    class Meta:
        model = Source
        fields = [
            'name', 'url', 'type', 'is_active', 'description', 'update_frequency'
        ]
    
    def validate_url(self, value):
        """Проверка уникальности URL источника."""
        if Source.objects.filter(url=value).exists():
            raise serializers.ValidationError("Источник с таким URL уже существует.")
        return value


class ArticleStatsSerializer(serializers.Serializer):
    """Сериализатор для статистики статей."""
    
    total_articles = serializers.IntegerField()
    featured_articles = serializers.IntegerField()
    analyzed_articles = serializers.IntegerField()
    articles_by_topic = serializers.DictField()
    articles_by_source = serializers.DictField()
    recent_articles_count = serializers.IntegerField()
    top_tags = serializers.ListField()
    top_locations = serializers.ListField()


class SourceStatsSerializer(serializers.Serializer):
    """Сериализатор для статистики источников."""
    
    total_sources = serializers.IntegerField()
    active_sources = serializers.IntegerField()
    sources_by_type = serializers.DictField()
    top_sources = serializers.ListField()