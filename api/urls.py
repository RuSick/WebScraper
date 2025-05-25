from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Статьи
    path('articles/', views.ArticleListCreateView.as_view(), name='article-list'),
    path('articles/<int:pk>/', views.ArticleDetailView.as_view(), name='article-detail'),
    path('articles/<int:pk>/toggle-featured/', views.toggle_article_featured, name='toggle-article-featured'),
    
    # Источники
    path('sources/', views.SourceListCreateView.as_view(), name='source-list'),
    path('sources/<int:pk>/', views.SourceDetailView.as_view(), name='source-detail'),
    path('sources/<int:pk>/parse/', views.parse_source, name='source-parse'),
    path('sources/parse-all/', views.parse_all_sources, name='sources-parse-all'),
    
    # Задачи
    path('tasks/<str:task_id>/status/', views.task_status, name='task-status'),
    
    # Анализ
    path('articles/analyze/', views.analyze_articles, name='articles-analyze'),
    
    # Статистика
    path('stats/articles/', views.articles_stats, name='articles-stats'),
    path('stats/sources/', views.sources_stats, name='sources-stats'),
    
    # Поиск и рекомендации
    path('search/', views.search_everything, name='search-everything'),
    path('trending/', views.trending_articles, name='trending-articles'),
]
