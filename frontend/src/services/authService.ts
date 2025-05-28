import axios from 'axios';
import {
  User,
  UserProfile,
  LoginCredentials,
  RegisterData,
  AuthResponse,
  PasswordChangeData,
  SubscriptionPlan,
  UserSubscription,
  FavoriteArticle,
  UserStats,
  DashboardData,
  AUTH_ENDPOINTS,
  UsageStats,
  PaymentMethod,
  PaymentIntent,
  SubscriptionDashboardData
} from '../types/auth';

// Create axios instance for auth
const authApi = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management
export const tokenManager = {
  getToken(): string | null {
    return localStorage.getItem('auth_token');
  },

  setToken(token: string): void {
    localStorage.setItem('auth_token', token);
  },

  removeToken(): void {
    localStorage.removeItem('auth_token');
  },

  isTokenValid(): boolean {
    const token = this.getToken();
    return !!token;
  }
};

// Request interceptor to add auth token
authApi.interceptors.request.use(
  (config) => {
    const token = tokenManager.getToken();
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    console.log(`🔐 Auth API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ Auth API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for auth errors
authApi.interceptors.response.use(
  (response) => {
    console.log(`✅ Auth API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ Auth API Response Error:', error.response?.status, error.message);
    
    // Handle 401 errors (unauthorized)
    if (error.response?.status === 401) {
      tokenManager.removeToken();
      // Redirect to login page or emit logout event
      window.dispatchEvent(new CustomEvent('auth:logout'));
    }
    
    return Promise.reject(error);
  }
);

// Auth service functions
export const authService = {
  // Authentication
  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await authApi.post(AUTH_ENDPOINTS.register, data);
    const authData = response.data;
    
    // Save token
    tokenManager.setToken(authData.token);
    
    return authData;
  },

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await authApi.post(AUTH_ENDPOINTS.login, credentials);
    const authData = response.data;
    
    // Save token
    tokenManager.setToken(authData.token);
    
    return authData;
  },

  async logout(): Promise<void> {
    try {
      await authApi.post(AUTH_ENDPOINTS.logout);
    } catch (error) {
      console.warn('Logout request failed, but continuing with local logout');
    } finally {
      tokenManager.removeToken();
    }
  },

  // Profile management
  async getProfile(): Promise<User> {
    const response = await authApi.get(AUTH_ENDPOINTS.profile);
    return response.data;
  },

  async updateProfile(data: Partial<UserProfile>): Promise<UserProfile> {
    const response = await authApi.patch(AUTH_ENDPOINTS.profileUpdate, data);
    return response.data;
  },

  async changePassword(data: PasswordChangeData): Promise<void> {
    await authApi.post(AUTH_ENDPOINTS.changePassword, data);
  },

  // Statistics and dashboard
  async getUserStats(): Promise<UserStats> {
    const response = await authApi.get(AUTH_ENDPOINTS.stats);
    return response.data;
  },

  async getDashboardData(): Promise<DashboardData> {
    const response = await authApi.get(AUTH_ENDPOINTS.dashboard);
    return response.data;
  },

  // Subscriptions
  async getSubscriptionPlans(): Promise<SubscriptionPlan[]> {
    const response = await authApi.get(AUTH_ENDPOINTS.subscriptionPlans);
    return response.data.results || response.data;
  },

  async getUserSubscriptions(): Promise<UserSubscription[]> {
    const response = await authApi.get(AUTH_ENDPOINTS.subscriptions);
    return response.data.results || response.data;
  },

  // Favorites
  async getFavoriteArticles(): Promise<FavoriteArticle[]> {
    const response = await authApi.get(AUTH_ENDPOINTS.favorites);
    return response.data.results || response.data;
  },

  async toggleFavoriteArticle(articleId: number): Promise<{ message: string; is_favorite: boolean }> {
    const response = await authApi.post(AUTH_ENDPOINTS.toggleFavorite(articleId));
    return response.data;
  },

  async checkFavoriteArticle(articleId: number): Promise<{ is_favorite: boolean }> {
    const response = await authApi.get(AUTH_ENDPOINTS.checkFavorite(articleId));
    return response.data;
  },

  async addFavoriteArticle(articleId: number, notes?: string): Promise<FavoriteArticle> {
    const response = await authApi.post(AUTH_ENDPOINTS.favorites, {
      article: articleId,
      notes: notes || ''
    });
    return response.data;
  },

  async removeFavoriteArticle(favoriteId: number): Promise<void> {
    await authApi.delete(`${AUTH_ENDPOINTS.favorites}${favoriteId}/`);
  },

  async updateFavoriteArticle(favoriteId: number, notes: string): Promise<FavoriteArticle> {
    const response = await authApi.patch(`${AUTH_ENDPOINTS.favorites}${favoriteId}/`, {
      notes
    });
    return response.data;
  },

  // Utility functions
  isAuthenticated(): boolean {
    return tokenManager.isTokenValid();
  },

  getCurrentToken(): string | null {
    return tokenManager.getToken();
  }
};

