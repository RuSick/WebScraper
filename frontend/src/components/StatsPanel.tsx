import React from 'react';
import { BarChart3, FileText, Brain, TrendingUp } from 'lucide-react';
import { ArticleStats } from '../types/api';
import { LoadingSpinner } from './LoadingSpinner';

interface StatsPanelProps {
  stats?: ArticleStats;
  isLoading: boolean;
  className?: string;
}

export const StatsPanel: React.FC<StatsPanelProps> = ({
  stats,
  isLoading,
  className = '',
}) => {
  if (isLoading) {
    return (
      <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-6 ${className}`}>
        <div className="flex items-center justify-center">
          <LoadingSpinner size="md" />
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-6 ${className}`}>
        <div className="flex items-center gap-2 text-gray-500">
          <BarChart3 className="w-5 h-5" />
          <span className="text-sm">Статистика недоступна</span>
        </div>
      </div>
    );
  }

  // Безопасное получение данных с проверками
  const topicsDistribution = stats.articles_by_topic || {};
  const totalArticles = stats.total_articles || 0;
  const analyzedArticles = stats.analyzed_articles || 0;
  const recentArticlesCount = stats.recent_articles_count || 0;

  const topTopics = Object.entries(topicsDistribution)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 5);

  const analysisPercentage = totalArticles > 0 
    ? Math.round((analyzedArticles / totalArticles) * 100)
    : 0;

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-primary-600" />
          <h3 className="font-semibold text-gray-900">Статистика</h3>
        </div>
      </div>

      {/* Stats */}
      <div className="p-4 space-y-4">
        {/* Total articles */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-gray-500" />
            <span className="text-sm text-gray-600">Всего статей</span>
          </div>
          <span className="font-semibold text-gray-900">
            {totalArticles.toLocaleString()}
          </span>
        </div>

        {/* Analyzed articles */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain className="w-4 h-4 text-green-500" />
            <span className="text-sm text-gray-600">Проанализировано</span>
          </div>
          <div className="text-right">
            <span className="font-semibold text-gray-900">
              {analyzedArticles.toLocaleString()}
            </span>
            <div className="text-xs text-green-600">
              {analysisPercentage}%
            </div>
          </div>
        </div>

        {/* Recent articles */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-blue-500" />
            <span className="text-sm text-gray-600">За сегодня</span>
          </div>
          <span className="font-semibold text-gray-900">
            {recentArticlesCount}
          </span>
        </div>

        {/* Progress bar */}
        <div className="pt-2">
          <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
            <span>Прогресс анализа</span>
            <span>{analysisPercentage}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-green-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${analysisPercentage}%` }}
            />
          </div>
        </div>

        {/* Top topics */}
        {topTopics.length > 0 && (
          <div className="pt-4 border-t border-gray-200">
            <h4 className="text-sm font-medium text-gray-900 mb-3">
              Популярные темы
            </h4>
            <div className="space-y-2">
              {topTopics.map(([topic, count]) => (
                <div key={topic} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 capitalize">
                    {topic === 'technology' ? 'Технологии' :
                     topic === 'politics' ? 'Политика' :
                     topic === 'economics' ? 'Экономика' :
                     topic === 'science' ? 'Наука' :
                     topic === 'business' ? 'Бизнес' :
                     topic}
                  </span>
                  <span className="text-sm font-medium text-gray-900">
                    {count}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}; 