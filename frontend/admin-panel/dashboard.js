// Admin Dashboard Script
const API_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:5000'
    : 'https://workwavecoast-backend.onrender.com';

let allApplications = [];
let filteredApplications = [];

// Check authentication on page load
window.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('adminToken');
    const username = localStorage.getItem('adminUsername');

    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    // Display admin username
    if (username) {
        document.getElementById('adminUsername').textContent = `👤 ${username}`;
    }

    // Load applications
    loadApplications();

    // Setup event listeners
    setupEventListeners();
});

// Setup all event listeners
function setupEventListeners() {
    // Logout button
    document.getElementById('logoutBtn').addEventListener('click', logout);

    // Search input
    document.getElementById('searchInput').addEventListener('input', (e) => {
        filterApplications();
    });

    // Status filter
    document.getElementById('statusFilter').addEventListener('change', () => {
        filterApplications();
    });

    // Position filter
    document.getElementById('positionFilter').addEventListener('change', () => {
        filterApplications();
    });

    // Export button
    document.getElementById('exportBtn').addEventListener('click', exportToCSV);
}

// Load applications from API
async function loadApplications() {
    const token = localStorage.getItem('adminToken');
    const loadingState = document.getElementById('loadingState');
    const applicationsList = document.getElementById('applicationsList');
    const emptyState = document.getElementById('emptyState');

    try {
        const response = await fetch(`${API_URL}/api/admin/applications`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.status === 401) {
            // Token expired or invalid
            logout();
            return;
        }

        const data = await response.json();

        if (data.success && data.data && data.data.applications) {
            allApplications = data.data.applications;
            filteredApplications = [...allApplications];

            // Populate position filter
            populatePositionFilter();

            // Update statistics
            updateStatistics();

            // Display applications
            displayApplications();

            loadingState.style.display = 'none';
            applicationsList.style.display = 'block';
        } else {
            throw new Error(data.message || 'Error al cargar aplicaciones');
        }
    } catch (error) {
        console.error('Error loading applications:', error);
        loadingState.innerHTML = `<p style="color: #dc3545;">Error: ${error.message}</p>`;
    }
}

// Populate position filter with unique positions
function populatePositionFilter() {
    const positions = [...new Set(allApplications.map(app => app.puesto))].sort();
    const select = document.getElementById('positionFilter');

    positions.forEach(position => {
        const option = document.createElement('option');
        option.value = position;
        option.textContent = position;
        select.appendChild(option);
    });
}

// Update statistics cards
function updateStatistics() {
    const total = allApplications.length;
    const today = new Date().toISOString().split('T')[0];
    const todayCount = allApplications.filter(app =>
        app.created_at && app.created_at.startsWith(today)
    ).length;
    const pendingCount = allApplications.filter(app => app.status === 'pending').length;
    const approvedCount = allApplications.filter(app => app.status === 'approved').length;

    document.getElementById('totalCount').textContent = total;
    document.getElementById('todayCount').textContent = todayCount;
    document.getElementById('pendingCount').textContent = pendingCount;
    document.getElementById('approvedCount').textContent = approvedCount;
}

// Filter applications based on search and filters
function filterApplications() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const statusFilter = document.getElementById('statusFilter').value;
    const positionFilter = document.getElementById('positionFilter').value;

    filteredApplications = allApplications.filter(app => {
        // Search filter
        const matchesSearch = !searchTerm ||
            app.nombre?.toLowerCase().includes(searchTerm) ||
            app.apellido?.toLowerCase().includes(searchTerm) ||
            app.email?.toLowerCase().includes(searchTerm) ||
            app.telefono?.includes(searchTerm);

        // Status filter
        const matchesStatus = !statusFilter || app.status === statusFilter;

        // Position filter
        const matchesPosition = !positionFilter || app.puesto === positionFilter;

        return matchesSearch && matchesStatus && matchesPosition;
    });

    displayApplications();
}

// Display applications in the list
function displayApplications() {
    const container = document.getElementById('applicationsList');
    const emptyState = document.getElementById('emptyState');

    if (filteredApplications.length === 0) {
        container.style.display = 'none';
        emptyState.style.display = 'block';
        return;
    }

    emptyState.style.display = 'none';
    container.style.display = 'block';

    container.innerHTML = filteredApplications.map(app => createApplicationCard(app)).join('');
}

