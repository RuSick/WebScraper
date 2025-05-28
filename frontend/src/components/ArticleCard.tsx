import React, { useState } from 'react';
import { Calendar, Tag, MapPin, ExternalLink, Star, Eye } from 'lucide-react';
import { Article } from '../types/api';
import { ArticleModal } from './ArticleModal';
import { useFavorites } from '../contexts/FavoritesContext';

interface ArticleCardProps {
  article: Article;
  className?: string;
  style?: React.CSSProperties;
}

export const ArticleCard: React.FC<ArticleCardProps> = ({ article, className = '', style }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { toggleFavorite, isFavorite } = useFavorites();
  const isArticleFavorite = isFavorite(article.id);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getTopicLabel = (topic: string) => {
    const topicLabels: Record<string, string> = {
      technology: 'Технологии',
      politics: 'Политика',
      economics: 'Экономика',
      science: 'Наука',
      business: 'Бизнес',
      war: 'Война',
      other: 'Прочее',
    };
    return topicLabels[topic] || topic;
  };

  const getTopicColor = (topic: string) => {
    const colors: Record<string, string> = {
      technology: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
      politics: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
      economics: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
      science: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
      business: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
      war: 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300',
      other: 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300',
    };
    return colors[topic] || colors.other;
  };

  const handleFavoriteClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    toggleFavorite(article.id);
  };

  return (
    <>
      <article 
        className={`group bg-white dark:bg-dark-800 rounded-xl shadow-sm hover:shadow-lg dark:shadow-dark-900/20 border border-gray-200 dark:border-dark-700 transition-all duration-300 hover:scale-[1.02] cursor-pointer animate-fade-in ${className}`}
        onClick={() => setIsModalOpen(true)}
        style={style}
      >
        {/* Header */}
        <div className="p-4 pb-3">
          <div className="flex items-start justify-between gap-3 mb-3">
            <div className="flex items-center gap-2 flex-wrap">
              <span className={`px-2 py-1 rounded-lg text-xs font-medium ${getTopicColor(article.topic)}`}>
                {getTopicLabel(article.topic)}
              </span>
              {article.is_analyzed && (
                <span className="px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 rounded-lg text-xs font-medium">
                  ✨ Анализ
                </span>
              )}
            </div>
            
            <button
              onClick={handleFavoriteClick}
              className={`p-1.5 rounded-lg transition-all duration-200 hover:scale-110 ${
                isArticleFavorite 
                  ? 'text-yellow-500 hover:text-yellow-600' 
                  : 'text-gray-400 dark:text-gray-500 hover:text-yellow-500'
              }`}
              aria-label={isArticleFavorite ? 'Удалить из избранного' : 'Добавить в избранное'}
            >
              <Star className={`w-4 h-4 ${isArticleFavorite ? 'fill-current' : ''}`} />
            </button>
          </div>

          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 line-clamp-2 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors duration-200">
            {article.title}
          </h3>

          {article.summary && (
            <p className="text-gray-600 dark:text-gray-300 text-sm line-clamp-3 mb-4 leading-relaxed">
              {article.summary}
            </p>
          )}
        </div>

        {/* Tags */}
        {article.tags && article.tags.length > 0 && (
          <div className="px-4 pb-3">
            <div className="flex items-center gap-1 mb-2">
              <Tag className="w-3 h-3 text-gray-400 dark:text-gray-500" />
              <span className="text-xs text-gray-500 dark:text-gray-400">Теги:</span>
            </div>
            <div className="flex flex-wrap gap-1">
              {article.tags.slice(0, 4).map((tag, index) => (
                <span
                  key={index}
                  className="px-2 py-1 bg-gray-100 dark:bg-dark-700 text-gray-700 dark:text-gray-300 rounded text-xs hover:bg-gray-200 dark:hover:bg-dark-600 transition-colors duration-200"
                >
                  {tag}
                </span>
              ))}
              {article.tags.length > 4 && (
                <span className="px-2 py-1 text-gray-500 dark:text-gray-400 text-xs">
                  +{article.tags.length - 4}
                </span>
              )}
            </div>
          </div>
        )}

        {/* Locations */}
        {article.locations && article.locations.length > 0 && (
          <div className="px-4 pb-3">
            <div className="flex items-center gap-1 mb-2">
              <MapPin className="w-3 h-3 text-gray-400 dark:text-gray-500" />
              <span className="text-xs text-gray-500 dark:text-gray-400">Локации:</span>
            </div>
            <div className="flex flex-wrap gap-1">
              {article.locations.slice(0, 3).map((location, index) => (
                <span
                  key={index}
                  className="px-2 py-1 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 rounded text-xs"
                >
                  📍 {location}
                </span>
              ))}
              {article.locations.length > 3 && (
                <span className="px-2 py-1 text-gray-500 dark:text-gray-400 text-xs">
                  +{article.locations.length - 3}
                </span>
              )}
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="px-4 py-3 bg-gray-50 dark:bg-dark-700/50 rounded-b-xl border-t border-gray-100 dark:border-dark-600">
          <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                <span>{formatDate(article.published_at)}</span>
              </div>
              
              <div className="flex items-center gap-1">
                <Eye className="w-3 h-3" />
                <span>{article.read_count}</span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-primary-600 dark:text-primary-400 font-medium">
                {article.source.name}
              </span>
              <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
            </div>
          </div>
        </div>
      </article>

      {/* Modal */}
      <ArticleModal
        article={article}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </>
  );
}; 