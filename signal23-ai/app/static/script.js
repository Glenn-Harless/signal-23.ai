document.addEventListener('DOMContentLoaded', () => {
    const chatContainer = document.getElementById('chat-container');
    const userInput = document.getElementById('user-input');
    
    // Simulate random but lore-appropriate coordinates
    const locations = [
        { lat: 47.212, lon: -123.444, name: "SIGNAL ORIGIN POINT ALPHA" },
        { lat: 47.321, lon: -123.553, name: "QUANTUM RESONANCE NODE" },
        { lat: 47.111, lon: -123.322, name: "TEMPORAL ANOMALY SITE" }
    ];
    
    setInterval(() => {
        const location = locations[Math.floor(Math.random() * locations.length)];
        const coordinates = document.querySelector('.coordinates');
        coordinates.innerHTML = `<span class="location-name">${location.name}</span><br/>${location.lat}°N ${location.lon}°W`;
    }, 5000);

    // Simulate signal strength variations with lore-specific frequencies
    const baseFreq = 23.976;
    setInterval(() => {
        const signal = document.querySelector('.signal-strength');
        const freq = (baseFreq + Math.random() * 0.1).toFixed(3);
        const strength = Math.floor(Math.random() * 20 + 80);
        signal.innerHTML = `SIGNAL: ${freq} kHz<br/>STRENGTH: ${strength}%`;
        
        // Add visual noise effect based on signal strength
        chatContainer.style.setProperty('--noise-intensity', `${(100 - strength) / 100}`);
    }, 3000);

    // Add glitch effect to messages occasionally
    function addGlitchEffect(element) {
        const glitchChars = '█▓░▒▀▄▌╔╗║═╝';
        setInterval(() => {
            if (Math.random() < 0.1) {
                const text = element.textContent;
                const glitched = text.split('').map(char => 
                    Math.random() < 0.1 ? glitchChars[Math.floor(Math.random() * glitchChars.length)] : char
                ).join('');
                element.textContent = glitched;
                setTimeout(() => element.textContent = text, 100);
            }
        }, 2000);
    }

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
        
        if (role === 'assistant') {
            addGlitchEffect(messageDiv);
        }
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