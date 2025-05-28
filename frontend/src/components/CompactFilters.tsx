import React from 'react';
import { Star, Brain, RotateCcw, Filter } from 'lucide-react';
import { ArticleFilters as Filters, Source } from '../types/api';

interface CompactFiltersProps {
  filters: Filters;
  onFiltersChange: (filters: Filters) => void;
  sources?: Source[];
  className?: string;
  articlesCount?: number;
  onApplyFilters?: () => void;
}

export const CompactFilters: React.FC<CompactFiltersProps> = ({
  filters,
  onFiltersChange,
  sources = [],
  className = '',
  articlesCount = 0,
  onApplyFilters,
}) => {
  const topicOptions = [
    { value: '', label: 'Все темы' },
    { value: 'technology', label: '💻 Технологии' },
    { value: 'politics', label: '🏛️ Политика' },
    { value: 'economics', label: '📈 Экономика' },
    { value: 'science', label: '🔬 Наука' },
    { value: 'business', label: '💼 Бизнес' },
    { value: 'war', label: '⚔️ Война' },
    { value: 'other', label: '📰 Прочее' },
  ];

  const handleFilterChange = (key: keyof Filters, value: any) => {
    const newFilters = {
      ...filters,
      [key]: value,
    };
    onFiltersChange(newFilters);
  };

  const resetFilters = () => {
    onFiltersChange({
      search: '',
      topic: '',
      source: undefined,
      is_analyzed: false,
      date_from: '',
      date_to: '',
      ordering: 'published_at',
      favorites: false,
    });
  };

  const hasActiveFilters = filters.topic || filters.source || 
                          filters.is_analyzed || filters.date_from || filters.date_to || 
                          filters.favorites;

  const handleApply = () => {
    if (onApplyFilters) {
      onApplyFilters();
    }
  };

  return (
    <div className={`bg-white dark:bg-dark-800 border-b border-gray-200 dark:border-dark-700 shadow-sm ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
        {/* Compact Filters */}
        <div className="space-y-3">
          {/* Main Filters Row */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Topic */}
            <div>
              <label className="block text-xs text-gray-400 dark:text-gray-500 mb-1">Тема</label>
              <select
                value={filters.topic || ''}
                onChange={(e) => handleFilterChange('topic', e.target.value)}
                className="w-full h-8 px-2 py-1 text-sm bg-gray-50 dark:bg-dark-700 border border-gray-200 dark:border-dark-600 rounded focus:outline-none focus:ring-1 focus:ring-primary-500 text-gray-900 dark:text-white"
              >
                {topicOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Source */}
            <div>
              <label className="block text-xs text-gray-400 dark:text-gray-500 mb-1">Источник</label>
              <select
                value={filters.source || ''}
                onChange={(e) => handleFilterChange('source', e.target.value ? parseInt(e.target.value) : undefined)}
                className="w-full h-8 px-2 py-1 text-sm bg-gray-50 dark:bg-dark-700 border border-gray-200 dark:border-dark-600 rounded focus:outline-none focus:ring-1 focus:ring-primary-500 text-gray-900 dark:text-white"
              >
                <option value="">Все источники</option>
                {sources.map((source) => (
                  <option key={source.id} value={source.id}>
                    {source.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Date From */}
            <div>
              <label className="block text-xs text-gray-400 dark:text-gray-500 mb-1">С даты</label>
              <input
                type="date"
                value={filters.date_from || ''}
                onChange={(e) => handleFilterChange('date_from', e.target.value)}
                className="w-full h-8 px-2 py-1 text-sm border border-gray-200 dark:border-dark-600 rounded focus:outline-none focus:ring-1 focus:ring-primary-500 bg-gray-50 dark:bg-dark-700 text-gray-900 dark:text-white"
              />
            </div>

            {/* Date To */}
            <div>
              <label className="block text-xs text-gray-400 dark:text-gray-500 mb-1">До даты</label>
              <input
                type="date"
                value={filters.date_to || ''}
                onChange={(e) => handleFilterChange('date_to', e.target.value)}
                className="w-full h-8 px-2 py-1 text-sm border border-gray-200 dark:border-dark-600 rounded focus:outline-none focus:ring-1 focus:ring-primary-500 bg-gray-50 dark:bg-dark-700 text-gray-900 dark:text-white"
              />
            </div>
          </div>

          {/* Secondary Row */}
          <div className="flex items-center justify-between">
            {/* Left side - Compact toggles and sorting */}
            <div className="flex items-center gap-6">
              {/* AI Analysis Toggle */}
              <label className="inline-flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={filters.is_analyzed || false}
                  onChange={(e) => handleFilterChange('is_analyzed', e.target.checked)}
                  className="w-4 h-4 text-primary-600 bg-gray-50 dark:bg-dark-700 border-gray-300 dark:border-dark-600 rounded focus:ring-primary-500 focus:ring-1"
                />
                <Brain className="w-4 h-4 text-green-600 dark:text-green-400" />
                <span className="text-sm text-gray-700 dark:text-gray-300">AI анализ</span>
              </label>

              {/* Favorites Toggle */}
              <label className="inline-flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={filters.favorites || false}
                  onChange={(e) => handleFilterChange('favorites', e.target.checked)}
                  className="w-4 h-4 text-primary-600 bg-gray-50 dark:bg-dark-700 border-gray-300 dark:border-dark-600 rounded focus:ring-primary-500 focus:ring-1"
                />
                <Star className="w-4 h-4 text-yellow-500" />
                <span className="text-sm text-gray-700 dark:text-gray-300">Избранное</span>
              </label>

              {/* Sorting */}
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400 dark:text-gray-500">Сортировка:</span>
                <select
                  value={filters.ordering || 'published_at'}
                  onChange={(e) => handleFilterChange('ordering', e.target.value)}
                  className="h-8 px-2 py-1 text-sm bg-gray-50 dark:bg-dark-700 border border-gray-200 dark:border-dark-600 rounded focus:outline-none focus:ring-1 focus:ring-primary-500 text-gray-900 dark:text-white"
                >
                  <option value="published_at">По дате</option>
                  <option value="created_at">По добавлению</option>
                  <option value="read_count">По популярности</option>
                </select>
              </div>
            </div>

            {/* Right side - Actions and count */}
            <div className="flex items-center gap-4">
              {/* Results count */}
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <Filter className="w-4 h-4" />
                <span>{articlesCount} статей</span>
                {hasActiveFilters && (
                  <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                )}
              </div>

              {/* Action buttons */}
              <div className="flex items-center gap-2">
                <button
                  onClick={resetFilters}
                  disabled={!hasActiveFilters}
                  className="px-3 py-1 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  title="Сбросить фильтры"
                >
                  <RotateCcw className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}; 