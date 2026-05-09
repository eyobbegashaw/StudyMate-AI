let isProcessing = false;

function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message || isProcessing) return;
    
    if (!window.pywebview || !window.pywebview.api) {
        alert('Application not ready. Please wait.');
        return;
    }
    
    addMessage('user', message);
    input.value = '';
    
    isProcessing = true;
    const sendBtn = document.getElementById('send-btn');
    sendBtn.disabled = true;
    sendBtn.textContent = 'Thinking...';
    
    addMessage('assistant', 'Thinking...', true);
    
    window.pywebview.api.ask_question(message).then(function(result) {
        const messagesContainer = document.getElementById('chat-messages');
        const thinkingMsg = messagesContainer.querySelector('.thinking');
        if (thinkingMsg) {
            thinkingMsg.remove();
        }
        
        if (result.status === 'success' || result.status === 'fallback') {
            addMessage('assistant', result.response);
        } else {
            addMessage('assistant', 'Error: ' + (result.message || 'Failed to get response'));
        }
    }).catch(function(error) {
        const messagesContainer = document.getElementById('chat-messages');
        const thinkingMsg = messagesContainer.querySelector('.thinking');
        if (thinkingMsg) {
            thinkingMsg.remove();
        }
        addMessage('assistant', 'Error: ' + error.message);
    }).finally(function() {
        isProcessing = false;
        sendBtn.disabled = false;
        sendBtn.textContent = 'Send';
    });
}

function addMessage(role, text, isThinking = false) {
    const container = document.getElementById('chat-messages');
    if (!container) return;
    
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}-message`;
    if (isThinking) {
        msgDiv.classList.add('thinking');
    }
    msgDiv.textContent = text;
    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
}

function loadChatHistory() {
    if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.get_chat_history().then(function(history) {
            if (history && history.length > 0) {
                history.forEach(function(msg) {
                    addMessage(msg.role, msg.content);
                });
            }
        }).catch(function(e) {
            console.error('Error loading chat history:', e);
        });
    }
}

// Initialize chat history loading
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(loadChatHistory, 500);
});
