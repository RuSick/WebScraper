import React from 'react';
import { Article } from '../types/api';
import { ModernArticleCard } from './ModernArticleCard';
import { LoadingSpinner } from './LoadingSpinner';

interface ModernArticlesGridProps {
  articles: Article[];
  loading?: boolean;
  hasMore?: boolean;
  onLoadMore?: () => void;
  className?: string;
}

export const ModernArticlesGrid: React.FC<ModernArticlesGridProps> = ({
  articles,
  loading = false,
  hasMore = false,
  onLoadMore,
  className = ''
}) => {
  // Фильтруем статьи с содержательным summary
  // Временно отключено для отладки
  const filteredArticles = articles;
  // const filteredArticles = articles.filter(article => {
  //   const hasContentfulSummary = article.summary && 
  //     article.summary.trim().length > 20 && 
  //     !article.summary.toLowerCase().includes('связаться с нами') &&
  //     !article.summary.toLowerCase().includes('правил');
  //   return hasContentfulSummary;
  // });

  if (filteredArticles.length === 0 && !loading) {
    return (
      <div className="text-center py-16">
        <div className="w-20 h-20 bg-gradient-to-br from-slate-800 to-slate-700 rounded-2xl flex items-center justify-center mx-auto mb-6 border border-slate-600/50">
          <span className="text-3xl">📰</span>
        </div>
        <h3 className="text-2xl font-bold text-white mb-3">Статьи не найдены</h3>
        <p className="text-slate-400 text-lg">Попробуйте изменить фильтры поиска</p>
      </div>
    );
  }

  return (
    <div className={className}>
      {/* Адаптивная сетка с улучшенными отступами */}
      <div className="grid gap-10 grid-cols-1 lg:grid-cols-2 xl:grid-cols-3">
        {filteredArticles.map((article) => (
          <ModernArticleCard 
            key={article.id} 
            article={article}
            className="transform hover:scale-[1.02] transition-transform duration-300"
          />
        ))}
      </div>

      {/* Load More Button */}
      {hasMore && (
        <div className="flex justify-center mt-16">
          <button
            onClick={onLoadMore}
            disabled={loading}
            className="group relative px-10 py-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 disabled:from-slate-700 disabled:to-slate-600 text-white rounded-2xl font-semibold transition-all duration-300 flex items-center gap-4 border border-blue-500/20 hover:border-blue-400/30 disabled:border-slate-600/20 shadow-lg hover:shadow-xl hover:shadow-blue-500/10"
          >
            {loading ? (
              <>
                <LoadingSpinner size="sm" />
                <span>Загрузка...</span>
              </>
            ) : (
              <>
                <span>Загрузить ещё</span>
                <div className="w-6 h-6 rounded-full bg-white/20 flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
                  <span className="text-sm font-bold">+</span>
                </div>
              </>
            )}
            
            {/* Gradient overlay on hover */}
            <div className="absolute inset-0 bg-gradient-to-r from-blue-400/0 via-blue-400/10 to-blue-400/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-2xl" />
          </button>
        </div>
      )}

      {/* Loading State - красивые скелетоны */}
      {loading && filteredArticles.length === 0 && (
        <div className="grid gap-10 grid-cols-1 lg:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <div
              key={index}
              className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl border border-slate-700/50 p-5 animate-pulse h-[400px] flex flex-col"
            >
              {/* Category Badge Skeleton */}
              <div className="flex items-center gap-2 mb-6">
                <div className="w-2 h-2 bg-slate-700 rounded-full" />
                <div className="h-3 bg-slate-700 rounded-full w-28" />
              </div>

              {/* Title Skeleton - 2 строки */}
              <div className="space-y-2 mb-3 h-[3.5rem]">
                <div className="h-5 bg-slate-700 rounded-lg w-full" />
                <div className="h-5 bg-slate-700 rounded-lg w-4/5" />
              </div>

              {/* Summary Skeleton - 3 строки */}
              <div className="space-y-2 mb-4 h-[4.5rem]">
                <div className="h-4 bg-slate-700 rounded w-full" />
                <div className="h-4 bg-slate-700 rounded w-full" />
                <div className="h-4 bg-slate-700 rounded w-3/4" />
              </div>

              {/* Tags Skeleton */}
              <div className="flex gap-2 mb-4 h-[2rem]">
                <div className="h-6 bg-slate-700 rounded-full w-20" />
                <div className="h-6 bg-slate-700 rounded-full w-16" />
              </div>

              {/* Spacer */}
              <div className="flex-1"></div>

              {/* Footer Skeleton */}
              <div className="flex items-center justify-between border-t border-slate-700/50 pt-3 h-[3rem]">
                <div className="h-4 bg-slate-700 rounded w-20" />
                <div className="h-3 bg-slate-700 rounded w-24" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}; 