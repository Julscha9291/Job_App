document.addEventListener('DOMContentLoaded', function() {
    // Event-Listener für das Suchformular
    document.getElementById('search-form').addEventListener('submit', function(event) {
        event.preventDefault();
        document.getElementById('loader').style.display = 'block';

        const formData = new FormData(this);
        fetch('/search', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('loader').style.display = 'none';

            if (data.total_jobs > 0) {
                // Entferne die hidden-summary Klasse, wenn es Ergebnisse gibt
                document.getElementById('summary').classList.remove('hidden-summary');
                document.getElementById('results').classList.remove('hidden');
            }    

            // Aktualisiere die Summary-Daten
            const summaryContainer = document.getElementById('summary');
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

            // Ergebnisse-Container leeren und neue Ergebnisse einfügen
            const resultsContainer = document.getElementById('results');
            resultsContainer.innerHTML = '';

            if (!data.jobs || data.jobs.length === 0) {
                resultsContainer.innerHTML = '<p>No results found.</p>';
            } else {
                let html = '';
                for (const job of data.jobs) {
                    html += `
                        <div class="job-item">
                            <h3>${job.title}</h3>
                            <div class="company">${job.company}</div>
                            <div class="location">${job.location}</div>
                            <div class="date-posted">Posted on ${job.date}</div>
                            <a href="${job.link}" class="apply-link" data-url="${job.link}">Apply here</a>
                        </div>
                    `;
                }
                resultsContainer.innerHTML = html;
            }
        })
        .catch(error => {
            document.getElementById('loader').style.display = 'none';
            console.error('Error:', error);
        });
    });

    // Event-Listener für das Öffnen des Links in einem neuen Tab
    document.getElementById('results').addEventListener('click', function(event) {
        if (event.target.classList.contains('apply-link')) {
            event.preventDefault();
            const url = event.target.getAttribute('data-url');
            window.open(url, '_blank'); // Öffne den Link in einem neuen Tab
        }
    });

    // Initialisiere den Radius-Schieberegler
    const radiusInput = document.getElementById('radius');
    const radiusValue = document.getElementById('radius-value');

    function updateRadiusValue() {
        radiusValue.textContent = `${radiusInput.value} km`;
    }

    updateRadiusValue();
    radiusInput.addEventListener('input', updateRadiusValue);

    // Event-Listener für den "Mehr Filter"-Button und Sidebar
    const toggleFiltersButton = document.getElementById('toggle-filters');
    const sidebar = document.querySelector('.sidebar');

    toggleFiltersButton.addEventListener('click', function(event) {
        event.preventDefault(); // Verhindere Standardverhalten des Buttons
        sidebar.classList.toggle('hidden-sidebar');
    });

    // Schließen der Sidebar beim Abschicken des Suchformulars
    const searchForm = document.getElementById('search-form');
    searchForm.addEventListener('submit', function() {
        sidebar.classList.add('hidden-sidebar');
    });
});
