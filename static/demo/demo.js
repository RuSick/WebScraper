// API Base URL
const API_BASE = 'http://localhost:8000/api';

// Debug info
console.log('🔧 MediaScope Demo JS loaded');
console.log('🌐 API Base URL:', API_BASE);

// State variables
let currentPage = 1;
let totalPages = 1;
let currentFilters = {};
let searchTimeout = null;
let isLoading = false;

// Theme management
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeToggle(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeToggle(newTheme);
}

function updateThemeToggle(theme) {
    const toggleBtn = document.getElementById('themeToggleBtn');
    if (toggleBtn) {
        const icon = toggleBtn.querySelector('i');
        if (icon) {
            icon.className = theme === 'light' ? 'bi bi-moon' : 'bi bi-sun';
        }
    }
}

// Topic labels
const TOPIC_LABELS = {
    'politics': 'Политика',
    'economics': 'Экономика', 
    'technology': 'Технологии',
    'science': 'Наука',
    'sports': 'Спорт',
    'culture': 'Культура',
    'health': 'Здоровье',
    'education': 'Образование',
    'environment': 'Экология',
    'society': 'Общество',
    'war': 'Война и конфликты',
    'international': 'Международные отношения',
    'business': 'Бизнес',
    'finance': 'Финансы',
    'entertainment': 'Развлечения',
    'travel': 'Путешествия',
    'food': 'Еда',
    'fashion': 'Мода',
    'auto': 'Автомобили',
    'real_estate': 'Недвижимость',
    'other': 'Прочее',
};

// Enhanced search with debouncing
function setupSearch() {
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) return;
    
    // Search on Enter
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            searchArticles();
        }
    });
    
    // Auto-search with debouncing
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            if (searchInput.value.length >= 3 || searchInput.value.length === 0) {
                searchArticles();
            }
        }, 500);
    });
}

// Filter toggle functions
function toggleFilter(filterType) {
    const toggle = document.getElementById(`${filterType}Toggle`);
    if (!toggle) return;
    
    const isActive = toggle.classList.contains('active');
    
    if (isActive) {
        toggle.classList.remove('active');
        delete currentFilters[filterType];
    } else {
        toggle.classList.add('active');
        currentFilters[filterType] = true;
    }
    
    updateActiveFilters();
    applyFilters();
}

// Update active filters display
function updateActiveFilters() {
    const activeFiltersDiv = document.getElementById('activeFilters');
    const filterPillsDiv = document.getElementById('filterPills');
    
    if (!activeFiltersDiv || !filterPillsDiv) return;
    
    // Clear existing pills
    filterPillsDiv.innerHTML = '';
    
    let hasFilters = false;
    
    // Add filter pills for each active filter
    Object.keys(currentFilters).forEach(filterKey => {
        if (currentFilters[filterKey]) {
            hasFilters = true;
            const pill = createFilterPill(filterKey, currentFilters[filterKey]);
            filterPillsDiv.appendChild(pill);
        }
    });
    
    // Show/hide active filters section
    if (hasFilters) {
        activeFiltersDiv.classList.add('show');
    } else {
        activeFiltersDiv.classList.remove('show');
    }
}

function createFilterPill(filterKey, filterValue) {
    const pill = document.createElement('div');
    pill.className = 'filter-pill';
    
    let label = '';
    switch(filterKey) {
        case 'topic':
            label = `Тема: ${TOPIC_LABELS[filterValue] || filterValue}`;
            break;
        case 'source':
            label = `Источник: ${filterValue}`;
            break;
        case 'tags':
            label = `Теги: ${filterValue}`;
            break;
        case 'locations':
            label = `Локации: ${filterValue}`;
            break;
        case 'featured':
            label = 'Избранные';
            break;
        case 'analyzed':
            label = 'Проанализированные';
            break;
        case 'search':
            label = `Поиск: "${filterValue}"`;
            break;
        default:
            label = `${filterKey}: ${filterValue}`;
    }
    
    pill.innerHTML = `
        <span>${label}</span>
        <i class="bi bi-x remove" onclick="removeFilter('${filterKey}')"></i>
    `;
    
    return pill;
}

