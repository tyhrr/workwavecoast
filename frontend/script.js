// WorkWave Coast - Frontend
// Compatible con backend Flask, MongoDB Atlas y Cloudinary
// Usa fetch() y FormData para enviar datos y archivos

function getApiBaseUrl() {
    // Detección automática de entorno
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'http://localhost:5000/api/submit';
    }
    // Producción con dominio personalizado
    if (window.location.hostname === 'workwavecoast.online') {
        return 'https://workwavecoast.onrender.com/api/submit';
    }
    // Fallback para GitHub Pages
    return 'https://workwavecoast.onrender.com/api/submit';
}

// Función para formatear tamaño de archivo
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Función para validar tamaño de archivo
function validateFileSize(file, maxSize, fieldName) {
    if (file.size > maxSize) {
        const maxSizeFormatted = formatFileSize(maxSize);
        const fileSizeFormatted = formatFileSize(file.size);
        return `El archivo ${fieldName} es demasiado grande (${fileSizeFormatted}). Máximo permitido: ${maxSizeFormatted}`;
    }
    return null;
}

// Validación en tiempo real de archivos
document.addEventListener('DOMContentLoaded', function() {
    const fileInputs = document.querySelectorAll('input[type="file"][data-max-size]');

    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            const maxSize = parseInt(e.target.getAttribute('data-max-size'));
            const messageDiv = document.getElementById('message');

            if (file) {
                const error = validateFileSize(file, maxSize, e.target.name);
                if (error) {
                    messageDiv.textContent = '⚠️ ' + error;
                    messageDiv.style.color = '#ff6b6b';
                    e.target.value = '';
                    return;
                } else {
                    messageDiv.textContent = '';
                    messageDiv.style.color = '#00587A';
                }
            }
        });
    });
});

document.getElementById('applicationForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const form = e.target;
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = '';
    messageDiv.style.color = '#00587A';

    // Validación básica de campos requeridos
    const requiredFields = ['nombre', 'apellido', 'nacionalidad', 'puesto', 'cv'];
    for (const field of requiredFields) {
        const el = form.elements[field];
        if (!el.value && el.type !== 'file') {
            messageDiv.textContent = '⚠️ Completa todos los campos obligatorios.';
            messageDiv.style.color = '#ff6b6b';
            return;
        }
        if (el.type === 'file' && el.files.length === 0) {
            messageDiv.textContent = '⚠️ Adjunta tu CV.';
            messageDiv.style.color = '#ff6b6b';
            return;
        }
    }

    // Validación de tamaño de archivos
    const fileInputs = form.querySelectorAll('input[type="file"][data-max-size]');
    for (const input of fileInputs) {
        if (input.files.length > 0) {
            const file = input.files[0];
            const maxSize = parseInt(input.getAttribute('data-max-size'));
            const error = validateFileSize(file, maxSize, input.name);
            if (error) {
                messageDiv.textContent = '⚠️ ' + error;
                messageDiv.style.color = '#ff6b6b';
                return;
            }
        }
    }

    // Mostrar indicador de carga
    messageDiv.textContent = '⏳ Enviando postulación...';
    messageDiv.style.color = '#0088B9';

    const formData = new FormData(form);

    // Renombrar campo de archivo adicional si es necesario
    if (formData.has('documentos')) {
        const file = form.elements['documentos'].files[0];
        if (file) formData.set('documentos', file);
    }

    try {
        const response = await fetch(getApiBaseUrl(), {
            method: 'POST',
            body: formData,
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        });

        const result = await response.json();

        if (response.ok && result.success) {
            messageDiv.textContent = '✅ Postulación enviada correctamente. ¡Gracias por tu interés!';
            messageDiv.style.color = '#00B4D8';
            form.reset();
        } else {
            console.error('Server error:', response.status, result);
            messageDiv.textContent = '❌ ' + (result.message || `Error del servidor (${response.status})`);
            messageDiv.style.color = '#ff6b6b';
        }
    } catch (err) {
        console.error('Error:', err);
        console.error('Detalles del error:', err.message, err.stack);
        messageDiv.textContent = '❌ Error de conexión con el servidor. Inténtalo de nuevo.';
        messageDiv.style.color = '#ff6b6b';
    }
});
