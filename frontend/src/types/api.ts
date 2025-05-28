// API Response types
export interface ApiResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Article types
export interface Article {
  id: number;
  title: string;
  content: string;
  summary: string;
  url: string;
  published_at: string;
  created_at: string;
  updated_at: string;
  topic: TopicType;
  tags: string[];
  locations: string[];
  is_analyzed: boolean;
  read_count: number;
  is_featured: boolean;
  is_active: boolean;
  source: Source;
  short_content: string;
}

// Source types
export interface Source {
  id: number;
  name: string;
  url: string;
  type: SourceType;
  type_display: string;
  is_active: boolean;
  description: string;
  update_frequency: number;
  last_parsed: string | null;
  articles_count: number;
  created_at: string;
  updated_at: string;
}

// Enums
export type TopicType = 
  | 'politics'
  | 'economics' 
  | 'technology'
  | 'science'
  | 'sports'
  | 'culture'
  | 'health'
  | 'education'
  | 'environment'
  | 'society'
  | 'war'
  | 'international'
  | 'business'
  | 'finance'
  | 'entertainment'
  | 'travel'
  | 'food'
  | 'fashion'
  | 'auto'
  | 'real_estate'
  | 'other';

export type SourceType = 'rss' | 'html' | 'spa' | 'api' | 'tg';

// Statistics types
export interface ArticleStats {
  total_articles: number;
  total_sources: number;
  featured_articles: number;
  analyzed_articles: number;
  articles_by_topic: Record<string, number>;
  articles_by_source: Record<string, number>;
  recent_articles_count: number;
  top_tags: Array<{ tag: string; count: number }>;
  top_locations: Array<{ location: string; count: number }>;
}

export interface SourceStats {
  source_name: string;
  articles_count: number;
  last_parsed: string | null;
}

// Filter types
export interface ArticleFilters {
  page?: number;
  page_size?: number;
  search?: string;
  topic?: TopicType | '';
  source?: number;
  analyzed?: boolean;
  is_analyzed?: boolean;
  tags?: string;
  is_featured?: boolean;
  ordering?: string;
  favorites?: boolean;
  date_from?: string;
  date_to?: string;
}

// API endpoints
export const API_ENDPOINTS = {
  articles: '/api/articles/',
  sources: '/api/sources/',
  stats: '/api/stats/articles/',
} as const; 