function removeFilter(filterKey) {
    delete currentFilters[filterKey];
    
    // Reset UI elements
    const elements = {
        'topic': 'topicFilter',
        'source': 'sourceFilter', 
        'tags': 'tagsFilter',
        'locations': 'locationsFilter',
        'search': 'searchInput'
    };
    
    const elementId = elements[filterKey];
    if (elementId) {
        const element = document.getElementById(elementId);
        if (element) element.value = '';
    }
    
    // Handle toggle buttons
    if (filterKey === 'featured' || filterKey === 'analyzed') {
        const toggle = document.getElementById(`${filterKey}Toggle`);
        if (toggle) toggle.classList.remove('active');
    }
    
    updateActiveFilters();
    applyFilters();
}

function clearAllFilters() {
    currentFilters = {};
    
    // Reset all UI elements
    const inputs = ['searchInput', 'topicFilter', 'sourceFilter', 'tagsFilter', 'locationsFilter'];
    inputs.forEach(id => {
        const element = document.getElementById(id);
        if (element) element.value = '';
    });
    
    // Reset toggles
    ['featuredToggle', 'analyzedToggle'].forEach(id => {
        const element = document.getElementById(id);
        if (element) element.classList.remove('active');
    });
    
    updateActiveFilters();
    loadArticles(1);
}

// Enhanced loading state
function setLoading(loading) {
    isLoading = loading;
    const loadingDiv = document.getElementById('loading');
    const articlesContainer = document.getElementById('articlesContainer');
    const emptyState = document.getElementById('emptyState');
    
    if (loadingDiv) {
        if (loading) {
            loadingDiv.classList.add('show');
        } else {
            loadingDiv.classList.remove('show');
        }
    }
    
    if (articlesContainer) {
        articlesContainer.style.opacity = loading ? '0.5' : '1';
    }
    
    if (emptyState && loading) {
        emptyState.style.display = 'none';
    }
}

// Enhanced error handling
function showError(message) {
    console.error('❌ Error:', message);
    
    const articlesContainer = document.getElementById('articlesContainer');
    if (articlesContainer) {
        articlesContainer.innerHTML = `
            <div style="grid-column: 1 / -1;">
                <div style="background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 12px; padding: 2rem; text-align: center;">
                    <i class="bi bi-exclamation-triangle-fill" style="font-size: 2rem; color: #ef4444; margin-bottom: 1rem;"></i>
                    <h5 style="color: var(--text-primary); margin-bottom: 0.5rem;">Ошибка загрузки</h5>
                    <p style="color: var(--text-secondary); margin-bottom: 1rem;">${message}</p>
                    <button onclick="loadArticles(1)" style="background: var(--gradient-primary); color: white; border: none; padding: 0.5rem 1rem; border-radius: 8px; cursor: pointer;">
                        Попробовать снова
                    </button>
                </div>
            </div>
        `;
    }
}

// Improved statistics loading with better undefined handling
async function loadStatistics() {
    try {
        console.log('📊 Loading statistics...');
        const response = await fetch(`${API_BASE}/stats/articles/`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const stats = await response.json();
        console.log('📊 Statistics loaded:', stats);
        
        // Update main stats with safe fallbacks
        const statElements = {
            'totalArticles': stats.total_articles ?? '—',
            'analyzedArticles': stats.analyzed_articles ?? '—',
            'totalSources': stats.total_sources ?? '—',
            'featuredCount': stats.featured_articles ?? '—',
            'recentCount': stats.recent_articles_count ?? '—',
            'topicsCount': stats.articles_by_topic ? Object.keys(stats.articles_by_topic).length : '—',
            'headerArticleCount': stats.total_articles ?? '—',
            'headerAnalyzedCount': stats.analyzed_articles ?? '—'
        };
        
        Object.keys(statElements).forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                const value = statElements[id];
                element.textContent = value === null || value === undefined ? '—' : value;
            }
        });
        
        // Update analytics
        displayTopTags(stats.top_tags || []);
        displayTopLocations(stats.top_locations || []);
        
    } catch (error) {
        console.error('❌ Error loading statistics:', error);
        // Set fallback values for all stats
        const fallbackElements = ['totalArticles', 'analyzedArticles', 'totalSources', 'featuredCount', 'recentCount', 'topicsCount', 'headerArticleCount', 'headerAnalyzedCount'];
        fallbackElements.forEach(id => {
            const element = document.getElementById(id);
            if (element) element.textContent = '—';
        });
    }
}

function displayTopTags(topTags) {
    const container = document.getElementById('topTags');
    if (!container) return;
    
    if (!topTags.length) {
        container.innerHTML = '<span style="color: var(--text-muted);">Нет данных</span>';
        return;
    }
    
    const tagsHtml = topTags.slice(0, 10).map(item => 
        `<span class="tag" onclick="filterByTag('${item.tag}')">${item.tag} (${item.count})</span>`
    ).join(' ');
    
    container.innerHTML = tagsHtml;
}

