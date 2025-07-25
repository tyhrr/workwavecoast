// Configuración del API endpoint
const API_BASE_URL = 'http://localhost:5000';

// Variables globales
let isSubmitting = false;

// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    initializeForm();
    setupEventListeners();
});

// Inicializar el formulario
function initializeForm() {
    const form = document.getElementById('applicationForm');
    const submitBtn = document.getElementById('submitBtn');
    
    // Resetear estado del formulario
    form.reset();
    submitBtn.disabled = false;
    isSubmitting = false;
    
    // Ocultar mensajes
    hideMessages();
    
    console.log('Formulario inicializado correctamente');
}

// Configurar event listeners
function setupEventListeners() {
    const form = document.getElementById('applicationForm');
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    // Envío del formulario
    form.addEventListener('submit', handleFormSubmit);
    
    // Validación en tiempo real
    form.addEventListener('input', handleInputValidation);
    
    // Validación de archivos
    fileInputs.forEach(input => {
        input.addEventListener('change', handleFileValidation);
    });
}

// Manejar envío del formulario
async function handleFormSubmit(event) {
    event.preventDefault();
    
    if (isSubmitting) return;
    
    const form = event.target;
    
    // Validar formulario
    if (!validateForm(form)) {
        showError('Por favor, completa todos los campos requeridos correctamente.');
        return;
    }
    
    // Cambiar estado de envío
    setSubmittingState(true);
    hideMessages();
    
    try {
        // Crear FormData
        const formData = new FormData(form);
        
        // Enviar datos
        const response = await submitFormData(formData);
        
        if (response.success) {
            showSuccess();
            form.reset();
        } else {
            throw new Error(response.message || 'Error desconocido');
        }
        
    } catch (error) {
        console.error('Error al enviar formulario:', error);
        showError(error.message || 'Error de conexión. Verifica que el servidor esté ejecutándose.');
    } finally {
        setSubmittingState(false);
    }
}

// Enviar datos del formulario
async function submitFormData(formData) {
    const response = await fetch(`${API_BASE_URL}/submit`, {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) {
        throw new Error(`Error del servidor: ${response.status}`);
    }
    
    return await response.json();
}

// Validar formulario completo
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
            field.classList.add('error');
        } else {
            field.classList.remove('error');
        }
    });
    
    return isValid;
}

// Validar campo individual
function validateField(field) {
    const value = field.value.trim();
    const type = field.type;
    
    // Campo vacío
    if (!value && field.hasAttribute('required')) {
        return false;
    }
    
    // Validaciones específicas por tipo
    switch (type) {
        case 'text':
            return value.length >= 2;
        case 'file':
            return field.files.length > 0;
        default:
            return value !== '';
    }
}

// Validación en tiempo real
function handleInputValidation(event) {
    const field = event.target;
    
    if (field.hasAttribute('required')) {
        const isValid = validateField(field);
        
        if (isValid) {
            field.classList.remove('error');
            field.classList.add('valid');
        } else {
            field.classList.remove('valid');
            if (field.value.length > 0) {
                field.classList.add('error');
            }
        }
    }
}

// Validación de archivos
function handleFileValidation(event) {
    const fileInput = event.target;
    const files = fileInput.files;
    const maxSize = 5 * 1024 * 1024; // 5MB
    
    let hasError = false;
    let errorMessage = '';
    
    Array.from(files).forEach(file => {
        // Validar tamaño
        if (file.size > maxSize) {
            hasError = true;
            errorMessage = `El archivo "${file.name}" es demasiado grande. Máximo 5MB.`;
            return;
        }
        
        // Validar tipo para CV (debe ser PDF)
        if (fileInput.id === 'cv' && file.type !== 'application/pdf') {
            hasError = true;
            errorMessage = 'El CV debe ser un archivo PDF.';
            return;
        }
    });
    
    if (hasError) {
        showError(errorMessage);
        fileInput.value = '';
        return;
    }
    
    // Archivo válido
    hideMessages();
}

// Cambiar estado de envío
function setSubmittingState(submitting) {
    isSubmitting = submitting;
    const submitBtn = document.getElementById('submitBtn');
    const submitText = document.getElementById('submitText');
    const loadingText = document.getElementById('loadingText');
    
    submitBtn.disabled = submitting;
    
    if (submitting) {
        submitText.style.display = 'none';
        loadingText.style.display = 'inline';
    } else {
        submitText.style.display = 'inline';
        loadingText.style.display = 'none';
    }
}

// Mostrar mensaje de éxito
function showSuccess() {
    const successMessage = document.getElementById('successMessage');
    const errorMessage = document.getElementById('errorMessage');
    
    errorMessage.style.display = 'none';
    successMessage.style.display = 'block';
    
    // Scroll al mensaje
    successMessage.scrollIntoView({ behavior: 'smooth' });
    
    // Auto-ocultar después de 5 segundos
    setTimeout(() => {
        successMessage.style.display = 'none';
    }, 5000);
}

// Mostrar mensaje de error
function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    const successMessage = document.getElementById('successMessage');
    
    successMessage.style.display = 'none';
    errorText.textContent = message;
    errorMessage.style.display = 'block';
    
    // Scroll al mensaje
    errorMessage.scrollIntoView({ behavior: 'smooth' });
    
    // Auto-ocultar después de 7 segundos
    setTimeout(() => {
        errorMessage.style.display = 'none';
    }, 7000);
}

// Ocultar todos los mensajes
function hideMessages() {
    document.getElementById('successMessage').style.display = 'none';
    document.getElementById('errorMessage').style.display = 'none';
}

// Utilidades adicionales
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Detectar si el servidor está disponible
async function checkServerConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`, {
            method: 'GET',
            timeout: 5000
        });
        return response.ok;
    } catch (error) {
        return false;
    }
}

// Mostrar información de conexión al cargar la página
window.addEventListener('load', async () => {
    const isServerOnline = await checkServerConnection();
    
    if (!isServerOnline) {
        console.warn('⚠️ Servidor no disponible. Ejecuta "python server.py" para procesar formularios.');
        
        // Mostrar aviso discreto
        const form = document.getElementById('applicationForm');
        const notice = document.createElement('div');
        notice.className = 'server-notice';
        notice.innerHTML = `
            <small style="color: #dc3545; background: #f8d7da; padding: 8px; border-radius: 4px; display: block; text-align: center; margin-bottom: 1rem;">
                ⚠️ Servidor no disponible. Para procesar formularios, ejecuta: <code>python server.py</code>
            </small>
        `;
        form.insertBefore(notice, form.firstChild);
    }
});
