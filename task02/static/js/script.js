document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');

    // --- Core function to add a message to the chat box ---
    function addMessage(message, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);
        const pElement = document.createElement('p');
        pElement.innerHTML = message; // Use innerHTML to render line breaks if any
        messageElement.appendChild(pElement);
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // --- Core function to handle sending a message to the backend ---
    async function sendMessage(userMessage) {
        // Display user's message
        addMessage(userMessage, 'user');
        
        try {
            // Send message to the Flask backend
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: userMessage }),
            });

            if (!response.ok) throw new Error('Network response was not ok');

            const data = await response.json();
            // Display bot's response
            addMessage(data.response, 'bot');

        } catch (error) {
            console.error('Error:', error);
            addMessage('Sorry, something went wrong. Please try again.', 'bot');
        }
    }
    
    // --- NEW: Function to fetch and display top FAQs ---
    async function displayTopFAQs() {
        try {
            const response = await fetch('/get_top_faqs');
            if (!response.ok) throw new Error('Failed to fetch top FAQs');
            
            const data = await response.json();
            const top_faqs = data.top_faqs;

            if (top_faqs && top_faqs.length > 0) {
                const suggestionsContainer = document.createElement('div');
                suggestionsContainer.classList.add('suggestions-container');
                
                top_faqs.forEach(faq => {
                    const button = document.createElement('button');
                    button.classList.add('suggestion-btn');
                    button.textContent = faq;
                    button.addEventListener('click', () => {
                        // When a suggestion is clicked, send it as a user message
                        sendMessage(faq);
                    });
                    suggestionsContainer.appendChild(button);
                });
                chatBox.appendChild(suggestionsContainer);
            }
        } catch(error) {
            console.error("Error displaying top FAQs:", error);
        }
    }

    // --- Handle form submission ---
    chatForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const userMessage = userInput.value.trim();
        if (userMessage === '') return;
        
        sendMessage(userMessage);
        userInput.value = ''; // Clear input field
    });
    
    // --- Initial Load ---
    // Fetch and display top FAQs when the page loads
    displayTopFAQs();
});