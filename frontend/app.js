document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const pdfInput = document.getElementById('pdf-input');
    const fileDetails = document.getElementById('file-details');
    const analyzeBtn = document.getElementById('analyze-btn');

    if (!dropZone || !pdfInput) {
        console.error("Critical Error: Upload elements missing from DOM.");
        return;
    }

    // Trigger file browser on click
    dropZone.addEventListener('click', () => pdfInput.click());

    // Drag and Drop Visual Effects
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#6366f1';
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.style.borderColor = '#1f293d';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#1f293d';
        if (e.dataTransfer.files.length > 0) {
            pdfInput.files = e.dataTransfer.files;
            updateFileLabel();
        }
    });

    pdfInput.addEventListener('change', updateFileLabel);

    function updateFileLabel() {
        if (pdfInput.files.length > 0) {
            fileDetails.innerText = `Selected: ${pdfInput.files[0].name}`;
            fileDetails.classList.remove('hidden');
        }
    }
});

// Standalone Tab Navigation
function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));

    const targetTab = document.getElementById(`tab-${tabId}`);
    if (targetTab) targetTab.classList.add('active');

    const activeLink = document.querySelector(`.nav-link[onclick="switchTab('${tabId}')"]`);
    if (activeLink) activeLink.classList.add('active');
}

// Asynchronous API Fetch Function
async function runAnalysis() {
    const pdfInput = document.getElementById('pdf-input');
    const jdText = document.getElementById('jd-input').value;
    const loadingState = document.getElementById('loading-state');
    const resultsSection = document.getElementById('results-section');

    if (!pdfInput || pdfInput.files.length === 0) {
        alert("Please select a PDF resume file first.");
        return;
    }
    if (!jdText.trim()) {
        alert("Please paste the target job description.");
        return;
    }

    const formData = new FormData();
    formData.append("file", pdfInput.files[0]);
    formData.append("job_description", jdText);

    loadingState.classList.remove('hidden');
    resultsSection.classList.add('hidden');

    try {
        const response = await fetch('/api/v1/analyze', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || `Server returned status ${response.status}`);
        }

        // Render Dashboard Metrics
        document.getElementById('score-val').innerText = `${data.match_score}%`;
        document.getElementById('missing-count').innerText = data.missing_keywords.length;
        document.getElementById('contact-val').innerText = (data.contact_info && data.contact_info.email) ? data.contact_info.email : "Not Found";

        // Render Keyword Chips
        const chipsContainer = document.getElementById('keyword-chips');
        chipsContainer.innerHTML = '';
        data.missing_keywords.forEach(kw => {
            const chip = document.createElement('span');
            chip.className = 'chip';
            chip.innerText = kw;
            chipsContainer.appendChild(chip);
        });

        // Render Generated Bullets
        const bulletList = document.getElementById('bullet-list');
        bulletList.innerHTML = '';
        data.suggested_bullets.forEach(b => {
            const li = document.createElement('li');
            li.innerText = b;
            bulletList.appendChild(li);
        });

        resultsSection.classList.remove('hidden');

    } catch (error) {
        console.error("Analysis Request Error:", error);
        alert(`Analysis Error: ${error.message}`);
    } finally {
        loadingState.classList.add('hidden');
    }
}