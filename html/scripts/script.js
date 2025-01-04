// Import statements
import {
    showNotification,
    initializeWebSocket,
    hideProcessingFeedback,
    showProcessingFeedback,
    updateProcessingFeedback
} from './feedback.js';

document.addEventListener('DOMContentLoaded', async () => {
    // Existing element declarations
    const fileUploadArea = document.getElementById('file-upload-area');
    const fileInput = document.getElementById('file-input');
    const generateSummaryButton = document.getElementById('generate-summary');
    const transcriptionOutput = document.getElementById('transcription-output');
    const summaryOutput = document.getElementById('summary-output');
    const downloadTranscription = document.getElementById('download-transcription');
    const downloadSummary = document.getElementById('download-summary');
    let uploadedFile = null;
    let PreviousFileName = null;


    // File upload area text update
    const updateFileUploadText = (fileName = null) => {
        const dropText = document.getElementById('drop-file');
        const formatsText = document.getElementById('supported-formats');

        if (fileName) {
            dropText.textContent = `Fichier sélectionné : ${fileName}`;
            formatsText.classList.add('hidden');
        } else {
            dropText.textContent = 'Glissez-déposez un fichier ici ou cliquez pour importer';
            formatsText.textContent = 'Formats pris en charge : MP3, WAV, M4A, TXT';
            formatsText.classList.remove('hidden');
        }
    };

    // Drag and drop handlers
    fileUploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        fileUploadArea.classList.add('dragover');
    });

    fileUploadArea.addEventListener('dragleave', () => {
        fileUploadArea.classList.remove('dragover');
    });

    fileUploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        fileUploadArea.classList.remove('dragover');
        uploadedFile = e.dataTransfer.files[0];
        updateFileUploadText(uploadedFile.name);
    });

    // Click to upload handlers
    fileUploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', () => {
        uploadedFile = fileInput.files[0];
        updateFileUploadText(uploadedFile.name);
    });

    // Generate summary handler
    generateSummaryButton.addEventListener('click', async () => {
        if (!uploadedFile && transcriptionOutput.textContent === '') {
            showNotification('error', 'Erreur', 'Veuillez importer un fichier avant de générer.');
            return;
        }

        const websocketUrl = 'ws://reecap.daniel-zaugg.ch/feedback';
        try{
             // 1. Initialiser le WebSocket et attendre le clientId
            const clientId = await initializeWebSocket(websocketUrl);
            console.log(`Client ID prêt : ${clientId}`);

            // 2. Préparer les données pour la requête POST
            const formData = new FormData();

            // Vérifie si le fichier téléchargé a changé
            if (uploadedFile && PreviousFileName === uploadedFile.name && transcriptionOutput.textContent !== '') {
                // Si le fichier n'a pas changé et qu'il y a une transcription, soumettre la transcription existante
                const transcriptionBlob = new Blob([transcriptionOutput.textContent], { type: 'text/plain' });
                formData.append('file', transcriptionBlob, 'transcription.txt'); // Fichier texte généré
                formData.append('client_id', clientId); // Inclure le clientId
                console.log('Utilisation de la transcription existante.');
            } else {
                // Mise à jour de la variable globale pour le nom du fichier
                PreviousFileName = uploadedFile ? uploadedFile.name : null;

                // Activation de l'overlay de téléchargement
                updateProcessingFeedback("Téléchargement en cours...", "")
                const uploadOverlay = document.querySelector('.upload-overlay');
                if (uploadOverlay) {
                    uploadOverlay.classList.remove('hidden');
                }


                // Traitement normal pour un nouvel audio
                if (!uploadedFile) {
                    showNotification('error', 'Erreur', 'Veuillez importer un fichier valide avant de générer.');
                    return;
                }

                formData.append('file', uploadedFile); // Fichier audio sélectionné
                formData.append('client_id', clientId); // Inclure le clientId

                // TODO: voir si la construction
                const context = `
                    Objectif: ${document.getElementById('objective').value || ''}
                    Date: ${document.getElementById('date').value || new Date().toLocaleDateString()}
                    Lieu: ${document.getElementById('location').value || ''}
                    Participants: ${document.getElementById('participants').value || ''}
                    ${document.getElementById('additional-info').value || ''}
                `.trim();
                formData.append('context', context);

                // Récupère le type de document à créer
                const documentType = document.querySelector('input[name="document-type"]:checked').value;
                formData.append('document_type', documentType);
            }

            // Envoyer la requête au backend
            const response = await fetch('/process', { method: 'POST', body: formData });
            const result = await response.json();

            // Récupère et affiche transcription
            if (result.transcription_file) {
                const transcriptionResponse = await fetch(`/get-file/transcriptions/${result.transcription_file}`);
                const transcriptionContent = await transcriptionResponse.text();
                transcriptionOutput.textContent = transcriptionContent;

                // Active le bouton de download pour la transcription
                downloadTranscription.classList.remove('hidden');
                downloadTranscription.addEventListener('click', () => {
                    const blob = new Blob([transcriptionContent], { type: 'text/plain' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = result.transcription_file;
                    a.click();
                    URL.revokeObjectURL(url);
                });
            }

            // Récupère le coût
            if (result.cost) {
                const costDisplay = document.getElementById('cost-display');
                const costValue = document.getElementById('cost-value');
                costDisplay.classList.remove('hidden');
                costValue.textContent = result.cost.toFixed(4);
            }

            // Initialisation de Markdown-it
            // TODO: Eliminer les doubles retours dans l'affichage
            const md = window.markdownit({
                breaks: false, // Désactive l'ajout de <br> pour les sauts de ligne uniques
                html: false     // Autorise le HTML dans le Markdown
            });

            // Récupère et affiche le résultat
            if (result.summary_file) {
                const summaryResponse = await fetch(`/get-file/summaries/${result.summary_file}`);
                const summaryContent = await summaryResponse.text();
                summaryOutput.innerHTML = md.render(summaryContent);
                //summaryOutput.textContent = summaryContent;

                // Active le bouton de download pour le résultat
                downloadSummary.classList.remove('hidden');
                downloadSummary.addEventListener('click', () => {
                    const blob = new Blob([summaryContent], { type: 'text/markdown' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = result.summary_file;
                    a.click();
                    URL.revokeObjectURL(url);
                });
            }

            hideProcessingFeedback();
            showNotification('success', 'Succès', 'Traitement terminé');
        } catch (error) {
            console.error('Erreur lors de la génération', error);
            hideProcessingFeedback();
            showNotification('error', 'Erreur', error.message);
        }
    });
});
