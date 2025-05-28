import React, { useState } from 'react';
import { Tag, MapPin, Globe, BarChart3 } from 'lucide-react';
import { ArticleStats } from '../types/api';

interface AnalyticsDashboardProps {
  stats?: ArticleStats;
  className?: string;
}

type TabType = 'tags' | 'locations' | 'sources';

export const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({ stats, className = '' }) => {
  const [activeTab, setActiveTab] = useState<TabType>('tags');

  if (!stats) return null;

  const topTags = stats.top_tags?.slice(0, 8) || [];
  const topLocations = stats.top_locations?.slice(0, 8) || [];
  const topSources = Object.entries(stats.articles_by_source || {})
    .sort(([, a], [, b]) => b - a)
    .slice(0, 8);

  const tabs = [
    {
      id: 'tags' as TabType,
      label: 'Теги',
      icon: Tag,
      count: topTags.length,
      color: 'text-blue-600 dark:text-blue-400',
      bgColor: 'bg-blue-50 dark:bg-blue-900/20',
      borderColor: 'border-blue-200 dark:border-blue-800'
    },
    {
      id: 'locations' as TabType,
      label: 'Локации',
      icon: MapPin,
      count: topLocations.length,
      color: 'text-green-600 dark:text-green-400',
      bgColor: 'bg-green-50 dark:bg-green-900/20',
      borderColor: 'border-green-200 dark:border-green-800'
    },
    {
      id: 'sources' as TabType,
      label: 'Источники',
      icon: Globe,
      count: topSources.length,
      color: 'text-purple-600 dark:text-purple-400',
      bgColor: 'bg-purple-50 dark:bg-purple-900/20',
      borderColor: 'border-purple-200 dark:border-purple-800'
    }
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'tags':
        return (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {topTags.map((tagData, index) => (
              <div
                key={index}
                className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-lg p-3 border border-blue-200 dark:border-blue-800 hover:shadow-md transition-all duration-200 cursor-pointer group"
              >
                <div className="text-center">
                  <div className="text-xl font-bold text-blue-600 dark:text-blue-400 group-hover:scale-110 transition-transform duration-200">
                    {tagData.count}
                  </div>
                  <div className="text-xs text-gray-700 dark:text-gray-300 font-medium mt-1 truncate">
                    {tagData.tag}
                  </div>
                </div>
              </div>
            ))}
          </div>
        );

      case 'locations':
        return (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {topLocations.map((locationData, index) => (
              <div
                key={index}
                className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-lg p-3 border border-green-200 dark:border-green-800 hover:shadow-md transition-all duration-200 cursor-pointer group"
              >
                <div className="text-center">
                  <div className="text-xl font-bold text-green-600 dark:text-green-400 group-hover:scale-110 transition-transform duration-200">
                    {locationData.count}
                  </div>
                  <div className="text-xs text-gray-700 dark:text-gray-300 font-medium mt-1 flex items-center justify-center gap-1 truncate">
                    <span>📍</span>
                    {locationData.location}
                  </div>
                </div>
              </div>
            ))}
          </div>
        );

      case 'sources':
        return (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {topSources.map(([sourceName, count], index) => (
              <div
                key={index}
                className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-lg p-3 border border-purple-200 dark:border-purple-800 hover:shadow-md transition-all duration-200 cursor-pointer group"
              >
                <div className="text-center">
                  <div className="text-xl font-bold text-purple-600 dark:text-purple-400 group-hover:scale-110 transition-transform duration-200">
                    {count}
                  </div>
                  <div className="text-xs text-gray-700 dark:text-gray-300 font-medium mt-1 truncate">
                    {sourceName}
                  </div>
                </div>
              </div>
            ))}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className={`bg-white dark:bg-dark-800 rounded-xl shadow-sm border border-gray-200 dark:border-dark-700 overflow-hidden animate-fade-in ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-dark-700">
        <div className="flex items-center gap-2 mb-3">
          <BarChart3 className="w-5 h-5 text-primary-600 dark:text-primary-400" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Аналитика</h3>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 bg-gray-100 dark:bg-dark-700 rounded-lg p-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-white dark:bg-dark-600 text-gray-900 dark:text-white shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden sm:inline">{tab.label}</span>
                <span className="bg-gray-200 dark:bg-dark-600 text-gray-600 dark:text-gray-400 text-xs rounded-full px-2 py-0.5 min-w-[20px]">
                  {tab.count}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {renderContent()}
      </div>
    </div>
  );
}; 