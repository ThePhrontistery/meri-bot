class CCASearchWidget {
    constructor(options = {}) {
        this.options = {
            apiUrl: options.apiUrl || 'http://localhost:5000/api/search',
            position: options.position || 'bottom-right',
            theme: options.theme || 'light',
            language: options.language || 'es',
            autoInit: options.autoInit !== false
        };
        
        this.isOpen = false;
        this.isSearching = false;
        
        if (this.options.autoInit) {
            this.init();
        }
    }

    init() {
        this.createWidget();
        this.bindEvents();
        this.render();
    }

    createWidget() {
        // Create container
        this.container = document.createElement('div');
        this.container.className = 'search-widget';
        this.container.style.display = 'none';
        
        // Create header
        this.container.innerHTML = `
            <div class="search-header">
                <h2 class="search-title">Buscador Semántico</h2>
                <button class="search-close">&times;</button>
            </div>
            <div class="search-box">
                <div class="search-input-container">
                    <input type="text" class="search-input" placeholder="Buscar en los documentos...">
                    <button class="search-button">
                        <i class="fas fa-search"></i>
                    </button>
                </div>
            </div>
            <div class="search-filters">
                <div class="filter-group">
                    <label for="doc-type">Tipo de documento</label>
                    <select id="doc-type" class="doc-type">
                        <option value="">Todos</option>
                        <option value="pdf">PDF</option>
                        <option value="docx">Word</option>
                        <option value="html">HTML</option>
                        <option value="txt">Texto</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label for="sort-by">Ordenar por</label>
                    <select id="sort-by" class="sort-by">
                        <option value="relevance">Relevancia</option>
                        <option value="date">Fecha</option>
                        <option value="title">Título</option>
                    </select>
                </div>
            </div>
            <div class="search-results">
                <div class="no-results">
                    <i class="fas fa-search"></i>
                    <p>Ingresa un término de búsqueda para comenzar</p>
                </div>
            </div>
        `;
        
        document.body.appendChild(this.container);
        
        // Store references to important elements
        this.searchInput = this.container.querySelector('.search-input');
        this.searchButton = this.container.querySelector('.search-button');
        this.resultsContainer = this.container.querySelector('.search-results');
        this.closeButton = this.container.querySelector('.search-close');
        this.docTypeFilter = this.container.querySelector('.doc-type');
        this.sortByFilter = this.container.querySelector('.sort-by');
    }

    bindEvents() {
        // Toggle widget visibility
        document.addEventListener('click', (e) => {
            if (e.target.matches('.search-widget, .search-widget *')) return;
            if (this.isOpen) this.hide();
        });
        
        // Search on button click
        this.searchButton.addEventListener('click', () => this.performSearch());
        
        // Search on Enter key
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.performSearch();
        });
        
        // Close button
        this.closeButton.addEventListener('click', () => this.hide());
        
        // Update search when filters change
        this.docTypeFilter.addEventListener('change', () => this.performSearch());
        this.sortByFilter.addEventListener('change', () => this.performSearch());
    }

    async performSearch() {
        const query = this.searchInput.value.trim();
        if (!query) {
            this.showNoResults('Ingresa un término de búsqueda');
            return;
        }
        
        this.showLoading();
        
        try {
            const response = await fetch(this.options.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    docType: this.docTypeFilter.value || null,
                    sortBy: this.sortByFilter.value
                })
            });
            
            if (!response.ok) throw new Error('Error en la búsqueda');
            
            const data = await response.json();
            this.displayResults(data.results || [], query);
            
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Error al realizar la búsqueda');
        }
    }

    displayResults(results, query) {
        if (!results || results.length === 0) {
            this.showNoResults('No se encontraron resultados');
            return;
        }
        
        const resultsHtml = results.map(result => `
            <div class="result-item">
                <h3 class="result-title">
                    ${this.highlightMatches(result.title || 'Documento sin título', query)}
                    <span class="result-source">${this.getFileIcon(result.source)} ${this.formatSource(result.source)}</span>
                </h3>
                <div class="result-content">
                    ${this.highlightMatches(this.truncateText(result.content, 200), query)}
                </div>
                <div class="result-meta">
                    <span class="result-score">${(result.score * 100).toFixed(1)}% relevancia</span>
                    ${result.page ? `<span>Página ${result.page}</span>` : ''}
                </div>
            </div>
        `).join('');
        
        this.resultsContainer.innerHTML = resultsHtml;
    }

    showLoading() {
        this.resultsContainer.innerHTML = `
            <div class="search-loading">
                <div class="loading-spinner"></div>
                <p>Buscando información...</p>
            </div>
        `;
    }

    showNoResults(message) {
        this.resultsContainer.innerHTML = `
            <div class="no-results">
                <i class="fas fa-search"></i>
                <p>${message}</p>
            </div>
        `;
    }

    showError(message) {
        this.resultsContainer.innerHTML = `
            <div class="no-results">
                <i class="fas fa-exclamation-triangle"></i>
                <p>${message}</p>
            </div>
        `;
    }

    highlightMatches(text, query) {
        if (!text || !query) return text || '';
        
        const terms = query.split(' ').filter(term => term.length > 2);
        let highlighted = text;
        
        terms.forEach(term => {
            const regex = new RegExp(`(${this.escapeRegExp(term)})`, 'gi');
            highlighted = highlighted.replace(regex, '<span class="highlight">$1</span>');
        });
        
        return highlighted;
    }

    escapeRegExp(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    truncateText(text, maxLength) {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    getFileIcon(filePath) {
        if (!filePath) return '📄';
        
        const extension = filePath.split('.').pop().toLowerCase();
        const icons = {
            'pdf': '📄',
            'doc': '📝',
            'docx': '📝',
            'txt': '📄',
            'html': '🌐',
            'htm': '🌐',
            'xls': '📊',
            'xlsx': '📊',
            'ppt': '📑',
            'pptx': '📑'
        };
        
        return icons[extension] || '📄';
    }

    formatSource(source) {
        if (!source) return 'Documento';
        return source.split('/').pop() || 'Documento';
    }

    show() {
        this.container.style.display = 'flex';
        this.isOpen = true;
        this.searchInput.focus();
    }

    hide() {
        this.container.style.display = 'none';
        this.isOpen = false;
    }

    toggle() {
        if (this.isOpen) {
            this.hide();
        } else {
            this.show();
        }
    }

    render() {
        // Add styles if not already added
        if (!document.getElementById('cca-search-styles')) {
            const styleLink = document.createElement('link');
            styleLink.id = 'cca-search-styles';
            styleLink.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css';
            styleLink.rel = 'stylesheet';
            document.head.appendChild(styleLink);
            
            const customStyle = document.createElement('style');
            customStyle.textContent = `
                .search-widget {
                    font-family: 'Ubuntu', sans-serif;
                }
                .highlight {
                    background-color: rgba(18, 171, 219, 0.2);
                    padding: 0 2px;
                    border-radius: 2px;
                }
            `;
            document.head.appendChild(customStyle);
        }
        
        // Add Google Fonts if not already added
        if (!document.getElementById('google-fonts')) {
            const fontLink = document.createElement('link');
            fontLink.id = 'google-fonts';
            fontLink.href = 'https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Ubuntu:wght@400;700&display=swap';
            fontLink.rel = 'stylesheet';
            document.head.appendChild(fontLink);
        }
    }
}

// Auto-initialize if script is included directly
if (typeof window !== 'undefined') {
    window.CCASearchWidget = CCASearchWidget;
    
    // Auto-initialize with default options if data attributes are present
    document.addEventListener('DOMContentLoaded', () => {
        const widgetEl = document.querySelector('[data-cca-search-widget]');
        if (widgetEl) {
            const options = {
                apiUrl: widgetEl.getAttribute('data-api-url') || undefined,
                position: widgetEl.getAttribute('data-position') || undefined,
                theme: widgetEl.getAttribute('data-theme') || undefined,
                language: widgetEl.getAttribute('data-language') || undefined
            };
            
            const widget = new CCASearchWidget(options);
            widgetEl.addEventListener('click', (e) => {
                e.preventDefault();
                widget.toggle();
            });
        }
    });
}

export default CCASearchWidget;
