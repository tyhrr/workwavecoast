// WorkWave Coast - Frontend Application
// Sistema de aplicación completo con validación y retry

// =================== CONFIGURACIÓN GLOBAL ===================
let isAppInitialized = false;
const retryConfig = {
    maxRetries: 3,
    baseDelay: 1000,
    maxDelay: 5000
};

// =================== FUNCIONES DE UTILIDAD ===================
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function retryWithBackoff(fn, context = 'operación') {
    let lastError;
    
    for (let attempt = 0; attempt <= retryConfig.maxRetries; attempt++) {
        try {
            return await fn();
        } catch (error) {
            lastError = error;
            
            if (attempt === retryConfig.maxRetries) {
                console.error(`❌ ${context} falló después de ${retryConfig.maxRetries} intentos:`, error);
                break;
            }
            
            const delay = Math.min(
                retryConfig.baseDelay * Math.pow(2, attempt),
                retryConfig.maxDelay
            );
            
            console.warn(`⚠️ ${context} falló (intento ${attempt + 1}), reintentando en ${delay}ms...`);
            await sleep(delay);
        }
    }
    
    throw lastError;
}

// =================== CONFIGURACIÓN DE API ===================
function getApiBaseUrl() {
    try {
        const hostname = window.location.hostname;
        
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return 'http://localhost:5000/api/submit';
        }
        
        if (hostname === 'workwavecoast.online' || hostname === 'www.workwavecoast.online') {
            return 'https://workwavecoast.onrender.com/api/submit';
        }
        
        if (hostname.includes('github.io')) {
            return 'https://workwavecoast.onrender.com/api/submit';
        }
        
        return 'https://workwavecoast.onrender.com/api/submit';
        
    } catch (error) {
        console.error('❌ Error detectando entorno:', error);
        return 'https://workwavecoast.onrender.com/api/submit';
    }
}

