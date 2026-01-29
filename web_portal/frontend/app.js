const form = document.getElementById('requestForm');
const submitBtn = document.getElementById('submitBtn');
const statusDiv = document.getElementById('statusMessage');
const spinner = document.querySelector('.spinner');
const btnText = submitBtn.querySelector('span');

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // UI Loading State
    setLoading(true);
    statusDiv.classList.add('hidden');
    statusDiv.className = 'status-message hidden'; // reset classes

    // Gather Data
    const formData = {
        name: document.getElementById('productName').value,
        environment: document.getElementById('environment').value,
        region: document.getElementById('region').value,
        encryption: {
            enabled: document.getElementById('encryption').checked
        },
        public_access: document.getElementById('publicAccess').checked
    };

    try {
        const response = await fetch('http://localhost:8000/api/products', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (response.ok) {
            showStatus('success', `✅ Success! ${data.message} <br> Created: <strong>${data.file}</strong>`);
            form.reset();
            // restore encryption checked state (it's disabled but visual)
            document.getElementById('encryption').checked = true;
        } else {
            // Parse error details
            let errorMsg = `⚠️ ${data.detail.message || 'Request Failed'}`;
            if (data.detail.errors) {
                errorMsg += '<ul>';
                data.detail.errors.forEach(err => {
                    errorMsg += `<li>${err}</li>`;
                });
                errorMsg += '</ul>';
            }
            showStatus('error', errorMsg);
        }

    } catch (err) {
        showStatus('error', '❌ Connection Failed. Is the backend server running?');
        console.error(err);
    } finally {
        setLoading(false);
    }
});

function setLoading(isLoading) {
    submitBtn.disabled = isLoading;
    if (isLoading) {
        spinner.classList.remove('hidden');
        btnText.textContent = 'Processing...';
    } else {
        spinner.classList.add('hidden');
        btnText.textContent = 'Provision Infrastructure';
    }
}

function showStatus(type, htmlContent) {
    statusDiv.innerHTML = htmlContent;
    statusDiv.classList.remove('hidden');
    statusDiv.classList.add(type);
}
