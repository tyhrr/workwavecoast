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

// Función para formatear teléfono según el país
function getPhoneFormat(countryCode) {
    const formats = {
        '+385': 'XX XXX XXXX (ej: 95 123 4567)', // Croacia
        '+34': 'XXX XXX XXX (ej: 612 345 678)', // España
        '+54': 'XX XXXX XXXX (ej: 11 1234 5678)', // Argentina
        '+52': 'XX XXXX XXXX (ej: 55 1234 5678)', // México
        '+57': 'XXX XXX XXXX (ej: 300 123 4567)', // Colombia
        '+56': 'X XXXX XXXX (ej: 9 1234 5678)', // Chile
        '+51': 'XXX XXX XXX (ej: 987 654 321)', // Perú
        '+58': 'XXX XXX XXXX (ej: 414 123 4567)', // Venezuela
        '+598': 'XXXX XXXX (ej: 9123 4567)', // Uruguay
        '+595': 'XXX XXX XXX (ej: 981 123 456)', // Paraguay
        '+591': 'XXXX XXXX (ej: 7123 4567)', // Bolivia
        '+593': 'XX XXX XXXX (ej: 99 123 4567)', // Ecuador
        '+39': 'XXX XXX XXXX (ej: 320 123 4567)', // Italia
        '+33': 'XX XX XX XX XX (ej: 06 12 34 56 78)', // Francia
        '+49': 'XXX XXXXXXX (ej: 170 1234567)', // Alemania
        '+44': 'XXXX XXX XXX (ej: 7700 123456)', // Reino Unido
        '+1': 'XXX XXX XXXX (ej: 555 123 4567)', // Estados Unidos
        '+55': 'XX XXXXX XXXX (ej: 11 99999 1234)', // Brasil
        '+351': 'XXX XXX XXX (ej: 910 123 456)' // Portugal
    };
    return formats[countryCode] || 'Formato según tu país';
}

