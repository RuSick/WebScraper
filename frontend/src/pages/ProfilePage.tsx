import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { User, Settings, Save, Eye, EyeOff } from 'lucide-react';
import { UserProfile, PasswordChangeData, UserStats } from '../types/auth';
import authService from '../services/authService';

export default function ProfilePage() {
  const { user, updateProfile } = useAuth();
  const [activeTab, setActiveTab] = useState<'profile' | 'password' | 'stats'>('profile');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [stats, setStats] = useState<UserStats | null>(null);

  // Profile form state
  const [profileData, setProfileData] = useState<Partial<UserProfile>>({
    bio: '',
    language: 'ru',
    theme: 'auto',
    timezone: 'Europe/Moscow',
    email_notifications: true,
    newsletter_subscription: true,
  });

  // Password form state
  const [passwordData, setPasswordData] = useState<PasswordChangeData>({
    old_password: '',
    new_password: '',
    new_password_confirm: '',
  });
  const [showPasswords, setShowPasswords] = useState({
    old: false,
    new: false,
    confirm: false,
  });

  // Load user profile data
  useEffect(() => {
    if (user?.profile) {
      setProfileData({
        bio: user.profile.bio || '',
        language: user.profile.language || 'ru',
        theme: user.profile.theme || 'auto',
        timezone: user.profile.timezone || 'Europe/Moscow',
        email_notifications: user.profile.email_notifications ?? true,
        newsletter_subscription: user.profile.newsletter_subscription ?? true,
      });
    }
  }, [user]);

  // Load user stats
  useEffect(() => {
    const loadStats = async () => {
      try {
        const userStats = await authService.getUserStats();
        setStats(userStats);
      } catch (error) {
        console.error('Failed to load stats:', error);
      }
    };

    if (activeTab === 'stats') {
      loadStats();
    }
  }, [activeTab]);

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage(null);

    try {
      await updateProfile(profileData);
      setMessage({ type: 'success', text: 'Профиль успешно обновлен!' });
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Ошибка обновления профиля' });
    } finally {
      setIsLoading(false);
    }
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage(null);

    if (passwordData.new_password !== passwordData.new_password_confirm) {
      setMessage({ type: 'error', text: 'Новые пароли не совпадают' });
      setIsLoading(false);
      return;
    }

    try {
      await authService.changePassword(passwordData);
      setMessage({ type: 'success', text: 'Пароль успешно изменен!' });
      setPasswordData({
        old_password: '',
        new_password: '',
        new_password_confirm: '',
      });
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Ошибка смены пароля' });
    } finally {
      setIsLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Необходима авторизация
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Пожалуйста, войдите в систему для доступа к профилю
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 mb-8">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
              <User className="w-8 h-8 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                {user.full_name}
              </h1>
              <p className="text-gray-600 dark:text-gray-400">{user.email}</p>
              <p className="text-sm text-gray-500 dark:text-gray-500">
                Зарегистрирован: {new Date(user.created_at).toLocaleDateString('ru-RU')}
              </p>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm">
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="flex space-x-8 px-6">
              <button
                onClick={() => setActiveTab('profile')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'profile'
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                <Settings className="w-4 h-4 inline mr-2" />
                Настройки профиля
              </button>
              <button
                onClick={() => setActiveTab('password')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'password'
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                Смена пароля
              </button>
              <button
                onClick={() => setActiveTab('stats')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'stats'
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                Статистика
              </button>
            </nav>
          </div>

          <div className="p-6">
            {/* Message */}
            {message && (
              <div className={`mb-6 p-4 rounded-md ${
                message.type === 'success'
                  ? 'bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-200 border border-green-200 dark:border-green-800'
                  : 'bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-200 border border-red-200 dark:border-red-800'
              }`}>
                {message.text}
              </div>
            )}

            {/* Profile Settings Tab */}
            {activeTab === 'profile' && (
              <form onSubmit={handleProfileSubmit} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    О себе
                  </label>
                  <textarea
                    value={profileData.bio || ''}
                    onChange={(e) => setProfileData(prev => ({ ...prev, bio: e.target.value }))}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                    placeholder="Расскажите о себе..."
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Язык
                    </label>
                    <select
                      value={profileData.language || 'ru'}
                      onChange={(e) => setProfileData(prev => ({ ...prev, language: e.target.value as 'ru' | 'en' }))}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                    >
                      <option value="ru">Русский</option>
                      <option value="en">English</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Тема
                    </label>
                    <select
                      value={profileData.theme || 'auto'}
                      onChange={(e) => setProfileData(prev => ({ ...prev, theme: e.target.value as 'light' | 'dark' | 'auto' }))}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                    >
                      <option value="auto">Автоматически</option>
                      <option value="light">Светлая</option>
                      <option value="dark">Темная</option>
                    </select>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center">
                    <input
                      id="email_notifications"
                      type="checkbox"
                      checked={profileData.email_notifications ?? true}
                      onChange={(e) => setProfileData(prev => ({ ...prev, email_notifications: e.target.checked }))}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="email_notifications" className="ml-2 block text-sm text-gray-900 dark:text-white">
                      Получать уведомления на email
                    </label>
                  </div>

                  <div className="flex items-center">
                    <input
                      id="newsletter_subscription"
                      type="checkbox"
                      checked={profileData.newsletter_subscription ?? true}
                      onChange={(e) => setProfileData(prev => ({ ...prev, newsletter_subscription: e.target.checked }))}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="newsletter_subscription" className="ml-2 block text-sm text-gray-900 dark:text-white">
                      Подписаться на новостную рассылку
                    </label>
                  </div>
                </div>

                <div className="flex justify-end">
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                  >
                    <Save className="w-4 h-4" />
                    {isLoading ? 'Сохранение...' : 'Сохранить'}
                  </button>
                </div>
              </form>
            )}

            {/* Password Change Tab */}
            {activeTab === 'password' && (
              <form onSubmit={handlePasswordSubmit} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Текущий пароль
                  </label>
                  <div className="relative">
                    <input
                      type={showPasswords.old ? 'text' : 'password'}
                      value={passwordData.old_password}
                      onChange={(e) => setPasswordData(prev => ({ ...prev, old_password: e.target.value }))}
                      className="w-full px-3 py-2 pr-10 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPasswords(prev => ({ ...prev, old: !prev.old }))}
                      className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    >
                      {showPasswords.old ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Новый пароль
                  </label>
                  <div className="relative">
                    <input
                      type={showPasswords.new ? 'text' : 'password'}
                      value={passwordData.new_password}
                      onChange={(e) => setPasswordData(prev => ({ ...prev, new_password: e.target.value }))}
                      className="w-full px-3 py-2 pr-10 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                      required
                      minLength={8}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPasswords(prev => ({ ...prev, new: !prev.new }))}
                      className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    >
                      {showPasswords.new ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Подтверждение нового пароля
                  </label>
                  <div className="relative">
                    <input
                      type={showPasswords.confirm ? 'text' : 'password'}
                      value={passwordData.new_password_confirm}
                      onChange={(e) => setPasswordData(prev => ({ ...prev, new_password_confirm: e.target.value }))}
                      className="w-full px-3 py-2 pr-10 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPasswords(prev => ({ ...prev, confirm: !prev.confirm }))}
                      className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    >
                      {showPasswords.confirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                <div className="flex justify-end">
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                  >
                    {isLoading ? 'Изменение...' : 'Изменить пароль'}
                  </button>
                </div>
              </form>
            )}

            {/* Stats Tab */}
            {activeTab === 'stats' && (
              <div className="space-y-6">
                {stats ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                      <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100">
                        Прочитано статей
                      </h3>
                      <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                        {stats.articles_read}
                      </p>
                    </div>

                    <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
                      <h3 className="text-lg font-semibold text-green-900 dark:text-green-100">
                        Избранных статей
                      </h3>
                      <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                        {stats.favorite_articles_count}
                      </p>
                    </div>

                    <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
                      <h3 className="text-lg font-semibold text-purple-900 dark:text-purple-100">
                        API запросов сегодня
                      </h3>
                      <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                        {stats.api_requests_today}
                      </p>
                    </div>

                    <div className="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg">
                      <h3 className="text-lg font-semibold text-yellow-900 dark:text-yellow-100">
                        Статус подписки
                      </h3>
                      <p className="text-lg font-bold text-yellow-600 dark:text-yellow-400">
                        {stats.subscription_status}
                      </p>
                    </div>

                    <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
                      <h3 className="text-lg font-semibold text-red-900 dark:text-red-100">
                        Дней до окончания
                      </h3>
                      <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                        {stats.subscription_days_remaining}
                      </p>
                    </div>

                    <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                        Последняя активность
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {new Date(stats.last_activity).toLocaleString('ru-RU')}
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-2 text-gray-600 dark:text-gray-400">Загрузка статистики...</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
} 