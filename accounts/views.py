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
    UserFavoriteArticle, APIUsageLog
)
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    UserProfileSerializer, PasswordChangeSerializer, SubscriptionPlanSerializer,
    UserSubscriptionSerializer, UserFavoriteArticleSerializer, UserStatsSerializer
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
