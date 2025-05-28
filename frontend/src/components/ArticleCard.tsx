import React, { useState } from 'react';
import { Article, TopicType } from '../types/api';
import { Clock, ExternalLink, Tag, MapPin, Eye } from 'lucide-react';
import { ArticleModal } from './ArticleModal';

interface ArticleCardProps {
  article: Article;
  onClick?: () => void;
  showFullContent?: boolean;
}

const topicLabels: Record<TopicType, string> = {
  politics: 'Политика',
  economics: 'Экономика',
  technology: 'Технологии',
  science: 'Наука',
  sports: 'Спорт',
  culture: 'Культура',
  health: 'Здоровье',
  education: 'Образование',
  environment: 'Экология',
  society: 'Общество',
  war: 'Война',
  international: 'Международные отношения',
  business: 'Бизнес',
  finance: 'Финансы',
  entertainment: 'Развлечения',
  travel: 'Путешествия',
  food: 'Еда',
  fashion: 'Мода',
  auto: 'Автомобили',
  real_estate: 'Недвижимость',
  other: 'Прочее',
};

const getTopicColor = (topic: TopicType): string => {
  const colors: Record<TopicType, string> = {
    politics: 'topic-politics',
    economics: 'topic-economics',
    technology: 'topic-technology',
    science: 'topic-science',
    business: 'topic-economics',
    finance: 'topic-economics',
    war: 'topic-politics',
    international: 'topic-politics',
    other: 'topic-other',
    sports: 'topic-other',
    culture: 'topic-other',
    health: 'topic-other',
    education: 'topic-other',
    environment: 'topic-other',
    society: 'topic-other',
    entertainment: 'topic-other',
    travel: 'topic-other',
    food: 'topic-other',
    fashion: 'topic-other',
    auto: 'topic-other',
    real_estate: 'topic-other',
  };
  return colors[topic] || 'topic-other';
};

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
  
  if (diffInHours < 1) {
    return 'Только что';
  } else if (diffInHours < 24) {
    return `${diffInHours} ч. назад`;
  } else if (diffInHours < 48) {
    return 'Вчера';
  } else {
    return date.toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'short',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
    });
  }
};

export const ArticleCard: React.FC<ArticleCardProps> = ({ 
  article, 
  onClick, 
  showFullContent = false 
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleCardClick = (e: React.MouseEvent) => {
    e.preventDefault();
    if (onClick) {
      onClick();
    } else {
      setIsModalOpen(true);
    }
  };

  const handleExternalClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    window.open(article.url, '_blank');
  };

  return (
    <>
      <article 
        className="card hover:shadow-lg transition-shadow duration-300 cursor-pointer group"
        onClick={handleCardClick}
      >
        {/* Header */}
        <div className="p-4 pb-3">
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <span className="font-medium text-primary-600">{article.source.name}</span>
              <span>•</span>
              <div className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                <time dateTime={article.published_at}>
                  {formatDate(article.published_at)}
                </time>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={handleExternalClick}
                className="p-1 text-gray-400 hover:text-primary-600 transition-colors"
                title="Открыть оригинал"
              >
                <ExternalLink className="w-4 h-4" />
              </button>
              <button
                onClick={handleCardClick}
                className="p-1 text-gray-400 hover:text-primary-600 transition-colors"
                title="Подробнее"
              >
                <Eye className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Title */}
          <h2 className="text-lg font-semibold text-gray-900 mb-3 line-clamp-2 group-hover:text-primary-700 transition-colors">
            {article.title}
          </h2>

          {/* Content */}
          <p className="text-gray-600 text-sm leading-relaxed mb-4 line-clamp-3">
            {showFullContent ? article.content : article.short_content}
          </p>
        </div>

        {/* Footer */}
        <div className="px-4 pb-4">
          {/* Topic and Tags */}
          <div className="flex flex-wrap items-center gap-2 mb-3">
            <span className={`tag ${getTopicColor(article.topic)}`}>
              {topicLabels[article.topic]}
            </span>
            
            {article.tags.slice(0, 3).map((tag, index) => (
              <span key={index} className="tag">
                <Tag className="w-3 h-3 mr-1" />
                {tag}
              </span>
            ))}
            
            {article.tags.length > 3 && (
              <span className="text-xs text-gray-500">
                +{article.tags.length - 3} еще
              </span>
            )}
          </div>

          {/* Locations */}
          {article.locations.length > 0 && (
            <div className="flex items-center gap-1 text-xs text-gray-500 mb-3">
              <MapPin className="w-3 h-3" />
              <span>{article.locations.slice(0, 2).join(', ')}</span>
              {article.locations.length > 2 && (
                <span>+{article.locations.length - 2}</span>
              )}
            </div>
          )}

          {/* Analysis indicator */}
          <div className="flex items-center justify-between pt-3 border-t border-gray-100">
            <div className="flex items-center gap-2">
              {article.is_analyzed ? (
                <>
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-xs text-gray-500">Проанализировано spaCy</span>
                </>
              ) : (
                <>
                  <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
                  <span className="text-xs text-gray-500">Ожидает анализа</span>
                </>
              )}
            </div>
            
            {article.is_featured && (
              <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full">
                Рекомендуемое
              </span>
            )}
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

export default ArticleCard; 