import React, { useState } from 'react';
import { Calendar, ExternalLink, Star, Plus } from 'lucide-react';
import { Article } from '../types/api';
import { ArticleModal } from './ArticleModal';
import { useFavorites } from '../contexts/FavoritesContext';

interface ModernArticleCardProps {
  article: Article;
  className?: string;
  style?: React.CSSProperties;
}

export const ModernArticleCard: React.FC<ModernArticleCardProps> = ({ 
  article, 
  className = '', 
  style 
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { toggleFavorite, isFavorite } = useFavorites();
  const isArticleFavorite = isFavorite(article.id);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffHours < 1) return 'только что';
    if (diffHours < 24) return `${diffHours}ч назад`;
    if (diffHours < 48) return 'вчера';
    
    return date.toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'short',
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
    const colors: Record<string, { bg: string; text: string; dot: string }> = {
      technology: { bg: 'bg-blue-500/20', text: 'text-blue-300', dot: 'bg-blue-500' },
      politics: { bg: 'bg-red-500/20', text: 'text-red-300', dot: 'bg-red-500' },
      economics: { bg: 'bg-green-500/20', text: 'text-green-300', dot: 'bg-green-500' }, 
      science: { bg: 'bg-purple-500/20', text: 'text-purple-300', dot: 'bg-purple-500' },
      business: { bg: 'bg-orange-500/20', text: 'text-orange-300', dot: 'bg-orange-500' },
      war: { bg: 'bg-gray-500/20', text: 'text-gray-300', dot: 'bg-gray-500' },
      other: { bg: 'bg-gray-500/20', text: 'text-gray-300', dot: 'bg-gray-500' },
    };
    return colors[topic] || colors.other;
  };

  const handleFavoriteClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    toggleFavorite(article.id);
  };

  // Строго ограничиваем теги - только первые 2
  const visibleTags = article.tags?.slice(0, 2) || [];
  const hiddenTagsCount = Math.max(0, (article.tags?.length || 0) - 2);
  const topicColors = getTopicColor(article.topic);

  // Получаем summary с жестким ограничением
  const getSummary = () => {
    let text = '';
    if (article.summary && article.summary.trim().length > 10) {
      text = article.summary;
    } else if (article.short_content && article.short_content.trim().length > 10) {
      text = article.short_content;
    } else if (article.content && article.content.trim().length > 10) {
      text = article.content;
    } else {
      text = 'Краткое описание статьи недоступно. Нажмите для просмотра полного содержания.';
    }
    
    // Жестко обрезаем до 150 символов для 3 строк
    if (text.length > 150) {
      text = text.substring(0, 147) + '...';
    }
    return text;
  };

  return (
    <>
      <article 
        className={`group relative bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl border border-slate-700/50 hover:border-slate-600/50 transition-all duration-500 hover:shadow-2xl hover:shadow-blue-500/10 cursor-pointer overflow-hidden backdrop-blur-sm h-[400px] ${className}`}
        onClick={() => setIsModalOpen(true)}
        style={style}
      >
        {/* Subtle gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 via-transparent to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
        
        {/* Category Badge - левый верхний угол */}
        <div className="absolute top-4 left-4 z-10">
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${topicColors.bg} backdrop-blur-sm border border-white/20`}>
            <div className={`w-2 h-2 rounded-full ${topicColors.dot}`} />
            <span className={`text-xs font-semibold ${topicColors.text} uppercase tracking-wide`}>
              {getTopicLabel(article.topic)}
            </span>
            {article.is_analyzed && (
              <span className="text-xs text-emerald-300">✨</span>
            )}
          </div>
        </div>

        {/* Favorite Button - правый верхний угол */}
        <button
          onClick={handleFavoriteClick}
          className={`absolute top-4 right-4 z-10 p-2 rounded-full backdrop-blur-sm border border-white/20 transition-all duration-300 hover:scale-110 ${
            isArticleFavorite 
              ? 'text-amber-300 bg-amber-400/20 border-amber-400/30' 
              : 'text-slate-300 hover:text-amber-300 hover:bg-amber-400/20 hover:border-amber-400/30'
          }`}
          aria-label={isArticleFavorite ? 'Удалить из избранного' : 'Добавить в избранное'}
        >
          <Star className={`w-4 h-4 ${isArticleFavorite ? 'fill-current' : ''}`} />
        </button>

        {/* Main Content - строго структурированный */}
        <div className="relative p-5 pt-16 h-full flex flex-col">
          {/* Title - показываем полностью */}
          <h3 className="text-lg font-bold text-white mb-3 leading-tight group-hover:text-blue-300 transition-colors duration-300 min-h-[3.5rem]">
            {article.title}
          </h3>

          {/* Summary - строго 3 строки */}
          <div className="mb-4 h-[4.5rem]">
            <p className="text-slate-200 text-sm leading-relaxed line-clamp-3 h-full">
              {getSummary()}
            </p>
          </div>

          {/* Tags - строго 2 видимых + счетчик */}
          <div className="mb-4 h-[2rem]">
            {article.tags && article.tags.length > 0 && (
              <div className="flex items-center gap-2 h-full">
                {visibleTags.map((tag, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-slate-800/60 text-slate-200 rounded-full text-xs border border-slate-700/60 font-medium truncate max-w-[120px]"
                  >
                    {tag}
                  </span>
                ))}
                {hiddenTagsCount > 0 && (
                  <span className="flex items-center gap-1 px-2 py-1 bg-slate-800/40 text-slate-400 rounded-full text-xs border border-slate-700/40">
                    <Plus className="w-3 h-3" />
                    {hiddenTagsCount}
                  </span>
                )}
              </div>
            )}
          </div>

          {/* Spacer - заполняет оставшееся место */}
          <div className="flex-1"></div>

          {/* Footer - фиксированная высота */}
          <div className="border-t border-slate-700/50 pt-3 h-[3rem] flex items-center justify-between text-sm">
            <div className="flex items-center gap-2 text-slate-300">
              <Calendar className="w-4 h-4 text-slate-400" />
              <span className="font-medium">{formatDate(article.published_at)}</span>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-blue-300 font-semibold truncate max-w-[120px] text-xs">
                {article.source.name}
              </span>
              <ExternalLink className="w-3 h-3 text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            </div>
          </div>
        </div>

        {/* Hover Effect Border */}
        <div className="absolute inset-0 rounded-2xl border border-transparent group-hover:border-blue-500/30 transition-all duration-500 pointer-events-none" />
        
        {/* Bottom gradient line */}
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-blue-500/30 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
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