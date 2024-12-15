document.addEventListener('DOMContentLoaded', () => {
    const chatContainer = document.getElementById('chat-container');
    const userInput = document.getElementById('user-input');
    
    // Simulate random coordinates
    setInterval(() => {
        const coordinates = document.querySelector('.coordinates');
        const lat = (Math.random() * (48 - 46) + 46).toFixed(3);
        const lon = (Math.random() * (124 - 122) + 122).toFixed(3);
        coordinates.textContent = `${lat}°N ${lon}°W`;
    }, 5000);

    // Simulate signal strength variations
    setInterval(() => {
        const signal = document.querySelector('.signal-strength');
        const freq = (23.976 + Math.random() * 0.1).toFixed(3);
        signal.textContent = `SIGNAL: ${freq} kHz`;
    }, 3000);

    userInput.addEventListener('keypress', async (e) => {
        if (e.key === 'Enter' && userInput.value.trim()) {
            const message = userInput.value.trim();
            appendMessage('user', message);
            userInput.value = '';
            userInput.disabled = true;

            try {
                const response = await sendMessage(message);
                appendMessage('assistant', response.response);
                if (response.sources && response.sources.length > 0) {
                    appendMessage('assistant', '\nSources:\n' + response.sources.join('\n'));
                }
            } catch (error) {
                appendMessage('assistant', 'ERROR: TRANSMISSION FAILED - ' + error.message);
            }

            userInput.disabled = false;
            userInput.focus();
        }
    });

    function appendMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${role}-message`);
        messageDiv.textContent = content;
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    async function sendMessage(content) {
        const response = await fetch('http://localhost:8000/v1/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                messages: [
                    { role: 'user', content: content }
                ],
                temperature: 0.7
            })
        });

        if (!response.ok) {
            throw new Error('SIGNAL LOST');
        }

        return await response.json();
    }

    userInput.focus();
});