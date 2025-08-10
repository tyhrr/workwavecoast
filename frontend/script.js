// WorkWave Coast - Frontend v2.0 - ESTRUCTURA CORREGIDA
// Compatible con backend Flask, MongoDB Atlas y Cloudinary
// Sistema optimizado con retry automático y manejo de errores

// =================== SISTEMA DE INICIALIZACIÓN ===================
class WorkWaveApp {
    constructor() {
        this.isInitialized = false;
        this.retryConfig = {
            maxRetries: 3,
            baseDelay: 1000,
            maxDelay: 5000
        };
        this.eventListeners = new Map(); // Prevenir duplicados

        // Detectar si el documento ya está listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            // DOM ya está listo
            this.init();
        }
    }

    async init() {
        if (this.isInitialized) return; // Prevenir inicialización múltiple

        try {
            console.log('🚀 Inicializando WorkWave Coast App...');

            // Cargar recursos críticos
            await this.loadCriticalResources();

            // Configurar funcionalidades principales
            this.setupCountrySelector();
            this.setupFormValidation();
            this.setupFileValidation();
            this.setupFormSubmission();
            this.setupAccessibilityFeatures();

            // Optimizaciones de rendimiento
            this.setupPerformanceOptimizations();

            this.isInitialized = true;
            console.log('✅ WorkWave Coast App inicializada correctamente');

        } catch (error) {
            console.error('❌ Error inicializando la aplicación:', error);
            this.handleInitializationError(error);
        }
    }

    async loadCriticalResources() {
        // Verificar disponibilidad de libphonenumber
        if (typeof libphonenumber === 'undefined') {
            console.warn('⚠️ libphonenumber no está disponible, usando validación básica');
        }
    }

    handleInitializationError(error) {
        const messageDiv = document.getElementById('message');
        if (messageDiv) {
            messageDiv.innerHTML = `
                <div style="color: #dc3545; text-align: center; padding: 1rem; background: #f8d7da; border-radius: 6px; margin: 1rem 0;">
                    ⚠️ Error cargando la aplicación.
                    <button onclick="location.reload()" style="margin-left: 0.5rem; padding: 0.3rem 0.8rem; background: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer;">
                        Recargar
                    </button>
                </div>
            `;
        }
    }

    // =================== CONFIGURACIÓN DE FUNCIONALIDADES ===================

    setupCountrySelector() {
        this.loadCountryOptions();
    }

    setupFormValidation() {
        this.addRealTimeValidation();
        this.addCharacterCounter();
    }

    setupFileValidation() {
        this.setupFileInputValidation();
    }

    setupFormSubmission() {
        this.setupFormSubmissionHandler();
    }

    setupAccessibilityFeatures() {
        this.enhanceFormAccessibility();
    }

    setupPerformanceOptimizations() {
        this.setupLazyLoading();
        this.setupResourcePrefetch();
        this.setupEventOptimization();
    }

    // =================== RETRY SYSTEM ===================

    async retryWithBackoff(fn, context = 'operación') {
        let lastError;

        for (let attempt = 0; attempt <= this.retryConfig.maxRetries; attempt++) {
            try {
                return await fn();
            } catch (error) {
                lastError = error;

                if (attempt === this.retryConfig.maxRetries) {
                    console.error(`❌ ${context} falló después de ${this.retryConfig.maxRetries} intentos:`, error);
                    break;
                }

                const delay = Math.min(
                    this.retryConfig.baseDelay * Math.pow(2, attempt),
                    this.retryConfig.maxDelay
                );

                console.warn(`⚠️ ${context} falló (intento ${attempt + 1}), reintentando en ${delay}ms...`);
                await this.sleep(delay);
            }
        }

        throw lastError;
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // =================== CARGA DE PAÍSES ===================

    loadCountryOptions() {
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

            // Códigos de respaldo por si libphonenumber no funciona
            const fallbackCodes = {
                'HR': '+385', 'ES': '+34', 'AR': '+54', 'MX': '+52', 'CO': '+57',
                'CL': '+56', 'PE': '+51', 'VE': '+58', 'UY': '+598', 'PY': '+595',
                'BO': '+591', 'EC': '+593', 'IT': '+39', 'FR': '+33', 'DE': '+49',
                'GB': '+44', 'US': '+1', 'BR': '+55', 'PT': '+351', 'NL': '+31',
                'BE': '+32', 'CH': '+41', 'AT': '+43', 'DK': '+45', 'SE': '+46',
                'NO': '+47', 'FI': '+358', 'PL': '+48', 'CZ': '+420', 'SK': '+421',
                'SI': '+386', 'HU': '+36', 'RO': '+40', 'BG': '+359', 'GR': '+30', 'TR': '+90'
            };

            // Intentar usar libphonenumber para obtener códigos de país
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
                        // Si libphonenumber falla para un país específico, usar fallback
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
            this.loadFallbackCountries(select);
        }
    }

    loadFallbackCountries(select) {
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

    // =================== API Y CONFIGURACIÓN ===================

    getApiBaseUrl() {
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

    // =================== VALIDACIÓN DE TELÉFONO ===================

    validatePhoneFormat(phone, countryCode) {
        const cleanPhone = phone.replace(/[\s\-\(\)]/g, '');

        try {
            if (typeof libphonenumber !== 'undefined' && libphonenumber.parsePhoneNumber) {
                const isoCode = this.getISOFromCallingCode(countryCode);
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

    getISOFromCallingCode(callingCode) {
        const mapping = {
            '+385': 'HR', '+34': 'ES', '+54': 'AR', '+52': 'MX', '+57': 'CO',
            '+56': 'CL', '+51': 'PE', '+58': 'VE', '+598': 'UY', '+595': 'PY',
            '+591': 'BO', '+593': 'EC', '+39': 'IT', '+33': 'FR', '+49': 'DE',
            '+44': 'GB', '+1': 'US', '+55': 'BR', '+351': 'PT'
        };
        return mapping[callingCode];
    }

    // =================== ENVÍO DE FORMULARIO CON RETRY ===================

    setupFormSubmissionHandler() {
        const form = document.getElementById('applicationForm');
        const messageDiv = document.getElementById('message');

        if (!form || !messageDiv) {
            console.warn('⚠️ Formulario o mensaje div no encontrado');
            return;
        }

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            this.showFormLoadingState(true, messageDiv);

            try {
                await this.retryWithBackoff(
                    () => this.submitFormData(form, messageDiv),
                    'envío del formulario'
                );
            } catch (error) {
                this.handleFormSubmissionError(error, messageDiv);
            } finally {
                this.showFormLoadingState(false, messageDiv);
            }
        });
    }

    async submitFormData(form, messageDiv) {
        // Validar campos requeridos
        const validationResult = this.validateRequiredFields(form);
        if (!validationResult.valid) {
            const error = new Error(validationResult.message);
            error.isValidationError = true;
            throw error;
        }

        // Validar teléfono
        const paisCodigo = form.elements['pais_codigo'].value;
        const telefono = form.elements['telefono'].value.trim();

        if (!this.validatePhoneFormat(telefono, paisCodigo)) {
            const error = new Error('⚠️ El formato del número de teléfono no es válido para el país seleccionado.');
            error.isValidationError = true;
            throw error;
        }

        // Validar archivos
        const fileValidation = this.validateFileInputs(form);
        if (!fileValidation.valid) {
            const error = new Error(fileValidation.message);
            error.isValidationError = true;
            throw error;
        }

        // Preparar FormData
        const formData = new FormData();

        // Agregar campos del formulario
        const formElements = form.elements;
        for (let i = 0; i < formElements.length; i++) {
            const element = formElements[i];

            if (element.type === 'checkbox' && element.name === 'puesto_adicional') {
                if (element.checked) {
                    formData.append('puestos_adicionales', element.value);
                }
            } else if (element.type === 'file') {
                if (element.files.length > 0) {
                    formData.append(element.name, element.files[0]);
                }
            } else if (element.name && element.value) {
                formData.append(element.name, element.value);
            }
        }

        // Agregar código de país al teléfono
        formData.set('telefono', `${paisCodigo} ${telefono}`);

        // Enviar al servidor
        const response = await fetch(this.getApiBaseUrl(), {
            method: 'POST',
            body: formData,
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`Error del servidor: ${response.status} ${response.statusText}`);
        }

        const result = await response.json();

        if (!result.success) {
            const error = new Error(result.message || 'Error desconocido del servidor');
            error.serverError = true;
            throw error;
        }

        this.handleFormSubmissionSuccess(form, messageDiv);
        return result;
    }

    validateRequiredFields(form) {
        const requiredFields = ['nombre', 'apellido', 'nacionalidad', 'email', 'pais_codigo', 'telefono', 'puesto', 'ingles_nivel', 'experiencia', 'cv'];

        for (const field of requiredFields) {
            const el = form.elements[field];

            if (!el) {
                return { valid: false, message: `Campo ${field} no encontrado`, field };
            }

            if (el.type === 'file') {
                if (el.files.length === 0) {
                    el.focus();
                    return { valid: false, message: '⚠️ Adjunta tu CV en formato PDF.', field };
                }
            } else {
                if (!el.value.trim()) {
                    el.focus();
                    return { valid: false, message: '⚠️ Completa todos los campos obligatorios.', field };
                }
            }
        }

        return { valid: true };
    }

    validateFileInputs(form) {
        const fileInputs = form.querySelectorAll('input[type="file"][data-max-size]');

        for (const input of fileInputs) {
            if (input.files.length > 0) {
                const file = input.files[0];
                const maxSize = parseInt(input.getAttribute('data-max-size'));

                if (file.size > maxSize) {
                    const maxSizeMB = Math.round(maxSize / 1024 / 1024);
                    input.focus();
                    return {
                        valid: false,
                        message: `⚠️ El archivo ${input.name} excede el tamaño máximo de ${maxSizeMB}MB.`
                    };
                }
            }
        }

        return { valid: true };
    }

    handleFormSubmissionSuccess(form, messageDiv) {
        messageDiv.innerHTML = `
            <div style="color: #28a745; text-align: center; padding: 1rem; background: #d4edda; border-radius: 6px; margin: 1rem 0;">
                ✅ <strong>¡Postulación enviada correctamente!</strong><br>
                <small>Gracias por tu interés. Te contactaremos pronto.</small>
            </div>
        `;

        form.reset();
        this.clearFormValidations();
        messageDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    handleFormSubmissionError(error, messageDiv) {
        console.error('❌ Error en envío del formulario:', error);

        let errorMessage = '❌ Error de conexión con el servidor. ';
        let errorClass = 'error-connection';

        if (error.isValidationError) {
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
                ${!error.isValidationError ? '<br><small>Si el problema persiste, contacta al administrador.</small>' : ''}
            </div>
        `;
    }

    showFormLoadingState(loading, messageDiv) {
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

    clearFormValidations() {
        // Limpiar validaciones de teléfono
        const phoneFormat = document.getElementById('telefono-help');
        if (phoneFormat) {
            phoneFormat.textContent = 'Selecciona tu país y escribe tu número de teléfono';
            phoneFormat.className = 'phone-format';
        }

        // Rehabilitar checkboxes
        const puestosAdicionales = document.querySelectorAll('input[name="puesto_adicional"]');
        puestosAdicionales.forEach(checkbox => {
            checkbox.disabled = false;
            checkbox.closest('label').style.opacity = '1';
        });

        // Limpiar errores de validación
        document.querySelectorAll('.field-error').forEach(errorDiv => {
            errorDiv.textContent = '';
            errorDiv.style.display = 'none';
        });

        // Resetear estados de validación
        document.querySelectorAll('input, select, textarea').forEach(element => {
            element.setAttribute('aria-invalid', 'false');
            element.classList.remove('field-invalid', 'field-valid');
        });
    }

    // =================== VALIDACIÓN EN TIEMPO REAL ===================

    addRealTimeValidation() {
        const fields = [
            { id: 'nombre', type: 'text', required: true },
            { id: 'apellido', type: 'text', required: true },
            { id: 'nacionalidad', type: 'select', required: true },
            { id: 'email', type: 'email', required: true },
            { id: 'telefono', type: 'tel', required: true },
            { id: 'puesto', type: 'select', required: true },
            { id: 'ingles_nivel', type: 'select', required: true },
            { id: 'experiencia', type: 'textarea', required: true },
            { id: 'cv', type: 'file', required: true },
            { id: 'documentos', type: 'file', required: false }
        ];

        fields.forEach(field => {
            const element = document.getElementById(field.id);
            const errorDiv = document.getElementById(`${field.id}-error`);

            if (!element || !errorDiv) return;

            element.addEventListener('blur', () => this.validateField(field, element, errorDiv));

            if (field.type === 'email' || field.type === 'text') {
                element.addEventListener('input', this.debounce(() => {
                    this.validateField(field, element, errorDiv);
                }, 300));
            }

            if (field.type === 'file') {
                element.addEventListener('change', () => this.validateFile(field, element, errorDiv));
            }
        });

        // Validación especial para teléfono cuando cambia el país
        const countrySelect = document.getElementById('pais_codigo');
        const phoneInput = document.getElementById('telefono');
        const phoneErrorDiv = document.getElementById('telefono-error');

        if (countrySelect && phoneInput) {
            countrySelect.addEventListener('change', () => {
                if (phoneInput.value.trim()) {
                    setTimeout(() => {
                        const phoneField = { id: 'telefono', type: 'tel', required: true };
                        this.validateField(phoneField, phoneInput, phoneErrorDiv);
                    }, 100);
                }
            });
        }
    }

    validateField(field, element, errorDiv) {
        let isValid = true;
        let errorMessage = '';

        if (field.required && !element.value.trim()) {
            isValid = false;
            errorMessage = `${this.getFieldDisplayName(field.id)} es requerido`;
        } else if (element.value.trim()) {
            switch (field.type) {
                case 'email':
                    if (!this.isValidEmail(element.value)) {
                        isValid = false;
                        errorMessage = 'Formato de email inválido';
                    }
                    break;
                case 'tel':
                    if (field.id === 'telefono') {
                        const countrySelect = document.getElementById('pais_codigo');
                        const countryCode = countrySelect ? countrySelect.value : '';
                        if (countryCode && !this.validatePhoneFormat(element.value, countryCode)) {
                            isValid = false;
                            errorMessage = 'Formato de teléfono inválido para el país seleccionado';
                        } else if (!countryCode) {
                            isValid = false;
                            errorMessage = 'Selecciona primero el código de país';
                        }
                    }
                    break;
                case 'text':
                case 'textarea':
                    if (element.maxLength && element.value.length > element.maxLength) {
                        isValid = false;
                        errorMessage = `Máximo ${element.maxLength} caracteres`;
                    }
                    break;
            }
        }

        this.updateFieldValidationState(element, errorDiv, isValid, errorMessage);
        return isValid;
    }

    validateFile(field, element, errorDiv) {
        const file = element.files[0];
        let isValid = true;
        let errorMessage = '';

        if (field.required && !file) {
            isValid = false;
            errorMessage = `${this.getFieldDisplayName(field.id)} es requerido`;
        } else if (file) {
            const maxSize = parseInt(element.dataset.maxSize) || 5242880;
            if (file.size > maxSize) {
                isValid = false;
                const maxSizeMB = Math.round(maxSize / 1024 / 1024);
                errorMessage = `El archivo excede el tamaño máximo de ${maxSizeMB}MB`;
            }

            const acceptedTypes = element.accept.split(',').map(t => t.trim());
            const fileType = file.type;
            const fileExtension = '.' + file.name.split('.').pop().toLowerCase();

            if (!acceptedTypes.some(type =>
                fileType.includes(type.replace('*', '')) ||
                type === fileExtension
            )) {
                isValid = false;
                errorMessage = 'Tipo de archivo no permitido';
            }
        }

        this.updateFieldValidationState(element, errorDiv, isValid, errorMessage);
        return isValid;
    }

    updateFieldValidationState(element, errorDiv, isValid, errorMessage) {
        element.setAttribute('aria-invalid', !isValid);

        if (errorDiv) {
            errorDiv.textContent = errorMessage;
            errorDiv.style.display = errorMessage ? 'block' : 'none';
        }

        element.classList.toggle('field-invalid', !isValid);
        element.classList.toggle('field-valid', isValid && element.value.trim());
    }

    addCharacterCounter() {
        const textarea = document.getElementById('experiencia');
        const counter = document.getElementById('experiencia-count');

        if (!textarea || !counter) return;

        const updateCounter = () => {
            const current = textarea.value.length;
            const max = textarea.maxLength;
            const remaining = max - current;

            counter.textContent = `${current} / ${max} caracteres`;

            counter.className = 'char-counter';
            if (remaining < 50) {
                counter.classList.add('error');
            } else if (remaining < 100) {
                counter.classList.add('warning');
            }
        };

        textarea.addEventListener('input', updateCounter);
        updateCounter();
    }

    setupFileInputValidation() {
        const fileInputs = document.querySelectorAll('input[type="file"][data-max-size]');

        fileInputs.forEach(input => {
            input.addEventListener('change', (e) => {
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
    }

    enhanceFormAccessibility() {
        const phoneInput = document.getElementById('telefono');
        const phoneHelp = document.getElementById('telefono-help');
        const countrySelect = document.getElementById('pais_codigo');

        if (phoneInput && phoneHelp && countrySelect) {
            const updatePhoneHelp = () => {
                const selectedCountry = countrySelect.value;
                if (selectedCountry) {
                    const countryName = countrySelect.options[countrySelect.selectedIndex].text;
                    phoneHelp.textContent = `Escribe tu número de teléfono para ${countryName}`;
                } else {
                    phoneHelp.textContent = 'Selecciona tu país y escribe tu número de teléfono';
                }
            };

            countrySelect.addEventListener('change', updatePhoneHelp);
        }
    }

    // =================== OPTIMIZACIONES DE RENDIMIENTO ===================

    setupLazyLoading() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.removeAttribute('data-src');
                            observer.unobserve(img);
                        }
                    }
                });
            });

            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
    }

    setupResourcePrefetch() {
        const apiUrl = this.getApiBaseUrl();
        if (apiUrl) {
            const link = document.createElement('link');
            link.rel = 'dns-prefetch';
            link.href = new URL(apiUrl).origin;
            document.head.appendChild(link);
        }
    }

    setupEventOptimization() {
        this.debounceMap = new Map();
    }

    debounce(func, wait, immediate = false) {
        return (...args) => {
            const later = () => {
                if (!immediate) func(...args);
            };
            const callNow = immediate && !this.debounceMap.has(func);
            clearTimeout(this.debounceMap.get(func));
            this.debounceMap.set(func, setTimeout(later, wait));
            if (callNow) func(...args);
        };
    }

    // =================== UTILIDADES ===================

    getFieldDisplayName(fieldId) {
        const displayNames = {
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'nacionalidad': 'Nacionalidad',
            'email': 'Email',
            'telefono': 'Teléfono',
            'puesto': 'Puesto',
            'ingles_nivel': 'Nivel de inglés',
            'experiencia': 'Experiencia laboral',
            'cv': 'Currículum Vitae',
            'documentos': 'Documentos adicionales'
        };
        return displayNames[fieldId] || fieldId;
    }

    isValidEmail(email) {
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return emailRegex.test(email);
    }
}

// =================== INICIALIZACIÓN ===================

// Crear instancia global de la aplicación
const workWaveApp = new WorkWaveApp();

// Agregar estilos CSS para animaciones de carga
const loadingStyles = document.createElement('style');
loadingStyles.textContent = `
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .field-valid {
        border-color: #28a745 !important;
        box-shadow: 0 0 0 2px rgba(40, 167, 69, 0.15) !important;
    }

    .field-invalid {
        border-color: #dc3545 !important;
        box-shadow: 0 0 0 2px rgba(220, 53, 69, 0.15) !important;
    }
`;
document.head.appendChild(loadingStyles);

// Exports para compatibilidad (si se necesita)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WorkWaveApp;
}
