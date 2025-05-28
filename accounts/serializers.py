from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile, SubscriptionPlan, UserSubscription, UserFavoriteArticle


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя."""
    
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'password_confirm']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Сериализатор для входа пользователя."""
    
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Неверный email или пароль')
            if not user.is_active:
                raise serializers.ValidationError('Аккаунт деактивирован')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Необходимо указать email и пароль')
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для профиля пользователя."""
    
    class Meta:
        model = UserProfile
        fields = [
            'avatar', 'bio', 'language', 'theme', 'timezone',
            'email_notifications', 'newsletter_subscription',
            'articles_read', 'last_activity'
        ]
        read_only_fields = ['articles_read', 'last_activity']


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя с профилем."""
    
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'full_name', 'is_email_verified', 'created_at', 'profile'
        ]
        read_only_fields = ['id', 'is_email_verified', 'created_at']


class PasswordChangeSerializer(serializers.Serializer):
    """Сериализатор для смены пароля."""
    
    old_password = serializers.CharField(style={'input_type': 'password'})
    new_password = serializers.CharField(
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(style={'input_type': 'password'})

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Неверный текущий пароль')
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError('Новые пароли не совпадают')
        return attrs

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Сериализатор для планов подписки."""
    
    features = serializers.SerializerMethodField()

    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'slug', 'plan_type', 'description',
            'price', 'billing_period', 'features', 'is_popular'
        ]

    def get_features(self, obj):
        """Возвращает список возможностей плана."""
        features = []
        
        if obj.max_api_requests_per_day > 0:
            features.append(f"До {obj.max_api_requests_per_day} API запросов в день")
        
        if obj.max_saved_articles > 0:
            features.append(f"До {obj.max_saved_articles} сохраненных статей")
        
        if obj.max_custom_sources > 0:
            features.append(f"До {obj.max_custom_sources} пользовательских источников")
        
        if obj.headless_parsing_enabled:
            features.append("Headless парсинг SPA сайтов")
        
        if obj.advanced_analytics:
            features.append("Расширенная аналитика и экспорт")
        
        if obj.api_access:
            features.append("Полный доступ к API")
        
        if obj.priority_support:
            features.append("Приоритетная поддержка")
        
        return features


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок пользователя."""
    
    plan = SubscriptionPlanSerializer(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)

    class Meta:
        model = UserSubscription
        fields = [
            'id', 'plan', 'status', 'start_date', 'end_date',
            'is_active', 'days_remaining', 'auto_renewal', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserFavoriteArticleSerializer(serializers.ModelSerializer):
    """Сериализатор для избранных статей."""
    
    article_title = serializers.CharField(source='article.title', read_only=True)
    article_url = serializers.URLField(source='article.url', read_only=True)
    article_source = serializers.CharField(source='article.source.name', read_only=True)
    article_published_at = serializers.DateTimeField(source='article.published_at', read_only=True)

    class Meta:
        model = UserFavoriteArticle
        fields = [
            'id', 'article', 'article_title', 'article_url', 
            'article_source', 'article_published_at', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserStatsSerializer(serializers.Serializer):
    """Сериализатор для статистики пользователя."""
    
    articles_read = serializers.IntegerField()
    favorite_articles_count = serializers.IntegerField()
    custom_sources_count = serializers.IntegerField()
    subscription_status = serializers.CharField()
    subscription_days_remaining = serializers.IntegerField()
    api_requests_today = serializers.IntegerField()
    registration_date = serializers.DateTimeField()
    last_activity = serializers.DateTimeField() 