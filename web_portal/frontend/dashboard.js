const API_URL = 'http://localhost:8000/api';
const user = JSON.parse(localStorage.getItem('currentUser'));

if (!user) window.location.href = 'login.html';
document.getElementById('welcomeMsg').innerText = `Logged in as: ${user.user.name} (${user.user.domain})`;

// --- Tabs ---
function switchTab(tabId) {
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

    // Find tab by text content approximation or index (simple map)
    const tabs = { 'marketplace': 0, 'inbox': 1, 'access': 2 };
    document.querySelectorAll('.nav-tab')[tabs[tabId]].classList.add('active');
    document.getElementById(tabId).classList.add('active');

    if (tabId === 'inbox') loadInbox();
    if (tabId === 'access') loadAccess();
}

function logout() {
    localStorage.removeItem('currentUser');
    window.location.href = 'login.html';
}

// --- Catalog ---
let selectedProduct = null;
async function loadCatalog() {
    const res = await fetch(`${API_URL}/catalog`);
    const data = await res.json();
    const grid = document.getElementById('catalogGrid');
    grid.innerHTML = '';
    data.products.forEach(p => {
        grid.innerHTML += `
            <div class="card">
                <h3>${p.name}</h3>
                <span class="status-badge" style="background: rgba(99,102,241,0.2); color: white;">${p.environment}</span>
                <p style="margin: 1rem 0; font-size: 0.8rem; color: #94a3b8;">Region: eu-central-1</p>
                <button onclick="openModal('${p.name}')" style="width:100%; padding: 0.5rem; background: transparent; border: 1px solid var(--primary); color: var(--primary); border-radius: 6px; cursor: pointer;">Request Access</button>
            </div>`;
    });
}

// --- Inbox ---
async function loadInbox() {
    const res = await fetch(`${API_URL}/notifications?username=${user.username}`);
    const data = await res.json();

    const badge = document.getElementById('badgeCount');
    const bellWrapper = document.querySelector('.bell-wrapper');
    const count = data.requests.length;

    if (count > 0) {
        badge.innerText = count;
        badge.classList.add('show');
        bellWrapper.classList.add('has-notifications');
    } else {
        badge.classList.remove('show');
        bellWrapper.classList.remove('has-notifications');
    }

    const list = document.getElementById('inboxList');
    if (count === 0) {
        list.innerHTML = '<p style="color: #64748b;">No pending requests.</p>';
        return;
    }
    list.innerHTML = '';
    data.requests.forEach(r => {
        list.innerHTML += `
            <div class="inbox-item">
                <div class="inbox-header">
                    <strong>${r.requester}</strong>
                    <span style="font-size: 0.8rem; color: #94a3b8;">${new Date(r.timestamp).toLocaleDateString()}</span>
                </div>
                <p style="font-size: 0.9rem; margin-bottom: 0.5rem;">Wants access to: <strong>${r.target_product}</strong></p>
                <p style="font-size: 0.85rem; color: #cbd5e1; font-style: italic;">"${r.reason}"</p>
                <div class="inbox-actions">
                    <button class="btn-approve" onclick="decide('${r.id}', 'APPROVED')">Approve</button>
                    <button class="btn-reject" onclick="decide('${r.id}', 'REJECTED')">Reject</button>
                </div>
            </div>`;
    });
}

async function decide(reqId, decision) {
    await fetch(`${API_URL}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            username: user.username,
            request_id: reqId,
            decision: decision
        })
    });
    loadInbox();
}

// --- Access ---
async function loadAccess() {
    const res = await fetch(`${API_URL}/access?username=${user.username}`);
    const data = await res.json();
    const list = document.getElementById('accessList');
    list.innerHTML = '';
    data.allowed_domains.forEach(d => {
        list.innerHTML += `
            <div class="access-row">
                <span>${d}</span>
                <span class="status-badge">Access Granted</span>
            </div>`;
    });
    if (data.allowed_domains.length === 0) {
        list.innerHTML = '<p style="color: #64748b;">No access granted yet.</p>';
    }
}

// --- Modal ---
function openModal(item) { selectedProduct = item; document.getElementById('modal').classList.add('active'); }
function closeModal() { document.getElementById('modal').classList.remove('active'); }
async function submitRequest() {
    await fetch(`${API_URL}/access`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            username: user.username,
            target_product: selectedProduct,
            reason: document.getElementById('requestReason').value
        })
    });
    alert('Request Submitted');
    closeModal();
}

// Init
loadCatalog();
loadInbox(); // Initialize badge count