// =================== CARGA DE PAÍSES ===================
function loadCountryOptions() {
    const select = document.getElementById('pais_codigo');
    
    if (!select) {
        console.warn('⚠️ Elemento select de país no encontrado');
        return;
    }

    try {
        const countries = [];
        
        // Lista de países comunes con sus códigos ISO
        const commonCountries = [
            'HR', 'ES', 'AR', 'MX', 'CO', 'CL', 'PE', 'VE', 'UY', 'PY', 'BO', 'EC',
            'IT', 'FR', 'DE', 'GB', 'US', 'BR', 'PT', 'NL', 'BE', 'CH', 'AT', 'DK',
            'SE', 'NO', 'FI', 'PL', 'CZ', 'SK', 'SI', 'HU', 'RO', 'BG', 'GR', 'TR'
        ];

        const countryNames = {
            'HR': 'Croacia', 'ES': 'España', 'AR': 'Argentina', 'MX': 'México', 'CO': 'Colombia',
            'CL': 'Chile', 'PE': 'Perú', 'VE': 'Venezuela', 'UY': 'Uruguay', 'PY': 'Paraguay',
            'BO': 'Bolivia', 'EC': 'Ecuador', 'IT': 'Italia', 'FR': 'Francia', 'DE': 'Alemania',
            'GB': 'Reino Unido', 'US': 'Estados Unidos', 'BR': 'Brasil', 'PT': 'Portugal',
            'NL': 'Países Bajos', 'BE': 'Bélgica', 'CH': 'Suiza', 'AT': 'Austria', 'DK': 'Dinamarca',
            'SE': 'Suecia', 'NO': 'Noruega', 'FI': 'Finlandia', 'PL': 'Polonia', 'CZ': 'República Checa',
            'SK': 'Eslovaquia', 'SI': 'Eslovenia', 'HU': 'Hungría', 'RO': 'Rumania', 'BG': 'Bulgaria',
            'GR': 'Grecia', 'TR': 'Turquía'
        };

        const countryFlags = {
            'HR': '🇭🇷', 'ES': '🇪🇸', 'AR': '🇦🇷', 'MX': '🇲🇽', 'CO': '🇨🇴',
            'CL': '🇨🇱', 'PE': '🇵🇪', 'VE': '🇻🇪', 'UY': '🇺🇾', 'PY': '🇵🇾',
            'BO': '🇧🇴', 'EC': '🇪🇨', 'IT': '🇮🇹', 'FR': '🇫🇷', 'DE': '🇩🇪',
            'GB': '🇬🇧', 'US': '🇺🇸', 'BR': '🇧🇷', 'PT': '🇵🇹', 'NL': '🇳🇱',
            'BE': '🇧🇪', 'CH': '🇨🇭', 'AT': '🇦🇹', 'DK': '🇩🇰', 'SE': '🇸🇪',
            'NO': '🇳🇴', 'FI': '🇫🇮', 'PL': '🇵🇱', 'CZ': '🇨🇿', 'SK': '🇸🇰',
            'SI': '🇸🇮', 'HU': '🇭🇺', 'RO': '🇷🇴', 'BG': '🇧🇬', 'GR': '🇬🇷', 'TR': '🇹🇷'
        };

        // Códigos de respaldo
        const fallbackCodes = {
            'HR': '+385', 'ES': '+34', 'AR': '+54', 'MX': '+52', 'CO': '+57',
            'CL': '+56', 'PE': '+51', 'VE': '+58', 'UY': '+598', 'PY': '+595',
            'BO': '+591', 'EC': '+593', 'IT': '+39', 'FR': '+33', 'DE': '+49',
            'GB': '+44', 'US': '+1', 'BR': '+55', 'PT': '+351', 'NL': '+31',
            'BE': '+32', 'CH': '+41', 'AT': '+43', 'DK': '+45', 'SE': '+46',
            'NO': '+47', 'FI': '+358', 'PL': '+48', 'CZ': '+420', 'SK': '+421',
            'SI': '+386', 'HU': '+36', 'RO': '+40', 'BG': '+359', 'GR': '+30', 'TR': '+90'
        };

        // Intentar usar libphonenumber si está disponible
        if (typeof libphonenumber !== 'undefined') {
            commonCountries.forEach(iso => {
                try {
                    const callingCode = libphonenumber.getCountryCallingCode(iso);
                    countries.push({
                        iso: iso,
                        code: '+' + callingCode,
                        name: countryNames[iso] || iso,
                        flag: countryFlags[iso] || '🌍'
                    });
                } catch (error) {
                    // Usar fallback si libphonenumber falla
                    if (fallbackCodes[iso]) {
                        countries.push({
                            iso: iso,
                            code: fallbackCodes[iso],
                            name: countryNames[iso] || iso,
                            flag: countryFlags[iso] || '🌍'
                        });
                    }
                }
            });
        } else {
            // Usar códigos de respaldo si libphonenumber no está disponible
            console.warn('⚠️ libphonenumber no está disponible, usando códigos de respaldo');
            commonCountries.forEach(iso => {
                if (fallbackCodes[iso]) {
                    countries.push({
                        iso: iso,
                        code: fallbackCodes[iso],
                        name: countryNames[iso] || iso,
                        flag: countryFlags[iso] || '🌍'
                    });
                }
            });
        }

        // Ordenar países por nombre
        countries.sort((a, b) => a.name.localeCompare(b.name));

        // Limpiar opciones existentes
        select.innerHTML = '<option value="">Seleccionar país...</option>';

        // Agregar opciones de países
        countries.forEach(country => {
            const option = document.createElement('option');
            option.value = country.code;
            option.textContent = `${country.flag} ${country.code} (${country.name})`;
            select.appendChild(option);
        });

        console.log(`✅ Cargados ${countries.length} países exitosamente`);

    } catch (error) {
        console.error('❌ Error cargando países:', error);
        loadFallbackCountries(select);
    }
}

