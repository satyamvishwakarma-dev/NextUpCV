// Tab Navigation Switcher
function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));

    const targetTab = document.getElementById(`tab-${tabId}`);
    if (targetTab) targetTab.classList.add('active');

    const activeLink = document.querySelector(`.nav-link[onclick="switchTab('${tabId}')"]`);
    if (activeLink) activeLink.classList.add('active');
}

// File Drag & Drop Handling
const dropZone = document.getElementById('drop-zone');
const pdfInput = document.getElementById('pdf-input');
const fileDetails = document.getElementById('file-details');

dropZone.addEventListener('click', () => pdfInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = '#6366f1';
});

dropZone.addEventListener('dragleave', () => {
    dropZone.style.borderColor = '#334155';
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = '#334155';
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

// Execute Analysis API Call
async function runAnalysis() {
    const jdText = document.getElementById('jd-input').value;

    if (pdfInput.files.length === 0) {
        alert("Please select a PDF resume file.");
        return;
    }
    if (!jdText.trim()) {
        alert("Please paste the target job description.");
        return;
    }

    const formData = new FormData();
    formData.append("file", pdfInput.files[0]);
    formData.append("job_description", jdText);

    // Toggle Loading Indicators
    document.getElementById('loading-state').classList.remove('hidden');
    document.getElementById('results-section').classList.add('hidden');

    try {
        const response = await fetch('/api/v1/analyze', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Error processing request.");
        }

        // Render Dashboard Results
        renderResults(data);

    } catch (error) {
        alert(`Analysis Failed: ${error.message}`);
    } finally {
        document.getElementById('loading-state').classList.add('hidden');
    }
}

function renderResults(data) {
    document.getElementById('score-val').innerText = `${data.match_score}%`;
    document.getElementById('missing-count').innerText = data.missing_keywords.length;
    document.getElementById('contact-val').innerText = data.contact_info.email || "Not Found";

    // Keyword Chips Rendering
    const chipsContainer = document.getElementById('keyword-chips');
    chipsContainer.innerHTML = '';
    data.missing_keywords.forEach(kw => {
        const chip = document.createElement('span');
        chip.className = 'chip';
        chip.innerText = kw;
        chipsContainer.appendChild(chip);
    });

    // Suggested Bullets Rendering
    const bulletList = document.getElementById('bullet-list');
    bulletList.innerHTML = '';
    data.suggested_bullets.forEach(b => {
        const li = document.createElement('li');
        li.innerText = b;
        bulletList.appendChild(li);
    });

    document.getElementById('results-section').classList.remove('hidden');
}