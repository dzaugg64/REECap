// theme.js

document.addEventListener("DOMContentLoaded", () => {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        // Load saved theme
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            toggleTheme();
        }
    }
    themeToggle.addEventListener('click', toggleTheme);
})

function toggleTheme() {
    const body = document.getElementById('theme');
    const cards = document.querySelectorAll('.card-container');
    const inputs = document.querySelectorAll('input, textarea');
    const outputAreas = document.querySelectorAll('#transcription-output, #summary-output, #cost-display, #processing-feedback');
    const isDarkMode = body.classList.contains('bg-gray-900');

    if (!isDarkMode) {
        // Switch to dark mode
        body.classList.remove('bg-gray-100', 'text-gray-900');
        body.classList.add('bg-gray-900', 'text-gray-100');
        cards.forEach(card => {
            card.classList.remove('bg-white');
            card.classList.add('bg-gray-800');
        });
        inputs.forEach(input => {
            input.classList.remove('bg-white', 'text-gray-900', 'border-gray-300');
            input.classList.add('bg-gray-700', 'text-gray-100', 'border-gray-600');
        });
        outputAreas.forEach(output => {
            output.classList.remove('bg-gray-100', 'text-gray-900');
            output.classList.add('bg-gray-700', 'text-gray-100');
        });
    } else {
        // Switch to light mode
        body.classList.remove('bg-gray-900', 'text-gray-100');
        body.classList.add('bg-gray-100', 'text-gray-900');
        cards.forEach(card => {
            card.classList.remove('bg-gray-800');
            card.classList.add('bg-white');
        });
        inputs.forEach(input => {
            input.classList.remove('bg-gray-700', 'text-gray-100', 'border-gray-600');
            input.classList.add('bg-white', 'text-gray-900', 'border-gray-300');
        });
        outputAreas.forEach(output => {
            output.classList.remove('bg-gray-700', 'text-gray-100');
            output.classList.add('bg-gray-100', 'text-gray-900');
        });
    }

    localStorage.setItem('theme', !isDarkMode ? 'dark' : 'light');
}


