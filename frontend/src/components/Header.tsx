import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Search, Newspaper, Moon, Sun } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

export const Header: React.FC = () => {
  const navigate = useNavigate();
  const { isDark, toggleTheme } = useTheme();
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/?search=${encodeURIComponent(searchQuery.trim())}`);
      setSearchQuery('');
    }
    // Используем глобальный обработчик поиска
    if ((window as any).handleGlobalSearch) {
      (window as any).handleGlobalSearch(searchQuery);
    }
  };

  return (
    <header className="bg-gradient-to-r from-primary-600 via-primary-700 to-primary-800 dark:from-dark-800 dark:via-dark-900 dark:to-black shadow-lg border-b border-primary-500/20 dark:border-dark-700 sticky top-0 z-50 backdrop-blur-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 flex-shrink-0 group">
            <div className="w-10 h-10 bg-gradient-to-br from-white/20 to-white/10 backdrop-blur-sm rounded-xl flex items-center justify-center shadow-lg group-hover:scale-105 transition-transform duration-200">
              <Newspaper className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white drop-shadow-sm">MediaScope</h1>
              <p className="text-xs text-white/80">Новостная аналитика</p>
            </div>
          </Link>

          {/* Search Bar */}
          <div className="flex-1 max-w-md mx-8 hidden md:block">
            <form onSubmit={handleSearch}>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/60 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Поиск новостей..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-white/10 backdrop-blur-sm border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-white/30 focus:border-transparent text-sm text-white placeholder-white/60 transition-all duration-200"
                />
              </div>
            </form>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-4">
            {/* Mobile Search */}
            <div className="md:hidden">
              <form onSubmit={handleSearch}>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/60 w-4 h-4" />
                  <input
                    type="text"
                    placeholder="Поиск..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-32 pl-10 pr-3 py-1.5 bg-white/10 backdrop-blur-sm border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-white/30 focus:border-transparent text-sm text-white placeholder-white/60 transition-all duration-200"
                  />
                </div>
              </form>
            </div>

            {/* Status indicator */}
            <div className="flex items-center gap-2 text-sm text-white/80">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="hidden sm:inline">spaCy активен</span>
            </div>

            {/* Theme toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition-all duration-200"
              aria-label={isDark ? 'Переключить на светлую тему' : 'Переключить на темную тему'}
            >
              {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}; 