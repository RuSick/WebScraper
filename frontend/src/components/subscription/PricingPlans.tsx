import React, { useState } from 'react';
import { SubscriptionPlan } from '../../types/auth';
import { useSubscription } from '../../contexts/SubscriptionContext';
import { useAuth } from '../../contexts/AuthContext';

interface PricingPlansProps {
  onSelectPlan?: (plan: SubscriptionPlan) => void;
  showCurrentPlan?: boolean;
}

const PricingPlans: React.FC<PricingPlansProps> = ({ 
  onSelectPlan, 
  showCurrentPlan = true 
}) => {
  const { availablePlans, currentSubscription, isLoading } = useSubscription();
  const { isAuthenticated } = useAuth();
  const [selectedPlan, setSelectedPlan] = useState<number | null>(null);

  const handleSelectPlan = (plan: SubscriptionPlan) => {
    if (plan.plan_type === 'free') return;
    
    setSelectedPlan(plan.id);
    onSelectPlan?.(plan);
  };

  const formatPrice = (price: number, period: string) => {
    if (price === 0) return 'Бесплатно';
    
    const periodText = {
      monthly: '/месяц',
      yearly: '/год',
      lifetime: 'навсегда'
    }[period] || '';
    
    return `${price} BYN${periodText}`;
  };

  const getPlanIcon = (planType: string) => {
    switch (planType) {
      case 'free':
        return '🆓';
      case 'basic':
        return '⭐';
      case 'premium':
        return '💎';
      case 'enterprise':
        return '🏢';
      default:
        return '📦';
    }
  };

  const isCurrentPlan = (plan: SubscriptionPlan) => {
    return currentSubscription?.plan.id === plan.id;
  };

  const canUpgrade = (plan: SubscriptionPlan) => {
    if (!currentSubscription) return plan.plan_type !== 'free';
    
    const planOrder = { free: 0, basic: 1, premium: 2, enterprise: 3 };
    const currentOrder = planOrder[currentSubscription.plan.plan_type];
    const targetOrder = planOrder[plan.plan_type];
    
    return targetOrder > currentOrder;
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Отладочная информация
  console.log('PricingPlans render:', { availablePlans, isLoading, currentSubscription });

  // Безопасная проверка availablePlans
  const plansArray = Array.isArray(availablePlans) ? availablePlans : [];

  if (!plansArray || plansArray.length === 0) {
    return (
      <div className="py-12">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            Выберите подходящий план
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto mb-8">
            Получите доступ ко всем возможностям MediaScope. Все планы включают 7 дней бесплатного пробного периода.
          </p>
          <div className="bg-yellow-100 dark:bg-yellow-900 border border-yellow-400 dark:border-yellow-600 text-yellow-700 dark:text-yellow-300 px-4 py-3 rounded">
            Планы подписки временно недоступны. Попробуйте обновить страницу.
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="py-12">
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          Выберите подходящий план
        </h2>
        <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
          Получите доступ ко всем возможностям MediaScope. Все планы включают 7 дней бесплатного пробного периода.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto px-4">
        {plansArray.map((plan) => (
          <div
            key={plan.id}
            className={`
              relative bg-white dark:bg-gray-800 rounded-2xl shadow-lg border-2 transition-all duration-300 hover:shadow-xl
              ${plan.is_popular ? 'border-blue-500 ring-2 ring-blue-200 dark:ring-blue-800' : 'border-gray-200 dark:border-gray-700'}
              ${isCurrentPlan(plan) ? 'ring-2 ring-green-500 border-green-500' : ''}
              ${selectedPlan === plan.id ? 'scale-105' : 'hover:scale-102'}
            `}
          >
            {/* Popular badge */}
            {plan.is_popular && (
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                <span className="bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-medium">
                  Популярный
                </span>
              </div>
            )}

            {/* Current plan badge */}
            {isCurrentPlan(plan) && showCurrentPlan && (
              <div className="absolute -top-3 right-4">
                <span className="bg-green-500 text-white px-3 py-1 rounded-full text-sm font-medium">
                  Текущий
                </span>
              </div>
            )}

            <div className="p-6">
              {/* Plan header */}
              <div className="text-center mb-6">
                <div className="text-4xl mb-2">{getPlanIcon(plan.plan_type)}</div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                  {plan.name}
                </h3>
                <div className="text-3xl font-bold text-gray-900 dark:text-white">
                  {formatPrice(plan.price, plan.billing_period)}
                </div>
                {plan.price > 0 && (
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    {plan.billing_period === 'yearly' && 'Экономия 20%'}
                  </p>
                )}
              </div>

              {/* Plan description */}
              <p className="text-gray-600 dark:text-gray-300 text-sm mb-6 text-center">
                {plan.description}
              </p>

              {/* Features list */}
              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, index) => (
                  <li key={index} className="flex items-start">
                    <svg className="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    <span className="text-sm text-gray-600 dark:text-gray-300">{feature}</span>
                  </li>
                ))}
              </ul>

              {/* Limits info */}
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 mb-6">
                <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">Лимиты:</h4>
                <div className="space-y-1 text-xs text-gray-600 dark:text-gray-300">
                  <div>
                    Статей в день: {plan.limits.daily_articles === null ? 'Безлимит' : plan.limits.daily_articles}
                  </div>
                  <div>
                    Избранное: {plan.limits.favorites === null ? 'Безлимит' : plan.limits.favorites}
                  </div>
                  {plan.limits.exports !== null && (
                    <div>Экспорт: {plan.limits.exports}/месяц</div>
                  )}
                  {plan.limits.api_calls !== null && (
                    <div>API запросы: {plan.limits.api_calls}/день</div>
                  )}
                </div>
              </div>

              {/* Action button */}
              <button
                onClick={() => handleSelectPlan(plan)}
                disabled={!isAuthenticated || isCurrentPlan(plan) || !canUpgrade(plan)}
                className={`
                  w-full py-3 px-4 rounded-lg font-medium transition-all duration-200
                  ${isCurrentPlan(plan) 
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 cursor-not-allowed'
                    : canUpgrade(plan)
                      ? plan.is_popular
                        ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg hover:shadow-xl'
                        : 'bg-gray-900 hover:bg-gray-800 dark:bg-white dark:hover:bg-gray-100 text-white dark:text-gray-900'
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }
                  ${selectedPlan === plan.id ? 'ring-2 ring-blue-500' : ''}
                `}
              >
                {!isAuthenticated 
                  ? 'Войдите для выбора плана'
                  : isCurrentPlan(plan)
                    ? 'Текущий план'
                    : canUpgrade(plan)
                      ? plan.plan_type === 'free' 
                        ? 'Текущий план'
                        : 'Выбрать план'
                      : 'Недоступно'
                }
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Additional info */}
      <div className="text-center mt-12">
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
          Все планы включают 7 дней бесплатного пробного периода. Отмена в любое время.
        </p>
        <div className="flex justify-center space-x-6 text-sm text-gray-600 dark:text-gray-300">
          <div className="flex items-center">
            <svg className="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            Безопасные платежи
          </div>
          <div className="flex items-center">
            <svg className="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            Поддержка 24/7
          </div>
          <div className="flex items-center">
            <svg className="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
            </svg>
            Возврат средств
          </div>
        </div>
      </div>
    </div>
  );
};

export default PricingPlans; 