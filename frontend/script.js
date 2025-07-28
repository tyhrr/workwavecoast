// WorkWave Coast - Frontend
// Compatible con backend Flask, MongoDB Atlas y Cloudinary
// Usa fetch() y FormData para enviar datos y archivos

function getApiBaseUrl() {
    // Detección automática de entorno
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'http://localhost:5000/api/submit';
    }
    // TEMPORAL: Usar backend local hasta que se despliegue en Render
    if (window.location.hostname === 'workwavecoast.online') {
        return 'http://localhost:5000/api/submit';
    }
    // Fallback para GitHub Pages
    return 'https://workwavecoast-backend.onrender.com/api/submit';
}

document.getElementById('applicationForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const form = e.target;
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = '';

    // Validación básica
    const requiredFields = ['nombre', 'apellido', 'nacionalidad', 'puesto', 'cv'];
    for (const field of requiredFields) {
        const el = form.elements[field];
        if (!el.value && el.type !== 'file') {
            messageDiv.textContent = 'Completa todos los campos obligatorios.';
            return;
        }
        if (el.type === 'file' && el.files.length === 0) {
            messageDiv.textContent = 'Adjunta tu CV.';
            return;
        }
    }

    const formData = new FormData(form);
    // Renombrar campo de archivo adicional si es necesario
    if (formData.has('documentos')) {
        const file = form.elements['documentos'].files[0];
        if (file) formData.set('documentos', file);
    }

    try {
        const response = await fetch(getApiBaseUrl(), {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        if (result.success) {
            messageDiv.textContent = '✅ Postulación enviada correctamente.';
            form.reset();
        } else {
            messageDiv.textContent = '❌ ' + (result.message || 'Error al enviar la postulación.');
        }
    } catch (err) {
        messageDiv.textContent = '❌ Error de conexión con el servidor.';
    }
});
