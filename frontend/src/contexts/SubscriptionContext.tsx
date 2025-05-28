import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { 
  SubscriptionContextType, 
  UserSubscription, 
  SubscriptionPlan, 
  UsageStats, 
  PaymentIntent 
} from '../types/auth';
import { subscriptionApi } from '../services/authService';
import { useAuth } from './AuthContext';

// Subscription state type
interface SubscriptionState {
  currentSubscription: UserSubscription | null;
  usageStats: UsageStats | null;
  availablePlans: SubscriptionPlan[];
  isLoading: boolean;
  error: string | null;
}

// Action types
type SubscriptionAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_SUBSCRIPTION'; payload: UserSubscription | null }
  | { type: 'SET_USAGE_STATS'; payload: UsageStats | null }
  | { type: 'SET_PLANS'; payload: SubscriptionPlan[] }
  | { type: 'UPDATE_USAGE'; payload: Partial<UsageStats> }
  | { type: 'RESET_STATE' };

// Initial state
const initialState: SubscriptionState = {
  currentSubscription: null,
  usageStats: null,
  availablePlans: [],
  isLoading: false,
  error: null,
};

// Reducer
function subscriptionReducer(state: SubscriptionState, action: SubscriptionAction): SubscriptionState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload, isLoading: false };
    case 'SET_SUBSCRIPTION':
      return { ...state, currentSubscription: action.payload };
    case 'SET_USAGE_STATS':
      return { ...state, usageStats: action.payload };
    case 'SET_PLANS':
      return { ...state, availablePlans: action.payload };
    case 'UPDATE_USAGE':
      return { 
        ...state, 
        usageStats: state.usageStats ? { ...state.usageStats, ...action.payload } : null 
      };
    case 'RESET_STATE':
      return initialState;
    default:
      return state;
  }
}

// Create context
const SubscriptionContext = createContext<SubscriptionContextType | undefined>(undefined);

// Provider component
interface SubscriptionProviderProps {
  children: ReactNode;
}

