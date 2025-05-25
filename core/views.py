from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Article, Source

def article_list(request):
    """Главная страница со списком статей"""
    articles = Article.objects.filter(is_active=True).select_related('source').order_by('-published_at')
    
    # Поиск
    search_query = request.GET.get('search', '')
    if search_query:
        articles = articles.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(summary__icontains=search_query)
        )
    
    # Фильтрация по теме
    topic_filter = request.GET.get('topic', '')
    if topic_filter:
        articles = articles.filter(topic=topic_filter)
    
    # Фильтрация по тону
    tone_filter = request.GET.get('tone', '')
    if tone_filter:
        articles = articles.filter(tone=tone_filter)
    
    # Фильтрация по источнику
    source_filter = request.GET.get('source', '')
    if source_filter:
        articles = articles.filter(source_id=source_filter)
    
    # Фильтрация по избранным
    featured_filter = request.GET.get('featured', '')
    if featured_filter == 'true':
        articles = articles.filter(is_featured=True)
    
    # Пагинация
    paginator = Paginator(articles, 12)  # 12 статей на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Данные для фильтров
    sources = Source.objects.filter(is_active=True)
    topics = Article.TOPIC_CHOICES
    tones = Article.TONE_CHOICES
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'topic_filter': topic_filter,
        'tone_filter': tone_filter,
        'source_filter': source_filter,
        'featured_filter': featured_filter,
        'sources': sources,
        'topics': topics,
        'tones': tones,
        'total_count': paginator.count,
    }
    
    return render(request, 'core/article_list.html', context)

def article_detail(request, pk):
    """Детальная страница статьи"""
    from django.shortcuts import get_object_or_404
    
    article = get_object_or_404(Article, pk=pk, is_active=True)
    
    # Увеличиваем счетчик просмотров
    article.read_count += 1
    article.save(update_fields=['read_count'])
    
    # Похожие статьи
    related_articles = Article.objects.filter(
        topic=article.topic, 
        is_active=True
    ).exclude(pk=article.pk).select_related('source')[:4]
    
    context = {
        'article': article,
        'related_articles': related_articles,
    }
    
    return render(request, 'core/article_detail.html', context)
