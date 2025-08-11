// MeriBot Widget - Embeddable Chat Interface
// Ensure MeriBot is in the global scope
window.MeriBot = window.MeriBot || {};

(function() {
    // Configuration with defaults
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

    // Create script element for the main widget code
    const widgetScript = document.createElement('script');
    widgetScript.src = window.location.origin + '/static/js/chat.js';
    
    // Set data attributes for configuration
    function setAttributes(element, attributes) {
        Object.keys(attributes).forEach(key => {
            if (attributes[key] !== undefined) {
                element.setAttribute(`data-${key.replace(/([a-z0-9]|(?=[A-Z]))([A-Z])/g, '$1-$2').toLowerCase()}`, 
                                  attributes[key]);
            }
        });
    }
    
    // Initialize the widget with the given configuration
    window.initMeriBot = function(config = {}) {
        // Merge config with defaults
        const finalConfig = { ...defaultConfig, ...config };
        
        // Set data attributes on the script tag
        setAttributes(widgetScript, finalConfig);
        
        // Add the script to the page if not already added
        if (!document.querySelector('script[src*="chat.js"]')) {
            document.body.appendChild(widgetScript);
            
            // Set up a promise that resolves when the widget is ready
            return new Promise((resolve) => {
                const checkReady = () => {
                    if (window.MeriBot && window.MeriBot.isInitialized) {
                        resolve(window.MeriBot);
                    } else {
                        setTimeout(checkReady, 100);
                    }
                };
                checkReady();
            });
        } else if (window.MeriBot) {
            // If widget is already loaded, update its configuration
            return Promise.resolve(window.MeriBot);
        }
        
        return Promise.resolve(window.MeriBot || MeriBotAPI);
    };
    
    // Initialize MeriBot API methods
    const MeriBotAPI = {
        show: function() {
            console.log('MeriBot: show() called');
            // Find the widget and toggle button in the DOM
            const widget = document.getElementById('meribot-widget');
            const toggleButton = document.getElementById('meribot-toggle');
            
            if (widget && toggleButton) {
                // Toggle the widget visibility
                const isVisible = widget.style.visibility === 'visible';
                widget.style.height = isVisible ? '0' : '500px';
                widget.style.opacity = isVisible ? '0' : '1';
                widget.style.visibility = isVisible ? 'hidden' : 'visible';
                
                // Update button text
                toggleButton.innerHTML = `
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                    <span style="margin-left: 8px;">${isVisible ? 'Chat with MeriBot' : 'Close Chat'}</span>
                `;
            }
            return this; // For method chaining
        },
        hide: function() {
            console.log('MeriBot: hide() called');
            widget.style.height = '0';
            widget.style.opacity = '0';
            widget.style.visibility = 'hidden';
            return this;
        },
        sendMessage: function(message) {
            console.log('MeriBot: sendMessage() called with:', message);
            if (typeof message === 'string') {
                userInput.value = message;
                sendMessage();
            }
            return this;
        },
        // Add initialization check
        isInitialized: function() {
            return true;
        }
    };

    // Make API globally available
    window.MeriBot = MeriBotAPI;
    
    // Log initialization
    console.log('MeriBot: Widget initialized successfully');
    console.log('MeriBot API methods:', Object.keys(MeriBotAPI).join(', '));

    // Auto-initialize if data-autoload is present on the script tag
    const currentScript = document.currentScript || 
        document.querySelector('script[src*="meribot-loader"]');
    
    if (currentScript && currentScript.hasAttribute('data-autoload')) {
        const config = {};
        
        // Get all data attributes
        for (const { name, value } of currentScript.attributes) {
            if (name.startsWith('data-')) {
                const propName = name.replace('data-', '').replace(/-([a-z])/g, 
                    (match, letter) => letter.toUpperCase());
                
                // Convert string 'true'/'false' to boolean
                if (value === 'true' || value === 'false') {
                    config[propName] = value === 'true';
                } else if (!isNaN(value) && value !== '') {
                    // Convert to number if it's a number
                    config[propName] = parseFloat(value);
                } else {
                    config[propName] = value;
                }
            }
        }
        
        // Initialize with config
        window.initMeriBot(config);
    }
})();
