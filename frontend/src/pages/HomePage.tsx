import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { ArticleCard } from '../components/ArticleCard';
import { CompactFilters } from '../components/CompactFilters';
import { CompactAnalytics } from '../components/CompactAnalytics';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { Article, ArticleStats, ArticleFilters as Filters, ApiResponse, Source } from '../types/api';
import { useFavorites } from '../contexts/FavoritesContext';

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

      const response = await fetch(`http://localhost:8000/api/articles/?${params}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: ApiResponse<Article> = await response.json();
      
      let filteredArticles = data.results;
      
      // Client-side filtering for favorites
      if (filters.favorites) {
        filteredArticles = filteredArticles.filter(article => 
          favorites.has(article.id)
        );
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
    setFilters(newFilters);
    setPage(1);
  };

  const loadMore = () => {
    if (!loading && hasMore) {
      fetchArticles(page + 1, false);
    }
  };

  if (loading && articles.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-dark-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex justify-center items-center h-64">
            <LoadingSpinner size="lg" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-dark-900">
      {/* Compact Filters */}
      <CompactFilters 
        filters={filters}
        onFiltersChange={handleFiltersChange}
        sources={sources}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Left Sidebar - Analytics */}
          <div className="lg:col-span-1">
            <div className="sticky top-32">
              <CompactAnalytics stats={stats} />
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {/* Header */}
            <div className="mb-6">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                    {filters.favorites ? 'Избранные статьи' : 
                     filters.topic ? `Статьи по теме: ${filters.topic}` : 
                     filters.search ? `Поиск: "${filters.search}"` : 
                     'Все статьи'}
                  </h1>
                  <p className="text-gray-600 dark:text-gray-400 mt-1">
                    {articles.length} {articles.length === 1 ? 'статья' : 
                     articles.length < 5 ? 'статьи' : 'статей'} найдено
                  </p>
                </div>
              </div>
            </div>

            {/* Error State */}
            {error && (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 mb-6">
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 bg-red-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-xs">!</span>
                  </div>
                  <p className="text-red-700 dark:text-red-300 font-medium">Ошибка загрузки</p>
                </div>
                <p className="text-red-600 dark:text-red-400 text-sm mt-1">{error}</p>
              </div>
            )}

            {/* Articles Grid */}
            {articles.length > 0 ? (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                  {articles.map((article) => (
                    <ArticleCard key={article.id} article={article} />
                  ))}
                </div>

                {/* Load More Button */}
                {hasMore && (
                  <div className="flex justify-center mt-8">
                    <button
                      onClick={loadMore}
                      disabled={loading}
                      className="px-6 py-3 bg-primary-600 hover:bg-primary-700 disabled:bg-primary-400 text-white rounded-lg font-medium transition-colors duration-200 flex items-center gap-2"
                    >
                      {loading ? (
                        <>
                          <LoadingSpinner size="sm" />
                          Загрузка...
                        </>
                      ) : (
                        'Загрузить ещё'
                      )}
                    </button>
                  </div>
                )}
              </>
            ) : !loading ? (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-gray-200 dark:bg-dark-700 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">📰</span>
                </div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  Статьи не найдены
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Попробуйте изменить параметры фильтрации
                </p>
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}; 