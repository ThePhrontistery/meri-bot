// MeriBot Widget - Embeddable Chat Interface
(function() {
    // Default configuration
    const defaultConfig = {
        apiUrl: 'http://localhost:8000/chatbot/query',
        position: 'bottom-right', // 'bottom-right', 'bottom-left', 'top-right', 'top-left'
        buttonText: 'Chat with MeriBot',
        buttonColor: '#2c3e50',
        title: 'MeriBot Assistant',
        subtitle: 'How can I help you today?',
        autoOpen: false,
        debug: false
    };
    
    // Get configuration from data attributes
    function getConfig() {
        const scriptElement = document.currentScript || 
            document.querySelector('script[src*="meribot-widget"]');
        if (!scriptElement) return defaultConfig;
        
        return {
            apiUrl: scriptElement.getAttribute('data-api-url') || defaultConfig.apiUrl,
            position: scriptElement.getAttribute('data-position') || defaultConfig.position,
            buttonText: scriptElement.getAttribute('data-button-text') || defaultConfig.buttonText,
            buttonColor: scriptElement.getAttribute('data-button-color') || defaultConfig.buttonColor,
            title: scriptElement.getAttribute('data-title') || defaultConfig.title,
            subtitle: scriptElement.getAttribute('data-subtitle') || defaultConfig.subtitle,
            autoOpen: scriptElement.hasAttribute('data-auto-open') ? 
                scriptElement.getAttribute('data-auto-open') === 'true' : defaultConfig.autoOpen,
            debug: scriptElement.hasAttribute('data-debug') ? 
                scriptElement.getAttribute('data-debug') === 'true' : defaultConfig.debug
        };
    }
    
    const config = getConfig();
    
    // Debug logging
    function debugLog(...args) {
        if (config.debug) {
            console.log('[MeriBot]', ...args);
        }
    }
    // Create widget container
    console.log('Creating widget container...');
    const widget = document.createElement('div');
    widget.id = 'meribot-widget';
    console.log('Widget container created with ID:', widget.id);
    widget.style.cssText = `
        position: fixed;
        ${config.position.includes('bottom') ? 'bottom: 20px;' : 'top: 20px;'}
        ${config.position.includes('right') ? 'right: 20px;' : 'left: 20px;'}
        width: 350px;
        height: 0;
        background: white;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        display: flex;
        flex-direction: column;
        z-index: 9999;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        overflow: hidden;
        transition: all 0.3s ease;
        opacity: 0;
        visibility: hidden;
    `;
    
    // Create toggle button
    const toggleButton = document.createElement('button');
    toggleButton.id = 'meribot-toggle';
    toggleButton.style.cssText = `
        position: fixed;
        ${config.position.includes('bottom') ? 'bottom: 20px;' : 'top: 20px;'}
        ${config.position.includes('right') ? 'right: 20px;' : 'left: 20px;'}
        background: ${config.buttonColor};
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 20px;
        cursor: pointer;
        z-index: 10000;
        display: flex;
        align-items: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    `;
    
    toggleButton.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
        <span style="margin-left: 8px;">${config.buttonText}</span>
    `;
    
    // Toggle widget visibility
    function toggleWidget() {
        const isVisible = widget.style.height !== '0px';
        if (isVisible) {
            widget.style.height = '0';
            widget.style.opacity = '0';
            widget.style.visibility = 'hidden';
        } else {
            widget.style.height = '500px';
            widget.style.opacity = '1';
            widget.style.visibility = 'visible';
            // Focus on input when opening
            const input = widget.querySelector('#user-input');
            if (input) input.focus();
        }
    }
    
    // Create chat header
    const chatHeader = document.createElement('div');
    chatHeader.className = 'chat-header';
    chatHeader.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 15px; border-bottom: 1px solid #eee;">
            <div>
                <h3 style="margin: 0; font-size: 16px; font-weight: 600;">${config.title}</h3>
                <p style="margin: 4px 0 0; font-size: 12px; color: #666;">${config.subtitle}</p>
            </div>
            <button id="meribot-close" style="background: none; border: none; cursor: pointer; font-size: 18px; color: #666;">×</button>
        </div>
    `;
    
    // Create chat messages container
    const chatMessages = document.createElement('div');
    chatMessages.id = 'chat-messages';
    chatMessages.style.cssText = `
        flex: 1;
        overflow-y: auto;
        padding: 15px;
        background: #f9f9f9;
    `;
    
    // Create input container
    const inputContainer = document.createElement('div');
    inputContainer.className = 'chat-input';
    inputContainer.style.cssText = `
        padding: 15px;
        border-top: 1px solid #eee;
        background: white;
        display: flex;
    `;
    
    // Create input field
    const userInput = document.createElement('input');
    userInput.id = 'user-input';
    userInput.type = 'text';
    userInput.placeholder = 'Type your message...';
    userInput.style.cssText = `
        flex: 1;
        padding: 10px 15px;
        border: 1px solid #ddd;
        border-radius: 20px;
        outline: none;
        font-size: 14px;
    `;
    
    // Create send button
    const sendButton = document.createElement('button');
    sendButton.id = 'send-button';
    sendButton.innerHTML = 'Send';
    sendButton.style.cssText = `
        margin-left: 10px;
        padding: 0 20px;
        background: ${config.buttonColor};
        color: white;
        border: none;
        border-radius: 20px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
    `;
    
    // Assemble the widget
    inputContainer.appendChild(userInput);
    inputContainer.appendChild(sendButton);
    
    widget.appendChild(chatHeader);
    widget.appendChild(chatMessages);
    widget.appendChild(inputContainer);
    
    // Add elements to the page
    document.body.appendChild(widget);
    document.body.appendChild(toggleButton);
    
    // Generate a unique conversation ID
    const conversationId = 'conv-' + Math.random().toString(36).substr(2, 9);
    
    // Event listeners
    toggleButton.addEventListener('click', toggleWidget);
    
    const closeButton = widget.querySelector('#meribot-close');
    if (closeButton) {
        closeButton.addEventListener('click', () => {
            widget.style.height = '0';
            widget.style.opacity = '0';
            widget.style.visibility = 'hidden';
        });
    }
    
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Auto-open if configured
    if (config.autoOpen) {
        toggleWidget();
    }
    
    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;
        
        // Show user message
        appendMessage('user', message);
        userInput.value = '';
        userInput.disabled = true;
        sendButton.disabled = true;
        
        // Show typing indicator
        showTypingIndicator();
        
        try {
            debugLog('Sending message to:', config.apiUrl);
            const response = await fetch(config.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: message,
                    conversation_id: conversationId
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            debugLog('Received response:', data);
            
            // Update conversation ID if provided
            if (data.conversation_id) {
                conversationId = data.conversation_id;
            }
            
            // Hide typing indicator and show response
            removeTypingIndicator();
            appendMessage('bot', data.response || 'I apologize, but I encountered an issue processing your request.');
            
        } catch (error) {
            console.error('Error sending message:', error);
            removeTypingIndicator();
            appendMessage('bot', 'I\'m sorry, I encountered an error while processing your request. Please try again later.');
        } finally {
            userInput.disabled = false;
            sendButton.disabled = false;
            userInput.focus();
        }
    }
    
    function appendMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.style.cssText = `
            max-width: 80%;
            margin-bottom: 10px;
            padding: 10px 15px;
            border-radius: 18px;
            line-height: 1.4;
            position: relative;
            word-wrap: break-word;
            ${sender === 'bot' ? 
                'background: #f0f4f8; align-self: flex-start; border-bottom-left-radius: 5px;' : 
                'background: #e3f2fd; align-self: flex-end; border-bottom-right-radius: 5px;'}
        `;
        
        // Convert newlines to <br> and escape HTML
        const formattedText = escapeHtml(text).replace(/\n/g, '<br>');
        messageDiv.innerHTML = formattedText;
        
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }
    
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.style.cssText = `
            display: flex;
            gap: 5px;
            padding: 10px 15px;
            background: #f0f4f8;
            border-radius: 18px;
            width: fit-content;
            margin-bottom: 10px;
        `;
        
        typingDiv.innerHTML = `
            <span style="
                height: 8px;
                width: 8px;
                background: #666;
                border-radius: 50%;
                display: inline-block;
                animation: bounce 1.5s infinite ease-in-out;
            "></span>
            <span style="
                height: 8px;
                width: 8px;
                background: #666;
                border-radius: 50%;
                display: inline-block;
                animation: bounce 1.5s infinite ease-in-out;
                animation-delay: 0.2s;
            "></span>
            <span style="
                height: 8px;
                width: 8px;
                background: #666;
                border-radius: 50%;
                display: inline-block;
                animation: bounce 1.5s infinite ease-in-out;
                animation-delay: 0.4s;
            "></span>
        `;
        
        // Add animation keyframes
        const style = document.createElement('style');
        style.textContent = `
            @keyframes bounce {
                0%, 60%, 100% { transform: translateY(0); }
                30% { transform: translateY(-5px); }
            }
        `;
        document.head.appendChild(style);
        
        chatMessages.appendChild(typingDiv);
        scrollToBottom();
    }
    
    function removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    function scrollToBottom() {
        chatMessages.scrollTo({
            top: chatMessages.scrollHeight,
            behavior: 'smooth'
        });
    }
    
    function escapeHtml(unsafe) {
        if (!unsafe) return '';
        const div = document.createElement('div');
        div.textContent = unsafe;
        return div.innerHTML;
    }
    
    // Add welcome message
    window.addEventListener('load', () => {
        setTimeout(() => {
            appendMessage('bot', config.subtitle || 'Hello! How can I help you today?');
        }, 500);
    });
    
    // Make widget available globally for debugging
    window.MeriBot = {
        show: toggleWidget,
        hide: () => {
            widget.style.height = '0';
            widget.style.opacity = '0';
            widget.style.visibility = 'hidden';
        },
        sendMessage: (message) => {
            if (typeof message === 'string') {
                userInput.value = message;
                sendMessage();
            }
        }
    };
})();
