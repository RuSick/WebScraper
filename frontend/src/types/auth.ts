// User types
export interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  full_name: string;
  is_email_verified: boolean;
  created_at: string;
  profile: UserProfile;
}

export interface UserProfile {
  avatar: string | null;
  bio: string;
  language: 'ru' | 'en';
  theme: 'light' | 'dark' | 'auto';
  timezone: string;
  email_notifications: boolean;
  newsletter_subscription: boolean;
  articles_read: number;
  last_activity: string;
}

// Authentication types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  password: string;
  password_confirm: string;
}

export interface AuthResponse {
  message: string;
  user: User;
  token: string;
}

export interface PasswordChangeData {
  old_password: string;
  new_password: string;
  new_password_confirm: string;
}

// Subscription types
export interface SubscriptionPlan {
  id: number;
  name: string;
  slug: string;
  plan_type: 'free' | 'basic' | 'premium' | 'enterprise';
  description: string;
  price: string;
  billing_period: 'monthly' | 'yearly' | 'lifetime';
  features: string[];
  is_popular: boolean;
}

export interface UserSubscription {
  id: number;
  plan: SubscriptionPlan;
  status: 'active' | 'expired' | 'cancelled' | 'pending';
  start_date: string;
  end_date: string;
  is_active: boolean;
  days_remaining: number;
  auto_renewal: boolean;
  created_at: string;
}

// Favorite articles
export interface FavoriteArticle {
  id: number;
  article: number;
  article_title: string;
  article_url: string;
  article_source: string;
  article_published_at: string;
  notes: string;
  created_at: string;
}

// User statistics
export interface UserStats {
  articles_read: number;
  favorite_articles_count: number;
  custom_sources_count: number;
  subscription_status: string;
  subscription_days_remaining: number;
  api_requests_today: number;
  registration_date: string;
  last_activity: string;
}

// Dashboard data
export interface DashboardData {
  user: User;
  subscription: UserSubscription | null;
  recent_favorites: FavoriteArticle[];
  api_usage_week: Array<{
    day: string;
    requests_count: number;
  }>;
  stats: {
    total_favorites: number;
    total_custom_sources: number;
    api_requests_today: number;
  };
}

// Auth context types
export interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  updateProfile: (data: Partial<UserProfile>) => Promise<void>;
  changePassword: (data: PasswordChangeData) => Promise<void>;
}

// API endpoints for auth
export const AUTH_ENDPOINTS = {
  register: '/api/auth/register/',
  login: '/api/auth/login/',
  logout: '/api/auth/logout/',
  profile: '/api/auth/profile/',
  profileUpdate: '/api/auth/profile/update/',
  changePassword: '/api/auth/change-password/',
  stats: '/api/auth/stats/',
  dashboard: '/api/auth/dashboard/',
  subscriptionPlans: '/api/auth/subscription-plans/',
  subscriptions: '/api/auth/subscriptions/',
  favorites: '/api/auth/favorites/',
  toggleFavorite: (articleId: number) => `/api/auth/articles/${articleId}/toggle-favorite/`,
  checkFavorite: (articleId: number) => `/api/auth/articles/${articleId}/check-favorite/`,
} as const; 