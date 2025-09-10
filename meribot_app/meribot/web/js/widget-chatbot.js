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
        
        this.responses = {
            // Respuestas por dominio
            "talent": {
                "carrera profesional": {
                    text: "En C&CA tenemos definidos grados profesionales claros, competencias esperadas por nivel, planes de evolución, mentoring programs y oportunidades de movilidad interna. Tu EM puede ayudarte con el plan de desarrollo personalizado.",
                    source: {
                        url: "https://intranet.capgemini.com/cca/carrera-profesional",
                        title: "Guía de Carrera Profesional CCA",
                        type: "document"
                    }
                },
                "contactos de rrhh": {
                    text: "Para temas de RRHH en C&CA:<br><br><strong>hr_cca@capgemini.com</strong> - Consultas generales<br><strong>rrhh.practicas@capgemini.com</strong> - Prácticas profesionales<br><strong>development.es@capgemini.com</strong> - Desarrollo profesional",
                    source: {
                        url: "https://intranet.capgemini.com/cca/directorio-contactos",
                        title: "Directorio de Contactos RRHH",
                        type: "page"
                    }
                },
                "beneficios": {
                    text: "Como parte de C&CA tienes acceso a: seguro médico premium, flexible benefits, programa de bienestar, formación continua, días adicionales de vacaciones, y programas de reconocimiento. También participas en eventos y actividades de team building."
                },
                "default": {
                    text: "En Talent puedo ayudarte con temas de desarrollo profesional, beneficios, contactos específicos, evaluaciones y procesos internos. ¿Qué necesitas saber?"
                }
            },
            "onboarding": {
                "primeros pasos": {
                    text: "¡Bienvenido a C&CA! Tus primeros pasos incluyen: completar el perfil corporativo, realizar las formaciones mandatory, conocer a tu EM y equipo, acceder a las herramientas necesarias, y revisar la documentación de bienvenida.",
                    source: {
                        url: "https://intranet.capgemini.com/cca/onboarding-checklist",
                        title: "Checklist de Onboarding CCA",
                        type: "document"
                    }
                },
                "formaciones mandatory": {
                    text: "Las formaciones obligatorias incluyen: Compliance & Ethics, Data Protection, Information Security, Health & Safety, y módulos específicos de C&CA. Tienes 30 días para completarlas desde tu incorporación.",
                    source: {
                        url: "https://learning.capgemini.com/mandatory-training",
                        title: "Portal de Formaciones Obligatorias",
                        type: "platform"
                    }
                },
                "herramientas acceso": {
                    text: "Herramientas principales: Outlook corporativo, Teams, SharePoint, portal empleado, VPN, GitHub Enterprise, Azure DevOps. Tu EM te facilitará los accesos necesarios según tu rol."
                },
                "default": {
                    text: "En Onboarding puedo ayudarte con el proceso de incorporación, primeros pasos, formaciones obligatorias y acceso a herramientas. ¿Qué necesitas saber?"
                }
            },
            "formacion": {
                "ac&cademy": {
                    text: "AC&CAdemy son los itinerarios formativos especializados de la SDO. Incluyen formación en Cloud Computing, desarrollo ágil, arquitectura de software, DevOps, y tecnologías emergentes. Cada itinerario está diseñado para diferentes niveles de experiencia.",
                    source: {
                        url: "https://academy.capgemini.com/cca/programs",
                        title: "Portal AC&CAdemy - Programas Formativos",
                        type: "platform"
                    }
                },
                "certificaciones": {
                    text: "Ofrecemos apoyo para certificaciones en AWS, Azure, Google Cloud, Microsoft, Oracle, y tecnologías específicas. También tenemos un programa de incentivos para certificaciones alineadas con los objetivos de la práctica.",
                    source: {
                        url: "https://intranet.capgemini.com/cca/certification-program",
                        title: "Programa de Certificaciones CCA",
                        type: "document"
                    }
                },
                "plataformas": {
                    text: "Tienes acceso a múltiples plataformas: Pluralsight para tecnología, LinkedIn Learning para soft skills, Microsoft Learn, AWS Training, Google Cloud Skills Boost, y recursos internos de la SDO."
                },
                "default": {
                    text: "En Formación puedo ayudarte con itinerarios formativos, certificaciones, plataformas de aprendizaje y planificación de carrera técnica. ¿Qué te interesa específicamente?"
                }
            },
            "general": {
                "cursos": {
                    text: "En C&CA tenemos una amplia oferta formativa que incluye itinerarios técnicos especializados, certificaciones oficiales en las principales tecnologías cloud, formaciones en metodologías ágiles, y programas de desarrollo de soft skills. Todos los cursos están alineados con las necesidades de nuestros proyectos y clientes.",
                    source: {
                        url: "https://intranet.capgemini.com/cca/catalogo-formativo",
                        title: "Catálogo Formativo C&CA 2025",
                        type: "document"
                    }
                },
                "¿qué es c&ca?": {
                    text: "Cloud & Custom Applications es la práctica de Capgemini especializada en soluciones cloud nativas, desarrollo a medida e integraciones. Trabajamos con las últimas tecnologías para ofrecer soluciones innovadoras a nuestros clientes."
                },
                "default": {
                    text: "Gracias por tu pregunta. Como asistente de C&CA, puedo ayudarte con información específica según el dominio que selecciones. Usa el filtro para obtener respuestas más precisas."
                }
            }
        };
        
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
            // De momento usamos los dominios predefinidos
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
            
            this.initializeWidget();
        } catch (error) {
            console.error('Error loading domains:', error);
            // Usar dominios por defecto en caso de error
            this.availableDomains = [];
            this.initializeWidget();
        }
    }
    
    initializeWidget() {
        // Validar que tenemos todos los elementos necesarios
        if (!this.widgetTrigger || !this.widgetPanel) {
            console.error('Error: Elementos del widget no encontrados');
            return;
        }

        // Inicializar eventos y funcionalidad
        this.initializeBasicEvents();
        this.initializeFilterEvents();
        
        // Agregar mensaje de bienvenida
        this.showWelcomeMessage();
        
        // Hacer visible el widget trigger después de la inicialización
        this.widgetTrigger.style.opacity = '1';
    }

    initializeBasicEvents() {
        if (!this.widgetTrigger || !this.widgetPanel || !this.panelCloseButton || !this.panelOverlay) {
            console.error('Error: No se pudieron encontrar elementos básicos del DOM');
            return;
        }

        // Evento para abrir el panel
        this.widgetTrigger.addEventListener('click', () => this.openPanel());

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
            const response = await fetch('./config/domains.json');
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
        if (!this.widgetTrigger || !this.widgetPanel || !this.panelCloseButton || !this.panelOverlay) {
            console.error('Error: No se pudieron encontrar elementos básicos del DOM');
            return;
        }

        // Evento para abrir el panel
        this.widgetTrigger.addEventListener('click', () => this.openPanel());

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
    }
    
    toggleFilterDropdown() {
        this.initializeFilters(); // Asegura que siempre esté actualizado al abrir
        const dropdown = document.getElementById('filterDropdown');
        const filterButton = document.getElementById('filterButton');
        dropdown.classList.toggle('active');
        filterButton.classList.toggle('active');
    }
    
    closeFilterDropdown() {
        const dropdown = document.getElementById('filterDropdown');
        const filterButton = document.getElementById('filterButton');
        
        dropdown.classList.remove('active');
        filterButton.classList.remove('active');
    }
    
    toggleDomainFilter(domainId) {
        const index = this.selectedDomains.indexOf(domainId);
        
        if (index > -1) {
            // Quitar filtro
            this.selectedDomains.splice(index, 1);
        } else {
            // Añadir filtro
            this.selectedDomains.push(domainId);
        }
        
        this.updateFilterUI();
        this.updateSelectedFiltersDisplay();
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
                        style="position: absolute; bottom: 8px; right: ${8 + idx * 28}px; z-index: 10;">
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
                    style="position: absolute; bottom: 8px; right: 8px; z-index: 10;">
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
            this.scrollToBottom();
        }, 50);
        messageDiv.style.transform = 'translateY(20px)';
        setTimeout(() => {
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0)';
            messageDiv.style.transition = 'all 0.3s ease';
        }, 50);
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
                this.showWelcomeMessage();
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
            this.widgetTrigger.classList.add('active'); // Añadir clase active al botón
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
        if (this.isOpen && this.widgetPanel && this.panelOverlay) {
            this.isOpen = false;
            this.widgetTrigger.classList.remove('active');
            this.widgetPanel.classList.remove('active');
            this.panelOverlay.classList.remove('active');
            setTimeout(() => {
                this.panelOverlay.style.display = 'none';
            }, 300);
        }
    }

    // Asegurarse de que initializeFilters esté correctamente definido dentro de la clase
    initializeFilters() {
        const dropdown = document.getElementById('filterDropdown');
        if (!dropdown) return;
        dropdown.innerHTML = '';
        this.availableDomains.forEach(domain => {
            const option = document.createElement('div');
            option.className = 'filter-option';
            option.setAttribute('data-domain-id', domain.id);
            // Marcar como seleccionado si está en selectedDomains
            if (this.selectedDomains.includes(domain.id)) {
                option.classList.add('selected');
            }
            option.innerHTML = `
                <div class="filter-option-content">
                    <div class="filter-option-name">${domain.name}</div>
                </div>
                <div class="filter-checkbox${this.selectedDomains.includes(domain.id) ? ' checked' : ''}">
                    <i class="fas fa-check" style="font-size: 10px;${this.selectedDomains.includes(domain.id) ? '' : 'display: none;'}"></i>
                </div>
            `;
            option.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleDomainFilter(domain.id);
                // Volver a renderizar para reflejar el cambio visual inmediato
                this.initializeFilters();
            });
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

        // Toggle del dropdown al hacer clic en el botón
        this.filterButton.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            // Toggle del estado del dropdown
            const isActive = filterDropdown.classList.contains('active');
            filterDropdown.classList.toggle('active');
            this.filterButton.classList.toggle('active');
            
            // Si estamos abriendo el dropdown, actualizamos las opciones
            if (!isActive) {
                this.initializeFilterOptions(filterDropdown);
            }
        });

        // Cerrar dropdown al hacer clic en cualquier parte fuera
        document.addEventListener('click', (e) => {
            const clickedElement = e.target;
            if (!this.filterButton.contains(clickedElement) && !filterDropdown.contains(clickedElement)) {
                filterDropdown.classList.remove('active');
                this.filterButton.classList.remove('active');
            }
        });

        // Inicializar las opciones del filtro
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

            // Evento de clic en la opción
            option.addEventListener('click', (e) => {
                e.stopPropagation();
                const checkbox = option.querySelector('.filter-checkbox');
                const domainId = checkbox.dataset.domain;
                const isCurrentlySelected = checkbox.classList.contains('checked');

                if (isCurrentlySelected) {
                    // Deseleccionar
                    checkbox.classList.remove('checked');
                    checkbox.textContent = '';
                    this.selectedDomains = this.selectedDomains.filter(id => id !== domainId);
                } else {
                    // Seleccionar
                    checkbox.classList.add('checked');
                    checkbox.textContent = '✓';
                    if (!this.selectedDomains.includes(domainId)) {
                        this.selectedDomains.push(domainId);
                    }
                }

                // Actualizar la visualización de los filtros seleccionados
                this.updateFilterSelection();
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
        if (this.widgetTrigger && this.widgetPanel && this.panelOverlay) {
            this.initialize();
            this.loadDomainsConfig();
        } else {
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
