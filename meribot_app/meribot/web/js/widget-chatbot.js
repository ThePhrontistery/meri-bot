/**
 * MeriBotWidget - Widget de chat accesible y modular para MeriBot
 * ---------------------------------------------------------------
 * Este archivo implementa el widget de chat para la práctica Cloud & Custom Applications.
 * Cumple las convenciones del proyecto (ver /.github/copilot-instructions.md):
 * - Sintaxis moderna JS (ES2020+), sin frameworks ni var.
 * - Accesibilidad: roles, ARIA, contraste, estructura semántica.
 * - Modularidad y centralización de referencias DOM.
 * - Documentación con JSDoc en clase y métodos.
 * - Seguridad básica y manejo robusto de errores.
 *
 * @author Capgemini Cloud & Custom Applications
 * @fileoverview Widget de chat MeriBot: interfaz, eventos, comunicación backend y filtros.
 */

/**
 * Clase principal del widget de chat MeriBot.
 * Gestiona la UI, eventos, filtros y comunicación con el backend.
 */
class MeriBotWidget {
    /**
     * Inicializa el widget, referencias DOM y carga dominios.
     */
    constructor() {
        this.isOpen = false;
        this.conversations = [];
        this.selectedDomains = [];
        this.availableDomains = [];
        this.conversationId = null;
        this.filterDropdownVisible = false; // Estado del dropdown de filtros
        
        // Inicializar cuando el DOM esté listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
        
        this.scrollToBottom = () => {
            if (this.chatContainer) {
                // Aseguramos que el contenedor existe y tiene contenido
                if (this.chatContainer.scrollHeight > 0) {
                    this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
                } else {
                    // Si no tiene altura, esperamos un poco y volvemos a intentar
                    setTimeout(() => {
                        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
                    }, 100);
                }
            }
        };

        // Inicializar dominios y widget
        this.loadDomainsConfig();
    }

    /**
     * Carga la configuración de dominios permitidos desde el backend.
     * @async
     * @returns {Promise<void>}
     */
    async loadDomainsConfig() {
        try {
            const response = await fetch('http://localhost:8000/chatbot/allowed_domains');
            if (!response.ok) throw new Error('Network response was not ok');
            const config = await response.json();
            this.availableDomains = (config.allowed_domains || []).map(domain => ({
                id: domain,
                name: domain,
                color: '#0070ad',
                description: ''
            }));
        } catch (error) {
            console.error('Error loading domains:', error);
            this.availableDomains = [];
        }
        this.initializeWidget();
    }
    
    /**
     * Inicializa el widget: referencias, eventos y filtros.
     * @returns {void}
     */
    initializeWidget() {
        // Inicializar referencias DOM primero
        this.initializeDOMReferences();

        // Validar que tenemos todos los elementos necesarios
        if (!this.widgetTrigger || !this.widgetPanel) {
            console.error('Error: Elementos del widget no encontrados');
            return;
        }

        // Inicializar eventos y funcionalidad
        this.initializeBasicEvents();
        this.initializeFilterEvents();
        
        // Inicializar filtros
        this.initializeFilters();
        
        // Hacer visible el widget trigger después de la inicialización
        this.widgetTrigger.style.opacity = '1';
    }

    /**
     * Asigna y limpia listeners de eventos básicos del widget.
     * @returns {void}
     */
    initializeBasicEvents() {
        if (!this.widgetTrigger || !this.widgetPanel || !this.panelCloseButton || !this.messageInput || !this.sendButton) {
            console.error('Error: No se pudieron encontrar elementos básicos del DOM');
            return;
        }

        // Funciones manejadoras reutilizables
        const handleTogglePanel = () => {
            if (this.isOpen) {
                this.closePanel();
            } else {
                this.openPanel();
            }
        };
        const handleClosePanel = (e) => {
            e.preventDefault();
            this.closePanel();
        };
        const handleSendMessage = () => {
            this.sendMessage();
        };
        const handleKeyDown = (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        };
        const handleInputResize = function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        };

