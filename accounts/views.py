from django.shortcuts import render
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime, timedelta

from .models import (
    User, UserProfile, SubscriptionPlan, UserSubscription,
    UserFavoriteArticle, APIUsageLog, UsageTracking, PaymentMethod, PaymentHistory
)
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    UserProfileSerializer, PasswordChangeSerializer, SubscriptionPlanSerializer,
    UserSubscriptionSerializer, UserFavoriteArticleSerializer, UserStatsSerializer,
    UsageStatsSerializer, SubscriptionDashboardSerializer, PaymentIntentSerializer,
    PaymentMethodSerializer, PaymentHistorySerializer
)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    """Регистрация нового пользователя."""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'message': 'Пользователь успешно зарегистрирован',
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """Вход пользователя в систему."""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        
        token, created = Token.objects.get_or_create(user=user)
        
        # Обновляем последнюю активность
        if hasattr(user, 'profile'):
            user.profile.last_activity = timezone.now()
            user.profile.save()
        
        return Response({
            'message': 'Успешный вход в систему',
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Выход пользователя из системы."""
    try:
        # Удаляем токен пользователя
        request.user.auth_token.delete()
    except:
        pass
    
    logout(request)
    return Response({
        'message': 'Успешный выход из системы'
    }, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Просмотр и редактирование профиля пользователя."""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UserProfileUpdateView(generics.UpdateAPIView):
    """Обновление профиля пользователя."""
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """Смена пароля пользователя."""
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Пароль успешно изменен'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionPlanListView(generics.ListAPIView):
    """Список доступных планов подписки."""
    
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]


class UserSubscriptionListView(generics.ListAPIView):
    """Список подписок пользователя."""
    
    serializer_class = UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserSubscription.objects.filter(user=self.request.user)


class UserFavoriteArticleListView(generics.ListCreateAPIView):
    """Список избранных статей пользователя."""
    
    serializer_class = UserFavoriteArticleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserFavoriteArticle.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserFavoriteArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Детали избранной статьи."""
    
    serializer_class = UserFavoriteArticleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserFavoriteArticle.objects.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats(request):
    """Статистика пользователя."""
    user = request.user
    
    # Получаем активную подписку
    active_subscription = UserSubscription.objects.filter(
        user=user,
        status='active',
        end_date__gt=timezone.now()
    ).first()
    
    # Считаем API запросы за сегодня
    today = timezone.now().date()
    api_requests_today = APIUsageLog.objects.filter(
        user=user,
        created_at__date=today
    ).count()
    
    stats_data = {
        'articles_read': user.profile.articles_read if hasattr(user, 'profile') else 0,
        'favorite_articles_count': user.favorite_articles.count(),
        'custom_sources_count': user.custom_sources.count(),
        'subscription_status': active_subscription.plan.name if active_subscription else 'Бесплатный',
        'subscription_days_remaining': active_subscription.days_remaining if active_subscription else 0,
        'api_requests_today': api_requests_today,
        'registration_date': user.created_at,
        'last_activity': user.profile.last_activity if hasattr(user, 'profile') else user.created_at,
    }
    
    serializer = UserStatsSerializer(stats_data)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_favorite_article(request, article_id):
    """Добавить/убрать статью из избранного."""
    from core.models import Article
    
    try:
        article = Article.objects.get(id=article_id)
    except Article.DoesNotExist:
        return Response({
            'error': 'Статья не найдена'
        }, status=status.HTTP_404_NOT_FOUND)
    
    favorite, created = UserFavoriteArticle.objects.get_or_create(
        user=request.user,
        article=article
    )
    
    if not created:
        # Если уже в избранном - удаляем
        favorite.delete()
        return Response({
            'message': 'Статья удалена из избранного',
            'is_favorite': False
        })
    else:
        # Если не было в избранном - добавляем
        return Response({
            'message': 'Статья добавлена в избранное',
            'is_favorite': True
        })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_favorite_article(request, article_id):
    """Проверить, находится ли статья в избранном."""
    is_favorite = UserFavoriteArticle.objects.filter(
        user=request.user,
        article_id=article_id
    ).exists()
    
    return Response({
        'is_favorite': is_favorite
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_data(request):
    """Данные для дашборда пользователя."""
    user = request.user
    
    # Активная подписка
    active_subscription = UserSubscription.objects.filter(
        user=user,
        status='active',
        end_date__gt=timezone.now()
    ).first()
    
    # Последние избранные статьи
    recent_favorites = UserFavoriteArticle.objects.filter(
        user=user
    ).select_related('article', 'article__source').order_by('-created_at')[:5]
    
    # API использование за последние 7 дней
    week_ago = timezone.now() - timedelta(days=7)
    api_usage_week = APIUsageLog.objects.filter(
        user=user,
        created_at__gte=week_ago
    ).extra(
        select={'day': 'date(created_at)'}
    ).values('day').annotate(
        requests_count=Count('id')
    ).order_by('day')
    
    return Response({
        'user': UserSerializer(user).data,
        'subscription': UserSubscriptionSerializer(active_subscription).data if active_subscription else None,
        'recent_favorites': UserFavoriteArticleSerializer(recent_favorites, many=True).data,
        'api_usage_week': list(api_usage_week),
        'stats': {
            'total_favorites': user.favorite_articles.count(),
            'total_custom_sources': user.custom_sources.count(),
            'api_requests_today': APIUsageLog.objects.filter(
                user=user,
                created_at__date=timezone.now().date()
            ).count()
        }
    })


# Subscription Views

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_subscription(request):
    """Получить текущую подписку пользователя."""
    subscription = UserSubscription.objects.filter(
        user=request.user,
        status='active'
    ).select_related('plan').first()
    
    if subscription:
        return Response(UserSubscriptionSerializer(subscription).data)
    else:
        return Response(None)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def usage_stats(request):
    """Получить статистику использования пользователя."""
    user = request.user
    
    # Получаем или создаем tracking объект
    usage_tracking, created = UsageTracking.objects.get_or_create(user=user)
    
    # Сбрасываем лимиты если нужно
    usage_tracking.reset_daily_limits()
    usage_tracking.reset_monthly_limits()
    
    # Получаем текущую подписку для лимитов
    subscription = UserSubscription.objects.filter(
        user=user,
        status='active'
    ).select_related('plan').first()
    
    # Формируем данные для фронтенда
    stats_data = {
        'daily_articles_read': usage_tracking.daily_articles_read,
        'daily_articles_limit': subscription.plan.daily_articles_limit if subscription else 10,
        'favorites_count': usage_tracking.total_favorites,
        'favorites_limit': subscription.plan.favorites_limit if subscription else 10,
        'exports_count': usage_tracking.monthly_exports,
        'exports_limit': subscription.plan.exports_limit if subscription else 0,
        'api_calls_count': usage_tracking.daily_api_calls,
        'api_calls_limit': subscription.plan.api_calls_limit if subscription else 0,
        'reset_date': timezone.datetime.combine(
            timezone.now().date() + timedelta(days=1),
            timezone.datetime.min.time()
        ).isoformat()
    }
    
    serializer = UsageStatsSerializer(stats_data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def subscription_dashboard(request):
    """Получить все данные для дашборда подписки."""
    user = request.user
    
    # Текущая подписка
    subscription = UserSubscription.objects.filter(
        user=user,
        status='active'
    ).select_related('plan').first()
    
    # Статистика использования
    usage_tracking, created = UsageTracking.objects.get_or_create(user=user)
    usage_tracking.reset_daily_limits()
    usage_tracking.reset_monthly_limits()
    
    # Доступные планы
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price')
    
    # Способы оплаты
    payment_methods = PaymentMethod.objects.filter(user=user, is_active=True)
    
    # Последние платежи
    recent_payments = PaymentHistory.objects.filter(user=user).order_by('-created_at')[:5]
    
    # Формируем статистику для фронтенда
    usage_stats = {
        'daily_articles_read': usage_tracking.daily_articles_read,
        'daily_articles_limit': subscription.plan.daily_articles_limit if subscription else 10,
        'favorites_count': usage_tracking.total_favorites,
        'favorites_limit': subscription.plan.favorites_limit if subscription else 10,
        'exports_count': usage_tracking.monthly_exports,
        'exports_limit': subscription.plan.exports_limit if subscription else 0,
        'api_calls_count': usage_tracking.daily_api_calls,
        'api_calls_limit': subscription.plan.api_calls_limit if subscription else 0,
        'reset_date': timezone.datetime.combine(
            timezone.now().date() + timedelta(days=1),
            timezone.datetime.min.time()
        ).isoformat()
    }
    
    dashboard_data = {
        'subscription': subscription,
        'usage': usage_stats,
        'plans': plans,
        'payment_methods': payment_methods,
        'recent_payments': recent_payments
    }
    
    serializer = SubscriptionDashboardSerializer(dashboard_data)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upgrade_subscription(request):
    """Создать платежное намерение для обновления подписки."""
    plan_id = request.data.get('plan_id')
    payment_method_id = request.data.get('payment_method')
    
    try:
        plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
    except SubscriptionPlan.DoesNotExist:
        return Response({
            'error': 'План подписки не найден'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Создаем платежное намерение (здесь будет интеграция с платежной системой)
    import uuid
    payment_intent_id = str(uuid.uuid4())
    
    # Создаем запись в истории платежей
    payment_history = PaymentHistory.objects.create(
        user=request.user,
        subscription=None,  # Будет установлено после успешной оплаты
        amount=plan.price,
        currency='BYN',
        payment_intent_id=payment_intent_id,
        description=f"Подписка на план {plan.name}"
    )
    
    # Возвращаем данные для фронтенда
    payment_intent_data = {
        'id': payment_intent_id,
        'amount': plan.price,
        'currency': 'BYN',
        'status': 'pending',
        'payment_method': payment_method_id or 'card',
        'client_secret': f"pi_{payment_intent_id}_secret"
    }
    
    serializer = PaymentIntentSerializer(payment_intent_data)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def confirm_payment(request):
    """Подтвердить платеж и активировать подписку."""
    payment_intent_id = request.data.get('payment_intent_id')
    
    try:
        payment = PaymentHistory.objects.get(
            payment_intent_id=payment_intent_id,
            user=request.user,
            status='pending'
        )
    except PaymentHistory.DoesNotExist:
        return Response({
            'error': 'Платеж не найден'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Здесь будет проверка статуса платежа в платежной системе
    # Для демо просто помечаем как успешный
    
    # Находим план по описанию (в реальности лучше хранить plan_id)
    plan_name = payment.description.split("план ")[-1]
    try:
        plan = SubscriptionPlan.objects.get(name=plan_name)
    except SubscriptionPlan.DoesNotExist:
        return Response({
            'error': 'План подписки не найден'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Создаем или обновляем подписку
    end_date = timezone.now()
    if plan.billing_period == 'monthly':
        end_date += timedelta(days=30)
    elif plan.billing_period == 'yearly':
        end_date += timedelta(days=365)
    elif plan.billing_period == 'lifetime':
        end_date += timedelta(days=365 * 100)  # 100 лет
    
    subscription = UserSubscription.objects.create(
        user=request.user,
        plan=plan,
        status='active',
        start_date=timezone.now(),
        end_date=end_date,
        amount_paid=payment.amount,
        payment_method='card',
        transaction_id=payment.payment_intent_id
    )
    
    # Обновляем платеж
    payment.subscription = subscription
    payment.mark_as_succeeded(transaction_id=payment.payment_intent_id)
    
    return Response(UserSubscriptionSerializer(subscription).data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_subscription(request):
    """Отменить подписку."""
    subscription = UserSubscription.objects.filter(
        user=request.user,
        status='active'
    ).first()
    
    if not subscription:
        return Response({
            'error': 'Активная подписка не найдена'
        }, status=status.HTTP_404_NOT_FOUND)
    
    subscription.status = 'cancelled'
    subscription.auto_renewal = False
    subscription.save()
    
    return Response({
        'message': 'Подписка отменена'
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_limit(request, feature):
    """Проверить лимит для определенной функции."""
    user = request.user
    
    # Получаем tracking
    usage_tracking, created = UsageTracking.objects.get_or_create(user=user)
    usage_tracking.reset_daily_limits()
    usage_tracking.reset_monthly_limits()
    
    # Получаем подписку
    subscription = UserSubscription.objects.filter(
        user=user,
        status='active'
    ).select_related('plan').first()
    
    allowed = True
    
    if feature == 'articles':
        limit = subscription.plan.daily_articles_limit if subscription else 10
        if limit is not None:
            allowed = usage_tracking.daily_articles_read < limit
    elif feature == 'favorites':
        limit = subscription.plan.favorites_limit if subscription else 10
        if limit is not None:
            allowed = usage_tracking.total_favorites < limit
    elif feature == 'exports':
        limit = subscription.plan.exports_limit if subscription else 0
        if limit is not None:
            allowed = usage_tracking.monthly_exports < limit
    elif feature == 'api':
        limit = subscription.plan.api_calls_limit if subscription else 0
        if limit is not None:
            allowed = usage_tracking.daily_api_calls < limit
    
    return Response({'allowed': allowed})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def payment_methods_list(request):
    """Список способов оплаты пользователя."""
    payment_methods = PaymentMethod.objects.filter(user=request.user, is_active=True)
    serializer = PaymentMethodSerializer(payment_methods, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def payment_history_list(request):
    """История платежей пользователя."""
    payments = PaymentHistory.objects.filter(user=request.user).order_by('-created_at')
    serializer = PaymentHistorySerializer(payments, many=True)
    return Response(serializer.data)