function loadFallbackCountries(select) {
    console.warn('🔄 Cargando países de respaldo mínimo...');
    
    const fallbackCountries = [
        { code: '+385', name: 'Croacia', flag: '🇭🇷' },
        { code: '+34', name: 'España', flag: '🇪🇸' },
        { code: '+54', name: 'Argentina', flag: '🇦🇷' },
        { code: '+52', name: 'México', flag: '🇲🇽' },
        { code: '+57', name: 'Colombia', flag: '🇨🇴' },
        { code: '+1', name: 'Estados Unidos', flag: '🇺🇸' },
        { code: '+33', name: 'Francia', flag: '🇫🇷' },
        { code: '+49', name: 'Alemania', flag: '🇩🇪' },
        { code: '+39', name: 'Italia', flag: '🇮🇹' },
        { code: '+351', name: 'Portugal', flag: '🇵🇹' }
    ];

    select.innerHTML = '<option value="">Seleccionar país...</option>';
    
    fallbackCountries.forEach(country => {
        const option = document.createElement('option');
        option.value = country.code;
        option.textContent = `${country.flag} ${country.code} (${country.name})`;
        select.appendChild(option);
    });

    console.log('✅ Cargados países de respaldo');
}

// =================== VALIDACIÓN DE TELÉFONO ===================
function validatePhoneFormat(phone, countryCode) {
    const cleanPhone = phone.replace(/[\s\-\(\)]/g, '');

    try {
        if (typeof libphonenumber !== 'undefined' && libphonenumber.parsePhoneNumber) {
            const isoCode = getISOFromCallingCode(countryCode);
            if (isoCode) {
                try {
                    const phoneNumber = libphonenumber.parsePhoneNumber(cleanPhone, isoCode);
                    return phoneNumber.isValid();
                } catch (error) {
                    console.warn('Error validando teléfono con libphonenumber:', error);
                }
            }
        }
    } catch (error) {
        console.warn('libphonenumber no disponible, usando validación básica');
    }

    // Fallback: validación básica por patrones
    const patterns = {
        '+385': /^[0-9]{8,9}$/,
        '+34': /^[0-9]{9}$/,
        '+54': /^[0-9]{10,11}$/,
        '+52': /^[0-9]{10}$/,
        '+57': /^[0-9]{10}$/,
        '+1': /^[0-9]{10}$/,
        '+33': /^[0-9]{10}$/,
        '+49': /^[0-9]{10,11}$/,
        '+39': /^[0-9]{9,10}$/,
        '+351': /^[0-9]{9}$/
    };

    const pattern = patterns[countryCode];
    return pattern ? pattern.test(cleanPhone) : cleanPhone.length >= 7 && cleanPhone.length <= 15;
}

function getISOFromCallingCode(callingCode) {
    const mapping = {
        '+385': 'HR', '+34': 'ES', '+54': 'AR', '+52': 'MX', '+57': 'CO',
        '+56': 'CL', '+51': 'PE', '+58': 'VE', '+598': 'UY', '+595': 'PY',
        '+591': 'BO', '+593': 'EC', '+39': 'IT', '+33': 'FR', '+49': 'DE',
        '+44': 'GB', '+1': 'US', '+55': 'BR', '+351': 'PT'
    };
    return mapping[callingCode];
}

function getPhoneFormat(countryCode) {
    const formats = {
        '+385': 'XX XXX XXXX',
        '+34': 'XXX XXX XXX',
        '+54': 'XX XXXX XXXX',
        '+52': 'XXX XXX XXXX',
        '+57': 'XXX XXX XXXX',
        '+1': 'XXX XXX XXXX',
        '+33': 'XX XX XX XX XX',
        '+49': 'XXXX XXXXXXX',
        '+39': 'XXX XXX XXXX',
        '+351': 'XXX XXX XXX'
    };
    return formats[countryCode] || 'Número de teléfono';
}

