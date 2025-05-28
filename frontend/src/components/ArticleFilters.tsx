import React from 'react';
import { Filter, Calendar, Tag, Star, RotateCcw } from 'lucide-react';
import { ArticleFilters as Filters } from '../types/api';

interface ArticleFiltersProps {
  filters: Filters;
  onFiltersChange: (filters: Filters) => void;
  className?: string;
}

export const ArticleFilters: React.FC<ArticleFiltersProps> = ({
  filters,
  onFiltersChange,
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

  const sortOptions = [
    { value: 'published_at', label: 'По дате' },
    { value: 'read_count', label: 'По популярности' },
    { value: 'title', label: 'По названию' },
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
      is_analyzed: false,
      date_from: '',
      date_to: '',
      ordering: 'published_at',
      favorites: false,
    });
  };

  const hasActiveFilters = filters.search || filters.topic || filters.is_analyzed || 
                          filters.date_from || filters.date_to || filters.favorites;

  return (
    <div className={`bg-white dark:bg-dark-800 rounded-xl shadow-sm border border-gray-200 dark:border-dark-700 overflow-hidden animate-fade-in ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-dark-700 bg-gradient-to-r from-gray-50 to-blue-50 dark:from-dark-700 dark:to-dark-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary-600 dark:bg-primary-500 rounded-lg flex items-center justify-center">
              <Filter className="w-4 h-4 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Фильтры</h3>
              <p className="text-xs text-gray-600 dark:text-gray-400">Настройте поиск статей</p>
            </div>
          </div>
          
          {hasActiveFilters && (
            <button
              onClick={resetFilters}
              className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white bg-gray-100 dark:bg-dark-600 hover:bg-gray-200 dark:hover:bg-dark-500 rounded-lg transition-all duration-200"
            >
              <RotateCcw className="w-3 h-3" />
              Сбросить
            </button>
          )}
        </div>
      </div>

      {/* Filters */}
      <div className="p-4 space-y-4">
        {/* Topic Filter */}
        <div className="space-y-2">
          <label className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300">
            <Tag className="w-4 h-4" />
            Тема
          </label>
          <select
            value={filters.topic}
            onChange={(e) => handleFilterChange('topic', e.target.value)}
            className="w-full px-3 py-2.5 border border-gray-300 dark:border-dark-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-dark-700 text-gray-900 dark:text-white text-sm transition-all duration-200"
          >
            {topicOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Date Range */}
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300">
              <Calendar className="w-4 h-4" />
              От
            </label>
            <input
              type="date"
              value={filters.date_from}
              onChange={(e) => handleFilterChange('date_from', e.target.value)}
              className="w-full px-3 py-2.5 border border-gray-300 dark:border-dark-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-dark-700 text-gray-900 dark:text-white text-sm transition-all duration-200"
            />
          </div>
          
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              До
            </label>
            <input
              type="date"
              value={filters.date_to}
              onChange={(e) => handleFilterChange('date_to', e.target.value)}
              className="w-full px-3 py-2.5 border border-gray-300 dark:border-dark-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-dark-700 text-gray-900 dark:text-white text-sm transition-all duration-200"
            />
          </div>
        </div>

        {/* Sort */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Сортировка
          </label>
          <select
            value={filters.ordering}
            onChange={(e) => handleFilterChange('ordering', e.target.value)}
            className="w-full px-3 py-2.5 border border-gray-300 dark:border-dark-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-dark-700 text-gray-900 dark:text-white text-sm transition-all duration-200"
          >
            {sortOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Checkboxes */}
        <div className="space-y-3 pt-2 border-t border-gray-200 dark:border-dark-600">
          <label className="flex items-center gap-3 cursor-pointer group">
            <input
              type="checkbox"
              checked={filters.is_analyzed}
              onChange={(e) => handleFilterChange('is_analyzed', e.target.checked)}
              className="w-4 h-4 text-primary-600 bg-white dark:bg-dark-700 border-gray-300 dark:border-dark-600 rounded focus:ring-primary-500 focus:ring-2 transition-all duration-200"
            />
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300 group-hover:text-gray-900 dark:group-hover:text-white transition-colors duration-200">
                Только проанализированные spaCy
              </span>
              <span className="px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-xs rounded-full">
                AI
              </span>
            </div>
          </label>

          <label className="flex items-center gap-3 cursor-pointer group">
            <input
              type="checkbox"
              checked={filters.favorites}
              onChange={(e) => handleFilterChange('favorites', e.target.checked)}
              className="w-4 h-4 text-primary-600 bg-white dark:bg-dark-700 border-gray-300 dark:border-dark-600 rounded focus:ring-primary-500 focus:ring-2 transition-all duration-200"
            />
            <div className="flex items-center gap-2">
              <Star className="w-4 h-4 text-yellow-500" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300 group-hover:text-gray-900 dark:group-hover:text-white transition-colors duration-200">
                Только избранные
              </span>
            </div>
          </label>
        </div>
      </div>

      {/* Footer */}
      <div className="px-4 py-3 bg-gray-50 dark:bg-dark-700/50 border-t border-gray-200 dark:border-dark-600">
        <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
          {hasActiveFilters ? 'Фильтры применены' : 'Все статьи отображаются'}
        </div>
      </div>
    </div>
  );
}; 