// Subscription API methods
export const subscriptionApi = {
  // Get available subscription plans
  getPlans: async (): Promise<SubscriptionPlan[]> => {
    const response = await authApi.get('/api/auth/subscription-plans/');
    return response.data.results || response.data;
  },

  // Get current user subscription
  getCurrentSubscription: async (): Promise<UserSubscription | null> => {
    const response = await authApi.get('/api/auth/subscription/current/');
    return response.data;
  },

  // Get usage statistics
  getUsageStats: async (): Promise<UsageStats> => {
    const response = await authApi.get('/api/auth/subscription/usage/');
    return response.data;
  },

  // Get subscription dashboard data
  getDashboardData: async (): Promise<SubscriptionDashboardData> => {
    const response = await authApi.get('/api/auth/subscription/dashboard/');
    return response.data;
  },

  // Create payment intent for subscription upgrade
  createPaymentIntent: async (planId: number, paymentMethod?: string): Promise<PaymentIntent> => {
    const response = await authApi.post('/api/auth/subscription/upgrade/', {
      plan_id: planId,
      payment_method: paymentMethod
    });
    return response.data;
  },

  // Confirm payment and activate subscription
  confirmPayment: async (paymentIntentId: string): Promise<UserSubscription> => {
    const response = await authApi.post('/api/auth/subscription/confirm-payment/', {
      payment_intent_id: paymentIntentId
    });
    return response.data;
  },

  // Cancel subscription
  cancelSubscription: async (): Promise<void> => {
    await authApi.post('/api/auth/subscription/cancel/');
  },

  // Reactivate subscription
  reactivateSubscription: async (): Promise<UserSubscription> => {
    const response = await authApi.post('/api/auth/subscription/reactivate/');
    return response.data;
  },

  // Check if user can perform action based on limits
  checkLimit: async (feature: 'articles' | 'favorites' | 'exports' | 'api'): Promise<boolean> => {
    const response = await authApi.get(`/api/auth/subscription/check-limit/${feature}/`);
    return response.data.allowed;
  },

  // Get payment methods
  getPaymentMethods: async (): Promise<PaymentMethod[]> => {
    const response = await authApi.get('/api/auth/subscription/payment-methods/');
    return response.data;
  },

  // Add payment method
  addPaymentMethod: async (paymentMethodData: any): Promise<PaymentMethod> => {
    const response = await authApi.post('/api/auth/subscription/payment-methods/', paymentMethodData);
    return response.data;
  },

  // Delete payment method
  deletePaymentMethod: async (paymentMethodId: string): Promise<void> => {
    await authApi.delete(`/api/auth/subscription/payment-methods/${paymentMethodId}/`);
  },

  // Get payment history
  getPaymentHistory: async (): Promise<any[]> => {
    const response = await authApi.get('/api/auth/subscription/payments/');
    return response.data;
  }
};

export default authService; 