        // Limpiar listeners previos para evitar duplicidad
        this.widgetTrigger.replaceWith(this.widgetTrigger.cloneNode(true));
        this.panelCloseButton.replaceWith(this.panelCloseButton.cloneNode(true));
        this.sendButton.replaceWith(this.sendButton.cloneNode(true));
        this.messageInput.replaceWith(this.messageInput.cloneNode(true));
        // Reasignar referencias tras clonar
        this.initializeDOMReferences();

        // Asignar listeners únicos
        this.widgetTrigger.addEventListener('click', handleTogglePanel);
        this.panelCloseButton.addEventListener('click', handleClosePanel);
        this.widgetPanel.addEventListener('click', (e) => e.stopPropagation());
        this.sendButton.addEventListener('click', handleSendMessage);
        this.messageInput.addEventListener('keydown', handleKeyDown);
        this.messageInput.addEventListener('input', handleInputResize);
    }

    /**
     * Centraliza y actualiza referencias a elementos DOM clave.
     * @returns {void}
     */
    initializeDOMReferences() {
        this.chatContainer = document.querySelector('.chat-container');
        this.widgetPanel = document.getElementById('widgetPanel');
        this.widgetTrigger = document.getElementById('widgetTrigger');
        this.panelCloseButton = document.getElementById('panelCloseButton');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.filterButton = document.getElementById('filterButton');
        this.chatMessages = document.getElementById('chatMessages');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.selectedFiltersContainer = document.getElementById('selectedFilters');
        if (!this.chatContainer || !this.widgetPanel || !this.widgetTrigger) {
            console.error('Error: No se pudieron encontrar elementos DOM requeridos');
            return;
        }
    }

    /**
     * Muestra/oculta el dropdown de filtros de dominio.
     * @returns {void}
     */
    toggleFilterDropdown() {
        const dropdown = document.getElementById('filterDropdown');
        const filterButton = document.getElementById('filterButton');
        
        if (!dropdown || !filterButton) {
            console.error('Error: Filter elements not found');
            return;
        }
        
        // Toggle del estado del dropdown y el botón
        const isActive = dropdown.classList.contains('active');
        
        // Si no está activo, actualizar las opciones antes de mostrar
        if (!isActive) {
            this.initializeFilters();
        }
        
        // Aplicar las clases después de la inicialización
        if (isActive) {
            dropdown.classList.remove('active');
            filterButton.classList.remove('active');
        } else {
            dropdown.classList.add('active');
            filterButton.classList.add('active');
            // Forzar un reflow para asegurar que la animación funcione
            dropdown.offsetHeight;
        }
    }
    
    /**
     * Cierra el dropdown de filtros.
     * @returns {void}
     */
    closeFilterDropdown() {
        const dropdown = document.getElementById('filterDropdown');
        const filterButton = document.getElementById('filterButton');
        
        dropdown.classList.remove('active');
        filterButton.classList.remove('active');
    }
    
    /**
     * Añade o quita un dominio de los filtros seleccionados.
     * @param {string} domainId - ID del dominio a alternar.
     * @returns {void}
     */
    toggleDomainFilter(domainId) {
        const index = this.selectedDomains.indexOf(domainId);
        const isSelected = index > -1;
        
        // Actualizar estado
        if (isSelected) {
            // Quitar filtro
            this.selectedDomains.splice(index, 1);
        } else {
            // Añadir filtro
            this.selectedDomains.push(domainId);
        }
        
        // Actualizar UI inmediatamente
        const checkbox = document.querySelector(`.filter-checkbox[data-domain="${domainId}"]`);
        if (checkbox) {
            checkbox.classList.toggle('checked', !isSelected);
            checkbox.textContent = !isSelected ? '✓' : '';
        }
        
        // No cerrar el dropdown después de seleccionar
        this.updateSelectedFiltersDisplay();
        // Mantener el estado del dropdown y botón
        const dropdown = document.getElementById('filterDropdown');
        const filterButton = document.getElementById('filterButton');
        if (dropdown && filterButton) {
            dropdown.classList.add('active');
            filterButton.classList.add('active');
        }
    }
    
    /**
     * Actualiza la UI de los filtros según los dominios seleccionados.
     * @returns {void}
     */
    updateFilterUI() {
        // Solo actualizar si hay dominios disponibles
        if (!this.availableDomains || this.availableDomains.length === 0) return;

        this.availableDomains.forEach(domain => {
            const option = document.querySelector(`[data-domain-id="${domain.id}"]`);
            // Si no existe el elemento, no hacer nada
            if (!option) return;
            
            const checkbox = option.querySelector('.filter-checkbox');
            if (!checkbox) return;
            
            const checkIcon = checkbox.querySelector('i');
            if (!checkIcon) return;
            
            if (this.selectedDomains.includes(domain.id)) {
                option.classList.add('selected');
                checkbox.classList.add('checked');
                checkIcon.style.display = 'block';
            } else {
                option.classList.remove('selected');
                checkbox.classList.remove('checked');
                checkIcon.style.display = 'none';
            }
        });
    }
    
    /**
     * Función auxiliar para crear un pill de filtro
     * @param {Object} domain - Objeto dominio.
     * @param {string} domainId - ID del dominio.
     * @returns {HTMLDivElement}
     */
    createFilterPill(domain, domainId) {
        const pill = document.createElement('div');
        pill.className = 'filter-pill';
        pill.innerHTML = `
            ${domain.name}
            <span class="filter-pill-remove" data-domain-id="${domainId}">×</span>
        `;
        pill.querySelector('.filter-pill-remove').addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleDomainFilter(domainId);
        });
        return pill;
    }

    /**
     * Actualiza la visualización de los filtros seleccionados.
     * @returns {void}
     */
    updateSelectedFiltersDisplay() {
        const container = this.selectedFiltersContainer;
        container.innerHTML = '';
        if (this.selectedDomains.length === 0) {
            container.style.display = 'none';
            return;
        }
        container.style.display = 'flex';
        this.selectedDomains.forEach(domainId => {
            const domain = this.availableDomains.find(d => d.id === domainId);
            if (domain) {
                container.appendChild(this.createFilterPill(domain, domainId));
            }
        });
    }

    /**
     * Construye el HTML de las fuentes/citas de un mensaje del bot.
     * @param {Object|Array} sources - Fuentes de información.
     * @returns {string} HTML generado.
     */
    buildSourcesHTML(sources) {
        if (!sources) return '';
        let sourcesHTML = '';
        if (Array.isArray(sources) && sources.length > 0) {
            sources.forEach((source, idx) => {
                const linkText = source.title ? source.title : (source.url ? source.url : 'Documento original');
                let url = source.url || '#';
                if (url && !/^https?:\/\//i.test(url) && url !== '#') {
                    url = window.location.origin + (url.startsWith('/') ? url : '/' + url);
                }
                sourcesHTML += `
                    <div class="source-indicator" 
                        data-source='${JSON.stringify(source)}' 
                        title="Ver fuente de información"
                        aria-label="Ver fuente de información"
                        style="position: absolute; bottom: 8px; right: ${8 + idx * 28}px; z-index: 10; cursor: pointer;">
                        <i class="fas fa-link"></i>
                        <div class="source-tooltip">
                            <div class="source-tooltip-title">Fuente consultada</div>
                            <div class="source-tooltip-subtitle">${source.title || ''}</div>
                            <a href="${url}" target="_blank" class="source-tooltip-link" title="${url}">
                                ${linkText} <i class="fas fa-external-link-alt"></i>
                            </a>
                        </div>
                    </div>
                `;
            });
        } else if (typeof sources === 'object' && sources.url) {
            const linkText = sources.title ? sources.title : (sources.url ? sources.url : 'Documento original');
            let url = sources.url || '#';
            if (url && !/^https?:\/\//i.test(url) && url !== '#') {
                url = window.location.origin + (url.startsWith('/') ? url : '/' + url);
            }
            sourcesHTML = `
                <div class="source-indicator" 
                    data-source='${JSON.stringify(sources)}' 
                    title="Ver fuente de información"
                    aria-label="Ver fuente de información"
                    style="position: absolute; bottom: 8px; right: 8px; z-index: 10; cursor: pointer;">
                    <i class="fas fa-link"></i>
                    <div class="source-tooltip">
                        <div class="source-tooltip-title">Fuente consultada</div>
                        <div class="source-tooltip-subtitle">${sources.title || ''}</div>
                        <a href="${url}" target="_blank" class="source-tooltip-link" title="${url}">
                            ${linkText} <i class="fas fa-external-link-alt"></i>
                        </a>
                    </div>
                </div>
            `;
        }
        return sourcesHTML;
    }

    /**
     * Añade un mensaje al historial y a la UI.
     * @param {string} sender - 'user' o 'bot'.
     * @param {string} text - Mensaje.
     * @param {Object|Array} [sources] - Fuentes/citas opcionales.
     * @returns {void}
     */
    addMessage(sender, text, sources = null) {
        const messagesContainer = this.chatMessages;
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        const time = new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
        let sourcesHTML = sender === 'bot' ? this.buildSourcesHTML(sources) : '';
        let processedText = text;
        if (sender === 'bot' && !/^\s*<.+?>/.test(text.trim())) {
            processedText = marked.parse(text, { breaks: true, gfm: true });
        }
        let messageBubbleHTML = '';
        if (sender === 'bot' && sourcesHTML) {
            messageBubbleHTML = `
                <div class="message-bubble" style="position: relative; padding-bottom: 32px;">
                    ${sourcesHTML}
                    <div>${processedText}</div>
                </div>
            `;
        } else {
            messageBubbleHTML = `
                <div class="message-bubble" style="position: relative;">
                    ${sender === 'bot' ? processedText : text}
                </div>
            `;
        }
        messageDiv.innerHTML = `
            <div class="avatar-small">
                ${sender === 'bot' ? '' : 'Tú'}
            </div>
            <div class="message-content">
                ${messageBubbleHTML}
                <div class="message-time">${time}</div>
            </div>
        `;
        this.conversations.push({ sender, text, timestamp: new Date(), sources });
        messagesContainer.appendChild(messageDiv);
        messageDiv.style.opacity = '0';
        setTimeout(() => {
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0)';
        }, 50);
        messageDiv.style.transform = 'translateY(20px)';
        setTimeout(() => { this.scrollToBottom(); }, 50);
        // Eventos para tooltips de fuente (sin cambios)
        if (sender === 'bot' && sources && Array.isArray(sources) && sources.length > 0) {
            const indicators = messageDiv.querySelectorAll('.source-indicator');
            indicators.forEach(indicator => {
                const tooltip = indicator.querySelector('.source-tooltip');
                indicator.addEventListener('click', (e) => {
                    e.stopPropagation();
                    document.querySelectorAll('.source-tooltip.active').forEach(t => {
                        if (t !== tooltip) t.classList.remove('active');
                    });
                    tooltip.classList.toggle('active');
                });
                document.addEventListener('click', (e) => {
                    if (!indicator.contains(e.target)) {
                        tooltip.classList.remove('active');
                    }
                });
                indicator.addEventListener('blur', () => {
                    tooltip.classList.remove('active');
                });
            });
            const chatPanel = document.getElementById('widgetPanel');
            if (chatPanel) {
                chatPanel.addEventListener('click', (e) => {
                    if (!e.target.closest('.source-indicator') && !e.target.closest('.source-tooltip')) {
                        document.querySelectorAll('.source-tooltip.active').forEach(t => t.classList.remove('active'));
                    }
                });
            }
        }
    }
    
    /**
     * Muestra el indicador de "escribiendo" del bot.
     * @returns {void}
     */
    showTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        indicator.classList.add('active');
        setTimeout(() => this.scrollToBottom(), 100); // Esperamos un poco para asegurar que el indicador está visible
    }
    
    /**
     * Oculta el indicador de "escribiendo".
     * @returns {void}
     */
    hideTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        indicator.classList.remove('active');
    }

    /**
     * Resetea la conversación y filtros seleccionados.
     * @returns {void}
     */
    resetConversation() {
        this.conversations = [];
        this.conversationId = null; // Reiniciar conversation_id
        this.selectedDomains = []; // Limpiar dominios seleccionados
        const messagesContainer = document.getElementById('chatMessages');
        if (messagesContainer) {
            messagesContainer.innerHTML = '';
        }
        this.updateFilterUI();
        this.updateSelectedFiltersDisplay();
    }
    
    /**
     * Alterna la visibilidad del widget.
     * @returns {void}
     */
    toggleWidget() {
        this.isOpen = !this.isOpen;
        if (this.isOpen) {
            this.resetConversation();
            this.widgetTrigger.classList.add('active');
            this.widgetPanel.classList.add('active');
            setTimeout(() => {
                this.messageInput.focus();
            }, 300);
        } else {
            this.closePanel();
        }
    }
    
    /**
     * Abre el panel de chat y muestra mensaje de bienvenida.
     * @returns {void}
     */
    openPanel() {
        if (!this.isOpen && this.widgetPanel) {
            this.isOpen = true;
            this.initializeFilters();
            this.resetConversation();
            this.widgetTrigger.classList.add('active');
            this.widgetTrigger.querySelector('.widget-text').textContent = 'Cerrar chat';
            this.widgetTrigger.setAttribute('aria-label', 'Cerrar chat de MeriBot');
            this.widgetPanel.classList.add('active');
            setTimeout(() => {
                setTimeout(() => this.scrollToBottom(), 400);
                this.showWelcomeMessage();
            }, 10);
        }
    }

    /**
     * Cierra el panel de chat y limpia estados.
     * @returns {void}
     */
    closePanel() {
        if (this.widgetTrigger) {
            this.widgetTrigger.classList.remove('active');
            if (this.widgetTrigger.querySelector('.widget-text')) {
                this.widgetTrigger.querySelector('.widget-text').textContent = 'Pregunta a MeriBot';
            }
            this.widgetTrigger.setAttribute('aria-label', 'Abrir chat de MeriBot');
        }
        if (this.widgetPanel) this.widgetPanel.classList.remove('active');
        if (this.messageInput) {
            this.messageInput.value = '';
            this.messageInput.style.height = '';
        }
        this.selectedDomains = [];
        this.updateFilterUI && this.updateFilterUI();
        this.updateSelectedFiltersDisplay && this.updateSelectedFiltersDisplay();
        const filterDropdown = document.getElementById('filterDropdown');
        const filterButton = document.getElementById('filterButton');
        if (filterDropdown && filterDropdown.classList.contains('active')) {
            filterDropdown.classList.remove('active');
        }
        if (filterButton && filterButton.classList.contains('active')) {
            filterButton.classList.remove('active');
        }
        this.initializeFilters && this.initializeFilters();
        this.isOpen = false;
    }

    /**
     * Inicializa las opciones de filtro de dominio.
     * @returns {void}
     */
    initializeFilters() {
        const dropdown = document.getElementById('filterDropdown');
        if (!dropdown) {
            console.error('Error: Filter dropdown not found');
            return;
        }
        
        // Si el dropdown está visible, no reinicializar
        if (dropdown.classList.contains('active')) {
            return;
        }
        
        // Limpiar el contenido actual
        dropdown.innerHTML = '';
        
        // Verificar si hay dominios disponibles
        if (!this.availableDomains || this.availableDomains.length === 0) {
            console.warn('No hay dominios disponibles para mostrar');
            dropdown.innerHTML = '<div class="filter-option">No hay dominios disponibles</div>';
            return;
        }
        
        // Crear las opciones de filtro para cada dominio
        this.availableDomains.forEach(domain => {
            const option = document.createElement('div');
            option.className = 'filter-option';
            option.setAttribute('data-domain-id', domain.id);
            const isSelected = this.selectedDomains.includes(domain.id);
            
            option.innerHTML = `
                <span>${domain.name}</span>
                <div class="filter-checkbox ${isSelected ? 'checked' : ''}" data-domain="${domain.id}">
                    ${isSelected ? '✓' : ''}
                </div>
            `;
            
            if (domain.description) {
                option.title = domain.description;
            }
            
            // Agregar evento de clic
            const handleClick = (e) => {
                e.stopPropagation();
                const checkbox = option.querySelector('.filter-checkbox');
                const domainId = checkbox.dataset.domain;
                this.toggleDomainFilter(domainId);
            };
            
            // Remover evento anterior si existe
            option.removeEventListener('click', handleClick);
            option.addEventListener('click', handleClick);
            
            dropdown.appendChild(option);
        });
    }

    /**
     * Inicializa eventos del filtro de dominio.
     * @returns {void}
     */
    initializeFilterEvents() {
        if (!this.filterButton) {
            console.error('Error: Filter button not found');
            return;
        }

        const filterDropdown = document.getElementById('filterDropdown');
        if (!filterDropdown) {
            console.error('Error: Filter dropdown not found');
            return;
        }

        // Remover eventos anteriores si existen
        const oldButton = this.filterButton.cloneNode(true);
        this.filterButton.parentNode.replaceChild(oldButton, this.filterButton);
        this.filterButton = oldButton;

        // Toggle del dropdown al hacer clic en el botón
        this.filterButton.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.toggleFilterDropdown();
        });

        // Manejar clics en el panel del widget
        const handlePanelClick = (e) => {
            // Si el dropdown está activo y el clic no fue ni en el dropdown ni en el botón de filtro
            if (filterDropdown.classList.contains('active') && 
                !filterDropdown.contains(e.target) && 
                !this.filterButton.contains(e.target)) {
                this.closeFilterDropdown();
            }
        };

        // Remover listener anterior si existe del panel del widget
        const widgetPanel = document.getElementById('widgetPanel');
        if (widgetPanel) {
            widgetPanel.removeEventListener('click', handlePanelClick);
            widgetPanel.addEventListener('click', handlePanelClick);
        }
        
        // Prevenir que los clics dentro del dropdown lo cierren
        filterDropdown.addEventListener('click', (e) => {
            e.stopPropagation();
        });
        
        // Inicializar las opciones del filtro una sola vez
        this.initializeFilterOptions(filterDropdown);
    }

    /**
     * Crea las opciones visuales del dropdown de filtros.
     * @param {HTMLElement} filterDropdown - Elemento dropdown.
     * @returns {void}
     */
    initializeFilterOptions(filterDropdown) {
        // Limpiar opciones existentes
        filterDropdown.innerHTML = '';

        // Crear y agregar nuevas opciones para cada dominio
        this.availableDomains.forEach(domain => {
            const option = document.createElement('div');
            option.className = 'filter-option';
            
            const isSelected = this.selectedDomains.includes(domain.id);
            option.innerHTML = `
                <span>${domain.name}</span>
                <div class="filter-checkbox ${isSelected ? 'checked' : ''}" data-domain="${domain.id}">
                    ${isSelected ? '✓' : ''}
                </div>
            `;

            // Añadir descripción si existe
            if (domain.description) {
                option.title = domain.description;
            }

            // Evento de clic en la opción que dispara la selección del filtro
            option.addEventListener('click', (e) => {
                e.stopPropagation();
                const checkbox = option.querySelector('.filter-checkbox');
                const domainId = checkbox.dataset.domain;
                this.toggleDomainFilter(domainId);
            });

            filterDropdown.appendChild(option);
        });

        // Si no hay dominios, mostrar mensaje
        if (this.availableDomains.length === 0) {
            const emptyMessage = document.createElement('div');
            emptyMessage.className = 'filter-option';
            emptyMessage.textContent = 'No hay dominios disponibles';
            filterDropdown.appendChild(emptyMessage);
        }
    }

    /**
     * Actualiza la visualización de los filtros seleccionados (legacy).
     * @returns {void}
     */
    updateFilterSelection() {
        const selectedFilters = document.querySelector('.selected-filters');
        if (!selectedFilters) return;

        // Mostrar u ocultar el contenedor según haya filtros seleccionados
        selectedFilters.style.display = this.selectedDomains.length > 0 ? 'flex' : 'none';

        // Limpiar filtros existentes
        selectedFilters.innerHTML = '';

        // Agregar nuevos pills para cada dominio seleccionado
        this.selectedDomains.forEach(domainId => {
            const domain = this.availableDomains.find(d => d.id === domainId);
            if (!domain) return;

            const pill = document.createElement('div');
            pill.className = 'filter-pill';
            pill.innerHTML = `
                ${domain.name}
                <span class="filter-pill-remove" data-domain="${domain.id}">×</span>
            `;

            // Evento para remover el filtro
            pill.querySelector('.filter-pill-remove').addEventListener('click', (e) => {
                const domainToRemove = e.target.dataset.domain;
                this.selectedDomains = this.selectedDomains.filter(id => id !== domainToRemove);
                this.updateFilterSelection();
                this.initializeFilterOptions(document.getElementById('filterDropdown'));
            });

            selectedFilters.appendChild(pill);
        });
    }

    /**
     * Muestra el mensaje de bienvenida del bot.
     * @returns {void}
     */
    showWelcomeMessage() {
        setTimeout(() => {
            const welcomeContent = `
                <div style="text-align: center; padding: 15px 10px 8px; color: #666;">
                    <div style="width: 60px; height: 60px; background: var(--capgemini-white); background-image: url('./img/Icono_Widget.png'); background-size: 80%; background-repeat: no-repeat; background-position: center; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px; border: 3px solid var(--capgemini-vibrant-blue);"></div>
                    <h4 style="font-size: 16px; font-weight: 700; margin-bottom: 8px; color: var(--color-text-dark);">¡Hola! Soy MeriBot</h4>
                    <p style="font-size: 14px; line-height: 1.4; margin-bottom: 12px;">Tu asistente virtual de Cloud & Custom Applications. Estoy aquí para ayudarte con información sobre la práctica, formaciones, contactos y más.</p>
                    <p>¿En qué puedo ayudarte hoy?</p>
                </div>
            `;
            this.addMessage('bot', welcomeContent);
        }, 500);
    }

    /**
     * Envía el mensaje del usuario (input) al backend.
     * @returns {void}
     */
    sendMessage() {
        const input = this.messageInput;
        const message = input.value.trim();
        if (message) {
            this.sendUserMessage(message);
            input.value = '';
            input.style.height = '';
            this.scrollToBottom();
        }
    }

    /**
     * Procesa y envía el mensaje del usuario al backend, mostrando respuesta.
     * @param {string} message - Mensaje del usuario.
     * @returns {void}
     */
    sendUserMessage(message) {
        const messageInput = this.messageInput;
        const sendButton = this.sendButton;
        messageInput.disabled = true;
        sendButton.disabled = true;
        this.addMessage('user', message);
        setTimeout(() => this.scrollToBottom(), 100);
        this.showTypingIndicator();

        // Preparar payload para la API
        const payload = {
            question: message,
            conversation_id: this.conversationId || null,
            domains: this.selectedDomains.length > 0 ? this.selectedDomains : undefined
        };

        fetch('http://localhost:8000/chatbot/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        })
        .then(async (response) => {
            this.hideTypingIndicator();
            // Habilitar input y botón
            messageInput.disabled = false;
            sendButton.disabled = false;
            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }
            const data = await response.json();
            // Guardar conversation_id de la respuesta para la siguiente interacción
            if (data && data.conversation_id) {
                this.conversationId = data.conversation_id;
            }
            // Mostrar la respuesta real del backend y las citas si existen
            if (data && data.response) {
                if (data.citations && Array.isArray(data.citations) && data.citations.length > 0) {
                    this.addMessage('bot', data.response, data.citations);
                } else {
                    this.addMessage('bot', data.response);
                }
            } else {
                this.addMessage('bot', 'No se ha recibido respuesta válida del servidor.');
            }
        })
        .catch((error) => {
            this.hideTypingIndicator();
            messageInput.disabled = false;
            sendButton.disabled = false;
            this.addMessage('bot', 'Error al conectar con el servidor: ' + error.message);
        });
    }

    /**
     * Inicializa referencias DOM tras carga del documento.
     * @returns {void}
     */
    init() {
        // Inicializar referencias DOM
        this.initializeDOMReferences();
        
        // Solo continuar si las referencias DOM son válidas
        if (!(this.widgetTrigger && this.widgetPanel)) {
            console.error('Error: No se pudieron encontrar elementos DOM requeridos');
        }
    }
}

// Inicializar widget cuando la página esté cargada
document.addEventListener('DOMContentLoaded', () => {
    new MeriBotWidget();
    
    // Mostrar notificación de bienvenida después de 3 segundos
    setTimeout(() => {
        const badge = document.querySelector('.notification-badge');
        if (badge) {
            badge.style.display = 'flex';
        }
    }, 3000);
});