function displayTopLocations(topLocations) {
    const container = document.getElementById('topLocations');
    if (!container) return;
    
    if (!topLocations.length) {
        container.innerHTML = '<span style="color: var(--text-muted);">Нет данных</span>';
        return;
    }
    
    const locationsHtml = topLocations.slice(0, 10).map(item => 
        `<span class="location" onclick="filterByLocation('${item.location}')">${item.location} (${item.count})</span>`
    ).join(' ');
    
    container.innerHTML = locationsHtml;
}

// Quick filter functions
function filterByTag(tag) {
    const tagsFilter = document.getElementById('tagsFilter');
    if (tagsFilter) {
        tagsFilter.value = tag;
        currentFilters.tags = tag;
        updateActiveFilters();
        applyFilters();
    }
}

function filterByLocation(location) {
    const locationsFilter = document.getElementById('locationsFilter');
    if (locationsFilter) {
        locationsFilter.value = location;
        currentFilters.locations = location;
        updateActiveFilters();
        applyFilters();
    }
}

// Enhanced article loading
async function loadArticles(page = 1) {
    if (isLoading) return;
    
    setLoading(true);
    currentPage = page;
    
    try {
        console.log(`📰 Loading articles page ${page}...`);
        
        // Build query parameters
        const params = new URLSearchParams();
        params.append('page', page);
        params.append('page_size', '12');
        
        // Add filters
        Object.keys(currentFilters).forEach(key => {
            if (currentFilters[key]) {
                params.append(key, currentFilters[key]);
            }
        });
        
        const url = `${API_BASE}/articles/?${params.toString()}`;
        console.log('🌐 Request URL:', url);
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log(`📰 Loaded ${data.results?.length || 0} articles`);
        
        displayArticles(data.results || []);
        updatePagination(data);
        
    } catch (error) {
        console.error('❌ Error loading articles:', error);
        showError(error.message);
    } finally {
        setLoading(false);
    }
}

// Modern article display with safe data handling
function displayArticles(articles) {
    const container = document.getElementById('articlesContainer');
    const emptyState = document.getElementById('emptyState');
    
    if (!container) return;
    
    if (!articles.length) {
        container.innerHTML = '';
        if (emptyState) emptyState.style.display = 'block';
        return;
    }
    
    if (emptyState) emptyState.style.display = 'none';
    
    const articlesHtml = articles.map(article => createArticleCard(article)).join('');
    
    container.innerHTML = articlesHtml;
}

function createArticleCard(article) {
    // Умная логика выбора контента для отображения
    const getArticleContent = (article) => {
        if (article.short_content && article.short_content.trim()) {
            return article.short_content.trim();
        }
        if (article.summary && article.summary.trim()) {
            return article.summary.trim();
        }
        if (article.content && article.content.trim()) {
            const content = article.content.trim();
            return content.length > 200 ? content.substring(0, 200) + '...' : content;
        }
        return null;
    };

    const articleContent = getArticleContent(article);

    return `
        <article class="article-card">
            <!-- Кнопка избранного в правом верхнем углу -->
            <div class="article-actions">
                <button class="featured-btn ${article.is_featured ? 'featured' : ''}" 
                        onclick="toggleArticleFeatured(${article.id}, this)"
                        title="${article.is_featured ? 'Убрать из избранного' : 'Добавить в избранное'}">
                    <i class="bi bi-${article.is_featured ? 'star-fill' : 'star'}"></i>
                </button>
            </div>
            
            <header class="article-header">
                <h3 class="article-title">
                    <a href="${article.url || '#'}" target="_blank">${article.title || 'Без заголовка'}</a>
                </h3>
            </header>
            
            <div class="article-meta">
                ${article.topic ? `<span class="topic-badge topic-${article.topic}">
                    ${TOPIC_LABELS[article.topic] || article.topic}
                </span>` : ''}
                <span class="analysis-status ${article.is_analyzed ? 'analyzed' : 'not-analyzed'}">
                    <i class="bi bi-${article.is_analyzed ? 'check-circle' : 'clock'}"></i>
                    ${article.is_analyzed ? 'Проанализирована' : 'Ожидает анализа'}
                </span>
                ${article.source_name ? `<small class="source-name">${article.source_name}</small>` : ''}
                ${article.published_at ? `<small class="publish-date">${formatDate(article.published_at)}</small>` : ''}
            </div>
            
            ${articleContent ? `<p class="article-content">${articleContent}</p>` : ''}
            
            <footer class="article-footer">
                <div class="article-tags">
                    ${displayTags(article.tags)}
                    ${displayLocations(article.locations)}
                </div>
                <small class="read-count">
                    <i class="bi bi-eye"></i> ${article.read_count ?? 0}
                </small>
            </footer>
        </article>
    `;
}

