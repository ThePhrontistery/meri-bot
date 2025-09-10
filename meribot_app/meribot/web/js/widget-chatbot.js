class MeriBotWidget {
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

    initializeBasicEvents() {
        if (!this.widgetTrigger || !this.widgetPanel || !this.panelCloseButton || !this.panelOverlay || !this.messageInput || !this.sendButton) {
            console.error('Error: No se pudieron encontrar elementos básicos del DOM');
            return;
        }

        // Evento para toggle del panel
        this.widgetTrigger.addEventListener('click', () => {
            if (this.isOpen) {
                this.closePanel();
            } else {
                this.openPanel();
            }
        });

        // Evento para cerrar el panel con el botón
        this.panelCloseButton.addEventListener('click', (e) => {
            e.preventDefault();
            this.closePanel();
        });

        // Evento para cerrar al hacer clic en el overlay
        this.panelOverlay.addEventListener('click', (e) => {
            e.preventDefault();
            this.closePanel();
        });

        // Prevenir que los clics dentro del panel lo cierren
        this.widgetPanel.addEventListener('click', (e) => {
            e.stopPropagation();
        });

        // Evento para enviar mensaje con el botón
        this.sendButton.addEventListener('click', () => {
            this.sendMessage();
        });

        // Evento para enviar mensaje con Enter (pero nueva línea con Shift+Enter)
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-ajustar altura del textarea
        this.messageInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    }

    initializeDOMReferences() {
        this.chatContainer = document.querySelector('.chat-container');
        this.widgetPanel = document.getElementById('widgetPanel');
        this.widgetTrigger = document.getElementById('widgetTrigger');
        this.panelOverlay = document.getElementById('panelOverlay');
        this.panelCloseButton = document.getElementById('panelCloseButton');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.filterButton = document.getElementById('filterButton');
        this.chatMessages = document.getElementById('chatMessages');
        this.typingIndicator = document.getElementById('typingIndicator');
        
        if (!this.chatContainer || !this.widgetPanel || !this.widgetTrigger) {
            console.error('Error: No se pudieron encontrar elementos DOM requeridos');
            return;
        }
    }

    async initialize() {
        // Primero inicializar los eventos básicos
        this.initializeBasicEvents();
        
        // Luego cargar la configuración de dominios
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
            console.warn('Could not load domains config, using fallback');
            // Fallback configuration
            this.availableDomains = [
                {
                    id: "talent",
                    name: "Talent",
                    color: "#0070ad",
                    description: "Gestión de talento, recursos humanos, carrera profesional"
                },
                {
                    id: "onboarding",
                    name: "Onboarding",
                    color: "#12abdb",
                    description: "Proceso de incorporación, primeros pasos, orientación inicial"
                },
                {
                    id: "formacion",
                    name: "Formación",
                    color: "#272936",
                    description: "Cursos, certificaciones, desarrollo profesional, AC&CAdemy"
                }
            ];
            this.initializeFilters(); // <-- También en el fallback
        }
    }
    
    initializeBasicEvents() {
        if (!this.widgetTrigger || !this.widgetPanel || !this.panelCloseButton || !this.panelOverlay || !this.messageInput || !this.sendButton) {
            console.error('Error: No se pudieron encontrar elementos básicos del DOM');
            return;
        }

        // Evento para toggle del panel
        this.widgetTrigger.addEventListener('click', () => {
            if (this.isOpen) {
                this.closePanel();
            } else {
                this.openPanel();
            }
        });

        // Evento para cerrar el panel con el botón
        this.panelCloseButton.addEventListener('click', (e) => {
            e.preventDefault();
            this.closePanel();
        });

        // Evento para cerrar al hacer clic en el overlay
        this.panelOverlay.addEventListener('click', (e) => {
            e.preventDefault();
            this.closePanel();
        });

        // Prevenir que los clics dentro del panel lo cierren
        this.widgetPanel.addEventListener('click', (e) => {
            e.stopPropagation();
        });

        // Evento para enviar mensaje con el botón
        this.sendButton.addEventListener('click', () => {
            this.sendMessage();
        });

        // Evento para enviar mensaje con Enter (pero nueva línea con Shift+Enter)
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-ajustar altura del textarea
        this.messageInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    }
    
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
    
    closeFilterDropdown() {
        const dropdown = document.getElementById('filterDropdown');
        const filterButton = document.getElementById('filterButton');
        
        dropdown.classList.remove('active');
        filterButton.classList.remove('active');
    }
    
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
    
    updateSelectedFiltersDisplay() {
        const container = document.getElementById('selectedFilters');
        container.innerHTML = '';
        
        if (this.selectedDomains.length === 0) {
            container.style.display = 'none';
            return;
        }
        
        container.style.display = 'flex';
        
        this.selectedDomains.forEach(domainId => {
            const domain = this.availableDomains.find(d => d.id === domainId);
            if (domain) {
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
                
                container.appendChild(pill);
            }
        });
    }
    
    showWelcomeMessage() {
        setTimeout(() => {
            // Crear mensaje de bienvenida con diseño visual centrado
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
    
    sendMessage() {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();
        
        if (message) {
            this.sendUserMessage(message);
            input.value = '';
            // Ajustar altura tras limpiar
            input.style.height = '';
            // Hacemos scroll después de limpiar el input
            this.scrollToBottom();
        }
    }
    
    sendUserMessage(message) {
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        // Deshabilitar input y botón
        messageInput.disabled = true;
        sendButton.disabled = true;
        this.addMessage('user', message);
        // Hacemos scroll después de añadir el mensaje del usuario
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
                // Si hay citas, pásalas a addMessage
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
            // Habilitar input y botón también en error
            messageInput.disabled = false;
            sendButton.disabled = false;
            this.addMessage('bot', 'Error al conectar con el servidor: ' + error.message);
        });
    }

    addMessage(sender, text, sources = null) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;

        const time = new Date().toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit'
        });

        // Si hay varias fuentes, mostrar varios iconos
        let sourcesHTML = '';
        if (sender === 'bot' && sources && Array.isArray(sources) && sources.length > 0) {
            sources.forEach((source, idx) => {
                // Usar el título como texto del enlace, o la url si no hay título
                const linkText = source.title ? source.title : (source.url ? source.url : 'Documento original');
                // Si la url no es absoluta, intentar convertirla a absoluta respecto al dominio actual
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
                            <div class="source-tooltip-title">
                                Fuente consultada
                            </div>
                            <div class="source-tooltip-subtitle">
                                ${source.title || ''}
                            </div>
                            <a href="${url}" target="_blank" class="source-tooltip-link">
                                ${linkText} <i class="fas fa-external-link-alt"></i>
                            </a>
                        </div>
                    </div>
                `;
            });
        } else if (sender === 'bot' && sources && typeof sources === 'object' && sources.url) {
            // Compatibilidad con fuente única como objeto
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
                        <div class="source-tooltip-title">
                            Fuente consultada
                        </div>
                        <div class="source-tooltip-subtitle">
                            ${sources.title || ''}
                        </div>
                        <a href="${url}" target="_blank" class="source-tooltip-link">
                            ${linkText} <i class="fas fa-external-link-alt"></i>
                        </a>
                    </div>
                </div>
            `;
        }

        // Procesar Markdown solo para mensajes del bot (no para el usuario ni para HTML ya seguro)
        let processedText = text;
        if (sender === 'bot') {
            // Si el texto ya contiene HTML (por ejemplo, mensajes de bienvenida), no procesar
            if (!/^\s*<.+?>/.test(text.trim())) {
                processedText = marked.parse(text, { breaks: true, gfm: true });
            }
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

        // Agregar mensaje al historial de conversaciones
        this.conversations.push({
            sender: sender,
            text: text,
            timestamp: new Date(),
            sources: sources
        });

        messagesContainer.appendChild(messageDiv);
        
        // Animación de entrada y scroll suave
        messageDiv.style.opacity = '0';
        setTimeout(() => {
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0)';
        }, 50);
        messageDiv.style.transform = 'translateY(20px)';
        setTimeout(() => {
            this.scrollToBottom();
        }, 50);

        // --- NUEVO: eventos para mostrar/ocultar tooltip de fuente ---
        if (sender === 'bot' && sources && Array.isArray(sources) && sources.length > 0) {
            const indicators = messageDiv.querySelectorAll('.source-indicator');
            indicators.forEach(indicator => {
                const tooltip = indicator.querySelector('.source-tooltip');
                // Mostrar al hacer clic
                indicator.addEventListener('click', (e) => {
                    e.stopPropagation();
                    // Cerrar otros tooltips abiertos
                    document.querySelectorAll('.source-tooltip.active').forEach(t => {
                        if (t !== tooltip) t.classList.remove('active');
                    });
                    tooltip.classList.toggle('active');
                });
                // Ocultar al hacer clic fuera (documento)
                document.addEventListener('click', (e) => {
                    if (!indicator.contains(e.target)) {
                        tooltip.classList.remove('active');
                    }
                });
                // Opcional: ocultar al perder foco
                indicator.addEventListener('blur', () => {
                    tooltip.classList.remove('active');
                });
            });
            // --- NUEVO: cerrar tooltip al hacer clic en el panel de conversación ---
            const chatPanel = document.getElementById('widgetPanel');
            if (chatPanel) {
                chatPanel.addEventListener('click', (e) => {
                    // Si el clic NO es sobre un icono de fuente ni sobre la tarjeta
                    if (!e.target.closest('.source-indicator') && !e.target.closest('.source-tooltip')) {
                        document.querySelectorAll('.source-tooltip.active').forEach(t => t.classList.remove('active'));
                    }
                });
            }
        }
    }
    
    showTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        indicator.classList.add('active');
        setTimeout(() => this.scrollToBottom(), 100); // Esperamos un poco para asegurar que el indicador está visible
    }
    
    hideTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        indicator.classList.remove('active');
    }

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
    
    toggleWidget() {
        this.isOpen = !this.isOpen;
        if (this.isOpen) {
            this.resetConversation();
            this.widgetTrigger.classList.add('active');
            this.panelOverlay.style.display = 'block';
            // Forzar reflow para la animación
            this.panelOverlay.offsetHeight;
            this.panelOverlay.classList.add('active');
            this.widgetPanel.classList.add('active');
            
            setTimeout(() => {
                this.messageInput.focus();
            }, 300);
        } else {
            this.closePanel();
        }
    }
    
    openPanel() {
        if (!this.isOpen && this.widgetPanel && this.panelOverlay) {
            this.isOpen = true;
            
            // Asegurar que los filtros estén inicializados antes de resetear
            this.initializeFilters();
            
            this.resetConversation(); // Reinicia el contenido del chat cada vez que se abre
            
            // Actualizar el botón flotante
            this.widgetTrigger.classList.add('active');
            this.widgetTrigger.querySelector('.widget-text').textContent = 'Cerrar chat';
            this.widgetTrigger.setAttribute('aria-label', 'Cerrar chat de MeriBot');
            
            this.widgetPanel.classList.add('active');
            this.panelOverlay.style.display = 'block';
            
            setTimeout(() => {
                this.panelOverlay.classList.add('active');
                // Forzar un scroll al fondo después de abrir
                setTimeout(() => this.scrollToBottom(), 400);
                this.showWelcomeMessage(); // Mostrar mensaje de bienvenida al abrir
            }, 10);
        }
    }

    closePanel() {
        // Restaurar el botón flotante
        if (this.widgetTrigger) {
            this.widgetTrigger.classList.remove('active');
            if (this.widgetTrigger.querySelector('.widget-text')) {
                this.widgetTrigger.querySelector('.widget-text').textContent = 'Pregunta a Meribot';
            }
            this.widgetTrigger.setAttribute('aria-label', 'Abrir chat de MeriBot');
        }
        if (this.widgetPanel) this.widgetPanel.classList.remove('active');
        if (this.panelOverlay) this.panelOverlay.classList.remove('active');
        // Limpiar el textarea y reajustar su altura
        if (this.messageInput) {
            this.messageInput.value = '';
            this.messageInput.style.height = '';
        }
        // Limpiar dominios seleccionados y actualizar UI de filtros
        this.selectedDomains = [];
        this.updateFilterUI && this.updateFilterUI();
        this.updateSelectedFiltersDisplay && this.updateSelectedFiltersDisplay();
        // Cerrar el dropdown de filtros si está abierto y reinicializar
        const filterDropdown = document.getElementById('filterDropdown');
        const filterButton = document.getElementById('filterButton');
        if (filterDropdown && filterDropdown.classList.contains('active')) {
            filterDropdown.classList.remove('active');
        }
        if (filterButton && filterButton.classList.contains('active')) {
            filterButton.classList.remove('active');
        }
        this.initializeFilters && this.initializeFilters();
        setTimeout(() => {
            if (this.panelOverlay) this.panelOverlay.style.display = 'none';
        }, 300);
        this.isOpen = false;
    }

    // Actualizar las opciones de filtro
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

    init() {
        // Inicializar referencias DOM
        this.initializeDOMReferences();
        
        // Solo continuar si las referencias DOM son válidas
        if (!(this.widgetTrigger && this.widgetPanel && this.panelOverlay)) {
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