// Create HTML for a single application card
function createApplicationCard(app) {
    const createdDate = app.created_at ? new Date(app.created_at).toLocaleString('es-ES') : 'N/A';
    const statusClass = app.status || 'pending';
    const statusText = app.status === 'pending' ? 'Pendiente' :
                      app.status === 'approved' ? 'Aprobada' :
                      app.status === 'rejected' ? 'Rechazada' : 'Desconocido';

    let filesHTML = '';
    if (app.files && typeof app.files === 'object') {
        const fileEntries = Object.entries(app.files).filter(([_, fileInfo]) => fileInfo && fileInfo.url);
        if (fileEntries.length > 0) {
            filesHTML = `
                <div class="files">
                    <strong>📎 Archivos adjuntos:</strong>
                    ${fileEntries.map(([fileType, fileInfo]) => {
                        const sizeKB = fileInfo.bytes ? (fileInfo.bytes / 1024).toFixed(1) : '?';
                        return `<a href="${fileInfo.url}" target="_blank" class="file-link">
                            📄 ${fileType.charAt(0).toUpperCase() + fileType.slice(1)} (${sizeKB}KB)
                        </a>`;
                    }).join('')}
                </div>
            `;
        }
    }

    return `
        <div class="application" data-id="${app._id || app.id}">
            <div class="app-header">
                <div class="app-name">${app.nombre || ''} ${app.apellido || ''}</div>
                <div class="app-date">${createdDate}</div>
            </div>

            <div class="app-details">
                <div class="detail"><strong>📧 Email:</strong> ${app.email || 'N/A'}</div>
                <div class="detail"><strong>📱 Teléfono:</strong> ${app.telefono || 'N/A'}</div>
                <div class="detail"><strong>🌍 Nacionalidad:</strong> ${app.nacionalidad || 'N/A'}</div>
                <div class="detail"><strong>💼 Puesto:</strong> ${app.puesto || 'N/A'}</div>
                <div class="detail"><strong>🇪🇸 Español:</strong> ${app.espanol_nivel || 'N/A'}</div>
                <div class="detail"><strong>🇬🇧 Inglés:</strong> ${app.ingles_nivel || 'N/A'}</div>
                ${app.otro_idioma ? `<div class="detail"><strong>🗣️ ${app.otro_idioma}:</strong> ${app.otro_idioma_nivel || 'N/A'}</div>` : ''}
                <div class="detail">
                    <strong>📊 Estado:</strong>
                    <span class="status ${statusClass}">${statusText}</span>
                </div>
            </div>

            ${filesHTML}

            ${app.status === 'pending' ? `
                <div class="app-actions">
                    <button class="btn-approve" onclick="approveApplication('${app._id || app.id}')">✅ Aprobar</button>
                    <button class="btn-reject" onclick="rejectApplication('${app._id || app.id}')">❌ Rechazar</button>
                </div>
            ` : ''}
        </div>
    `;
}

// Approve application
async function approveApplication(applicationId) {
    const token = localStorage.getItem('adminToken');

    if (!confirm('¿Estás seguro de que deseas aprobar esta aplicación?')) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/admin/applications/${applicationId}/approve`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                send_notification: true
            })
        });

        const data = await response.json();

        if (data.success) {
            alert('✅ Aplicación aprobada exitosamente');
            loadApplications(); // Reload applications
        } else {
            throw new Error(data.message || 'Error al aprobar la aplicación');
        }
    } catch (error) {
        console.error('Error approving application:', error);
        alert(`Error: ${error.message}`);
    }
}

// Reject application
async function rejectApplication(applicationId) {
    const token = localStorage.getItem('adminToken');
    const reason = prompt('¿Razón del rechazo? (opcional)');

    if (reason === null) return; // User cancelled

    try {
        const response = await fetch(`${API_URL}/api/admin/applications/${applicationId}/reject`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                reason: reason || 'No especificado',
                send_notification: true
            })
        });

        const data = await response.json();

        if (data.success) {
            alert('❌ Aplicación rechazada');
            loadApplications(); // Reload applications
        } else {
            throw new Error(data.message || 'Error al rechazar la aplicación');
        }
    } catch (error) {
        console.error('Error rejecting application:', error);
        alert(`Error: ${error.message}`);
    }
}

// Export applications to CSV
async function exportToCSV() {
    const token = localStorage.getItem('adminToken');

    try {
        const response = await fetch(`${API_URL}/api/admin/applications/export?format=csv`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `applications_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } else {
            throw new Error('Error al exportar');
        }
    } catch (error) {
        console.error('Error exporting:', error);
        alert(`Error al exportar: ${error.message}`);
    }
}

// Logout function
function logout() {
    if (confirm('¿Estás seguro de que deseas cerrar sesión?')) {
        localStorage.clear();
        window.location.href = 'login.html';
    }
}

// Make functions available globally for onclick handlers
window.approveApplication = approveApplication;
window.rejectApplication = rejectApplication;