function displayTags(tags) {
    if (!tags || !tags.length) return '';
    
    return tags.slice(0, 5).map(tag => 
        `<span class="tag" onclick="filterByTag('${tag}')">${tag}</span>`
    ).join('');
}

function displayLocations(locations) {
    if (!locations || !locations.length) return '';
    
    return locations.slice(0, 3).map(location => 
        `<span class="location" onclick="filterByLocation('${location}')">${location}</span>`
    ).join('');
}

// Enhanced date formatting
function formatDate(dateStr) {
    try {
        const date = new Date(dateStr);
        const now = new Date();
        const diffMs = now - date;
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
        
        if (diffDays === 0) {
            const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
            if (diffHours === 0) {
                const diffMinutes = Math.floor(diffMs / (1000 * 60));
                return diffMinutes <= 1 ? 'только что' : `${diffMinutes} мин назад`;
            }
            return `${diffHours} ч назад`;
        } else if (diffDays === 1) {
            return 'вчера';
        } else if (diffDays <= 7) {
            return `${diffDays} дн назад`;
        } else {
            return date.toLocaleDateString('ru-RU', {
                day: 'numeric',
                month: 'short',
                year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
            });
        }
    } catch (error) {
        console.warn('⚠️ Date formatting error:', error);
        return 'неизвестно';
    }
}

// Modern pagination
function updatePagination(data) {
    const container = document.getElementById('pagination');
    if (!container) return;
    
    const totalPages = Math.ceil(data.count / (data.page_size || 12));
    
    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }
    
    let paginationHtml = '';
    
    // Previous button
    paginationHtml += `
        <button class="page-btn" onclick="loadArticles(${currentPage - 1})" 
                ${currentPage <= 1 ? 'disabled' : ''}>
            <i class="bi bi-chevron-left"></i>
        </button>
    `;
    
    // Page numbers
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    
    if (startPage > 1) {
        paginationHtml += `<button class="page-btn" onclick="loadArticles(1)">1</button>`;
        if (startPage > 2) {
            paginationHtml += `<span class="page-btn" style="cursor: default;">...</span>`;
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        paginationHtml += `
            <button class="page-btn ${i === currentPage ? 'active' : ''}" 
                    onclick="loadArticles(${i})">${i}</button>
        `;
    }
    
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            paginationHtml += `<span class="page-btn" style="cursor: default;">...</span>`;
        }
        paginationHtml += `<button class="page-btn" onclick="loadArticles(${totalPages})">${totalPages}</button>`;
    }
    
    // Next button
    paginationHtml += `
        <button class="page-btn" onclick="loadArticles(${currentPage + 1})" 
                ${currentPage >= totalPages ? 'disabled' : ''}>
            <i class="bi bi-chevron-right"></i>
        </button>
    `;
    
    container.innerHTML = paginationHtml;
}

// Enhanced sources loading
async function loadSources() {
    try {
        console.log('🔗 Loading sources...');
        const response = await fetch(`${API_BASE}/sources/`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log(`🔗 Loaded ${data.results?.length || 0} sources`);
        
        const sourceFilter = document.getElementById('sourceFilter');
        if (!sourceFilter) return;
        
        sourceFilter.innerHTML = '<option value="">Все источники</option>';
        
        if (data.results) {
            data.results.forEach(source => {
                const option = document.createElement('option');
                option.value = source.id;
                option.textContent = `${source.name} (${source.articles_count || 0})`;
                sourceFilter.appendChild(option);
            });
        }
        
    } catch (error) {
        console.error('❌ Error loading sources:', error);
    }
}

// Enhanced search function
function searchArticles() {
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) return;
    
    const searchTerm = searchInput.value.trim();
    
    if (searchTerm) {
        currentFilters.search = searchTerm;
        searchInput.classList.add('has-value');
    } else {
        delete currentFilters.search;
        searchInput.classList.remove('has-value');
    }
    
    updateActiveFilters();
    loadArticles(1);
}

