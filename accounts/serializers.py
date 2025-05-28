from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import (
    User, UserProfile, SubscriptionPlan, UserSubscription, 
    UserFavoriteArticle, UsageTracking, PaymentMethod, PaymentHistory
)


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
    
    limits = serializers.SerializerMethodField()

    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'slug', 'plan_type', 'description',
            'price', 'billing_period', 'features', 'is_popular', 
            'is_active', 'limits', 'created_at', 'updated_at'
        ]

    def get_limits(self, obj):
        """Возвращает лимиты плана."""
        return {
            'daily_articles': obj.daily_articles_limit,
            'favorites': obj.favorites_limit,
            'exports': obj.exports_limit,
            'api_calls': obj.api_calls_limit,
        }


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


class UsageTrackingSerializer(serializers.ModelSerializer):
    """Сериализатор для отслеживания использования."""
    
    reset_date = serializers.SerializerMethodField()

    class Meta:
        model = UsageTracking
        fields = [
            'daily_articles_read', 'daily_api_calls', 'monthly_exports',
            'total_favorites', 'reset_date', 'last_daily_reset', 'last_monthly_reset'
        ]
        read_only_fields = ['last_daily_reset', 'last_monthly_reset']

    def get_reset_date(self, obj):
        """Возвращает дату следующего сброса дневных лимитов."""
        from django.utils import timezone
        from datetime import timedelta
        
        tomorrow = timezone.now().date() + timedelta(days=1)
        return timezone.datetime.combine(tomorrow, timezone.datetime.min.time())


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Сериализатор для способов оплаты."""
    
    expires = serializers.SerializerMethodField()
    brand = serializers.CharField(source='card_brand', read_only=True)

    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'type', 'last_four', 'brand', 'expires',
            'is_default', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_expires(self, obj):
        """Возвращает дату истечения карты."""
        if obj.expires_month and obj.expires_year:
            return f"{obj.expires_month:02d}/{obj.expires_year}"
        return None


class PaymentHistorySerializer(serializers.ModelSerializer):
    """Сериализатор для истории платежей."""
    
    payment_method_display = PaymentMethodSerializer(source='payment_method', read_only=True)

    class Meta:
        model = PaymentHistory
        fields = [
            'id', 'amount', 'currency', 'status', 'description',
            'payment_intent_id', 'transaction_id', 'payment_method_display',
            'processed_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PaymentIntentSerializer(serializers.Serializer):
    """Сериализатор для создания платежного намерения."""
    
    id = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField()
    status = serializers.CharField()
    payment_method = serializers.CharField()
    client_secret = serializers.CharField(required=False)


class UsageStatsSerializer(serializers.Serializer):
    """Сериализатор для статистики использования (для фронтенда)."""
    
    daily_articles_read = serializers.IntegerField()
    daily_articles_limit = serializers.IntegerField(allow_null=True)
    favorites_count = serializers.IntegerField()
    favorites_limit = serializers.IntegerField(allow_null=True)
    exports_count = serializers.IntegerField()
    exports_limit = serializers.IntegerField(allow_null=True)
    api_calls_count = serializers.IntegerField()
    api_calls_limit = serializers.IntegerField(allow_null=True)
    reset_date = serializers.DateTimeField()


class SubscriptionDashboardSerializer(serializers.Serializer):
    """Сериализатор для данных дашборда подписки."""
    
    subscription = UserSubscriptionSerializer(allow_null=True)
    usage = UsageStatsSerializer()
    plans = SubscriptionPlanSerializer(many=True)
    payment_methods = PaymentMethodSerializer(many=True)
    recent_payments = PaymentHistorySerializer(many=True) 