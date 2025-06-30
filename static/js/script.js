const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const resetButton = document.getElementById('reset-button');
const chatMessages = document.getElementById('chat-messages');
const instructionsButton = document.getElementById('instructions-button');
const instructionsModal = document.getElementById('instructions-modal');
const closeModal = document.getElementById('close-modal');

// Fetch and display full chat history on page load
async function displayChatHistory() {
    try {
        const response = await fetch('/history', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.json();

        if (response.ok) {
            chatMessages.innerHTML = ''; // Clear existing messages
            data.history.forEach(message => {
                const messageElement = document.createElement('div');
                messageElement.className = `message ${message.role === 'USER' ? 'user-message' : 'bot-message'}`;
                messageElement.textContent = message.message;
                chatMessages.appendChild(messageElement);
            });
            // Update placeholder if user has sent at least one message
            if (data.history.some(message => message.role === 'USER')) {
                userInput.placeholder = 'Type your message here';
            }
            chatMessages.scrollTop = chatMessages.scrollHeight;
        } else {
            const errorMessage = document.createElement('div');
            errorMessage.className = 'message bot-message';
            errorMessage.textContent = `Error: ${data.error || 'Failed to load chat history'}`;
            chatMessages.appendChild(errorMessage);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    } catch (error) {
        const errorMessage = document.createElement('div');
        errorMessage.className = 'message bot-message';
        errorMessage.textContent = 'Error: Unable to connect to server for chat history';
        chatMessages.appendChild(errorMessage);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// Call displayChatHistory when the page loads
document.addEventListener('DOMContentLoaded', displayChatHistory);

// Show instructions modal
instructionsButton.addEventListener('click', () => {
    instructionsModal.style.display = 'flex';
    instructionsModal.style.justifyContent = 'center';
    instructionsModal.style.alignItems = 'center';
});

// Close instructions modal
closeModal.addEventListener('click', () => {
    instructionsModal.style.display = 'none';
});

// Close modal when clicking outside of it
window.addEventListener('click', (event) => {
    if (event.target === instructionsModal) {
        instructionsModal.style.display = 'none';
    }
});

async function sendMessage() {
    const messageText = userInput.value.trim();
    if (!messageText) return;

    const userMessage = document.createElement('div');
    userMessage.className = 'message user-message';
    userMessage.textContent = messageText;
    chatMessages.appendChild(userMessage);
    userInput.value = '';
    // Update placeholder to 'Type your message here' after first user message
    userInput.placeholder = 'Type your message here';
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: messageText })
        });
        const data = await response.json();

        const botMessage = document.createElement('div');
        botMessage.className = 'message bot-message';
        botMessage.textContent = response.ok ? data.response : `Error: ${data.error || 'Something went wrong'}`;
        chatMessages.appendChild(botMessage);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    } catch (error) {
        const errorMessage = document.createElement('div');
        errorMessage.className = 'message bot-message';
        errorMessage.textContent = 'Error: Unable to connect to server';
        chatMessages.appendChild(errorMessage);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// Socrates image positioning
const socratesWrapper = document.querySelector('.socrates-wrapper');

function updateSocratesPosition() {
    const botMessages = chatMessages.getElementsByClassName('bot-message');
    if (botMessages.length > 0) {
        const lastBotMessage = botMessages[botMessages.length - 1];
        const rect = lastBotMessage.getBoundingClientRect();
        const containerRect = chatMessages.getBoundingClientRect();
        const offset = 20; // Adjust this value to control the jump
        socratesWrapper.style.top = `${rect.top - containerRect.top + lastBotMessage.offsetHeight / 2 - socratesWrapper.offsetHeight / 2 + offset}px`;
    }
}

// Use MutationObserver to detect new messages
const observer = new MutationObserver(() => {
    updateSocratesPosition();
});
observer.observe(chatMessages, { childList: true, subtree: true });

// Initial check and event listeners
updateSocratesPosition();
chatMessages.addEventListener('scroll', updateSocratesPosition);
window.addEventListener('resize', updateSocratesPosition);

// Reset chat
async function resetChat() {
    try {
        await fetch('/reset', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        chatMessages.innerHTML = '';
        userInput.placeholder = 'State your belief or idea. Socratobot will then use the ‘Socratic Dialogue’ method to encourage you to defend your stance with reason and logic.';
        await displayChatHistory();
    } catch (error) {
        console.error('Reset failed:', error);
    }
}

// Chat buttons
sendButton.addEventListener('click', sendMessage);
resetButton.addEventListener('click', resetChat);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});