export function SubscriptionProvider({ children }: SubscriptionProviderProps) {
  const [state, dispatch] = useReducer(subscriptionReducer, initialState);
  const { user, isAuthenticated } = useAuth();

  // Load subscription data
  const loadSubscriptionData = async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'SET_ERROR', payload: null });

      console.log('Loading subscription data, isAuthenticated:', isAuthenticated);

      if (isAuthenticated) {
        // Load all subscription data in parallel for authenticated users
        console.log('Loading dashboard data and plans for authenticated user...');
        
        try {
          const [dashboardData, plans] = await Promise.all([
            subscriptionApi.getDashboardData(),
            subscriptionApi.getPlans()
          ]);

          console.log('Dashboard data received:', dashboardData);
          console.log('Plans received:', plans);

          dispatch({ type: 'SET_SUBSCRIPTION', payload: dashboardData.subscription });
          dispatch({ type: 'SET_USAGE_STATS', payload: dashboardData.usage });
          dispatch({ type: 'SET_PLANS', payload: plans });
        } catch (dashboardError) {
          console.error('Dashboard API failed, trying individual endpoints:', dashboardError);
          
          // Fallback: try individual endpoints
          const plans = await subscriptionApi.getPlans();
          console.log('Plans loaded as fallback:', plans);
          
          try {
            const currentSub = await subscriptionApi.getCurrentSubscription();
            const usageStats = await subscriptionApi.getUsageStats();
            console.log('Individual data loaded:', { currentSub, usageStats });
            
            dispatch({ type: 'SET_SUBSCRIPTION', payload: currentSub });
            dispatch({ type: 'SET_USAGE_STATS', payload: usageStats });
          } catch (individualError) {
            console.error('Individual endpoints also failed:', individualError);
            // Set default values for free plan
            dispatch({ type: 'SET_SUBSCRIPTION', payload: null });
            dispatch({ type: 'SET_USAGE_STATS', payload: {
              daily_articles_read: 0,
              daily_articles_limit: 10,
              favorites_count: 0,
              favorites_limit: 10,
              exports_count: 0,
              exports_limit: 0,
              api_calls_count: 0,
              api_calls_limit: 0,
              reset_date: new Date().toISOString()
            }});
          }
          
          dispatch({ type: 'SET_PLANS', payload: plans });
        }
      } else {
        // Load only plans for non-authenticated users
        console.log('Loading plans for non-authenticated user...');
        const plans = await subscriptionApi.getPlans();
        console.log('Plans loaded for non-authenticated user:', plans);
        dispatch({ type: 'SET_PLANS', payload: plans });
        dispatch({ type: 'SET_SUBSCRIPTION', payload: null });
        dispatch({ type: 'SET_USAGE_STATS', payload: null });
      }
    } catch (error: any) {
      console.error('Failed to load subscription data:', error);
      dispatch({ type: 'SET_ERROR', payload: error.message || 'Ошибка загрузки данных подписки' });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  // Upgrade to new plan
  const upgradePlan = async (planId: number): Promise<PaymentIntent> => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'SET_ERROR', payload: null });

      const paymentIntent = await subscriptionApi.createPaymentIntent(planId);
      
      // Reload subscription data after successful upgrade
      await loadSubscriptionData();
      
      return paymentIntent;
    } catch (error: any) {
      console.error('Failed to upgrade plan:', error);
      dispatch({ type: 'SET_ERROR', payload: error.message || 'Ошибка при обновлении плана' });
      throw error;
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  // Cancel subscription
  const cancelSubscription = async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'SET_ERROR', payload: null });

      await subscriptionApi.cancelSubscription();
      
      // Reload subscription data
      await loadSubscriptionData();
    } catch (error: any) {
      console.error('Failed to cancel subscription:', error);
      dispatch({ type: 'SET_ERROR', payload: error.message || 'Ошибка при отмене подписки' });
      throw error;
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  // Check if user can perform action based on limits
  const checkLimit = (feature: 'articles' | 'favorites' | 'exports' | 'api'): boolean => {
    if (!state.usageStats) return false;

    const usage = state.usageStats;
    
    switch (feature) {
      case 'articles':
        return usage.daily_articles_limit === null || usage.daily_articles_read < usage.daily_articles_limit;
      case 'favorites':
        return usage.favorites_limit === null || usage.favorites_count < usage.favorites_limit;
      case 'exports':
        return usage.exports_limit === null || usage.exports_count < usage.exports_limit;
      case 'api':
        return usage.api_calls_limit === null || usage.api_calls_count < usage.api_calls_limit;
      default:
        return false;
    }
  };

  // Get remaining limit for feature
  const getRemainingLimit = (feature: 'articles' | 'favorites' | 'exports' | 'api'): number | null => {
    if (!state.usageStats) return null;

    const usage = state.usageStats;
    
    switch (feature) {
      case 'articles':
        return usage.daily_articles_limit === null ? null : usage.daily_articles_limit - usage.daily_articles_read;
      case 'favorites':
        return usage.favorites_limit === null ? null : usage.favorites_limit - usage.favorites_count;
      case 'exports':
        return usage.exports_limit === null ? null : usage.exports_limit - usage.exports_count;
      case 'api':
        return usage.api_calls_limit === null ? null : usage.api_calls_limit - usage.api_calls_count;
      default:
        return null;
    }
  };

  // Load data when user changes
  useEffect(() => {
    loadSubscriptionData();
  }, [isAuthenticated, user]);

  // Context value
  const contextValue: SubscriptionContextType = {
    currentSubscription: state.currentSubscription,
    usageStats: state.usageStats,
    availablePlans: state.availablePlans,
    isLoading: state.isLoading,
    error: state.error,
    loadSubscriptionData,
    upgradePlan,
    cancelSubscription,
    checkLimit,
    getRemainingLimit,
  };

  return (
    <SubscriptionContext.Provider value={contextValue}>
      {children}
    </SubscriptionContext.Provider>
  );
}

// Hook to use subscription context
export function useSubscription(): SubscriptionContextType {
  const context = useContext(SubscriptionContext);
  if (context === undefined) {
    throw new Error('useSubscription must be used within a SubscriptionProvider');
  }
  return context;
}

export default SubscriptionContext; 