document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const docTypeFilter = document.getElementById('doc-type');
    const sortByFilter = document.getElementById('sort-by');
    const resultsContainer = document.getElementById('results');
    const loadingIndicator = document.getElementById('loading');
    
    // Estado de la aplicación
    let isSearching = false;
    let currentQuery = '';
    
    // Función para mostrar el indicador de carga
    function showLoading(show) {
        if (show) {
            loadingIndicator.classList.remove('hidden');
            resultsContainer.innerHTML = '';
        } else {
            loadingIndicator.classList.add('hidden');
        }
    }
    
    // Función para formatear la fecha
    function formatDate(dateString) {
        if (!dateString) return 'Fecha no disponible';
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        return new Date(dateString).toLocaleDateString('es-ES', options);
    }
    
    // Función para resaltar términos de búsqueda en el texto
    function highlightText(text, query) {
        if (!query) return text;
        
        const terms = query.split(' ').filter(term => term.length > 2);
        let highlighted = text;
        
        terms.forEach(term => {
            const regex = new RegExp(`(${escapeRegExp(term)})`, 'gi');
            highlighted = highlighted.replace(regex, '<span class="highlight">$1</span>');
        });
        
        return highlighted;
    }
    
    // Función auxiliar para escapar caracteres especiales en expresiones regulares
    function escapeRegExp(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
    
    // Función para obtener el ícono según el tipo de archivo
    function getFileIcon(filePath) {
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
    
    // Función para mostrar los resultados de la búsqueda
    function displayResults(results, query) {
        resultsContainer.innerHTML = '';
        
        if (!results || results.length === 0) {
            resultsContainer.innerHTML = `
                <div class="no-results">
                    <i class="fas fa-inbox"></i>
                    <p>No se encontraron resultados para tu búsqueda.</p>
                </div>
            `;
            return;
        }
        
        results.forEach((result, index) => {
            const resultElement = document.createElement('div');
            resultElement.className = 'result-card';
            resultElement.style.animationDelay = `${index * 50}ms`;
            
            const fileIcon = getFileIcon(result.source);
            const highlightedContent = highlightText(result.content, query);
            const sourceName = result.source ? result.source.split('/').pop() || 'Documento' : 'Documento';
            
            resultElement.innerHTML = `
                <div class="result-header">
                    <h3 class="result-title">
                        ${result.title || 'Documento sin título'}
                        <span class="result-source">${fileIcon} ${sourceName}</span>
                    </h3>
                </div>
                <div class="result-content">
                    ${highlightedContent}
                </div>
                <div class="result-footer">
                    <span class="result-score">Relevancia: ${(result.score * 100).toFixed(1)}%</span>
                    ${result.source ? `
                        <a href="${result.source}" class="result-link" target="_blank">
                            Ver documento <i class="fas fa-external-link-alt"></i>
                        </a>
                    ` : ''}
                </div>
            `;
            
            resultsContainer.appendChild(resultElement);
        });
    }
    
    // Función para realizar la búsqueda
    async function performSearch() {
        const query = searchInput.value.trim();
        
        if (!query || isSearching) return;
        
        currentQuery = query;
        isSearching = true;
        showLoading(true);
        
        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    docType: docTypeFilter.value || null,
                    sortBy: sortByFilter.value
                })
            });
            
            if (!response.ok) {
                throw new Error('Error en la búsqueda');
            }
            
            const data = await response.json();
            displayResults(data.results, query);
            
        } catch (error) {
            console.error('Error:', error);
            resultsContainer.innerHTML = `
                <div class="bg-red-50 border-l-4 border-red-500 p-4">
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <i class="fas fa-exclamation-circle text-red-500 text-xl"></i>
                        </div>
                        <div class="ml-3">
                            <p class="text-sm text-red-700">Error al realizar la búsqueda. Por favor, inténtalo de nuevo.</p>
                        </div>
                    </div>
                </div>
            `;
        } finally {
            isSearching = false;
            showLoading(false);
        }
    }
    
    // Event Listeners
    searchBtn.addEventListener('click', performSearch);
    
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
    
    // Actualizar búsqueda cuando cambian los filtros
    docTypeFilter.addEventListener('change', performSearch);
    sortByFilter.addEventListener('change', performSearch);
    
    // Inicialización
    showLoading(false);
});
