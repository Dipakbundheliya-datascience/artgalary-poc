const API_URL = 'http://localhost:8000';
let conversationHistory = [];

// Initialize chat on page load
window.addEventListener('DOMContentLoaded', async () => {
    await initChat();

    // Enter key to send message
    document.getElementById('userInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});

async function initChat() {
    try {
        const response = await fetch(`${API_URL}/greeting`);
        const data = await response.json();

        addMessage('assistant', data.message);
    } catch (error) {
        console.error('Error initializing chat:', error);
        showError('Failed to connect to the server. Please make sure the backend is running.');
    }
}

function addMessage(role, content) {
    const chatContainer = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = formatMessage(content);

    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);

    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function formatMessage(content) {
    // Convert markdown-style bold
    content = content.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

    // Convert line breaks
    content = content.replace(/\n/g, '<br>');

    return content;
}

function addArtworkCards(artworks) {
    const chatContainer = document.getElementById('chatContainer');

    artworks.forEach((artwork, index) => {
        const card = document.createElement('div');
        card.className = 'artwork-card';

        const priceFormatted = new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0
        }).format(artwork.price);

        card.innerHTML = `
            <img src="${artwork.image_url}"
                 alt="${artwork.title}"
                 onclick="window.open('${artwork.image_url}', '_blank')"
                 onerror="this.src='https://via.placeholder.com/400x300?text=Image+Not+Available'">
            <div class="artwork-title">${artwork.title}</div>
            ${artwork.artist ? `<div style="font-size: 15px; color: #64748b; margin-bottom: 8px; font-style: italic;">by ${artwork.artist}</div>` : ''}
            <div class="artwork-price">${priceFormatted}</div>
            <div class="artwork-info">
                <div><strong>Medium:</strong> ${artwork.medium}</div>
                ${artwork.dimensions ? `<div><strong>Dimensions:</strong> ${artwork.dimensions}</div>` : ''}
                ${artwork.period ? `<div><strong>Period:</strong> ${artwork.period}</div>` : ''}
                <div style="margin-top: 12px;">
                    <strong>Style:</strong><br>
                    ${artwork.style.map(s => `<span class="badge style">${s}</span>`).join('')}
                </div>
                <div style="margin-top: 8px;">
                    <strong>Colors:</strong><br>
                    ${artwork.colors.map(c => `<span class="badge color">${c}</span>`).join('')}
                </div>
                <div style="margin-top: 8px;">
                    <strong>Mood:</strong><br>
                    ${artwork.mood.map(m => `<span class="badge mood">${m}</span>`).join('')}
                </div>
            </div>
        `;

        chatContainer.appendChild(card);
    });

    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function showTyping() {
    document.getElementById('typingIndicator').classList.add('active');
}

function hideTyping() {
    document.getElementById('typingIndicator').classList.remove('active');
}

function showError(message) {
    const chatContainer = document.getElementById('chatContainer');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    chatContainer.appendChild(errorDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function sendMessage() {
    const input = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const message = input.value.trim();

    if (!message) return;

    // Disable input
    input.disabled = true;
    sendBtn.disabled = true;

    // Add user message to UI
    addMessage('user', message);

    // Add to conversation history
    conversationHistory.push({
        role: 'user',
        content: message
    });

    // Clear input
    input.value = '';

    // Show typing indicator
    showTyping();

    try {
        // Send to backend
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                messages: conversationHistory
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Hide typing indicator
        hideTyping();

        // Add assistant message
        addMessage('assistant', data.message);

        // Add to conversation history
        conversationHistory.push({
            role: 'assistant',
            content: data.message
        });

        // If recommendations, show artwork cards
        if (data.type === 'recommendation' && data.artworks) {
            addArtworkCards(data.artworks);
        }

    } catch (error) {
        hideTyping();
        console.error('Error sending message:', error);
        showError('Sorry, something went wrong. Please try again.');
    } finally {
        // Re-enable input
        input.disabled = false;
        sendBtn.disabled = false;
        input.focus();
    }
}