// Enhanced filters
function applyFilters() {
    // Collect all filter values
    const filterElements = {
        'topic': 'topicFilter',
        'source': 'sourceFilter',
        'tags': 'tagsFilter',
        'locations': 'locationsFilter'
    };
    
    Object.keys(filterElements).forEach(filterKey => {
        const element = document.getElementById(filterElements[filterKey]);
        if (element) {
            const value = element.value.trim();
            if (value) {
                currentFilters[filterKey] = value;
                element.classList.add('has-value');
            } else {
                delete currentFilters[filterKey];
                element.classList.remove('has-value');
            }
        }
    });
    
    // Highlight search input if has value
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        if (searchInput.value.trim()) {
            searchInput.classList.add('has-value');
        } else {
            searchInput.classList.remove('has-value');
        }
    }
    
    updateActiveFilters();
    loadArticles(1);
}

// Mobile filter toggle functionality
function initMobileFilters() {
    // Add mobile filter toggle button
    const searchSection = document.querySelector('.search-section .container');
    if (!searchSection) return;
    
    const mobileToggle = document.createElement('button');
    mobileToggle.className = 'mobile-filter-toggle';
    mobileToggle.innerHTML = '<i class="bi bi-funnel"></i> Фильтры';
    mobileToggle.onclick = toggleMobileFilters;
    
    // Insert before search grid
    const searchGrid = document.querySelector('.search-grid');
    if (searchGrid) {
        searchSection.insertBefore(mobileToggle, searchGrid);
    }
}

function toggleMobileFilters() {
    const searchGrid = document.querySelector('.search-grid');
    const toggle = document.querySelector('.mobile-filter-toggle');
    
    if (searchGrid && toggle) {
        searchGrid.classList.toggle('collapsed');
        const isCollapsed = searchGrid.classList.contains('collapsed');
        toggle.innerHTML = isCollapsed ? 
            '<i class="bi bi-funnel"></i> Показать фильтры' : 
            '<i class="bi bi-funnel-fill"></i> Скрыть фильтры';
    }
}

// Article grouping functionality
function addArticleGroupHeaders(articles) {
    if (!articles || !articles.length) return articles;
    
    const now = new Date();
    const oneDayAgo = new Date(now - 24 * 60 * 60 * 1000);
    const threeDaysAgo = new Date(now - 3 * 24 * 60 * 60 * 1000);
    
    const groups = {
        'new': [],
        'recent': [],
        'older': []
    };
    
    articles.forEach(article => {
        const publishDate = new Date(article.published_at);
        if (publishDate > oneDayAgo) {
            groups.new.push(article);
        } else if (publishDate > threeDaysAgo) {
            groups.recent.push(article);
        } else {
            groups.older.push(article);
        }
    });
    
    return groups;
}

function displayArticlesWithGroups(articles) {
    const container = document.getElementById('articlesContainer');
    const emptyState = document.getElementById('emptyState');
    
    if (!container) return;
    
    if (!articles.length) {
        container.innerHTML = '';
        if (emptyState) emptyState.style.display = 'block';
        return;
    }
    
    if (emptyState) emptyState.style.display = 'none';
    
    const groups = addArticleGroupHeaders(articles);
    let articlesHtml = '';
    
    // Add group sections with clean styling
    if (groups.new.length > 0) {
        articlesHtml += `
            <div class="article-group-header new">
                <i class="bi bi-lightning-fill" style="color: #22c55e;"></i>
                Новые (${groups.new.length})
            </div>
        `;
        articlesHtml += groups.new.map(article => createArticleCard(article)).join('');
    }
    
    if (groups.recent.length > 0) {
        articlesHtml += `
            <div class="article-group-header recent">
                <i class="bi bi-clock-fill" style="color: #3b82f6;"></i>
                Актуальные (${groups.recent.length})
            </div>
        `;
        articlesHtml += groups.recent.map(article => createArticleCard(article)).join('');
    }
    
    if (groups.older.length > 0) {
        articlesHtml += `
            <div class="article-group-header older">
                <i class="bi bi-archive-fill"></i>
                Архив (${groups.older.length})
            </div>
        `;
        articlesHtml += groups.older.map(article => createArticleCard(article)).join('');
    }
    
    container.innerHTML = articlesHtml;
}

// Update displayArticles to use grouping
function displayArticles(articles) {
    // Use grouped display for better organization
    displayArticlesWithGroups(articles);
}

