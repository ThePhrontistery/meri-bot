// Chat Widget Functionality
document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const chatBubble = document.getElementById('chat-bubble');
    const chatWidget = document.getElementById('chat-widget');
    const minimizeButton = document.getElementById('minimize-button');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const suggestedQuestions = document.querySelectorAll('.suggested-question');
    const sendButton = document.getElementById('send-button');

    // Add message to chat
    function addMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.innerHTML = `
            <div class="message-content">
                <p>${text}</p>
            </div>
        `;
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }

    // Show typing indicator
    function addTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot typing';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class="message-content">
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        chatMessages.appendChild(typingDiv);
        scrollToBottom();
    }

    // Remove typing indicator
    function removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    // Scroll to bottom of chat
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Toggle chat widget
    chatBubble.addEventListener('click', function(e) {
        e.stopPropagation();
        chatWidget.classList.add('expanded');
    });

    // Minimize chat
    minimizeButton.addEventListener('click', function(e) {
        e.stopPropagation();
        chatWidget.classList.remove('expanded');
    });

    // Handle form submission
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const message = userInput.value.trim();
        if (message) {
            addMessage('user', message);
            userInput.value = '';
            
            // Show typing indicator
            addTypingIndicator();
            
            // Simulate bot response
            setTimeout(function() {
                removeTypingIndicator();
                addMessage('bot', 'Gracias por tu mensaje. ¿En qué más puedo ayudarte?');
            }, 1500);
        }
    });

    // Handle suggested questions
    suggestedQuestions.forEach(button => {
        button.addEventListener('click', function() {
            const question = this.textContent;
            addMessage('user', question);
            
            // Show typing indicator
            addTypingIndicator();
            
            // Simulate bot response
            setTimeout(function() {
                removeTypingIndicator();
                addMessage('bot', 'Gracias por tu pregunta. ¿Hay algo más en lo que pueda ayudarte?');
            }, 1500);
        });
    });
});
