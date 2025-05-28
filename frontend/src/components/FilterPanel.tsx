import React, { useState, useEffect } from 'react';
import { Search, Filter, X, ChevronDown } from 'lucide-react';
import { TopicType, Source, ArticleFilters } from '../types/api';
import { apiService } from '../services/api';

interface FilterPanelProps {
  filters: ArticleFilters;
  onFiltersChange: (filters: ArticleFilters) => void;
  className?: string;
}

const topicOptions: { value: TopicType; label: string }[] = [
  { value: 'politics', label: 'Политика' },
  { value: 'economics', label: 'Экономика' },
  { value: 'technology', label: 'Технологии' },
  { value: 'science', label: 'Наука' },
  { value: 'business', label: 'Бизнес' },
  { value: 'war', label: 'Война' },
  { value: 'international', label: 'Международные отношения' },
  { value: 'other', label: 'Прочее' },
];

export const FilterPanel: React.FC<FilterPanelProps> = ({
  filters,
  onFiltersChange,
  className = '',
}) => {
  const [sources, setSources] = useState<Source[]>([]);
  const [isExpanded, setIsExpanded] = useState(false);
  const [searchQuery, setSearchQuery] = useState(filters.search || '');

  useEffect(() => {
    const loadSources = async () => {
      try {
        const sourcesData = await apiService.getSources();
        setSources(sourcesData.filter(source => source.is_active));
      } catch (error) {
        console.error('Failed to load sources:', error);
      }
    };
    loadSources();
  }, []);

  const handleSearchChange = (value: string) => {
    setSearchQuery(value);
    onFiltersChange({ ...filters, search: value || undefined, page: 1 });
  };

  const handleFilterChange = (key: keyof ArticleFilters, value: any) => {
    onFiltersChange({ 
      ...filters, 
      [key]: value === '' ? undefined : value,
      page: 1 // Reset to first page when filters change
    });
  };

  const clearFilters = () => {
    setSearchQuery('');
    onFiltersChange({ page: 1, page_size: filters.page_size });
  };

  const hasActiveFilters = Boolean(
    filters.search || 
    filters.topic || 
    filters.source || 
    filters.analyzed !== undefined ||
    filters.tags
  );

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 ${className}`}>
      {/* Search Bar */}
      <div className="p-4 border-b border-gray-200">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Поиск статей..."
            value={searchQuery}
            onChange={(e) => handleSearchChange(e.target.value)}
            className="input-field pl-10 pr-4"
          />
          {searchQuery && (
            <button
              onClick={() => handleSearchChange('')}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Filter Toggle */}
      <div className="p-4">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center justify-between w-full text-left"
        >
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <span className="font-medium text-gray-700">Фильтры</span>
            {hasActiveFilters && (
              <span className="bg-primary-100 text-primary-800 text-xs px-2 py-1 rounded-full">
                Активны
              </span>
            )}
          </div>
          <ChevronDown 
            className={`w-4 h-4 text-gray-500 transition-transform ${
              isExpanded ? 'rotate-180' : ''
            }`} 
          />
        </button>

        {/* Expanded Filters */}
        {isExpanded && (
          <div className="mt-4 space-y-4">
            {/* Topic Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Тема
              </label>
              <select
                value={filters.topic || ''}
                onChange={(e) => handleFilterChange('topic', e.target.value)}
                className="input-field"
              >
                <option value="">Все темы</option>
                {topicOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Source Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Источник
              </label>
              <select
                value={filters.source || ''}
                onChange={(e) => handleFilterChange('source', e.target.value ? Number(e.target.value) : undefined)}
                className="input-field"
              >
                <option value="">Все источники</option>
                {sources.map((source) => (
                  <option key={source.id} value={source.id}>
                    {source.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Analysis Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Анализ
              </label>
              <select
                value={filters.analyzed === undefined ? '' : filters.analyzed.toString()}
                onChange={(e) => handleFilterChange('analyzed', e.target.value === '' ? undefined : e.target.value === 'true')}
                className="input-field"
              >
                <option value="">Все статьи</option>
                <option value="true">Только проанализированные</option>
                <option value="false">Не проанализированные</option>
              </select>
            </div>

            {/* Tags Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Теги
              </label>
              <input
                type="text"
                placeholder="Поиск по тегам..."
                value={filters.tags || ''}
                onChange={(e) => handleFilterChange('tags', e.target.value)}
                className="input-field"
              />
            </div>

            {/* Sorting */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Сортировка
              </label>
              <select
                value={filters.ordering || '-published_at'}
                onChange={(e) => handleFilterChange('ordering', e.target.value)}
                className="input-field"
              >
                <option value="-published_at">Сначала новые</option>
                <option value="published_at">Сначала старые</option>
                <option value="-created_at">По дате добавления</option>
                <option value="title">По алфавиту</option>
              </select>
            </div>

            {/* Clear Filters */}
            {hasActiveFilters && (
              <button
                onClick={clearFilters}
                className="w-full btn-secondary flex items-center justify-center gap-2"
              >
                <X className="w-4 h-4" />
                Очистить фильтры
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default FilterPanel; 