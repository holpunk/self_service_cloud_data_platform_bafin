const API_URL = 'http://localhost:8000/api';

document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const msg = document.getElementById('msg');
    msg.innerText = "";

    try {
        const res = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (res.ok) {
            const data = await res.json();
            localStorage.setItem('currentUser', JSON.stringify(data));
            window.location.href = 'dashboard.html';
        } else {
            const err = await res.json();
            msg.innerText = err.detail || "Login failed";
        }
    } catch (err) {
        console.error(err);
        msg.innerText = "Server error";
    }
});
