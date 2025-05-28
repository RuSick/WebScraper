import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from './contexts/ThemeContext';
import { FavoritesProvider } from './contexts/FavoritesContext';
import { AuthProvider } from './contexts/AuthContext';
import { SubscriptionProvider } from './contexts/SubscriptionContext';
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { HomePage } from './pages/HomePage';
import ProfilePage from './pages/ProfilePage';
import PricingPage from './pages/PricingPage';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <SubscriptionProvider>
            <FavoritesProvider>
              <Router>
                <div className="min-h-screen bg-gray-50 dark:bg-dark-900 transition-colors duration-200">
                  <Header />
                  <main className="flex-1">
                    <Routes>
                      <Route path="/" element={<HomePage />} />
                      <Route path="/topic/:topic" element={<HomePage />} />
                      <Route path="/source/:sourceId" element={<HomePage />} />
                      <Route path="/profile" element={<ProfilePage />} />
                      <Route path="/pricing" element={<PricingPage />} />
                      <Route path="/subscription" element={<PricingPage />} />
                    </Routes>
                  </main>
                  <Footer />
                </div>
              </Router>
            </FavoritesProvider>
          </SubscriptionProvider>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
