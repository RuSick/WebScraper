import React, { createContext, useContext, useEffect, useState } from 'react';

interface FavoritesContextType {
  favorites: Set<number>;
  toggleFavorite: (articleId: number) => void;
  isFavorite: (articleId: number) => boolean;
}

const FavoritesContext = createContext<FavoritesContextType | undefined>(undefined);

export const useFavorites = () => {
  const context = useContext(FavoritesContext);
  if (context === undefined) {
    throw new Error('useFavorites must be used within a FavoritesProvider');
  }
  return context;
};

interface FavoritesProviderProps {
  children: React.ReactNode;
}

export const FavoritesProvider: React.FC<FavoritesProviderProps> = ({ children }) => {
  const [favorites, setFavorites] = useState<Set<number>>(() => {
    // Загружаем избранные из localStorage
    const saved = localStorage.getItem('favorites');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        return new Set(parsed);
      } catch (error) {
        console.error('Error parsing favorites from localStorage:', error);
      }
    }
    return new Set();
  });

  useEffect(() => {
    // Сохраняем избранные в localStorage
    localStorage.setItem('favorites', JSON.stringify(Array.from(favorites)));
  }, [favorites]);

  const toggleFavorite = (articleId: number) => {
    setFavorites(prev => {
      const newFavorites = new Set(prev);
      if (newFavorites.has(articleId)) {
        newFavorites.delete(articleId);
      } else {
        newFavorites.add(articleId);
      }
      return newFavorites;
    });
  };

  const isFavorite = (articleId: number) => {
    return favorites.has(articleId);
  };

  return (
    <FavoritesContext.Provider value={{ favorites, toggleFavorite, isFavorite }}>
      {children}
    </FavoritesContext.Provider>
  );
}; 