// Initialize everything
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initializing MediaScope interface...');
    
    // Initialize theme
    initTheme();
    
    // Setup enhanced search
    setupSearch();
    
    // Initialize mobile filters
    initMobileFilters();
    
    // Load initial data
    Promise.all([
        loadStatistics(),
        loadSources(),
        loadArticles(1)
    ]).then(() => {
        console.log('✅ MediaScope interface loaded successfully');
    }).catch(error => {
        console.error('❌ Error initializing interface:', error);
        showError('Ошибка инициализации интерфейса');
    });
    
    // Auto-refresh statistics every 5 minutes
    setInterval(loadStatistics, 5 * 60 * 1000);
});

// Global functions for HTML onclick handlers
window.toggleTheme = toggleTheme;
window.searchArticles = searchArticles;
window.applyFilters = applyFilters;
window.loadArticles = loadArticles;
window.toggleFilter = toggleFilter;
window.removeFilter = removeFilter;
window.clearAllFilters = clearAllFilters;
window.filterByTag = filterByTag;
window.filterByLocation = filterByLocation;
window.toggleMobileFilters = toggleMobileFilters;
window.toggleArticleFeatured = toggleArticleFeatured;

// Toggle article featured status
async function toggleArticleFeatured(articleId, buttonElement) {
    try {
        // Сохраняем текущее состояние для возможного отката
        const originalContent = buttonElement.innerHTML;
        const originalClasses = buttonElement.className;
        const originalTitle = buttonElement.title;
        const wasFeature = buttonElement.classList.contains('featured');
        
        // Оптимистичное обновление UI
        updateFeaturedButton(buttonElement, !wasFeature);
        
        // Показываем состояние загрузки
        buttonElement.innerHTML = '<i class="bi bi-hourglass-split"></i>';
        buttonElement.disabled = true;
        buttonElement.style.opacity = '0.7';
        
        const response = await fetch(`${API_BASE}/articles/${articleId}/toggle-featured/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Восстанавливаем стили и обновляем UI с правильным состоянием
        buttonElement.style.opacity = '1';
        updateFeaturedButton(buttonElement, data.is_featured);
        
        // Показываем уведомление
        showNotification(data.message, 'success');
        
        // Обновляем статистику
        loadStatistics();
        
        console.log(`✅ ${data.message}`);
        
    } catch (error) {
        console.error('❌ Error toggling featured status:', error);
        
        // Откатываем изменения при ошибке
        buttonElement.innerHTML = originalContent;
        buttonElement.className = originalClasses;
        buttonElement.title = originalTitle;
        buttonElement.disabled = false;
        buttonElement.style.opacity = '1';
        
        showNotification('Ошибка при изменении статуса избранного', 'error');
    }
}

// Update featured button appearance
function updateFeaturedButton(buttonElement, isFeatured) {
    buttonElement.disabled = false;
    
    // Убираем старые классы
    buttonElement.classList.remove('featured');
    
    if (isFeatured) {
        buttonElement.innerHTML = '<i class="bi bi-star-fill"></i>';
        buttonElement.classList.add('featured');
        buttonElement.title = 'Убрать из избранного';
        
        // Добавляем анимацию пульса
        const icon = buttonElement.querySelector('i');
        if (icon) {
            icon.style.animation = 'none';
            // Принудительный reflow для сброса анимации
            icon.offsetHeight;
            icon.style.animation = 'starPulse 0.4s ease-out';
        }
    } else {
        buttonElement.innerHTML = '<i class="bi bi-star"></i>';
        buttonElement.title = 'Добавить в избранное';
    }
}

// Show notification
function showNotification(message, type = 'info') {
    // Создаем контейнер для уведомлений если его нет
    let container = document.getElementById('notificationContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notificationContainer';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
        `;
        document.body.appendChild(container);
    }
    
    // Создаем уведомление
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        transform: translateX(100%);
        transition: transform 0.3s ease;
        display: flex;
        align-items: center;
        gap: 8px;
    `;
    
    const icon = type === 'success' ? 'check-circle-fill' : 
                 type === 'error' ? 'exclamation-triangle-fill' : 
                 'info-circle-fill';
    
    const color = type === 'success' ? '#22c55e' : 
                  type === 'error' ? '#ef4444' : 
                  '#3b82f6';
    
    notification.innerHTML = `
        <i class="bi bi-${icon}" style="color: ${color};"></i>
        <span style="color: var(--text-primary);">${message}</span>
    `;
    
    container.appendChild(notification);
    
    // Анимация появления
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 10);
    
    // Автоматическое удаление
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
} 