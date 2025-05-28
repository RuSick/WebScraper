import React from 'react';
import { Newspaper, TrendingUp, Zap, Brain, Database } from 'lucide-react';
import { ArticleStats } from '../types/api';

interface StatsPanelProps {
  stats?: ArticleStats;
  className?: string;
}

export const StatsPanel: React.FC<StatsPanelProps> = ({ stats, className = '' }) => {
  if (!stats) {
    return (
      <div className={`bg-white dark:bg-dark-800 rounded-xl shadow-sm border border-gray-200 dark:border-dark-700 p-6 animate-fade-in ${className}`}>
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-5 h-5 text-primary-600 dark:text-primary-400" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Статистика</h3>
        </div>
        <div className="space-y-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="h-4 bg-gray-200 dark:bg-dark-600 rounded w-3/4 mb-2"></div>
              <div className="h-6 bg-gray-200 dark:bg-dark-600 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const statItems = [
    {
      label: 'Всего статей',
      value: stats.total_articles?.toLocaleString() || '0',
      icon: Newspaper,
      color: 'text-blue-600 dark:text-blue-400',
      bgColor: 'bg-blue-50 dark:bg-blue-900/20',
      change: '+12% за неделю'
    },
    {
      label: 'Проанализировано spaCy',
      value: stats.analyzed_articles?.toLocaleString() || '0',
      icon: Brain,
      color: 'text-green-600 dark:text-green-400',
      bgColor: 'bg-green-50 dark:bg-green-900/20',
      change: `${Math.round(((stats.analyzed_articles || 0) / (stats.total_articles || 1)) * 100)}%`
    },
    {
      label: 'Активных источников',
      value: Object.keys(stats.articles_by_source || {}).length.toString(),
      icon: Database,
      color: 'text-purple-600 dark:text-purple-400',
      bgColor: 'bg-purple-50 dark:bg-purple-900/20',
      change: 'Онлайн'
    },
    {
      label: 'Уникальных тем',
      value: Object.keys(stats.articles_by_topic || {}).length.toString(),
      icon: TrendingUp,
      color: 'text-orange-600 dark:text-orange-400',
      bgColor: 'bg-orange-50 dark:bg-orange-900/20',
      change: 'Активно'
    }
  ];

  return (
    <div className={`bg-white dark:bg-dark-800 rounded-xl shadow-sm border border-gray-200 dark:border-dark-700 overflow-hidden animate-fade-in ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-dark-700 bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/20 dark:to-blue-900/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary-600 dark:bg-primary-500 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-4 h-4 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Статистика системы</h3>
              <p className="text-xs text-gray-600 dark:text-gray-400">Обновлено в реальном времени</p>
            </div>
          </div>
          
          {/* AI Status */}
          <div className="flex items-center gap-2 px-3 py-1.5 bg-green-100 dark:bg-green-900/30 rounded-full">
            <Zap className="w-3 h-3 text-green-600 dark:text-green-400" />
            <span className="text-xs font-medium text-green-700 dark:text-green-300">AI активен</span>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="p-4 space-y-4">
        {statItems.map((item, index) => {
          const Icon = item.icon;
          
          return (
            <div
              key={index}
              className="group p-4 rounded-lg border border-gray-100 dark:border-dark-600 hover:border-gray-200 dark:hover:border-dark-500 transition-all duration-200 hover:shadow-sm"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 ${item.bgColor} rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform duration-200`}>
                    <Icon className={`w-5 h-5 ${item.color}`} />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">
                      {item.label}
                    </p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {item.value}
                    </p>
                  </div>
                </div>
                
                <div className="text-right">
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    item.change.includes('%') 
                      ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300'
                      : 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                  }`}>
                    {item.change}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer */}
      <div className="px-4 py-3 bg-gray-50 dark:bg-dark-700/50 border-t border-gray-200 dark:border-dark-600">
        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
          <span>Последнее обновление: сейчас</span>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span>Система работает</span>
          </div>
        </div>
      </div>
    </div>
  );
}; 