// Admin Dashboard Script
// Use relative URLs when served from same domain, otherwise use full API URL
const API_URL = window.location.hostname.includes('onrender.com')
    ? '' // Use relative URLs when on Render
    : window.location.hostname === 'localhost'
    ? 'http://localhost:5000'
    : 'https://workwavecoast-backend.onrender.com';

let allApplications = [];
let filteredApplications = [];

// Check authentication on page load
window.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('adminToken');
    const username = localStorage.getItem('adminUsername');

    if (!token) {
        window.location.href = '/admin/login.html';
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

    // Create table structure
    container.innerHTML = `
        <table class="applications-table">
            <thead>
                <tr>
                    <th>Nombre</th>
                    <th>Contacto</th>
                    <th>Nacionalidad</th>
                    <th>Puesto/s</th>
                    <th>Idiomas</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                ${filteredApplications.map(app => createApplicationRow(app)).join('')}
            </tbody>
        </table>
    `;
}

// Create HTML for a single application row
function createApplicationRow(app) {
    const statusClass = app.status || 'pending';
    const statusText = app.status === 'pending' ? 'Pendiente' :
                      app.status === 'approved' ? 'Aprobada' :
                      app.status === 'rejected' ? 'Rechazada' : 'Desconocido';

    // Prepare languages info (horizontal with commas)
    const languages = [];
    if (app.ingles_nivel) languages.push(`Inglés: ${app.ingles_nivel}`);
    if (app.espanol_nivel) languages.push(`Español: ${app.espanol_nivel}`);
    if (app.otro_idioma && app.otro_idioma_nivel) {
        languages.push(`${app.otro_idioma}: ${app.otro_idioma_nivel}`);
    }
    const languagesText = languages.join(', ') || 'N/A';

    // Prepare additional positions (horizontal with commas)
    const puestos = [];

    // Add main position
    if (app.puesto) {
        puestos.push(app.puesto);
    }

    // Add additional positions - handle different formats
    if (app.puestos_adicionales) {
        if (Array.isArray(app.puestos_adicionales)) {
            // Already an array
            puestos.push(...app.puestos_adicionales);
        } else if (typeof app.puestos_adicionales === 'string') {
            // Parse string - could be JSON array or comma-separated
            try {
                const parsed = JSON.parse(app.puestos_adicionales);
                if (Array.isArray(parsed)) {
                    puestos.push(...parsed);
                }
            } catch (e) {
                // Not JSON, try splitting by comma
                const split = app.puestos_adicionales.split(',').map(p => p.trim()).filter(p => p);
                puestos.push(...split);
            }
        }
    }

    const puestosText = puestos.filter(p => p && p.trim()).join(', ') || 'N/A';

    // Parse files from database (can be string or object)
    let filesData = {};
    if (app.files) {
        if (typeof app.files === 'string') {
            try {
                filesData = JSON.parse(app.files);
            } catch (e) {
                console.error('Error parsing files:', e);
            }
        } else {
            filesData = app.files;
        }
    }

    // Get file URLs from parsed data
    const cvUrl = filesData.cv?.url || filesData.curriculum?.url || app.cv_url || '#';
    const otherDocsUrl = filesData.documentos_adicionales?.url || filesData.additional?.url || app.documentos_adicionales_url || '#';
    const hasCv = cvUrl !== '#' && cvUrl;
    const hasOtherDocs = otherDocsUrl !== '#' && otherDocsUrl;

    // Get status checkboxes states
    const isContactado = app.contactado || false;
    const isEnProceso = app.en_proceso || false;
    const isNoCumple = app.no_cumple || false;

    return `
        <tr data-id="${app._id || app.id}">
            <td class="name-cell">${app.nombre || ''} ${app.apellido || ''}</td>
            <td class="contact-cell">
                <div>📧 ${app.email || 'N/A'}</div>
                <div>📱 ${app.telefono || 'N/A'}</div>
            </td>
            <td>${app.nacionalidad || 'N/A'}</td>
            <td class="positions-cell">${puestosText}</td>
            <td class="languages-cell">${languagesText}</td>
            <td class="status-cell">
                <label class="status-checkbox">
                    <input type="checkbox" ${isContactado ? 'checked' : ''}
                           onchange="updateStatus('${app._id || app.id}', 'contactado', this.checked)">
                    <span>Contactado</span>
                </label>
                <label class="status-checkbox">
                    <input type="checkbox" ${isEnProceso ? 'checked' : ''}
                           onchange="updateStatus('${app._id || app.id}', 'en_proceso', this.checked)">
                    <span>En proceso</span>
                </label>
                <label class="status-checkbox no-cumple ${isNoCumple ? 'checked' : ''}">
                    <input type="checkbox" ${isNoCumple ? 'checked' : ''}
                           onchange="updateStatus('${app._id || app.id}', 'no_cumple', this.checked)">
                    <span>No cumple</span>
                </label>
            </td>
            <td class="actions-cell">
                <button class="btn-detail" onclick="showExperience('${app._id || app.id}', \`${(app.experiencia || 'Sin información').replace(/`/g, '\\`').replace(/\n/g, '\\n')}\`)">
                    📝 Detalle
                </button>
                <button class="btn-cv ${hasCv ? '' : 'disabled'}"
                        onclick="${hasCv ? `window.open('${cvUrl}', '_blank')` : 'return false'}"
                        ${!hasCv ? 'disabled' : ''}>
                    📄 Ver CV
                </button>
                <button class="btn-docs ${hasOtherDocs ? '' : 'disabled'}"
                        onclick="${hasOtherDocs ? `window.open('${otherDocsUrl}', '_blank')` : 'return false'}"
                        ${!hasOtherDocs ? 'disabled' : ''}>
                    📎 Ver Otros Docs
                </button>
            </td>
        </tr>
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
        window.location.href = '/admin/login.html';
    }
}

// Show experience details in a modal
function showExperience(applicationId, experiencia) {
    // Create modal if it doesn't exist
    let modal = document.getElementById('experienceModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'experienceModal';
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>📝 Experiencia Laboral</h2>
                    <span class="close-modal">&times;</span>
                </div>
                <div class="modal-body" id="experienceContent"></div>
            </div>
        `;
        document.body.appendChild(modal);

        // Close modal when clicking X or outside
        modal.querySelector('.close-modal').addEventListener('click', () => {
            modal.style.display = 'none';
        });
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    }

    // Set content and show modal
    const content = document.getElementById('experienceContent');
    content.innerHTML = `<p>${experiencia.replace(/\n/g, '<br>') || 'Sin información de experiencia proporcionada.'}</p>`;
    modal.style.display = 'flex';
}

// Update application status
async function updateStatus(applicationId, statusField, isChecked) {
    const token = localStorage.getItem('adminToken');

    try {
        const response = await fetch(`${API_URL}/api/admin/applications/${applicationId}`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                [statusField]: isChecked
            })
        });

        if (!response.ok) {
            throw new Error('Error al actualizar estado');
        }

        const data = await response.json();

        if (data.success) {
            // Update the visual state
            const checkbox = event.target;
            const label = checkbox.closest('.status-checkbox');

            if (statusField === 'no_cumple') {
                if (isChecked) {
                    label.classList.add('checked');
                } else {
                    label.classList.remove('checked');
                }
            }

            console.log('Estado actualizado correctamente');
        } else {
            throw new Error(data.message || 'Error al actualizar');
        }
    } catch (error) {
        console.error('Error updating status:', error);
        alert(`Error al actualizar estado: ${error.message}`);
        // Revert checkbox state
        event.target.checked = !isChecked;
    }
}

// Make functions available globally for onclick handlers
window.approveApplication = approveApplication;
window.rejectApplication = rejectApplication;
window.showExperience = showExperience;
window.updateStatus = updateStatus;
