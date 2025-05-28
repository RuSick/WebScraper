import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useParams, useSearchParams } from 'react-router-dom';
import { ArticleCard } from '../components/ArticleCard';
import { FilterPanel } from '../components/FilterPanel';
import { Pagination } from '../components/Pagination';
import { StatsPanel } from '../components/StatsPanel';
import { LoadingSpinner, ArticleCardSkeleton, StatsPanelSkeleton } from '../components/LoadingSpinner';
import { apiService } from '../services/api';
import { ArticleFilters, ApiResponse, Article } from '../types/api';
import { AlertCircle, RefreshCw, TrendingUp, Clock, Filter } from 'lucide-react';

export const HomePage: React.FC = () => {
  const { topic, sourceId } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const [showMobileFilters, setShowMobileFilters] = useState(false);
  
  // Initialize filters from URL params
  const [filters, setFilters] = useState<ArticleFilters>(() => {
    const initialFilters: ArticleFilters = {
      page: parseInt(searchParams.get('page') || '1'),
      page_size: 12,
      ordering: '-published_at',
    };

    if (topic) initialFilters.topic = topic as any;
    if (sourceId) initialFilters.source = parseInt(sourceId);
    if (searchParams.get('search')) initialFilters.search = searchParams.get('search') || undefined;
    if (searchParams.get('analyzed')) initialFilters.analyzed = searchParams.get('analyzed') === 'true';
    if (searchParams.get('tags')) initialFilters.tags = searchParams.get('tags') || undefined;

    return initialFilters;
  });

  // Update filters when URL params change
  useEffect(() => {
    const newFilters: ArticleFilters = {
      page: parseInt(searchParams.get('page') || '1'),
      page_size: 12,
      ordering: '-published_at',
    };

    if (topic) newFilters.topic = topic as any;
    if (sourceId) newFilters.source = parseInt(sourceId);
    if (searchParams.get('search')) newFilters.search = searchParams.get('search') || undefined;
    if (searchParams.get('analyzed')) newFilters.analyzed = searchParams.get('analyzed') === 'true';
    if (searchParams.get('tags')) newFilters.tags = searchParams.get('tags') || undefined;

    setFilters(newFilters);
  }, [topic, sourceId, searchParams]);

  // Fetch articles
  const {
    data: articlesData,
    isLoading: articlesLoading,
    error: articlesError,
    refetch: refetchArticles,
    isFetching: articlesFetching,
  } = useQuery<ApiResponse<Article>>({
    queryKey: ['articles', filters],
    queryFn: () => apiService.getArticles(filters),
    placeholderData: (previousData) => previousData,
    staleTime: 30000, // 30 seconds
  });

  // Fetch statistics
  const {
    data: stats,
    isLoading: statsLoading,
    error: statsError,
  } = useQuery({
    queryKey: ['stats'],
    queryFn: () => apiService.getStats(),
    refetchInterval: 60000, // Refresh every minute
    staleTime: 30000,
  });

  // Update URL when filters change
  const handleFiltersChange = (newFilters: ArticleFilters) => {
    setFilters(newFilters);
    
    const params = new URLSearchParams();
    Object.entries(newFilters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.set(key, String(value));
      }
    });
    setSearchParams(params);
  };

  const handlePageChange = (page: number) => {
    handleFiltersChange({ ...filters, page });
    // Scroll to top when page changes
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleRefresh = () => {
    refetchArticles();
  };

  // Get page title based on current filters
  const getPageTitle = () => {
    if (topic) {
      const topicLabels: Record<string, string> = {
        politics: 'Политика',
        economics: 'Экономика',
        technology: 'Технологии',
        science: 'Наука',
        business: 'Бизнес',
        war: 'Война',
        other: 'Прочее',
      };
      return `${topicLabels[topic] || topic}`;
    }
    if (filters.search) {
      return `Поиск: "${filters.search}"`;
    }
    return 'Все новости';
  };

  // Error state
  if (articlesError) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-red-900 mb-2">
            Ошибка загрузки данных
          </h2>
          <p className="text-red-700 mb-4">
            {articlesError instanceof Error 
              ? articlesError.message 
              : 'Не удалось загрузить статьи. Проверьте подключение к серверу.'
            }
          </p>
          <button
            onClick={handleRefresh}
            className="btn-primary"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Попробовать снова
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Sidebar */}
        <div className="lg:col-span-1 space-y-6">
          {/* Statistics */}
          {statsLoading ? (
            <StatsPanelSkeleton />
          ) : statsError ? (
            <div className="card p-4">
              <div className="flex items-center gap-2 text-red-600">
                <AlertCircle className="w-4 h-4" />
                <span className="text-sm">Ошибка загрузки статистики</span>
              </div>
            </div>
          ) : (
            <StatsPanel stats={stats} isLoading={false} />
          )}
          
          {/* Filters - Desktop */}
          <div className="hidden lg:block">
            <FilterPanel
              filters={filters}
              onFiltersChange={handleFiltersChange}
            />
          </div>
        </div>

        {/* Main content */}
        <div className="lg:col-span-3">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4">
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                {filters.search && <span className="text-primary-600">🔍</span>}
                {topic && <TrendingUp className="w-6 h-6 text-primary-600" />}
                {getPageTitle()}
              </h1>
              {articlesData && (
                <p className="text-gray-600 mt-1 flex items-center gap-2">
                  <Clock className="w-4 h-4" />
                  Найдено {articlesData.count.toLocaleString()} статей
                  {articlesFetching && (
                    <span className="text-primary-600 text-sm">(обновляется...)</span>
                  )}
                </p>
              )}
            </div>
            
            <div className="flex items-center gap-3">
              {/* Mobile filter toggle */}
              <button
                onClick={() => setShowMobileFilters(!showMobileFilters)}
                className="lg:hidden btn-secondary flex items-center gap-2"
              >
                <Filter className="w-4 h-4" />
                Фильтры
              </button>
              
              {/* Refresh button */}
              <button
                onClick={handleRefresh}
                disabled={articlesLoading || articlesFetching}
                className="btn-secondary flex items-center gap-2"
                title="Обновить данные"
              >
                <RefreshCw className={`w-4 h-4 ${(articlesLoading || articlesFetching) ? 'animate-spin' : ''}`} />
                <span className="hidden sm:inline">Обновить</span>
              </button>
            </div>
          </div>

          {/* Mobile Filters */}
          {showMobileFilters && (
            <div className="lg:hidden mb-6">
              <FilterPanel
                filters={filters}
                onFiltersChange={handleFiltersChange}
                className="border-2 border-primary-200"
              />
            </div>
          )}

          {/* Articles grid */}
          {articlesLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
              {Array.from({ length: 12 }).map((_, index) => (
                <ArticleCardSkeleton key={index} />
              ))}
            </div>
          ) : !articlesData || articlesData.results.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-gray-400 mb-4">
                <AlertCircle className="w-16 h-16 mx-auto" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Статьи не найдены
              </h3>
              <p className="text-gray-600 mb-4">
                {filters.search 
                  ? `По запросу "${filters.search}" ничего не найдено`
                  : 'Попробуйте изменить фильтры или поисковый запрос'
                }
              </p>
              {(filters.search || filters.topic || filters.source) && (
                <button
                  onClick={() => handleFiltersChange({ page: 1, page_size: filters.page_size })}
                  className="btn-primary"
                >
                  Сбросить фильтры
                </button>
              )}
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
                {articlesData.results.map((article: Article) => (
                  <ArticleCard
                    key={article.id}
                    article={article}
                  />
                ))}
              </div>

              {/* Pagination */}
              {articlesData && articlesData.count > (filters.page_size || 12) && (
                <Pagination
                  currentPage={filters.page || 1}
                  totalPages={Math.ceil(articlesData.count / (filters.page_size || 12))}
                  onPageChange={handlePageChange}
                />
              )}
            </>
          )}

          {/* Loading overlay for fetching */}
          {articlesFetching && !articlesLoading && (
            <div className="fixed bottom-4 right-4 bg-white rounded-lg shadow-lg border border-gray-200 p-3">
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <LoadingSpinner size="sm" />
                Обновление данных...
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}; 