import axios from 'axios';
import { 
  Article, 
  Source, 
  ArticleStats, 
  ApiResponse, 
  ArticleFilters,
  API_ENDPOINTS 
} from '../types/api';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.status, error.message);
    return Promise.reject(error);
  }
);

// API service functions
export const apiService = {
  // Articles
  async getArticles(filters: ArticleFilters = {}): Promise<ApiResponse<Article>> {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, String(value));
      }
    });
    
    const response = await api.get(`${API_ENDPOINTS.articles}?${params}`);
    return response.data;
  },

  async getArticle(id: number): Promise<Article> {
    const response = await api.get(`${API_ENDPOINTS.articles}${id}/`);
    return response.data;
  },

  async toggleFeatured(id: number): Promise<Article> {
    const response = await api.patch(`${API_ENDPOINTS.articles}${id}/toggle_featured/`);
    return response.data;
  },

  // Sources
  async getSources(): Promise<Source[]> {
    const response = await api.get(API_ENDPOINTS.sources);
    return response.data;
  },

  async getSource(id: number): Promise<Source> {
    const response = await api.get(`${API_ENDPOINTS.sources}${id}/`);
    return response.data;
  },

  // Statistics
  async getStats(): Promise<ArticleStats> {
    const response = await api.get(API_ENDPOINTS.stats);
    return response.data;
  },

  // Search and recommendations
  async searchArticles(query: string, filters: Omit<ArticleFilters, 'search'> = {}): Promise<ApiResponse<Article>> {
    return this.getArticles({ ...filters, search: query });
  },

  async getRecommendedArticles(limit: number = 6): Promise<Article[]> {
    const response = await this.getArticles({ 
      is_featured: true, 
      page_size: limit,
      ordering: '-published_at'
    });
    return response.results;
  },

  async getRecentArticles(limit: number = 12): Promise<Article[]> {
    const response = await this.getArticles({ 
      page_size: limit,
      ordering: '-published_at'
    });
    return response.results;
  },

  async getArticlesByTopic(topic: string, limit: number = 12): Promise<Article[]> {
    const response = await this.getArticles({ 
      topic: topic as any,
      page_size: limit,
      ordering: '-published_at'
    });
    return response.results;
  },
};

export default api; 