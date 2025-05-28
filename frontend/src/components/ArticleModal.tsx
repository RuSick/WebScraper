import React from 'react';
import { Article, TopicType } from '../types/api';
import { X, ExternalLink, Clock, Tag, MapPin, User, Building, Globe } from 'lucide-react';

interface ArticleModalProps {
  article: Article;
  isOpen: boolean;
  onClose: () => void;
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
    politics: 'bg-red-100 text-red-800',
    economics: 'bg-green-100 text-green-800',
    technology: 'bg-blue-100 text-blue-800',
    science: 'bg-purple-100 text-purple-800',
    business: 'bg-green-100 text-green-800',
    finance: 'bg-green-100 text-green-800',
    war: 'bg-red-100 text-red-800',
    international: 'bg-red-100 text-red-800',
    other: 'bg-gray-100 text-gray-800',
    sports: 'bg-orange-100 text-orange-800',
    culture: 'bg-pink-100 text-pink-800',
    health: 'bg-emerald-100 text-emerald-800',
    education: 'bg-indigo-100 text-indigo-800',
    environment: 'bg-green-100 text-green-800',
    society: 'bg-gray-100 text-gray-800',
    entertainment: 'bg-pink-100 text-pink-800',
    travel: 'bg-cyan-100 text-cyan-800',
    food: 'bg-yellow-100 text-yellow-800',
    fashion: 'bg-pink-100 text-pink-800',
    auto: 'bg-slate-100 text-slate-800',
    real_estate: 'bg-amber-100 text-amber-800',
  };
  return colors[topic] || 'bg-gray-100 text-gray-800';
};

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const ArticleModal: React.FC<ArticleModalProps> = ({ article, isOpen, onClose }) => {
  if (!isOpen) return null;

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const handleOpenOriginal = () => {
    window.open(article.url, '_blank');
  };

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
      onClick={handleBackdropClick}
    >
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
              <Building className="w-4 h-4 text-primary-600" />
            </div>
            <div>
              <h3 className="font-medium text-gray-900">{article.source.name}</h3>
              <p className="text-sm text-gray-500">{article.source.type_display}</p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={handleOpenOriginal}
              className="btn-secondary flex items-center gap-2"
            >
              <ExternalLink className="w-4 h-4" />
              Открыть оригинал
            </button>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="overflow-y-auto max-h-[calc(90vh-120px)]">
          <div className="p-6">
            {/* Title */}
            <h1 className="text-2xl font-bold text-gray-900 mb-4 leading-tight">
              {article.title}
            </h1>

            {/* Meta information */}
            <div className="flex flex-wrap items-center gap-4 mb-6 text-sm text-gray-600">
              <div className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                <span>Опубликовано: {formatDate(article.published_at)}</span>
              </div>
              
              {article.read_count > 0 && (
                <div className="flex items-center gap-1">
                  <User className="w-4 h-4" />
                  <span>{article.read_count} просмотров</span>
                </div>
              )}
              
              {article.is_analyzed && (
                <div className="flex items-center gap-1 text-green-600">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Проанализировано spaCy</span>
                </div>
              )}
            </div>

            {/* Topic and Tags */}
            <div className="flex flex-wrap items-center gap-2 mb-6">
              <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getTopicColor(article.topic)}`}>
                {topicLabels[article.topic]}
              </span>
              
              {article.tags.map((tag, index) => (
                <span key={index} className="inline-flex items-center gap-1 bg-gray-100 text-gray-700 text-sm px-2 py-1 rounded-full">
                  <Tag className="w-3 h-3" />
                  {tag}
                </span>
              ))}
            </div>

            {/* Locations */}
            {article.locations.length > 0 && (
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
                  <MapPin className="w-4 h-4" />
                  Географические упоминания
                </h3>
                <div className="flex flex-wrap gap-2">
                  {article.locations.map((location, index) => (
                    <span key={index} className="inline-flex items-center gap-1 bg-blue-50 text-blue-700 text-sm px-2 py-1 rounded-full">
                      <Globe className="w-3 h-3" />
                      {location}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Summary */}
            {article.summary && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Краткое содержание</h3>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-gray-700 leading-relaxed">{article.summary}</p>
                </div>
              </div>
            )}

            {/* Content */}
            {article.content && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Полный текст</h3>
                <div className="prose prose-gray max-w-none">
                  <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                    {article.content}
                  </p>
                </div>
              </div>
            )}

            {/* Footer */}
            <div className="border-t border-gray-200 pt-4 mt-6">
              <div className="flex items-center justify-between text-sm text-gray-500">
                <div>
                  Добавлено в систему: {formatDate(article.created_at)}
                </div>
                {article.is_featured && (
                  <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs font-medium">
                    Рекомендуемое
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ArticleModal; 