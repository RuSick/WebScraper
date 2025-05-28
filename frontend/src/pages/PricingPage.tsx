import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import PricingPlans from '../components/subscription/PricingPlans';
import UsageLimits from '../components/subscription/UsageLimits';
import { SubscriptionPlan } from '../types/auth';
import { useSubscription } from '../contexts/SubscriptionContext';
import { useAuth } from '../contexts/AuthContext';

const PricingPage: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const { upgradePlan, isLoading } = useSubscription();
  const [selectedPlan, setSelectedPlan] = useState<SubscriptionPlan | null>(null);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [paymentLoading, setPaymentLoading] = useState(false);

  const handleSelectPlan = (plan: SubscriptionPlan) => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    setSelectedPlan(plan);
    setShowPaymentModal(true);
  };

  const handlePayment = async () => {
    if (!selectedPlan) return;

    try {
      setPaymentLoading(true);
      
      // Create payment intent
      const paymentIntent = await upgradePlan(selectedPlan.id);
      
      // Here you would integrate with actual payment processor
      // For now, we'll simulate successful payment
      console.log('Payment intent created:', paymentIntent);
      
      // Close modal and show success
      setShowPaymentModal(false);
      setSelectedPlan(null);
      
      // Show success message (you could use a toast library)
      alert('Подписка успешно активирована!');
      
    } catch (error: any) {
      console.error('Payment failed:', error);
      alert('Ошибка при оплате: ' + error.message);
    } finally {
      setPaymentLoading(false);
    }
  };

  const closeModal = () => {
    setShowPaymentModal(false);
    setSelectedPlan(null);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Hero section */}
      <div className="bg-gradient-to-br from-blue-600 to-purple-700 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-6">
            Выберите план для MediaScope
          </h1>
          <p className="text-xl md:text-2xl text-blue-100 max-w-3xl mx-auto">
            Получите доступ к лучшим новостям Беларуси с персональными рекомендациями и расширенными возможностями
          </p>
        </div>
      </div>

      {/* Current usage (for authenticated users) */}
      {isAuthenticated && (
        <div className="max-w-4xl mx-auto px-4 -mt-8 relative z-10">
          <UsageLimits 
            showUpgradeButton={false}
            onUpgrade={() => {
              const element = document.getElementById('pricing-plans');
              element?.scrollIntoView({ behavior: 'smooth' });
            }}
          />
        </div>
      )}

      {/* Pricing plans */}
      <div id="pricing-plans" className="max-w-7xl mx-auto px-4">
        <PricingPlans onSelectPlan={handleSelectPlan} />
      </div>

      {/* Features comparison */}
      <div className="bg-white dark:bg-gray-800 py-16">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12">
            Сравнение возможностей
          </h2>
          
          <div className="overflow-x-auto">
            <table className="w-full border-collapse border border-gray-300 dark:border-gray-600">
              <thead>
                <tr className="bg-gray-50 dark:bg-gray-700">
                  <th className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-left text-gray-900 dark:text-white">
                    Возможности
                  </th>
                  <th className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-center text-gray-900 dark:text-white">
                    Бесплатный
                  </th>
                  <th className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-center text-gray-900 dark:text-white">
                    Базовый
                  </th>
                  <th className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-center text-gray-900 dark:text-white">
                    Премиум
                  </th>
                  <th className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-center text-gray-900 dark:text-white">
                    Корпоративный
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-gray-900 dark:text-white">
                    Статей в день
                  </td>
                  <td className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-center text-gray-900 dark:text-white">10</td>
                  <td className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-center text-gray-900 dark:text-white">100</td>
                  <td className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-center text-gray-900 dark:text-white">∞</td>
                  <td className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-center text-gray-900 dark:text-white">∞</td>
                </tr>
                <tr className="bg-gray-50 dark:bg-gray-700">
                  <td className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-gray-900 dark:text-white">
                    Избранные статьи
                  </td>
                  <td className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-center text-gray-900 dark:text-white">10</td>
                  <td className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-center text-gray-900 dark:text-white">50</td>
                  <td className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-center text-gray-900 dark:text-white">∞</td>
                  <td className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-center text-gray-900 dark:text-white">∞</td>
                </tr>
                <tr>
                  <td className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-gray-900 dark:text-white">
                    Экспорт в PDF
                  </td>
                  <td className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-center text-gray-900 dark:text-white">❌</td>
                  <td className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-center text-gray-900 dark:text-white">5/месяц</td>
                  <td className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-center text-gray-900 dark:text-white">∞</td>
                  <td className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-center text-gray-900 dark:text-white">∞</td>
                </tr>
                <tr className="bg-gray-50 dark:bg-gray-700">
                  <td className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-gray-900 dark:text-white">
                    Персональные рекомендации
                  </td>
                  <td className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-center text-gray-900 dark:text-white">❌</td>
                  <td className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-center text-gray-900 dark:text-white">❌</td>
                  <td className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-center text-gray-900 dark:text-white">✅</td>
                  <td className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-center text-gray-900 dark:text-white">✅</td>
                </tr>
                <tr>
                  <td className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-gray-900 dark:text-white">
                    API доступ
                  </td>
                  <td className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-center text-gray-900 dark:text-white">❌</td>
                  <td className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-center text-gray-900 dark:text-white">❌</td>
                  <td className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-center text-gray-900 dark:text-white">❌</td>
                  <td className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-center text-gray-900 dark:text-white">✅</td>
                </tr>
                <tr className="bg-gray-50 dark:bg-gray-700">
                  <td className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-gray-900 dark:text-white">
                    Приоритетная поддержка
                  </td>
                  <td className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-center text-gray-900 dark:text-white">❌</td>
                  <td className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-center text-gray-900 dark:text-white">❌</td>
                  <td className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-center text-gray-900 dark:text-white">✅</td>
                  <td className="border border-gray-300 dark:border-gray-600 px-4 py-3 text-center text-gray-900 dark:text-white">✅</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Payment Modal */}
      {showPaymentModal && selectedPlan && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Оплата подписки
              </h3>
              <button
                onClick={closeModal}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="mb-6">
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                  {selectedPlan.name}
                </h4>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {selectedPlan.price} BYN
                  <span className="text-sm font-normal text-gray-500 dark:text-gray-400">
                    /{selectedPlan.billing_period === 'monthly' ? 'месяц' : 'год'}
                  </span>
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-300 mt-2">
                  7 дней бесплатного пробного периода
                </p>
              </div>
            </div>

            <div className="mb-6">
              <h4 className="font-medium text-gray-900 dark:text-white mb-3">
                Способы оплаты:
              </h4>
              <div className="space-y-2">
                <div className="flex items-center p-3 border border-gray-200 dark:border-gray-600 rounded-lg">
                  <input type="radio" name="payment" id="belkart" defaultChecked className="mr-3" />
                  <label htmlFor="belkart" className="flex items-center">
                    <span className="text-sm text-gray-900 dark:text-white">💳 Белкарт</span>
                  </label>
                </div>
                <div className="flex items-center p-3 border border-gray-200 dark:border-gray-600 rounded-lg">
                  <input type="radio" name="payment" id="visa" className="mr-3" />
                  <label htmlFor="visa" className="flex items-center">
                    <span className="text-sm text-gray-900 dark:text-white">💳 Visa/MasterCard</span>
                  </label>
                </div>
                <div className="flex items-center p-3 border border-gray-200 dark:border-gray-600 rounded-lg">
                  <input type="radio" name="payment" id="crypto" className="mr-3" />
                  <label htmlFor="crypto" className="flex items-center">
                    <span className="text-sm text-gray-900 dark:text-white">₿ Криптовалюта</span>
                  </label>
                </div>
              </div>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={closeModal}
                className="flex-1 py-2 px-4 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                Отмена
              </button>
              <button
                onClick={handlePayment}
                disabled={paymentLoading}
                className="flex-1 py-2 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-lg font-medium transition-colors"
              >
                {paymentLoading ? 'Обработка...' : 'Оплатить'}
              </button>
            </div>

            <p className="text-xs text-gray-500 dark:text-gray-400 text-center mt-4">
              Нажимая "Оплатить", вы соглашаетесь с условиями использования и политикой конфиденциальности
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default PricingPage; 