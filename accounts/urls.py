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
    
    # Подписки - планы
    path('subscription-plans/', views.SubscriptionPlanListView.as_view(), name='subscription-plans'),
    path('subscriptions/', views.UserSubscriptionListView.as_view(), name='user-subscriptions'),
    
    # Подписки - управление
    path('subscription/current/', views.current_subscription, name='current-subscription'),
    path('subscription/usage/', views.usage_stats, name='usage-stats'),
    path('subscription/dashboard/', views.subscription_dashboard, name='subscription-dashboard'),
    path('subscription/upgrade/', views.upgrade_subscription, name='upgrade-subscription'),
    path('subscription/confirm-payment/', views.confirm_payment, name='confirm-payment'),
    path('subscription/cancel/', views.cancel_subscription, name='cancel-subscription'),
    path('subscription/check-limit/<str:feature>/', views.check_limit, name='check-limit'),
    
    # Платежи
    path('subscription/payment-methods/', views.payment_methods_list, name='payment-methods'),
    path('subscription/payments/', views.payment_history_list, name='payment-history'),
    
    # Избранные статьи
    path('favorites/', views.UserFavoriteArticleListView.as_view(), name='favorites'),
    path('favorites/<int:pk>/', views.UserFavoriteArticleDetailView.as_view(), name='favorite-detail'),
    path('articles/<int:article_id>/toggle-favorite/', views.toggle_favorite_article, name='toggle-favorite'),
    path('articles/<int:article_id>/check-favorite/', views.check_favorite_article, name='check-favorite'),
] 