// =================== ENVÍO DE FORMULARIO ===================
async function submitForm(form, messageDiv) {
    // Validación básica de campos requeridos
    const requiredFields = ['nombre', 'apellido', 'nacionalidad', 'email', 'pais_codigo', 'telefono', 'puesto', 'ingles_nivel', 'experiencia', 'cv'];
    
    for (const fieldName of requiredFields) {
        const field = form.elements[fieldName];
        if (!field) {
            throw new Error(`Campo ${fieldName} no encontrado`);
        }
        
        if (field.type === 'file') {
            if (field.files.length === 0) {
                field.focus();
                throw new Error('⚠️ Adjunta tu CV en formato PDF.');
            }
        } else {
            if (!field.value.trim()) {
                field.focus();
                throw new Error('⚠️ Completa todos los campos obligatorios.');
            }
        }
    }

    // Validación específica de teléfono
    const paisCodigo = form.elements['pais_codigo'].value;
    const telefono = form.elements['telefono'].value.trim();

    if (!validatePhoneFormat(telefono, paisCodigo)) {
        throw new Error('⚠️ El formato del número de teléfono no es válido para el país seleccionado.');
    }

    // Validación de tamaño de archivos
    const fileInputs = form.querySelectorAll('input[type="file"][data-max-size]');
    for (const input of fileInputs) {
        if (input.files.length > 0) {
            const file = input.files[0];
            const maxSize = parseInt(input.getAttribute('data-max-size'));
            if (file.size > maxSize) {
                const maxSizeMB = Math.round(maxSize / 1024 / 1024);
                throw new Error(`⚠️ El archivo ${input.name} excede el tamaño máximo de ${maxSizeMB}MB.`);
            }
        }
    }

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

    const response = await fetch(getApiBaseUrl(), {
        method: 'POST',
        body: formData,
        credentials: 'include',
        headers: {
            'Accept': 'application/json'
        }
    });

    const result = await response.json();

    if (!response.ok || !result.success) {
        const error = new Error(result.message || `Error del servidor (${response.status})`);
        error.serverError = true;
        throw error;
    }

    return result;
}

function showFormLoadingState(loading, messageDiv) {
    const submitBtn = document.querySelector('.submit-btn');
    const btnText = submitBtn?.querySelector('span');
    
    if (loading) {
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.setAttribute('aria-disabled', 'true');
            if (btnText) btnText.textContent = 'Enviando...';
        }
        
        messageDiv.innerHTML = `
            <div style="color: #0088B9; text-align: center; padding: 1rem;">
                <div style="display: inline-block; width: 20px; height: 20px; border: 2px solid #00B4D8; border-top: 2px solid transparent; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 0.5rem;"></div>
                Procesando tu postulación...
            </div>
        `;
    } else {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.setAttribute('aria-disabled', 'false');
            if (btnText) btnText.textContent = 'Enviar Postulación';
        }
    }
}

