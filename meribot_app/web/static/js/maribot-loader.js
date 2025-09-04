// MariBot Widget - Embeddable Chat Interface
// Ensure MariBot is in the global scope
window.MariBot = window.MariBot || {};

(function() {
    // Configuration with defaults
    const defaultConfig = {
        apiUrl: 'http://localhost:8000/chatbot/query',
        position: 'bottom-right',
        buttonText: 'Chat with MariBot',
        buttonColor: '#2c3e50',
        title: 'MariBot Assistant',
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
    window.initMariBot = function(config = {}) {
        // Merge config with defaults
        const finalConfig = { ...defaultConfig, ...config };
        
        // Set attributes on the script tag
        setAttributes(widgetScript, finalConfig);
        
        // Only add the script once
        if (!document.querySelector('script[src*="chat.js"]')) {
            document.body.appendChild(widgetScript);
            
            // Set up a promise that resolves when the widget is ready
            return new Promise((resolve) => {
                const checkReady = () => {
                    if (window.MariBot && window.MariBot.isInitialized) {
                        resolve(window.MariBot);
                    } else {
                        setTimeout(checkReady, 100);
                    }
                };
                checkReady();
            });
        } else if (window.MariBot) {
            // If widget is already loaded, update its configuration
            return Promise.resolve(window.MariBot);
        }
        
        return Promise.resolve(window.MariBot || MariBotAPI);
    };
    
    // Initialize MariBot API methods
    const MariBotAPI = {
        show: function() {
            console.log('MariBot: show() called');
            // Find the widget and toggle button in the DOM
            const widget = document.getElementById('maribot-widget');
            const toggleButton = document.getElementById('maribot-toggle');
            
            if (widget && toggleButton) {
                // Toggle the widget visibility
                const isVisible = widget.style.height !== '0px' && widget.style.visibility !== 'hidden';
                
                if (isVisible) {
                    widget.style.height = '0';
                    widget.style.opacity = '0';
                    widget.style.visibility = 'hidden';
                } else {
                    widget.style.height = '600px';
                    widget.style.opacity = '1';
                    widget.style.visibility = 'visible';
                }
                
                // Update button text
                toggleButton.innerHTML = `
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                    <span style="margin-left: 8px;">${isVisible ? 'Chat with MariBot' : 'Close Chat'}</span>
                `;
            }
            return this; // For method chaining
        },
        hide: function() {
            console.log('MariBot: hide() called');
            const widget = document.getElementById('maribot-widget');
            const toggleButton = document.getElementById('maribot-toggle');
            
            if (widget && toggleButton) {
                widget.style.height = '0';
                widget.style.opacity = '0';
                widget.style.visibility = 'hidden';
                
                // Update button text
                toggleButton.innerHTML = `
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                    <span style="margin-left: 8px;">Chat with MariBot</span>
                `;
            }
            return this;
        },
        sendMessage: function(message) {
            console.log('MariBot: sendMessage() called with:', message);
            const input = document.getElementById('maribot-input');
            if (input) {
                input.value = message;
                const event = new Event('input', { bubbles: true });
                input.dispatchEvent(event);
                
                const form = document.getElementById('maribot-form');
                if (form) {
                    form.dispatchEvent(new Event('submit', { cancelable: true }));
                }
            }
            return this;
        },
        // Add initialization check
        isInitialized: false
    };

    // Make API globally available
    window.MariBot = MariBotAPI;
    
    // Log initialization
    console.log('MariBot: Widget loader initialized');
    console.log('MariBot API methods:', Object.keys(MariBotAPI).join(', '));

    // Auto-initialize if data-autoload is present on the script tag
    const currentScript = document.currentScript || 
        document.querySelector('script[src*="maribot-loader"]');
    
    if (currentScript && currentScript.hasAttribute('data-autoload')) {
        const config = {};
        
        // Get config from data attributes
        for (const attr of currentScript.attributes) {
            if (attr.name.startsWith('data-')) {
                const propName = attr.name
                    .substring(5) // Remove 'data-'
                    .split('-')
                    .map((word, i) => 
                        i === 0 ? word : word[0].toUpperCase() + word.slice(1)
                    )
                    .join('');
                
                // Convert string 'true'/'false' to boolean
                config[propName] = attr.value === 'true' ? true : 
                                 attr.value === 'false' ? false : 
                                 !isNaN(attr.value) ? Number(attr.value) : 
                                 attr.value;
            }
        }
        
        // Initialize with config
        window.initMariBot(config);
    }
})();
