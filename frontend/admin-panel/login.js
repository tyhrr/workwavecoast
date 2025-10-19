// Admin Login Script
// Use relative URLs when served from same domain, otherwise use full API URL
const API_URL = window.location.hostname.includes('onrender.com')
    ? '' // Use relative URLs when on Render
    : window.location.hostname === 'localhost'
    ? 'http://localhost:5000'
    : 'https://workwavecoast-backend.onrender.com';

document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('errorMessage');
    const loadingDiv = document.getElementById('loadingMessage');
    const submitBtn = e.target.querySelector('button[type="submit"]');

    // Clear previous errors
    errorDiv.style.display = 'none';
    loadingDiv.style.display = 'block';
    submitBtn.disabled = true;

    try {
        const response = await fetch(`${API_URL}/api/admin/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (data.success && data.data && data.data.access_token) {
            // Store token and admin info
            localStorage.setItem('adminToken', data.data.access_token);
            localStorage.setItem('adminRefreshToken', data.data.refresh_token);
            localStorage.setItem('adminUsername', username);
            localStorage.setItem('adminRole', data.data.role || 'admin');

            // Redirect to dashboard
            window.location.href = 'dashboard.html';
        } else {
            throw new Error(data.message || 'Error de autenticación');
        }
    } catch (error) {
        console.error('Login error:', error);
        errorDiv.textContent = error.message || 'Error al iniciar sesión. Verifica tus credenciales.';
        errorDiv.style.display = 'block';
    } finally {
        loadingDiv.style.display = 'none';
        submitBtn.disabled = false;
    }
});

// Check if already logged in
window.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('adminToken');
    if (token) {
        // Verify token is still valid
        fetch(`${API_URL}/api/admin/auth/verify`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                window.location.href = 'dashboard.html';
            } else {
                // Token invalid, clear storage
                localStorage.clear();
            }
        })
        .catch(() => {
            localStorage.clear();
        });
    }
});
