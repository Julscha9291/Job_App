document.addEventListener('DOMContentLoaded', () => {
    const loader = document.getElementById('loader');
    const searchForm = document.getElementById('search-form');
    const resultsContainer = document.getElementById('results');
    const summaryContainer = document.getElementById('summary');
    const radiusInput = document.getElementById('radius');
    const radiusValue = document.getElementById('radius-value');
    const toggleFiltersButton = document.getElementById('toggle-filters');
    const sidebar = document.querySelector('.sidebar');

    // 🔄 Loader-Anzeige
    const toggleLoader = (show) => {
        loader.style.display = show ? 'block' : 'none';
    };

    // 🧾 Zusammenfassung anzeigen
    const renderSummary = (data) => {
        summaryContainer.classList.remove('hidden-summary');
        summaryContainer.innerHTML = `
            <div class="summary-item">
                <h2>Total Results:</h2>
                <p id="total-results">${data.total_jobs}</p>
            </div>
            <div class="summary-item">
                <h2>Posted Today:</h2>
                <p id="posted-today">${data.today_jobs}</p>
            </div>
            <div class="summary-item">
                <h2>Posted in Last 7 Days:</h2>
                <p id="posted-7-days">${data.last_7_days_jobs}</p>
            </div>
        `;
    };

    // 📄 Jobs rendern
    const renderResults = (jobs) => {
        resultsContainer.classList.remove('hidden');
        resultsContainer.innerHTML = jobs.length === 0
            ? '<p>No results found.</p>'
            : jobs.map(job => `
                <div class="job-item">
                    <h3>${job.title}</h3>
                    <div class="company">${job.company}</div>
                    <div class="location">${job.location}</div>
                    <div class="date-posted">Posted on ${job.date}</div>
                    <a href="${job.link}" class="apply-link" data-url="${job.link}">Apply here</a>
                </div>
            `).join('');
    };

    // 🔎 Radius aktualisieren
    const updateRadiusValue = () => {
        radiusValue.textContent = `${radiusInput.value} km`;
    };

    // 📤 Formular absenden
    const handleFormSubmit = async (event) => {
        event.preventDefault();
        toggleLoader(true);

        try {
            const formData = new FormData(searchForm);
            const response = await fetch('/search', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            toggleLoader(false);
            if (data.total_jobs > 0) {
                renderSummary(data);
                renderResults(data.jobs || []);
            } else {
                renderResults([]);
            }
        } catch (error) {
            toggleLoader(false);
            console.error('Error:', error);
        }

        sidebar.classList.add('hidden-sidebar');
    };

    // 🔗 Bewerbungslinks in neuem Tab öffnen
    const handleResultClick = (event) => {
        if (event.target.classList.contains('apply-link')) {
            event.preventDefault();
            const url = event.target.dataset.url;
            window.open(url, '_blank');
        }
    };

    // 🎛️ Sidebar anzeigen/ausblenden
    const toggleSidebar = (event) => {
        event.preventDefault();
        sidebar.classList.toggle('hidden-sidebar');
    };

    // 📌 Event Listeners
    searchForm.addEventListener('submit', handleFormSubmit);
    resultsContainer.addEventListener('click', handleResultClick);
    radiusInput.addEventListener('input', updateRadiusValue);
    toggleFiltersButton.addEventListener('click', toggleSidebar);

    // 🟢 Initialisierung
    updateRadiusValue();
});
