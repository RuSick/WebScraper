from rest_framework import serializers
from core.models import Article, Source


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = '__all__'


class ArticleSerializer(serializers.ModelSerializer):
    source = SourceSerializer(read_only=True)  # вложенная сериализация

    class Meta:
        model = Article
        fields = '__all__'