// Función para validar formato de teléfono
function validatePhoneFormat(phone, countryCode) {
    // Remover espacios, guiones y paréntesis
    const cleanPhone = phone.replace(/[\s\-\(\)]/g, '');

    const patterns = {
        '+385': /^[0-9]{8,9}$/, // Croacia: 8-9 dígitos
        '+34': /^[0-9]{9}$/, // España: 9 dígitos
        '+54': /^[0-9]{10,11}$/, // Argentina: 10-11 dígitos
        '+52': /^[0-9]{10}$/, // México: 10 dígitos
        '+57': /^[0-9]{10}$/, // Colombia: 10 dígitos
        '+56': /^[0-9]{9}$/, // Chile: 9 dígitos
        '+51': /^[0-9]{9}$/, // Perú: 9 dígitos
        '+58': /^[0-9]{10}$/, // Venezuela: 10 dígitos
        '+598': /^[0-9]{8}$/, // Uruguay: 8 dígitos
        '+595': /^[0-9]{9}$/, // Paraguay: 9 dígitos
        '+591': /^[0-9]{8}$/, // Bolivia: 8 dígitos
        '+593': /^[0-9]{9}$/, // Ecuador: 9 dígitos
        '+39': /^[0-9]{9,10}$/, // Italia: 9-10 dígitos
        '+33': /^[0-9]{10}$/, // Francia: 10 dígitos
        '+49': /^[0-9]{10,11}$/, // Alemania: 10-11 dígitos
        '+44': /^[0-9]{10,11}$/, // Reino Unido: 10-11 dígitos
        '+1': /^[0-9]{10}$/, // Estados Unidos: 10 dígitos
        '+55': /^[0-9]{10,11}$/, // Brasil: 10-11 dígitos
        '+351': /^[0-9]{9}$/ // Portugal: 9 dígitos
    };

    const pattern = patterns[countryCode];
    return pattern ? pattern.test(cleanPhone) : cleanPhone.length >= 7 && cleanPhone.length <= 15;
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

// Validación en tiempo real de archivos y configuración de eventos
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

    // Configurar validación de teléfono en tiempo real
    const paisCodigo = document.getElementById('pais_codigo');
    const telefono = document.getElementById('telefono');
    const phoneFormat = document.getElementById('phoneFormat');

    // Mostrar formato cuando se selecciona un país
    paisCodigo.addEventListener('change', function() {
        const countryCode = this.value;
        if (countryCode) {
            phoneFormat.textContent = `Formato esperado: ${getPhoneFormat(countryCode)}`;
            phoneFormat.className = '';
        } else {
            phoneFormat.textContent = '';
        }

        // Validar teléfono actual si existe
        if (telefono.value) {
            validatePhoneInput();
        }
    });

    // Validar formato de teléfono mientras se escribe
    telefono.addEventListener('input', validatePhoneInput);
    telefono.addEventListener('blur', validatePhoneInput);

    function validatePhoneInput() {
        const countryCode = paisCodigo.value;
        const phoneNumber = telefono.value.trim();

        if (!countryCode) {
            phoneFormat.textContent = 'Selecciona primero tu país';
            phoneFormat.className = 'phone-format phone-error';
            return false;
        }

        if (!phoneNumber) {
            phoneFormat.textContent = `Formato esperado: ${getPhoneFormat(countryCode)}`;
            phoneFormat.className = 'phone-format';
            return false;
        }

        const isValid = validatePhoneFormat(phoneNumber, countryCode);
        if (isValid) {
            phoneFormat.textContent = `✓ Formato correcto`;
            phoneFormat.className = 'phone-format phone-success';
            return true;
        } else {
            phoneFormat.textContent = `✗ Formato incorrecto. Esperado: ${getPhoneFormat(countryCode)}`;
            phoneFormat.className = 'phone-format phone-error';
            return false;
        }
    }

    // Configurar interacción entre puesto principal y adicionales
    const puestoPrincipal = document.getElementById('puesto');
    const puestosAdicionales = document.querySelectorAll('input[name="puesto_adicional"]');

    puestoPrincipal.addEventListener('change', function() {
        const selectedMain = this.value;

        // Deshabilitar el puesto principal en las opciones adicionales
        puestosAdicionales.forEach(checkbox => {
            if (checkbox.value === selectedMain) {
                checkbox.checked = false;
                checkbox.disabled = true;
                checkbox.closest('label').style.opacity = '0.5';
            } else {
                checkbox.disabled = false;
                checkbox.closest('label').style.opacity = '1';
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
    const requiredFields = ['nombre', 'apellido', 'nacionalidad', 'email', 'pais_codigo', 'telefono', 'puesto', 'ingles_nivel', 'cv'];
    for (const field of requiredFields) {
        const el = form.elements[field];
        if (!el.value && el.type !== 'file') {
            messageDiv.textContent = '⚠️ Completa todos los campos obligatorios.';
            messageDiv.style.color = '#ff6b6b';
            el.focus();
            return;
        }
        if (el.type === 'file' && el.files.length === 0) {
            messageDiv.textContent = '⚠️ Adjunta tu CV en formato PDF.';
            messageDiv.style.color = '#ff6b6b';
            el.focus();
            return;
        }
    }

    // Validación específica de teléfono
    const paisCodigo = form.elements['pais_codigo'].value;
    const telefono = form.elements['telefono'].value.trim();

    if (!validatePhoneFormat(telefono, paisCodigo)) {
        messageDiv.textContent = '⚠️ El formato del número de teléfono no es válido para el país seleccionado.';
        messageDiv.style.color = '#ff6b6b';
        form.elements['telefono'].focus();
        return;
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
    messageDiv.textContent = '⏳ Verificando datos y enviando postulación...';
    messageDiv.style.color = '#0088B9';

    const formData = new FormData(form);

    // Agregar código de país completo al teléfono
    const telefonoCompleto = paisCodigo + ' ' + telefono.replace(/[\s\-\(\)]/g, '');
    formData.set('telefono', telefonoCompleto);

    // Recopilar puestos adicionales seleccionados
    const puestosAdicionales = [];
    const checkboxes = form.querySelectorAll('input[name="puesto_adicional"]:checked');
    checkboxes.forEach(checkbox => {
        puestosAdicionales.push(checkbox.value);
    });

    if (puestosAdicionales.length > 0) {
        formData.set('puestos_adicionales', puestosAdicionales.join(', '));
    }

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

            // Limpiar validaciones visuales
            const phoneFormat = document.getElementById('phoneFormat');
            phoneFormat.textContent = '';
            phoneFormat.className = 'phone-format';

            // Rehabilitar todos los checkboxes
            const puestosAdicionales = document.querySelectorAll('input[name="puesto_adicional"]');
            puestosAdicionales.forEach(checkbox => {
                checkbox.disabled = false;
                checkbox.closest('label').style.opacity = '1';
            });

        } else {
            console.error('Server error:', response.status, result);

            // Manejar errores específicos
            if (result.message && result.message.includes('ya aplicó anteriormente')) {
                messageDiv.textContent = '⚠️ Ya existe una aplicación con este email. Cada persona solo puede aplicar una vez.';
            } else {
                messageDiv.textContent = '❌ ' + (result.message || `Error del servidor (${response.status})`);
            }
            messageDiv.style.color = '#ff6b6b';
        }
    } catch (err) {
        console.error('Error:', err);
        console.error('Detalles del error:', err.message, err.stack);
        messageDiv.textContent = '❌ Error de conexión con el servidor. Verifica tu conexión e inténtalo de nuevo.';
        messageDiv.style.color = '#ff6b6b';
    }
});