function handleFormSubmissionSuccess(form, messageDiv) {
    messageDiv.innerHTML = `
        <div style="color: #28a745; text-align: center; padding: 1rem; background: #d4edda; border-radius: 6px; margin: 1rem 0;">
            ✅ <strong>¡Postulación enviada correctamente!</strong><br>
            <small>Gracias por tu interés. Te contactaremos pronto.</small>
        </div>
    `;
    
    form.reset();
    clearFormValidations();
    messageDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function handleFormSubmissionError(error, messageDiv) {
    console.error('❌ Error en envío del formulario:', error);
    
    let errorMessage = '❌ Error de conexión con el servidor. ';
    let errorClass = 'error-connection';
    
    if (error.message.includes('⚠️')) {
        errorMessage = error.message;
        errorClass = 'error-validation';
    } else if (error.serverError) {
        if (error.message.includes('ya aplicó anteriormente')) {
            errorMessage = '⚠️ Ya existe una aplicación con este email. Cada persona solo puede aplicar una vez.';
            errorClass = 'error-duplicate';
        } else {
            errorMessage = `❌ ${error.message}`;
            errorClass = 'error-server';
        }
    } else {
        errorMessage += 'Verifica tu conexión e inténtalo de nuevo.';
    }
    
    messageDiv.innerHTML = `
        <div class="${errorClass}" style="color: #dc3545; text-align: center; padding: 1rem; background: #f8d7da; border-radius: 6px; margin: 1rem 0;">
            ${errorMessage}
            ${!error.message.includes('⚠️') ? '<br><small>Si el problema persiste, contacta al administrador.</small>' : ''}
        </div>
    `;
}

function clearFormValidations() {
    // Limpiar validaciones de teléfono
    const phoneFormat = document.getElementById('phoneFormat');
    if (phoneFormat) {
        phoneFormat.textContent = '';
        phoneFormat.className = 'phone-format';
    }
    
    // Rehabilitar checkboxes
    const puestosAdicionales = document.querySelectorAll('input[name="puesto_adicional"]');
    puestosAdicionales.forEach(checkbox => {
        checkbox.disabled = false;
        checkbox.closest('label').style.opacity = '1';
    });
}

// =================== VALIDACIONES EN TIEMPO REAL ===================
function setupRealTimeValidation() {
    // Validación de archivos
    const fileInputs = document.querySelectorAll('input[type="file"][data-max-size]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            const maxSize = parseInt(e.target.getAttribute('data-max-size'));
            const messageDiv = document.getElementById('message');

            if (file && file.size > maxSize) {
                const maxSizeMB = Math.round(maxSize / 1024 / 1024);
                messageDiv.innerHTML = `
                    <div style="color: #dc3545; text-align: center; padding: 1rem; background: #f8d7da; border-radius: 6px; margin: 1rem 0;">
                        ⚠️ El archivo "${file.name}" excede el tamaño máximo de ${maxSizeMB}MB.
                    </div>
                `;
                e.target.value = '';
            } else if (messageDiv.textContent.includes('excede el tamaño')) {
                messageDiv.textContent = '';
            }
        });
    });

    // Configurar validación de teléfono en tiempo real
    const paisCodigo = document.getElementById('pais_codigo');
    const telefono = document.getElementById('telefono');
    const phoneFormat = document.getElementById('phoneFormat');

    if (paisCodigo && telefono && phoneFormat) {
        // Mostrar formato cuando se selecciona un país
        paisCodigo.addEventListener('change', function() {
            const countryCode = this.value;
            if (countryCode) {
                phoneFormat.textContent = `Formato esperado: ${getPhoneFormat(countryCode)}`;
                phoneFormat.className = 'phone-format';
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
    }

    // Configurar interacción entre puesto principal y adicionales
    const puestoPrincipal = document.getElementById('puesto');
    const puestosAdicionales = document.querySelectorAll('input[name="puesto_adicional"]');

    if (puestoPrincipal && puestosAdicionales.length > 0) {
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
    }
}

// =================== INICIALIZACIÓN ===================
function initializeApp() {
    if (isAppInitialized) return;
    
    try {
        console.log('🚀 Inicializando WorkWave Coast App...');
        
        // Cargar países
        loadCountryOptions();
        
        // Configurar validaciones en tiempo real
        setupRealTimeValidation();
        
        // Configurar envío de formulario
        const form = document.getElementById('applicationForm');
        const messageDiv = document.getElementById('message');
        
        if (form && messageDiv) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                showFormLoadingState(true, messageDiv);
                
                try {
                    await retryWithBackoff(
                        () => submitForm(form, messageDiv),
                        'envío del formulario'
                    );
                    handleFormSubmissionSuccess(form, messageDiv);
                } catch (error) {
                    handleFormSubmissionError(error, messageDiv);
                } finally {
                    showFormLoadingState(false, messageDiv);
                }
            });
        }
        
        isAppInitialized = true;
        console.log('✅ WorkWave Coast App inicializada correctamente');
        
    } catch (error) {
        console.error('❌ Error inicializando la aplicación:', error);
    }
}

// Agregar estilos CSS para animaciones de carga
const loadingStyles = document.createElement('style');
loadingStyles.textContent = `
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .phone-format {
        color: #666;
        font-size: 0.8rem;
        margin-top: 0.25rem;
        display: block;
    }
    
    .phone-success {
        color: #28a745;
    }
    
    .phone-error {
        color: #dc3545;
    }
`;
document.head.appendChild(loadingStyles);

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}
