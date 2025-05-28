import React from 'react';
import { Tag, MapPin, Globe } from 'lucide-react';
import { ArticleStats } from '../types/api';

interface AnalyticsCardsProps {
  stats?: ArticleStats;
  className?: string;
}

export const AnalyticsCards: React.FC<AnalyticsCardsProps> = ({ stats, className = '' }) => {
  if (!stats) return null;

  const topTags = stats.top_tags?.slice(0, 10) || [];
  const topLocations = stats.top_locations?.slice(0, 8) || [];
  const topSources = Object.entries(stats.articles_by_source || {})
    .sort(([, a], [, b]) => b - a)
    .slice(0, 6);

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Popular Tags */}
      {topTags.length > 0 && (
        <div className="bg-white dark:bg-dark-800 rounded-xl shadow-sm border border-gray-200 dark:border-dark-700 p-6 animate-fade-in">
          <div className="flex items-center gap-2 mb-4">
            <Tag className="w-5 h-5 text-primary-600 dark:text-primary-400" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Популярные теги</h3>
          </div>
          
          <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-hide">
            {topTags.map((tagData, index) => (
              <div
                key={index}
                className="flex-shrink-0 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800 hover:shadow-md transition-all duration-200 cursor-pointer group"
              >
                <div className="text-center min-w-[120px]">
                  <div className="text-2xl font-bold text-blue-600 dark:text-blue-400 group-hover:scale-110 transition-transform duration-200">
                    {tagData.count}
                  </div>
                  <div className="text-sm text-gray-700 dark:text-gray-300 font-medium mt-1">
                    {tagData.tag}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Popular Locations */}
      {topLocations.length > 0 && (
        <div className="bg-white dark:bg-dark-800 rounded-xl shadow-sm border border-gray-200 dark:border-dark-700 p-6 animate-fade-in">
          <div className="flex items-center gap-2 mb-4">
            <MapPin className="w-5 h-5 text-green-600 dark:text-green-400" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Популярные локации</h3>
          </div>
          
          <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-hide">
            {topLocations.map((locationData, index) => (
              <div
                key={index}
                className="flex-shrink-0 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800 hover:shadow-md transition-all duration-200 cursor-pointer group"
              >
                <div className="text-center min-w-[120px]">
                  <div className="text-2xl font-bold text-green-600 dark:text-green-400 group-hover:scale-110 transition-transform duration-200">
                    {locationData.count}
                  </div>
                  <div className="text-sm text-gray-700 dark:text-gray-300 font-medium mt-1 flex items-center justify-center gap-1">
                    <span>📍</span>
                    {locationData.location}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Top Sources */}
      {topSources.length > 0 && (
        <div className="bg-white dark:bg-dark-800 rounded-xl shadow-sm border border-gray-200 dark:border-dark-700 p-6 animate-fade-in">
          <div className="flex items-center gap-2 mb-4">
            <Globe className="w-5 h-5 text-purple-600 dark:text-purple-400" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Активные источники</h3>
          </div>
          
          <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-hide">
            {topSources.map(([sourceName, count], index) => (
              <div
                key={index}
                className="flex-shrink-0 bg-gradient-to-r from-purple-50 to-violet-50 dark:from-purple-900/20 dark:to-violet-900/20 rounded-lg p-4 border border-purple-200 dark:border-purple-800 hover:shadow-md transition-all duration-200 cursor-pointer group"
              >
                <div className="text-center min-w-[140px]">
                  <div className="text-2xl font-bold text-purple-600 dark:text-purple-400 group-hover:scale-110 transition-transform duration-200">
                    {count}
                  </div>
                  <div className="text-sm text-gray-700 dark:text-gray-300 font-medium mt-1">
                    {sourceName}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}; 