import React from 'react';
import { useSubscription } from '../../contexts/SubscriptionContext';
import { useAuth } from '../../contexts/AuthContext';

interface UsageLimitsProps {
  compact?: boolean;
  showUpgradeButton?: boolean;
  onUpgrade?: () => void;
}

const UsageLimits: React.FC<UsageLimitsProps> = ({ 
  compact = false, 
  showUpgradeButton = true,
  onUpgrade 
}) => {
  const { usageStats, currentSubscription, checkLimit } = useSubscription();
  const { isAuthenticated } = useAuth();

  // Отладочная информация
  console.log('UsageLimits render:', { usageStats, currentSubscription, isAuthenticated });

  // Don't show anything for non-authenticated users
  if (!isAuthenticated) {
    return null;
  }

  // Show loading state if usageStats is not loaded yet
  if (!usageStats) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600 dark:text-gray-300">Загрузка...</span>
        </div>
      </div>
    );
  }

  const getProgressColor = (used: number, limit: number | null) => {
    if (limit === null) return 'bg-green-500';
    
    const percentage = (used / limit) * 100;
    if (percentage >= 90) return 'bg-red-500';
    if (percentage >= 75) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const getProgressPercentage = (used: number, limit: number | null) => {
    if (limit === null) return 0;
    return Math.min((used / limit) * 100, 100);
  };

  const formatLimit = (used: number, limit: number | null) => {
    if (limit === null) return `${used} / ∞`;
    return `${used} / ${limit}`;
  };

  const isNearLimit = (used: number, limit: number | null) => {
    if (limit === null) return false;
    return (used / limit) >= 0.8;
  };

  const limits = [
    {
      key: 'articles',
      label: 'Статьи сегодня',
      used: usageStats.daily_articles_read || 0,
      limit: usageStats.daily_articles_limit,
      icon: '📰'
    },
    {
      key: 'favorites',
      label: 'Избранное',
      used: usageStats.favorites_count || 0,
      limit: usageStats.favorites_limit,
      icon: '⭐'
    },
    {
      key: 'exports',
      label: 'Экспорт',
      used: usageStats.exports_count || 0,
      limit: usageStats.exports_limit,
      icon: '📄'
    }
  ];

  // Filter out unlimited features in compact mode
  const visibleLimits = compact 
    ? limits.filter(limit => limit.limit !== null)
    : limits;

  if (compact) {
    // Compact view for header
    const criticalLimits = visibleLimits.filter(limit => 
      isNearLimit(limit.used, limit.limit) || !checkLimit(limit.key as any)
    );

    if (criticalLimits.length === 0) {
      return null;
    }

    return (
      <div className="flex items-center space-x-2">
        {criticalLimits.map((limit) => (
          <div key={limit.key} className="flex items-center space-x-1">
            <span className="text-sm">{limit.icon}</span>
            <span className={`text-xs font-medium ${
              !checkLimit(limit.key as any) ? 'text-red-500' : 'text-yellow-500'
            }`}>
              {formatLimit(limit.used, limit.limit)}
            </span>
          </div>
        ))}
        {showUpgradeButton && criticalLimits.length > 0 && (
          <button
            onClick={onUpgrade}
            className="text-xs bg-blue-500 hover:bg-blue-600 text-white px-2 py-1 rounded-md transition-colors"
          >
            Upgrade
          </button>
        )}
      </div>
    );
  }

  // Full view for dashboard/modal
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Использование
        </h3>
        <div className="text-sm text-gray-500 dark:text-gray-400">
          План: <span className="font-medium text-gray-900 dark:text-white">
            {currentSubscription?.plan.name || 'Бесплатный'}
          </span>
        </div>
      </div>

      <div className="space-y-6">
        {visibleLimits.map((limit) => {
          const isUnlimited = limit.limit === null;
          const isAtLimit = !checkLimit(limit.key as any);
          const percentage = getProgressPercentage(limit.used, limit.limit);
          
          return (
            <div key={limit.key}>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <span className="text-lg">{limit.icon}</span>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {limit.label}
                  </span>
                </div>
                <span className={`text-sm font-medium ${
                  isAtLimit ? 'text-red-500' : 
                  isNearLimit(limit.used, limit.limit) ? 'text-yellow-500' : 
                  'text-gray-600 dark:text-gray-300'
                }`}>
                  {formatLimit(limit.used, limit.limit)}
                </span>
              </div>
              
              {!isUnlimited && (
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-300 ${
                      getProgressColor(limit.used, limit.limit)
                    }`}
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              )}
              
              {isUnlimited && (
                <div className="text-xs text-green-600 dark:text-green-400 font-medium">
                  Безлимитно
                </div>
              )}
              
              {isAtLimit && (
                <div className="text-xs text-red-500 mt-1">
                  Лимит исчерпан
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Reset info */}
      <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Дневные лимиты обновляются: {new Date(usageStats.reset_date).toLocaleString('ru-RU')}
        </p>
      </div>

      {/* Upgrade button */}
      {showUpgradeButton && currentSubscription?.plan.plan_type !== 'enterprise' && (
        <div className="mt-6">
          <button
            onClick={onUpgrade}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg font-medium transition-colors"
          >
            Увеличить лимиты
          </button>
        </div>
      )}
    </div>
  );
};

export default UsageLimits; 