// feedback.js

let currentClientId = null;

/**
 * Initialise un WebSocket et retourne une Promise contenant le clientId.
 * @param {string} websocketUrl - L'URL du WebSocket.
 * @returns {Promise<string>} - Une Promise qui se résout avec le clientId.
 */
export function initializeWebSocket(websocketUrl) {
    return new Promise((resolve, reject) => {
        const socket = new WebSocket(websocketUrl);

        socket.onopen = () => {
            console.log('WebSocket ouvert.');
        };

        socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === 'client_id') {
                    currentClientId = data.client_id; // Stocke le clientId
                    console.log(`Client ID reçu : ${currentClientId}`);
                    resolve(currentClientId); // Résout la Promise avec le clientId
                } else if (data.type === 'status') {
                    updateProcessingFeedback(data.message, data.subtitle); // Gère d'autres messages
                } else if (data.type === 'progress') {
                    updateProgressBar(data.percentage); // Gère d'autres messages
                } else if (data.type === 'file_uploaded') {
                    hideUploadOverlay();
                } else if (data.type === 'close') {
                    socket.close();
                } else {
                    console.warn('Type de message inconnu :', data);
                }
            } catch (error) {
                console.error('Erreur en analysant le message WebSocket :', error);
                reject(error);
            }
        };

        socket.onerror = (error) => {
            console.error('Erreur WebSocket :', error);
            reject(error);
        };

        socket.onclose = () => {
            console.log('Connexion WebSocket fermée.');
        };
    });
}

/**
 * Update the processing feedback dynamically.
 * @param {string} message - The message to display in the feedback element.
 * @param {string} subtitle - The subtitle to display in the feedback element.
 */
export function updateProcessingFeedback(message, subtitle) {
    const feedbackElement = document.getElementById('processing-feedback');
    if (!feedbackElement) {
        console.error('Processing feedback element not found');
        return;
    }
    // Update the feedback text
    const statusElement = document.getElementById('processing-status-text');
    const subtitleElement = document.getElementById('processing-status-subtext');
    if (statusElement) statusElement.textContent = message;
    if (subtitleElement) subtitleElement.textContent = subtitle || '';
    // Ensure the feedback element is visible
    feedbackElement.classList.remove('hidden');
}

 /**
 * MàJ de la barre de progression
 * @param {string} percent - Pourcentage d'avancement.
 */
export function updateProgressBar(percent) {
    const progressBar = document.getElementById('progress-bar');
    progressBar.style.width = `${percent}%`; // Met à jour la largeur
    progressBar.textContent = `${percent}%`;
  }


  function hideUploadOverlay() {
    const uploadOverlay = document.querySelector('.upload-overlay');
    if (uploadOverlay) {
        uploadOverlay.classList.add('hidden');
    }
}

/**
 * Hide the processing feedback element.
 */
export function hideProcessingFeedback() {
    const feedbackElement = document.getElementById('processing-feedback');

    if (!feedbackElement) {
        console.error('Processing feedback element not found');
        return;
    }

    feedbackElement.classList.add('hidden');
}

/**
 * Show a user notification with a specific type, title, and message.
 * @param {string} type - Type of the notification ('success', 'error').
 * @param {string} title - Title of the notification.
 * @param {string} message - Detailed message for the notification.
 */
export function showNotification(type, title, message) {
    const notification = document.createElement('div');
    notification.className = `fixed bottom-4 right-4 p-4 rounded-lg shadow-lg ${
        type === 'success' ? 'bg-green-50 text-green-900' : 'bg-red-50 text-red-900'
    }`;
    notification.innerHTML = `
        <div class="flex items-center">
            <div class="flex-shrink-0">
                ${
                    type === 'success'
                        ? '<svg class="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>'
                        : '<svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path></svg>'
                }
            </div>
            <div class="ml-3">
                <h3 class="text-sm font-medium">${title}</h3>
                <div class="mt-1 text-sm">${message}</div>
            </div>
        </div>
    `;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 5000);
}


