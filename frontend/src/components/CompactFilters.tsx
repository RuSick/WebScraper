import React from 'react';
import { Calendar, Star, Brain, RotateCcw, Filter } from 'lucide-react';
import { ArticleFilters as Filters, Source } from '../types/api';

interface CompactFiltersProps {
  filters: Filters;
  onFiltersChange: (filters: Filters) => void;
  sources?: Source[];
  className?: string;
}

export const CompactFilters: React.FC<CompactFiltersProps> = ({
  filters,
  onFiltersChange,
  sources = [],
  className = '',
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
    onFiltersChange({
      ...filters,
      [key]: value,
    });
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

  const hasActiveFilters = filters.search || filters.topic || filters.source || 
                          filters.is_analyzed || filters.date_from || filters.date_to || 
                          filters.favorites;

  return (
    <div className={`bg-white dark:bg-dark-800 border-b border-gray-200 dark:border-dark-700 shadow-sm ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="py-4">
          <div className="flex items-center gap-3 flex-wrap">
            {/* Filter Icon */}
            <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
              <Filter className="w-4 h-4" />
              <span className="text-sm font-medium hidden sm:inline">Фильтры:</span>
            </div>

            {/* Topic Select */}
            <select
              value={filters.topic || ''}
              onChange={(e) => handleFilterChange('topic', e.target.value)}
              className="px-3 py-2 bg-gray-50 dark:bg-dark-700 border border-gray-200 dark:border-dark-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 text-gray-900 dark:text-white"
            >
              {topicOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>

            {/* Source Select */}
            <select
              value={filters.source || ''}
              onChange={(e) => handleFilterChange('source', e.target.value ? parseInt(e.target.value) : undefined)}
              className="px-3 py-2 bg-gray-50 dark:bg-dark-700 border border-gray-200 dark:border-dark-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 text-gray-900 dark:text-white"
            >
              <option value="">Все источники</option>
              {sources.map((source) => (
                <option key={source.id} value={source.id}>
                  {source.name}
                </option>
              ))}
            </select>

            {/* Date From */}
            <div className="flex items-center gap-1">
              <Calendar className="w-4 h-4 text-gray-400" />
              <input
                type="date"
                value={filters.date_from || ''}
                onChange={(e) => handleFilterChange('date_from', e.target.value)}
                className="px-3 py-2 border border-gray-200 dark:border-dark-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-gray-50 dark:bg-dark-700 text-gray-900 dark:text-white"
                placeholder="От"
              />
            </div>

            {/* Date To */}
            <input
              type="date"
              value={filters.date_to || ''}
              onChange={(e) => handleFilterChange('date_to', e.target.value)}
              className="px-3 py-2 border border-gray-200 dark:border-dark-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-gray-50 dark:bg-dark-700 text-gray-900 dark:text-white"
              placeholder="До"
            />

            {/* AI Checkbox */}
            <label className="flex items-center gap-2 px-3 py-2 bg-gray-50 dark:bg-dark-700 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-dark-600 transition-all duration-200">
              <input
                type="checkbox"
                checked={filters.is_analyzed || false}
                onChange={(e) => handleFilterChange('is_analyzed', e.target.checked)}
                className="w-4 h-4 text-primary-600 bg-white dark:bg-dark-700 border-gray-300 dark:border-dark-600 rounded focus:ring-primary-500 focus:ring-2"
              />
              <Brain className="w-4 h-4 text-green-600 dark:text-green-400" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">AI</span>
            </label>

            {/* Favorites Checkbox */}
            <label className="flex items-center gap-2 px-3 py-2 bg-gray-50 dark:bg-dark-700 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-dark-600 transition-all duration-200">
              <input
                type="checkbox"
                checked={filters.favorites || false}
                onChange={(e) => handleFilterChange('favorites', e.target.checked)}
                className="w-4 h-4 text-primary-600 bg-white dark:bg-dark-700 border-gray-300 dark:border-dark-600 rounded focus:ring-primary-500 focus:ring-2"
              />
              <Star className="w-4 h-4 text-yellow-500" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Избранное</span>
            </label>

            {/* Action Buttons */}
            <div className="flex items-center gap-2 ml-auto">
              {/* Active Filters Indicator */}
              {hasActiveFilters && (
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse"></div>
                  <span className="text-xs text-primary-600 dark:text-primary-400 font-medium hidden sm:inline">
                    Активны
                  </span>
                </div>
              )}

              {/* Reset Button */}
              <button
                onClick={resetFilters}
                disabled={!hasActiveFilters}
                className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                title="Сбросить все фильтры"
              >
                <RotateCcw className="w-4 h-4" />
                <span className="hidden sm:inline">Сбросить</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}; 