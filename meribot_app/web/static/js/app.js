/**
 * MariBot Frontend Application
 * Maneja la interfaz de usuario y la comunicación con el backend
 */

class MariBotApp {
    constructor() {
        // Configuración
        this.config = {
            apiBaseUrl: 'http://localhost:8000/api',
            conversationId: this.generateConversationId(),
        };
        
        // Elementos del DOM
        this.elements = {
            chatMessages: document.querySelector('.chat-messages'),
            userInput: document.getElementById('user-input'),
            sendButton: document.getElementById('send-button'),
            chatContainer: document.querySelector('.chat-container'),
        };
        
        // Estado de la aplicación
        this.state = {
            conversationHistory: [],
            isTyping: false,
        };
        
        // Inicializar la aplicación
        this.init();
    }
    
    /**
     * Inicializa la aplicación
     */
    init() {
        // Mostrar el chat
        this.showChat();
        
        // Configurar manejadores de eventos
        this.setupEventListeners();
        this.updateUI();
        
        // Si ya está autenticado, cargar el historial de conversación
        if (this.state.isAuthenticated) {
            this.loadConversationHistory();
        }
    }
    
    /**
     * Configura los manejadores de eventos
     */
    setupEventListeners() {
        // Enviar mensaje al hacer clic en el botón
        this.elements.sendButton.addEventListener('click', () => this.sendMessage());
        
        // Enviar mensaje al presionar Enter
        this.elements.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
    }
    
    /**
     * Maneja el envío de un mensaje
     */
    async sendMessage() {
        const message = this.elements.userInput.value.trim();
        if (!message) return;
        
        // Agregar mensaje del usuario al chat
        this.addMessage('user', message);
        this.elements.userInput.value = '';
        
        // Mostrar indicador de escritura
        this.showTypingIndicator();
        
        try {
            // Enviar mensaje al backend
            const response = await this.sendToBackend(message);
            
            // Ocultar indicador de escritura
            this.hideTypingIndicator();
            
            // Agregar respuesta al chat
            this.addMessage('bot', response.response);
            
            // Actualizar historial de conversación
            this.state.conversationHistory.push({
                role: 'user',
                content: message
            }, {
                role: 'assistant',
                content: response.response
            });
            
        } catch (error) {
            console.error('Error al enviar mensaje:', error);
            this.hideTypingIndicator();
            this.addMessage('bot', 'Lo siento, ha ocurrido un error al procesar tu mensaje. Por favor, inténtalo de nuevo.');
        }
    }
    
    /**
     * Envía una solicitud al backend
     */
    async sendToBackend(data) {
        const url = `${this.config.apiBaseUrl}/chat/query`;
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: data,
                conversation_id: this.config.conversationId
            })
        });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || 'Error en la solicitud');
        }
        
        return response.json();
    }
    
    /**
     * Muestra un indicador de escritura
     */
    showTypingIndicator() {
        const typingElement = document.createElement('div');
        typingElement.className = 'message bot typing-indicator';
        typingElement.id = 'typing-indicator';
        typingElement.innerHTML = `
            <div class="typing">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        
        this.elements.chatMessages.appendChild(typingElement);
        this.scrollToBottom();
    }
    
    /**
     * Oculta el indicador de escritura
     */
    hideTypingIndicator() {
        const typingElement = document.getElementById('typing-indicator');
        if (typingElement) {
            typingElement.remove();
        }
    }
    
    /**
     * Añade un mensaje al chat
     */
    addMessage(sender, text) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}`;
        
        const contentElement = document.createElement('div');
        contentElement.className = 'message-content';
        contentElement.textContent = text;
        
        messageElement.appendChild(contentElement);
        this.elements.chatMessages.appendChild(messageElement);
        
        this.scrollToBottom();
    }
    
    /**
     * Desplaza el chat hacia abajo
     */
    scrollToBottom() {
        this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
    }
    
    /**
     * Muestra el chat
     */
    showChat() {
        this.elements.chatContainer.style.display = 'block';
        this.elements.userInput.focus();
    }
    
    /**
     * Carga el estado guardado
     */
    loadState() {
        // Cargar historial de conversación si existe
        const savedHistory = localStorage.getItem('conversation_history');
        if (savedHistory) {
            this.state.conversationHistory = JSON.parse(savedHistory);
        }
    }
    
    /**
     * Guarda el estado actual
     */
    saveState() {
        // En una implementación real, aquí se guardaría el estado en el almacenamiento local
        // o se sincronizaría con el backend
    }
    
    /**
     * Genera un ID único para la conversación
     * @returns {string} Un ID único
     */
    generateConversationId() {
        return 'conv_' + Math.random().toString(36).substr(2, 9);
    }
}

// Inicializar la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.app = new MariBotApp();
});
