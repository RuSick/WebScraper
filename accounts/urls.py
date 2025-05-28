from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Аутентификация
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Профиль пользователя
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/update/', views.UserProfileUpdateView.as_view(), name='profile-update'),
    path('change-password/', views.change_password, name='change-password'),
    
    # Статистика и дашборд
    path('stats/', views.user_stats, name='user-stats'),
    path('dashboard/', views.dashboard_data, name='dashboard'),
    
    # Подписки
    path('subscription-plans/', views.SubscriptionPlanListView.as_view(), name='subscription-plans'),
    path('subscriptions/', views.UserSubscriptionListView.as_view(), name='user-subscriptions'),
    
    # Избранные статьи
    path('favorites/', views.UserFavoriteArticleListView.as_view(), name='favorites'),
    path('favorites/<int:pk>/', views.UserFavoriteArticleDetailView.as_view(), name='favorite-detail'),
    path('articles/<int:article_id>/toggle-favorite/', views.toggle_favorite_article, name='toggle-favorite'),
    path('articles/<int:article_id>/check-favorite/', views.check_favorite_article, name='check-favorite'),
] 