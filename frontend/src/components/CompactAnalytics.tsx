import React, { useState } from 'react';
import { Tag, MapPin, Globe, BarChart3 } from 'lucide-react';
import { ArticleStats } from '../types/api';

interface CompactAnalyticsProps {
  stats?: ArticleStats;
  className?: string;
  onFilterChange?: (filterType: 'topic' | 'search', value: string) => void;
  activeFilters?: {
    topic?: string;
    search?: string;
  };
}

type TabType = 'overview' | 'tags' | 'locations' | 'sources';

export const CompactAnalytics: React.FC<CompactAnalyticsProps> = ({ 
  stats, 
  className = '', 
  onFilterChange,
  activeFilters = {}
}) => {
  const [activeTab, setActiveTab] = useState<TabType>('overview');

  if (!stats) {
    return (
      <div className={`bg-white dark:bg-dark-800 rounded-xl shadow-sm border border-gray-200 dark:border-dark-700 p-4 animate-fade-in ${className}`}>
        <div className="flex items-center gap-2 mb-3">
          <BarChart3 className="w-4 h-4 text-primary-600 dark:text-primary-400" />
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Аналитика</h3>
        </div>
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="h-3 bg-gray-200 dark:bg-dark-600 rounded w-3/4 mb-1"></div>
              <div className="h-4 bg-gray-200 dark:bg-dark-600 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const topTags = stats.top_tags?.slice(0, 5) || [];
  const topLocations = stats.top_locations?.slice(0, 5) || [];
  const topSources = Object.entries(stats.articles_by_source || {})
    .sort(([, a], [, b]) => b - a)
    .slice(0, 5);

  const tabs = [
    { id: 'overview' as TabType, label: 'Обзор', icon: BarChart3 },
    { id: 'tags' as TabType, label: 'Теги', icon: Tag },
    { id: 'locations' as TabType, label: 'Места', icon: MapPin },
    { id: 'sources' as TabType, label: 'Источники', icon: Globe },
  ];

  const handleTopicClick = (topic: string) => {
    if (onFilterChange) {
      onFilterChange('topic', topic);
    }
  };

  const handleTagClick = (tag: string) => {
    if (onFilterChange) {
      onFilterChange('search', tag);
    }
  };

  const handleLocationClick = (location: string) => {
    if (onFilterChange) {
      onFilterChange('search', location);
    }
  };

  const renderOverview = () => (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-3">
        <div className="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <div className="text-lg font-bold text-blue-600 dark:text-blue-400">
            {stats.total_articles?.toLocaleString()}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">Статей</div>
        </div>
        <div className="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
          <div className="text-lg font-bold text-green-600 dark:text-green-400">
            {Math.round(((stats.analyzed_articles || 0) / (stats.total_articles || 1)) * 100)}%
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">AI анализ</div>
        </div>
      </div>
      
      <div className="space-y-2">
        <h4 className="text-xs font-medium text-gray-700 dark:text-gray-300 uppercase tracking-wider">
          Топ темы
        </h4>
        {Object.entries(stats.articles_by_topic || {})
          .sort(([, a], [, b]) => b - a)
          .slice(0, 3)
          .map(([topic, count]) => {
            const isActive = activeFilters.topic === topic;
            const topicLabel = topic === 'technology' ? 'Технологии' :
                             topic === 'politics' ? 'Политика' :
                             topic === 'economics' ? 'Экономика' :
                             topic === 'science' ? 'Наука' :
                             topic === 'business' ? 'Бизнес' :
                             topic === 'war' ? 'Война' :
                             topic;
            
            return (
              <button
                key={topic}
                onClick={() => handleTopicClick(topic)}
                className={`w-full flex items-center justify-between text-sm p-2 rounded-lg transition-all duration-200 ${
                  isActive 
                    ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300' 
                    : 'hover:bg-gray-100 dark:hover:bg-dark-700'
                }`}
              >
                <span className="text-gray-600 dark:text-gray-400 capitalize truncate">
                  {topicLabel}
                </span>
                <span className="font-medium text-gray-900 dark:text-white">{count}</span>
              </button>
            );
          })}
      </div>
    </div>
  );

  const renderTags = () => (
    <div className="space-y-2">
      {topTags.map((tagData, index) => {
        const isActive = activeFilters.search === tagData.tag;
        return (
          <button
            key={index}
            onClick={() => handleTagClick(tagData.tag)}
            className={`w-full flex items-center justify-between p-2 rounded-lg transition-all duration-200 ${
              isActive 
                ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800' 
                : 'bg-blue-50 dark:bg-blue-900/20 hover:bg-blue-100 dark:hover:bg-blue-900/30'
            }`}
          >
            <span className="text-sm text-gray-700 dark:text-gray-300 truncate flex-1 text-left">
              {tagData.tag}
            </span>
            <span className="text-sm font-medium text-blue-600 dark:text-blue-400 ml-2">
              {tagData.count}
            </span>
          </button>
        );
      })}
    </div>
  );

  const renderLocations = () => (
    <div className="space-y-2">
      {topLocations.map((locationData, index) => {
        const isActive = activeFilters.search === locationData.location;
        return (
          <button
            key={index}
            onClick={() => handleLocationClick(locationData.location)}
            className={`w-full flex items-center justify-between p-2 rounded-lg transition-all duration-200 ${
              isActive 
                ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 border border-green-200 dark:border-green-800' 
                : 'bg-green-50 dark:bg-green-900/20 hover:bg-green-100 dark:hover:bg-green-900/30'
            }`}
          >
            <span className="text-sm text-gray-700 dark:text-gray-300 truncate flex-1 flex items-center gap-1 text-left">
              {locationData.location}
            </span>
            <span className="text-sm font-medium text-green-600 dark:text-green-400 ml-2">
              {locationData.count}
            </span>
          </button>
        );
      })}
    </div>
  );

  const renderSources = () => (
    <div className="space-y-2">
      {topSources.map(([sourceName, count], index) => (
        <div
          key={index}
          className="flex items-center justify-between p-2 bg-purple-50 dark:bg-purple-900/20 rounded-lg"
        >
          <span className="text-sm text-gray-700 dark:text-gray-300 truncate flex-1">
            {sourceName}
          </span>
          <span className="text-sm font-medium text-purple-600 dark:text-purple-400 ml-2">
            {count}
          </span>
        </div>
      ))}
    </div>
  );

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return renderOverview();
      case 'tags':
        return renderTags();
      case 'locations':
        return renderLocations();
      case 'sources':
        return renderSources();
      default:
        return renderOverview();
    }
  };

  return (
    <div className={`bg-white dark:bg-dark-800 rounded-xl shadow-sm border border-gray-200 dark:border-dark-700 overflow-hidden animate-fade-in ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-dark-700">
        <div className="flex items-center gap-2 mb-3">
          <BarChart3 className="w-4 h-4 text-primary-600 dark:text-primary-400" />
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Аналитика</h3>
        </div>

        {/* Compact Tabs */}
        <div className="flex gap-1 bg-gray-100 dark:bg-dark-700 rounded-lg p-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 flex items-center justify-center gap-1 px-2 py-1.5 rounded-md text-xs font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-white dark:bg-dark-600 text-gray-900 dark:text-white shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                }`}
                title={tab.label}
              >
                <Icon className="w-3 h-3" />
              </button>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {renderContent()}
      </div>

      {/* Footer */}
      <div className="px-4 py-2 bg-gray-50 dark:bg-dark-700/50 border-t border-gray-200 dark:border-dark-600">
        <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
          Обновлено в реальном времени
        </div>
      </div>
    </div>
  );
}; 