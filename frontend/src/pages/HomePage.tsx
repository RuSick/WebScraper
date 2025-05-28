import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { CompactFilters } from '../components/CompactFilters';
import { CompactAnalytics } from '../components/CompactAnalytics';
import { Article, ArticleStats, ArticleFilters as Filters, ApiResponse, Source } from '../types/api';
import { useFavorites } from '../contexts/FavoritesContext';
import { ModernArticlesGrid } from '../components/ModernArticlesGrid';

export const HomePage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const { favorites } = useFavorites();
  
  const [articles, setArticles] = useState<Article[]>([]);
  const [stats, setStats] = useState<ArticleStats | undefined>();
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  // Initialize filters from URL params
  const [filters, setFilters] = useState<Filters>(() => {
    return {
      search: searchParams.get('search') || '',
      topic: (searchParams.get('topic') as any) || '',
      source: searchParams.get('source') ? parseInt(searchParams.get('source')!) : undefined,
      is_analyzed: searchParams.get('analyzed') === 'true',
      date_from: searchParams.get('date_from') || '',
      date_to: searchParams.get('date_to') || '',
      ordering: searchParams.get('ordering') || 'published_at',
      favorites: searchParams.get('favorites') === 'true',
    };
  });

  // Update URL when filters change
  useEffect(() => {
    const params = new URLSearchParams();
    
    if (filters.search) params.set('search', filters.search);
    if (filters.topic) params.set('topic', filters.topic);
    if (filters.source) params.set('source', filters.source.toString());
    if (filters.is_analyzed) params.set('analyzed', 'true');
    if (filters.date_from) params.set('date_from', filters.date_from);
    if (filters.date_to) params.set('date_to', filters.date_to);
    if (filters.ordering && filters.ordering !== 'published_at') {
      params.set('ordering', filters.ordering);
    }
    if (filters.favorites) params.set('favorites', 'true');

    setSearchParams(params);
  }, [filters, setSearchParams]);

  const fetchArticles = useCallback(async (pageNum: number = 1, resetList: boolean = true) => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams({
        page: pageNum.toString(),
        page_size: '12',
        ordering: `-${filters.ordering}`,
      });

      if (filters.search) params.append('search', filters.search);
      if (filters.topic) params.append('topic', filters.topic);
      if (filters.source) params.append('source', filters.source.toString());
      if (filters.is_analyzed) params.append('is_analyzed', 'true');
      if (filters.date_from) params.append('published_at__gte', filters.date_from);
      if (filters.date_to) params.append('published_at__lte', filters.date_to);

      const url = `http://localhost:8000/api/articles/?${params}`;
      console.log('🔍 API Request URL:', url);
      console.log('📋 Current filters:', filters);

      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: ApiResponse<Article> = await response.json();
      console.log('📰 API Response:', data.results.length, 'articles');
      console.log('🏷️ Topics in response:', data.results.map(a => a.topic));
      
      let filteredArticles = data.results;
      
      // Client-side filtering for favorites
      if (filters.favorites) {
        filteredArticles = filteredArticles.filter(article => 
          favorites.has(article.id)
        );
        if (resetList) {
          setTotalCount(filteredArticles.length);
        }
      } else {
        setTotalCount(data.count);
      }

      if (resetList) {
        setArticles(filteredArticles);
      } else {
        setArticles(prev => [...prev, ...filteredArticles]);
      }
      
      setHasMore(!!data.next && filteredArticles.length > 0);
      setPage(pageNum);
    } catch (err) {
      console.error('Error fetching articles:', err);
      setError(err instanceof Error ? err.message : 'Произошла ошибка при загрузке статей');
    } finally {
      setLoading(false);
    }
  }, [filters, favorites]);

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/stats/articles/');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: ArticleStats = await response.json();
      setStats(data);
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

  const fetchSources = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/sources/');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: ApiResponse<Source> = await response.json();
      setSources(data.results);
    } catch (err) {
      console.error('Error fetching sources:', err);
    }
  };

  useEffect(() => {
    fetchArticles(1, true);
  }, [fetchArticles]);

  useEffect(() => {
    fetchStats();
    fetchSources();
  }, []);

  const handleFiltersChange = (newFilters: Filters) => {
    console.log('🔄 Filters changed:', newFilters);
    setFilters(newFilters);
    setPage(1);
  };

  const handleAnalyticsFilter = (filterType: 'topic' | 'search', value: string) => {
    const newFilters = { ...filters };
    
    if (filterType === 'topic') {
      // Если тот же топик уже выбран, сбрасываем его
      if (newFilters.topic === value) {
        newFilters.topic = '';
      } else {
        newFilters.topic = value as any; // Приведение типа для совместимости
      }
    } else if (filterType === 'search') {
      // Если тот же поиск уже активен, сбрасываем его
      if (newFilters.search === value) {
        newFilters.search = '';
      } else {
        newFilters.search = value;
      }
    }
    
    handleFiltersChange(newFilters);
  };

  const handleApplyFilters = () => {
    fetchArticles(1, true);
  };

  const loadMore = () => {
    if (!loading && hasMore) {
      fetchArticles(page + 1, false);
    }
  };

  // Передаем функцию поиска в Header через контекст или пропсы
  useEffect(() => {
    // Устанавливаем глобальный обработчик поиска
    (window as any).handleGlobalSearch = (query: string) => {
      handleFiltersChange({
        ...filters,
        search: query || '',
      });
    };
    return () => {
      delete (window as any).handleGlobalSearch;
    };
  }, [filters, handleFiltersChange]);

  if (loading && articles.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex justify-center items-center h-64">
            <div className="text-center">
              <div className="w-16 h-16 border-4 border-blue-200 dark:border-blue-800 border-t-blue-600 dark:border-t-blue-400 rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-gray-600 dark:text-slate-400 text-lg">Загрузка статей...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
      {/* Compact Filters */}
      <CompactFilters 
        filters={filters}
        onFiltersChange={handleFiltersChange}
        sources={sources}
        articlesCount={totalCount}
        onApplyFilters={handleApplyFilters}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Left Sidebar - Analytics */}
          <div className="lg:col-span-1">
            <div className="sticky top-24">
              <CompactAnalytics 
                stats={stats} 
                onFilterChange={handleAnalyticsFilter}
                activeFilters={{
                  topic: filters.topic,
                  search: filters.search,
                }}
              />
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {/* Header */}
            <div className="mb-10">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-slate-300 bg-clip-text text-transparent mb-3">
                    {filters.favorites ? '⭐ Избранные статьи' : 
                     filters.topic ? `📂 ${filters.topic}` : 
                     filters.search ? `🔍 "${filters.search}"` : 
                     'Все статьи'}
                  </h1>
                  <p className="text-gray-600 dark:text-slate-400 text-lg">
                    {totalCount} {totalCount === 1 ? 'статья' : 
                     totalCount < 5 ? 'статьи' : 'статей'} найдено
                  </p>
                </div>
              </div>
            </div>

            {/* Error State */}
            {error && (
              <div className="text-center py-20">
                <div className="w-32 h-32 bg-gradient-to-br from-red-100 to-red-200 dark:from-red-900 dark:to-red-800 rounded-3xl flex items-center justify-center mx-auto mb-8 border border-red-200 dark:border-red-700">
                  <span className="text-5xl">⚠️</span>
                </div>
                <h3 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Ошибка загрузки</h3>
                <p className="text-gray-600 dark:text-slate-400 text-xl mb-8 max-w-md mx-auto">
                  {error}
                </p>
                <button
                  onClick={() => window.location.reload()}
                  className="px-8 py-4 bg-gradient-to-r from-red-500 to-red-600 hover:from-red-400 hover:to-red-500 text-white rounded-2xl font-semibold transition-all duration-300 shadow-lg hover:shadow-xl hover:shadow-red-500/10"
                >
                  Попробовать снова
                </button>
              </div>
            )}

            {/* Modern Articles Grid */}
            <ModernArticlesGrid
              articles={articles}
              loading={loading}
              hasMore={hasMore}
              onLoadMore={loadMore}
            />

            {/* Empty State for no articles */}
            {!loading && articles.length === 0 && !error && (
              <div className="text-center py-20">
                <div className="w-32 h-32 bg-gradient-to-br from-gray-100 to-gray-200 dark:from-slate-800 dark:to-slate-700 rounded-3xl flex items-center justify-center mx-auto mb-8 border border-gray-200 dark:border-slate-600/50">
                  <span className="text-5xl">🔍</span>
                </div>
                <h3 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Статьи не найдены</h3>
                <p className="text-gray-600 dark:text-slate-400 text-xl mb-8 max-w-md mx-auto">
                  Попробуйте изменить параметры поиска или фильтры
                </p>
                <button
                  onClick={() => handleFiltersChange({
                    search: '',
                    topic: '',
                    is_analyzed: false,
                    date_from: '',
                    date_to: '',
                    ordering: '-published_at',
                    favorites: false,
                    source: undefined,
                  })}
                  className="px-8 py-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white rounded-2xl font-semibold transition-all duration-300 shadow-lg hover:shadow-xl hover:shadow-blue-500/10"
                >
                  Сбросить фильтры
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}; 