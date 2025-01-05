// theme.js

document.addEventListener("DOMContentLoaded", () => {
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.getElementById('theme');
    const outputAreas = document.querySelectorAll('#transcription-output, #summary-output, #cost-display, #processing-feedback');
    const savedTheme = localStorage.getItem('theme');

    // Fonction pour appliquer le thème
    const applyTheme = (isDark) => {
        body.classList.toggle('bg-gray-900', isDark);
        body.classList.toggle('text-gray-100', isDark);
        body.classList.toggle('bg-gray-100', !isDark);
        body.classList.toggle('text-gray-900', !isDark);

        outputAreas.forEach(area => {
            area.classList.toggle('bg-gray-900', isDark);
            area.classList.toggle('text-gray-100', isDark);
            area.classList.toggle('bg-gray-100', !isDark);
            area.classList.toggle('text-gray-900', !isDark);
        });

        const feedbackElement = document.getElementById('processing-feedback');
        if (feedbackElement) {
            feedbackElement.style.backgroundColor = isDark ? '#2d3748' : '#ebf8ff';
            feedbackElement.style.color = isDark ? '#a0aec0' : '#2c5282';
        }
    };

    // Initialisation du thème au chargement
    if (savedTheme === 'dark') {
        applyTheme(true);
    } else {
        applyTheme(false);
    }

    // Écouteur pour basculer le thème
    themeToggle.addEventListener('click', () => {
        const isDark = body.classList.contains('bg-gray-900');
        applyTheme(!isDark);
        localStorage.setItem('theme', !isDark ? 'dark' : 'light');
    });
});