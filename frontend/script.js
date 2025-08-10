// WorkWave Coast - Frontend
// Compatible con backend Flask, MongoDB Atlas y Cloudinary
// Usa fetch() y FormData para enviar datos y archivos

// Cargar países automáticamente al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    loadCountryOptions();
});

// Función para cargar opciones de países dinámicamente
function loadCountryOptions() {
    const select = document.getElementById('pais_codigo');

    try {
        // Obtener lista de países usando libphonenumber
        const countries = [];

        // Lista de países más comunes con sus códigos ISO
        const commonCountries = [
            'HR', 'ES', 'AR', 'MX', 'CO', 'CL', 'PE', 'VE', 'UY', 'PY', 'BO', 'EC',
            'IT', 'FR', 'DE', 'GB', 'US', 'BR', 'PT', 'NL', 'BE', 'CH', 'AT', 'DK',
            'SE', 'NO', 'FI', 'PL', 'CZ', 'SK', 'SI', 'HU', 'RO', 'BG', 'GR', 'TR',
            'RU', 'UA', 'RS', 'ME', 'BA', 'MK', 'XK', 'AL', 'CA', 'AU', 'NZ', 'ZA',
            'EG', 'MA', 'IN', 'CN', 'JP', 'KR', 'TH', 'VN', 'ID', 'MY', 'SG', 'PH',
            'PK', 'BD', 'LK', 'NP', 'IR', 'IQ', 'KW', 'SA', 'AE', 'QA', 'BH', 'OM',
            'JO', 'LB', 'IL', 'PS', 'SY', 'TN', 'DZ', 'LY', 'NG', 'KE', 'GH', 'ET',
            'UG', 'TZ', 'RW', 'BI', 'CD', 'CG', 'CM', 'TD', 'CF', 'ZM', 'ZW', 'BW',
            'NA', 'SZ', 'LS', 'MW', 'MZ', 'MG', 'MU', 'SC', 'RE', 'KM', 'GP', 'MQ',
            'GF', 'PM', 'NC', 'PF', 'CK', 'WS', 'TO', 'VU', 'FJ', 'PG', 'SB', 'WF',
            'AS', 'TL', 'BN', 'KH', 'LA', 'MM', 'MN', 'KG', 'TJ', 'TM', 'UZ', 'KZ',
            'AM', 'AZ', 'GE', 'BY', 'MD', 'EE', 'LV', 'LT', 'IS', 'IE', 'LU', 'MC',
            'SM', 'VA', 'AD', 'GI', 'MT', 'CY', 'GL', 'FO', 'FK', 'GT', 'SV', 'HN',
            'NI', 'CR', 'PA', 'HT', 'CU', 'JM', 'DO', 'PR', 'TT', 'BB', 'AG', 'VG',
            'VI', 'KY', 'BM', 'GD', 'TC', 'MS', 'MP', 'GU', 'SX', 'LC', 'DM', 'VC',
            'KN', 'BQ', 'BL', 'MF', 'YT', 'GY', 'SR', 'CW'
        ];

        // Mapeo de códigos de país a nombres en español
        const countryNames = {
            'HR': 'Croacia', 'ES': 'España', 'AR': 'Argentina', 'MX': 'México', 'CO': 'Colombia',
            'CL': 'Chile', 'PE': 'Perú', 'VE': 'Venezuela', 'UY': 'Uruguay', 'PY': 'Paraguay',
            'BO': 'Bolivia', 'EC': 'Ecuador', 'IT': 'Italia', 'FR': 'Francia', 'DE': 'Alemania',
            'GB': 'Reino Unido', 'US': 'Estados Unidos', 'BR': 'Brasil', 'PT': 'Portugal',
            'NL': 'Países Bajos', 'BE': 'Bélgica', 'CH': 'Suiza', 'AT': 'Austria', 'DK': 'Dinamarca',
            'SE': 'Suecia', 'NO': 'Noruega', 'FI': 'Finlandia', 'PL': 'Polonia', 'CZ': 'República Checa',
            'SK': 'Eslovaquia', 'SI': 'Eslovenia', 'HU': 'Hungría', 'RO': 'Rumania', 'BG': 'Bulgaria',
            'GR': 'Grecia', 'TR': 'Turquía', 'RU': 'Rusia', 'UA': 'Ucrania', 'RS': 'Serbia',
            'ME': 'Montenegro', 'BA': 'Bosnia y Herzegovina', 'MK': 'Macedonia del Norte', 'XK': 'Kosovo',
            'AL': 'Albania', 'CA': 'Canadá', 'AU': 'Australia', 'NZ': 'Nueva Zelanda', 'ZA': 'Sudáfrica',
            'EG': 'Egipto', 'MA': 'Marruecos', 'IN': 'India', 'CN': 'China', 'JP': 'Japón',
            'KR': 'Corea del Sur', 'TH': 'Tailandia', 'VN': 'Vietnam', 'ID': 'Indonesia', 'MY': 'Malasia',
            'SG': 'Singapur', 'PH': 'Filipinas', 'PK': 'Pakistán', 'BD': 'Bangladesh', 'LK': 'Sri Lanka',
            'NP': 'Nepal', 'IR': 'Irán', 'IQ': 'Irak', 'KW': 'Kuwait', 'SA': 'Arabia Saudí',
            'AE': 'Emiratos Árabes Unidos', 'QA': 'Qatar', 'BH': 'Baréin', 'OM': 'Omán',
            'JO': 'Jordania', 'LB': 'Líbano', 'IL': 'Israel', 'PS': 'Palestina', 'SY': 'Siria',
            'TN': 'Túnez', 'DZ': 'Argelia', 'LY': 'Libia', 'NG': 'Nigeria', 'KE': 'Kenia',
            'GH': 'Ghana', 'ET': 'Etiopía', 'UG': 'Uganda', 'TZ': 'Tanzania', 'RW': 'Ruanda',
            'BI': 'Burundi', 'CD': 'República Democrática del Congo', 'CG': 'República del Congo',
            'CM': 'Camerún', 'TD': 'Chad', 'CF': 'República Centroafricana', 'ZM': 'Zambia',
            'ZW': 'Zimbabue', 'BW': 'Botsuana', 'NA': 'Namibia', 'SZ': 'Esuatini', 'LS': 'Lesoto',
            'MW': 'Malaui', 'MZ': 'Mozambique', 'MG': 'Madagascar', 'MU': 'Mauricio',
            'SC': 'Seychelles', 'RE': 'Reunión', 'KM': 'Comoras', 'GT': 'Guatemala',
            'SV': 'El Salvador', 'HN': 'Honduras', 'NI': 'Nicaragua', 'CR': 'Costa Rica',
            'PA': 'Panamá', 'HT': 'Haití', 'CU': 'Cuba', 'JM': 'Jamaica', 'DO': 'República Dominicana',
            'PR': 'Puerto Rico', 'TT': 'Trinidad y Tobago', 'BB': 'Barbados', 'AG': 'Antigua y Barbuda',
            'VG': 'Islas Vírgenes Británicas', 'VI': 'Islas Vírgenes de EE.UU.', 'KY': 'Islas Caimán',
            'BM': 'Bermudas', 'GD': 'Granada', 'TC': 'Islas Turcas y Caicos', 'MS': 'Montserrat',
            'MP': 'Islas Marianas del Norte', 'GU': 'Guam', 'AS': 'Samoa Americana', 'TL': 'Timor Oriental',
            'BN': 'Brunéi', 'KH': 'Camboya', 'LA': 'Laos', 'MM': 'Myanmar', 'MN': 'Mongolia',
            'KG': 'Kirguistán', 'TJ': 'Tayikistán', 'TM': 'Turkmenistán', 'UZ': 'Uzbekistán',
            'KZ': 'Kazajistán', 'AM': 'Armenia', 'AZ': 'Azerbaiyán', 'GE': 'Georgia',
            'BY': 'Bielorrusia', 'MD': 'Moldavia', 'EE': 'Estonia', 'LV': 'Letonia',
            'LT': 'Lituania', 'IS': 'Islandia', 'IE': 'Irlanda', 'LU': 'Luxemburgo',
            'MC': 'Mónaco', 'SM': 'San Marino', 'VA': 'Ciudad del Vaticano', 'AD': 'Andorra',
            'GI': 'Gibraltar', 'MT': 'Malta', 'CY': 'Chipre', 'GL': 'Groenlandia',
            'FO': 'Islas Feroe', 'FK': 'Islas Malvinas', 'GP': 'Guadalupe', 'MQ': 'Martinica',
            'GF': 'Guayana Francesa', 'PM': 'San Pedro y Miquelón', 'NC': 'Nueva Caledonia',
            'PF': 'Polinesia Francesa', 'CK': 'Islas Cook', 'WS': 'Samoa', 'TO': 'Tonga',
            'VU': 'Vanuatu', 'FJ': 'Fiyi', 'PG': 'Papúa Nueva Guinea', 'SB': 'Islas Salomón',
            'WF': 'Wallis y Futuna', 'SX': 'Sint Maarten', 'LC': 'Santa Lucía', 'DM': 'Dominica',
            'VC': 'San Vicente y las Granadinas', 'KN': 'San Cristóbal y Nieves', 'BQ': 'Bonaire',
            'BL': 'San Bartolomé', 'MF': 'San Martín', 'YT': 'Mayotte', 'GY': 'Guyana',
            'SR': 'Surinam', 'CW': 'Curazao'
        };

        // Mapeo de códigos de país a banderas
        const countryFlags = {
            'HR': '🇭🇷', 'ES': '🇪🇸', 'AR': '🇦🇷', 'MX': '🇲🇽', 'CO': '🇨🇴', 'CL': '🇨🇱',
            'PE': '🇵🇪', 'VE': '🇻🇪', 'UY': '🇺🇾', 'PY': '🇵🇾', 'BO': '🇧🇴', 'EC': '🇪🇨',
            'IT': '🇮🇹', 'FR': '🇫🇷', 'DE': '🇩🇪', 'GB': '🇬🇧', 'US': '🇺🇸', 'BR': '🇧🇷',
            'PT': '🇵🇹', 'NL': '🇳🇱', 'BE': '🇧🇪', 'CH': '🇨🇭', 'AT': '🇦🇹', 'DK': '🇩🇰',
            'SE': '🇸🇪', 'NO': '🇳🇴', 'FI': '🇫🇮', 'PL': '🇵🇱', 'CZ': '🇨🇿', 'SK': '🇸🇰',
            'SI': '🇸🇮', 'HU': '🇭🇺', 'RO': '🇷🇴', 'BG': '🇧🇬', 'GR': '🇬🇷', 'TR': '🇹🇷',
            'RU': '🇷🇺', 'UA': '🇺🇦', 'RS': '🇷🇸', 'ME': '🇲🇪', 'BA': '🇧🇦', 'MK': '🇲🇰',
            'XK': '🇽🇰', 'AL': '🇦🇱', 'CA': '🇨🇦', 'AU': '🇦🇺', 'NZ': '🇳🇿', 'ZA': '🇿🇦',
            'EG': '🇪🇬', 'MA': '🇲🇦', 'IN': '🇮🇳', 'CN': '🇨🇳', 'JP': '🇯🇵', 'KR': '🇰🇷',
            'TH': '🇹🇭', 'VN': '🇻🇳', 'ID': '🇮🇩', 'MY': '🇲🇾', 'SG': '🇸🇬', 'PH': '🇵🇭',
            'PK': '🇵🇰', 'BD': '🇧🇩', 'LK': '🇱🇰', 'NP': '🇳🇵', 'IR': '🇮🇷', 'IQ': '🇮🇶',
            'KW': '🇰🇼', 'SA': '🇸🇦', 'AE': '🇦🇪', 'QA': '🇶🇦', 'BH': '🇧🇭', 'OM': '🇴🇲',
            'JO': '🇯🇴', 'LB': '🇱🇧', 'IL': '🇮🇱', 'PS': '🇵🇸', 'SY': '🇸🇾', 'TN': '🇹🇳',
            'DZ': '🇩🇿', 'LY': '🇱🇾', 'NG': '🇳🇬', 'KE': '🇰🇪', 'GH': '🇬🇭', 'ET': '🇪🇹',
            'UG': '🇺🇬', 'TZ': '🇹🇿', 'RW': '🇷🇼', 'BI': '🇧🇮', 'CD': '🇨🇩', 'CG': '🇨🇬',
            'CM': '🇨🇲', 'TD': '🇹🇩', 'CF': '🇨🇫', 'ZM': '🇿🇲', 'ZW': '🇿🇼', 'BW': '🇧🇼',
            'NA': '🇳🇦', 'SZ': '🇸🇿', 'LS': '🇱🇸', 'MW': '🇲🇼', 'MZ': '🇲🇿', 'MG': '🇲🇬',
            'MU': '🇲🇺', 'SC': '🇸🇨', 'RE': '🇷🇪', 'KM': '🇰🇲', 'GT': '🇬🇹', 'SV': '🇸🇻',
            'HN': '🇭🇳', 'NI': '🇳🇮', 'CR': '🇨🇷', 'PA': '🇵🇦', 'HT': '🇭🇹', 'CU': '🇨🇺',
            'JM': '🇯🇲', 'DO': '🇩🇴', 'PR': '🇵🇷', 'TT': '🇹🇹', 'BB': '🇧🇧', 'AG': '🇦🇬',
            'VG': '🇻🇬', 'VI': '🇻🇮', 'KY': '🇰🇾', 'BM': '🇧🇲', 'GD': '🇬🇩', 'TC': '🇹🇨',
            'MS': '🇲🇸', 'MP': '🇲🇵', 'GU': '🇬🇺', 'AS': '🇦🇸', 'TL': '🇹🇱', 'BN': '🇧🇳',
            'KH': '🇰🇭', 'LA': '🇱🇦', 'MM': '🇲🇲', 'MN': '🇲🇳', 'KG': '🇰🇬', 'TJ': '🇹🇯',
            'TM': '🇹🇲', 'UZ': '🇺🇿', 'KZ': '🇰🇿', 'AM': '🇦🇲', 'AZ': '🇦🇿', 'GE': '🇬🇪',
            'BY': '🇧🇾', 'MD': '🇲🇩', 'EE': '🇪🇪', 'LV': '🇱🇻', 'LT': '🇱🇹', 'IS': '🇮🇸',
            'IE': '🇮🇪', 'LU': '🇱🇺', 'MC': '🇲🇨', 'SM': '🇸🇲', 'VA': '🇻🇦', 'AD': '🇦🇩',
            'GI': '🇬🇮', 'MT': '🇲🇹', 'CY': '🇨🇾', 'GL': '🇬🇱', 'FO': '🇫🇴', 'FK': '🇫🇰',
            'GP': '🇬🇵', 'MQ': '🇲🇶', 'GF': '🇬🇫', 'PM': '🇵🇲', 'NC': '🇳🇨', 'PF': '🇵🇫',
            'CK': '🇨🇰', 'WS': '🇼🇸', 'TO': '🇹🇴', 'VU': '🇻🇺', 'FJ': '🇫🇯', 'PG': '🇵🇬',
            'SB': '🇸🇧', 'WF': '🇼🇫', 'SX': '🇸🇽', 'LC': '🇱🇨', 'DM': '🇩🇲', 'VC': '🇻🇨',
            'KN': '🇰🇳', 'BQ': '🇧🇶', 'BL': '🇧🇱', 'MF': '🇲🇫', 'YT': '🇾🇹', 'GY': '🇬🇾',
            'SR': '🇸🇷', 'CW': '🇨🇼'
        };

        // Generar opciones para países comunes
        commonCountries.forEach(countryCode => {
            try {
                if (typeof libphonenumber !== 'undefined' && libphonenumber.getCountryCallingCode) {
                    const callingCode = libphonenumber.getCountryCallingCode(countryCode);
                    const flag = countryFlags[countryCode] || '🌍';
                    const name = countryNames[countryCode] || countryCode;

                    countries.push({
                        code: `+${callingCode}`,
                        name: name,
                        flag: flag,
                        iso: countryCode
                    });
                }
            } catch (error) {
                console.warn(`Error procesando país ${countryCode}:`, error);
            }
        });

        // Ordenar países alfabéticamente por nombre
        countries.sort((a, b) => a.name.localeCompare(b.name, 'es'));

        // Limpiar opciones existentes (excepto la primera)
        select.innerHTML = '<option value="">Selecciona país...</option>';

        // Agregar opciones de países
        countries.forEach(country => {
            const option = document.createElement('option');
            option.value = country.code;
            option.textContent = `${country.flag} ${country.code} (${country.name})`;
            select.appendChild(option);
        });

        console.log(`Cargados ${countries.length} países exitosamente`);

    } catch (error) {
        console.error('Error cargando países:', error);
        // Fallback: cargar algunos países básicos si libphonenumber falla
        loadFallbackCountries(select);
    }
}

// Función de respaldo si libphonenumber no está disponible
function loadFallbackCountries(select) {
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
        { code: '+44', name: 'Reino Unido', flag: '🇬🇧' }
    ];

    select.innerHTML = '<option value="">Selecciona país...</option>';

    fallbackCountries.forEach(country => {
        const option = document.createElement('option');
        option.value = country.code;
        option.textContent = `${country.flag} ${country.code} (${country.name})`;
        select.appendChild(option);
    });

    console.log('Cargados países de respaldo');
}

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
        '+1': 'XXX XXX XXXX (ej: 555 123 4567)', // Estados Unidos/Canadá
        '+55': 'XX XXXXX XXXX (ej: 11 99999 1234)', // Brasil
        '+351': 'XXX XXX XXX (ej: 910 123 456)', // Portugal
        '+31': 'XX XXX XXXX (ej: 06 1234 5678)', // Países Bajos
        '+32': 'XXX XX XX XX (ej: 478 12 34 56)', // Bélgica
        '+41': 'XX XXX XX XX (ej: 76 123 45 67)', // Suiza
        '+43': 'XXX XXXXXXX (ej: 664 1234567)', // Austria
        '+45': 'XX XX XX XX (ej: 12 34 56 78)', // Dinamarca
        '+46': 'XX XXX XX XX (ej: 70 123 45 67)', // Suecia
        '+47': 'XXX XX XXX (ej: 123 45 678)', // Noruega
        '+358': 'XX XXX XXXX (ej: 40 123 4567)', // Finlandia
        '+48': 'XXX XXX XXX (ej: 601 123 456)', // Polonia
        '+420': 'XXX XXX XXX (ej: 601 123 456)', // República Checa
        '+421': 'XXX XXX XXX (ej: 905 123 456)', // Eslovaquia
        '+386': 'XX XXX XXX (ej: 31 123 456)', // Eslovenia
        '+36': 'XX XXX XXXX (ej: 20 123 4567)', // Hungría
        '+40': 'XXX XXX XXXX (ej: 712 345 678)', // Rumania
        '+359': 'XX XXX XXXX (ej: 87 123 4567)', // Bulgaria
        '+30': 'XXX XXX XXXX (ej: 694 123 4567)', // Grecia
        '+90': 'XXX XXX XX XX (ej: 532 123 45 67)', // Turquía
        '+7': 'XXX XXX XX XX (ej: 912 345 67 89)', // Rusia/Kazajistán
        '+380': 'XX XXX XX XX (ej: 50 123 45 67)', // Ucrania
        '+381': 'XX XXX XXXX (ej: 63 123 4567)', // Serbia
        '+382': 'XX XXX XXX (ej: 67 123 456)', // Montenegro
        '+387': 'XX XXX XXX (ej: 61 123 456)', // Bosnia y Herzegovina
        '+389': 'XX XXX XXX (ej: 70 123 456)', // Macedonia del Norte
        '+383': 'XX XXX XXX (ej: 44 123 456)', // Kosovo
        '+355': 'XX XXX XXXX (ej: 69 123 4567)', // Albania
        '+61': 'XXX XXX XXX (ej: 412 345 678)', // Australia
        '+64': 'XX XXX XXXX (ej: 21 123 4567)', // Nueva Zelanda
        '+27': 'XX XXX XXXX (ej: 82 123 4567)', // Sudáfrica
        '+91': 'XXXXX XXXXX (ej: 98765 43210)', // India
        '+86': 'XXX XXXX XXXX (ej: 138 0013 8000)', // China
        '+81': 'XX XXXX XXXX (ej: 90 1234 5678)', // Japón
        '+82': 'XX XXXX XXXX (ej: 10 1234 5678)', // Corea del Sur
        '+354': 'XXX XXXX (ej: 581 2345)', // Islandia
        '+353': 'XX XXX XXXX (ej: 85 123 4567)', // Irlanda
        '+352': 'XXX XXX XXX (ej: 621 123 456)', // Luxemburgo
        '+356': 'XXXX XXXX (ej: 2123 4567)', // Malta
        '+357': 'XX XXX XXX (ej: 96 123 456)', // Chipre
        '+372': 'XXX XXXX (ej: 512 3456)', // Estonia
        '+371': 'XXXX XXXX (ej: 2123 4567)', // Letonia
        '+370': 'XXX XXXXX (ej: 612 34567)', // Lituania
        '+502': 'XXXX XXXX (ej: 5123 4567)', // Guatemala
        '+503': 'XXXX XXXX (ej: 7123 4567)', // El Salvador
        '+504': 'XXXX XXXX (ej: 9123 4567)', // Honduras
        '+505': 'XXXX XXXX (ej: 8123 4567)', // Nicaragua
        '+506': 'XXXX XXXX (ej: 8123 4567)', // Costa Rica
        '+507': 'XXXX XXXX (ej: 6123 4567)', // Panamá
        '+509': 'XXXX XXXX (ej: 3412 3456)', // Haití
        '+53': 'X XXX XXXX (ej: 5 123 4567)', // Cuba
        '+1-876': 'XXX XXXX (ej: 876 1234)', // Jamaica
        '+1-809': 'XXX XXXX (ej: 809 1234)', // República Dominicana
        '+212': 'XXX XXX XXX (ej: 612 345 678)', // Marruecos
        '+216': 'XX XXX XXX (ej: 20 123 456)', // Túnez
        '+213': 'XXX XX XX XX (ej: 551 23 45 67)', // Argelia
        '+20': 'XX XXXX XXXX (ej: 10 1234 5678)', // Egipto
        '+966': 'XX XXX XXXX (ej: 50 123 4567)', // Arabia Saudí
        '+971': 'XX XXX XXXX (ej: 50 123 4567)', // Emiratos Árabes Unidos
        '+234': 'XXX XXX XXXX (ej: 803 123 4567)', // Nigeria
        '+254': 'XXX XXX XXX (ej: 712 345 678)', // Kenia
        '+233': 'XXX XXX XXXX (ej: 244 123 456)', // Ghana
        '+66': 'XX XXX XXXX (ej: 81 123 4567)', // Tailandia
        '+84': 'XXX XXX XXXX (ej: 912 345 678)', // Vietnam
        '+60': 'XX XXXX XXXX (ej: 12 3456 7890)', // Malasia
        '+65': 'XXXX XXXX (ej: 9123 4567)', // Singapur
        '+63': 'XXX XXX XXXX (ej: 917 123 4567)', // Filipinas
        '+62': 'XXX XXXX XXXX (ej: 812 3456 7890)', // Indonesia
        '+92': 'XXX XXX XXXX (ej: 300 123 4567)', // Pakistán
        '+880': 'XXXX XXXXXX (ej: 1712 345678)', // Bangladesh
        '+94': 'XX XXX XXXX (ej: 71 123 4567)', // Sri Lanka
        '+977': 'XXX XXX XXXX (ej: 984 123 4567)' // Nepal
    };
    return formats[countryCode] || 'Formato según tu país';
}

// Función para validar formato de teléfono usando libphonenumber
function validatePhoneFormat(phone, countryCode) {
    // Remover espacios, guiones y paréntesis
    const cleanPhone = phone.replace(/[\s\-\(\)]/g, '');

    try {
        // Intentar usar libphonenumber para validación avanzada
        if (typeof libphonenumber !== 'undefined' && libphonenumber.parsePhoneNumber) {
            // Obtener código ISO del país desde el código de teléfono
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
        '+1': /^[0-9]{10}$/, // Estados Unidos/Canadá: 10 dígitos
        '+55': /^[0-9]{10,11}$/, // Brasil: 10-11 dígitos
        '+351': /^[0-9]{9}$/, // Portugal: 9 dígitos
        '+31': /^[0-9]{9}$/, // Países Bajos: 9 dígitos
        '+32': /^[0-9]{9}$/, // Bélgica: 9 dígitos
        '+41': /^[0-9]{9}$/, // Suiza: 9 dígitos
        '+43': /^[0-9]{10,11}$/, // Austria: 10-11 dígitos
        '+45': /^[0-9]{8}$/, // Dinamarca: 8 dígitos
        '+46': /^[0-9]{9}$/, // Suecia: 9 dígitos
        '+47': /^[0-9]{8}$/, // Noruega: 8 dígitos
        '+358': /^[0-9]{9}$/, // Finlandia: 9 dígitos
        '+48': /^[0-9]{9}$/, // Polonia: 9 dígitos
        '+420': /^[0-9]{9}$/, // República Checa: 9 dígitos
        '+421': /^[0-9]{9}$/, // Eslovaquia: 9 dígitos
        '+386': /^[0-9]{8}$/, // Eslovenia: 8 dígitos
        '+36': /^[0-9]{9}$/, // Hungría: 9 dígitos
        '+40': /^[0-9]{9}$/, // Rumania: 9 dígitos
        '+359': /^[0-9]{9}$/, // Bulgaria: 9 dígitos
        '+30': /^[0-9]{10}$/, // Grecia: 10 dígitos
        '+90': /^[0-9]{10}$/, // Turquía: 10 dígitos
        '+7': /^[0-9]{10}$/, // Rusia: 10 dígitos
        '+380': /^[0-9]{9}$/, // Ucrania: 9 dígitos
        '+381': /^[0-9]{8,9}$/, // Serbia: 8-9 dígitos
        '+382': /^[0-9]{8}$/, // Montenegro: 8 dígitos
        '+387': /^[0-9]{8}$/, // Bosnia y Herzegovina: 8 dígitos
        '+389': /^[0-9]{8}$/, // Macedonia del Norte: 8 dígitos
        '+383': /^[0-9]{8}$/, // Kosovo: 8 dígitos
        '+355': /^[0-9]{9}$/, // Albania: 9 dígitos
        '+61': /^[0-9]{9}$/, // Australia: 9 dígitos
        '+64': /^[0-9]{8,10}$/, // Nueva Zelanda: 8-10 dígitos
        '+27': /^[0-9]{9}$/, // Sudáfrica: 9 dígitos
        '+91': /^[0-9]{10}$/, // India: 10 dígitos
        '+86': /^[0-9]{11}$/, // China: 11 dígitos
        '+81': /^[0-9]{10,11}$/, // Japón: 10-11 dígitos
        '+82': /^[0-9]{10,11}$/, // Corea del Sur: 10-11 dígitos
        '+66': /^[0-9]{9}$/, // Tailandia: 9 dígitos
        '+84': /^[0-9]{9,10}$/, // Vietnam: 9-10 dígitos
        '+60': /^[0-9]{9,10}$/, // Malasia: 9-10 dígitos
        '+65': /^[0-9]{8}$/, // Singapur: 8 dígitos
        '+63': /^[0-9]{10}$/, // Filipinas: 10 dígitos
        '+62': /^[0-9]{9,12}$/, // Indonesia: 9-12 dígitos
        '+92': /^[0-9]{10}$/, // Pakistán: 10 dígitos
        '+880': /^[0-9]{10}$/, // Bangladesh: 10 dígitos
        '+94': /^[0-9]{9}$/, // Sri Lanka: 9 dígitos
        '+977': /^[0-9]{10}$/ // Nepal: 10 dígitos
    };

    const pattern = patterns[countryCode];
    return pattern ? pattern.test(cleanPhone) : cleanPhone.length >= 7 && cleanPhone.length <= 15;
}

// Función auxiliar para obtener código ISO desde código de llamada
function getISOFromCallingCode(callingCode) {
    const mapping = {
        '+385': 'HR', '+34': 'ES', '+54': 'AR', '+52': 'MX', '+57': 'CO',
        '+56': 'CL', '+51': 'PE', '+58': 'VE', '+598': 'UY', '+595': 'PY',
        '+591': 'BO', '+593': 'EC', '+39': 'IT', '+33': 'FR', '+49': 'DE',
        '+44': 'GB', '+1': 'US', '+55': 'BR', '+351': 'PT', '+31': 'NL',
        '+32': 'BE', '+41': 'CH', '+43': 'AT', '+45': 'DK', '+46': 'SE',
        '+47': 'NO', '+358': 'FI', '+48': 'PL', '+420': 'CZ', '+421': 'SK',
        '+386': 'SI', '+36': 'HU', '+40': 'RO', '+359': 'BG', '+30': 'GR',
        '+90': 'TR', '+7': 'RU', '+380': 'UA', '+381': 'RS', '+382': 'ME',
        '+387': 'BA', '+389': 'MK', '+383': 'XK', '+355': 'AL', '+61': 'AU',
        '+64': 'NZ', '+27': 'ZA', '+91': 'IN', '+86': 'CN', '+81': 'JP',
        '+82': 'KR', '+66': 'TH', '+84': 'VN', '+60': 'MY', '+65': 'SG',
        '+63': 'PH', '+62': 'ID', '+92': 'PK', '+880': 'BD', '+94': 'LK',
        '+977': 'NP'
    };
    return mapping[callingCode];
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
    const requiredFields = ['nombre', 'apellido', 'nacionalidad', 'email', 'pais_codigo', 'telefono', 'puesto', 'ingles_nivel', 'experiencia', 'cv'];
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

// =================== VALIDACIÓN EN TIEMPO REAL Y ACCESIBILIDAD ===================

document.addEventListener('DOMContentLoaded', function() {
    // Agregar validación en tiempo real a todos los campos
    addRealTimeValidation();
    
    // Agregar contador de caracteres para textarea
    addCharacterCounter();
    
    // Mejorar accesibilidad del formulario
    enhanceFormAccessibility();
});

function addRealTimeValidation() {
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

        // Agregar listeners para validación
        element.addEventListener('blur', () => validateField(field, element, errorDiv));
        element.addEventListener('input', () => {
            // Validación inmediata para algunos campos
            if (field.type === 'email' || field.type === 'text') {
                setTimeout(() => validateField(field, element, errorDiv), 300);
            }
        });

        // Validación especial para archivos
        if (field.type === 'file') {
            element.addEventListener('change', () => validateFile(field, element, errorDiv));
        }
    });

    // Agregar validación especial para el selector de país
    const countrySelect = document.getElementById('pais_codigo');
    const phoneInput = document.getElementById('telefono');
    const phoneErrorDiv = document.getElementById('telefono-error');
    
    if (countrySelect && phoneInput) {
        countrySelect.addEventListener('change', () => {
            // Revalidar el teléfono cuando cambie el país
            if (phoneInput.value.trim()) {
                setTimeout(() => {
                    const phoneField = { id: 'telefono', type: 'tel', required: true };
                    validateField(phoneField, phoneInput, phoneErrorDiv);
                }, 100);
            }
        });
    }
}

function validateField(field, element, errorDiv) {
    let isValid = true;
    let errorMessage = '';

    // Validar campo requerido
    if (field.required) {
        const value = element.value.trim();
        if (!value) {
            isValid = false;
            errorMessage = `${getFieldDisplayName(field.id)} es requerido`;
        }
    }

    // Validaciones específicas por tipo
    if (isValid && element.value.trim()) {
        switch (field.type) {
            case 'email':
                if (!isValidEmail(element.value)) {
                    isValid = false;
                    errorMessage = 'Formato de email inválido';
                }
                break;
            case 'text':
                if (element.value.length > element.maxLength) {
                    isValid = false;
                    errorMessage = `Máximo ${element.maxLength} caracteres`;
                }
                break;
            case 'tel':
                if (field.id === 'telefono') {
                    const countrySelect = document.getElementById('pais_codigo');
                    const countryCode = countrySelect ? countrySelect.value : '';
                    if (countryCode && element.value.trim()) {
                        if (!validatePhoneFormat(element.value, countryCode)) {
                            isValid = false;
                            errorMessage = 'Formato de teléfono inválido para el país seleccionado';
                        }
                    } else if (!countryCode && element.value.trim()) {
                        isValid = false;
                        errorMessage = 'Selecciona primero el código de país';
                    }
                }
                break;
            case 'textarea':
                if (element.value.length > element.maxLength) {
                    isValid = false;
                    errorMessage = `Máximo ${element.maxLength} caracteres`;
                }
                break;
        }
    }

    // Actualizar estado visual
    updateFieldValidationState(element, errorDiv, isValid, errorMessage);
    return isValid;
}

function validateFile(field, element, errorDiv) {
    const file = element.files[0];
    let isValid = true;
    let errorMessage = '';

    if (field.required && !file) {
        isValid = false;
        errorMessage = `${getFieldDisplayName(field.id)} es requerido`;
    } else if (file) {
        // Validar tamaño
        const maxSize = parseInt(element.dataset.maxSize) || 5242880; // 5MB default
        if (file.size > maxSize) {
            isValid = false;
            const maxSizeMB = Math.round(maxSize / 1024 / 1024);
            errorMessage = `El archivo excede el tamaño máximo de ${maxSizeMB}MB`;
        }

        // Validar tipo de archivo
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

    updateFieldValidationState(element, errorDiv, isValid, errorMessage);
    return isValid;
}

function updateFieldValidationState(element, errorDiv, isValid, errorMessage) {
    // Actualizar aria-invalid
    element.setAttribute('aria-invalid', !isValid);

    // Mostrar/ocultar mensaje de error
    if (errorDiv) {
        errorDiv.textContent = errorMessage;
        errorDiv.style.display = errorMessage ? 'block' : 'none';
    }

    // Actualizar clases CSS para estilos visuales
    if (isValid) {
        element.classList.remove('field-invalid');
        element.classList.add('field-valid');
    } else {
        element.classList.remove('field-valid');
        element.classList.add('field-invalid');
    }
}

function addCharacterCounter() {
    const textarea = document.getElementById('experiencia');
    const counter = document.getElementById('experiencia-count');
    
    if (!textarea || !counter) return;

    function updateCounter() {
        const current = textarea.value.length;
        const max = textarea.maxLength;
        const remaining = max - current;
        
        counter.textContent = `${current} / ${max} caracteres`;
        
        // Cambiar color según proximidad al límite
        counter.className = 'char-counter';
        if (remaining < 50) {
            counter.classList.add('error');
        } else if (remaining < 100) {
            counter.classList.add('warning');
        }
    }

    textarea.addEventListener('input', updateCounter);
    updateCounter(); // Inicializar
}

function enhanceFormAccessibility() {
    // Mejorar el feedback del teléfono
    const phoneInput = document.getElementById('telefono');
    const phoneHelp = document.getElementById('telefono-help');
    const countrySelect = document.getElementById('pais_codigo');
    
    if (phoneInput && phoneHelp && countrySelect) {
        function updatePhoneHelp() {
            const selectedCountry = countrySelect.value;
            if (selectedCountry) {
                const countryName = countrySelect.options[countrySelect.selectedIndex].text;
                phoneHelp.textContent = `Escribe tu número de teléfono para ${countryName}`;
            } else {
                phoneHelp.textContent = 'Selecciona tu país y escribe tu número de teléfono';
            }
        }
        
        countrySelect.addEventListener('change', updatePhoneHelp);
    }

    // Mejorar feedback del formulario
    const form = document.getElementById('applicationForm');
    const submitBtn = form.querySelector('.submit-btn');
    
    form.addEventListener('submit', function(e) {
        // Cambiar estado del botón durante el envío
        if (submitBtn) {
            const originalText = submitBtn.querySelector('span').textContent;
            submitBtn.querySelector('span').textContent = 'Enviando...';
            submitBtn.disabled = true;
            submitBtn.setAttribute('aria-disabled', 'true');
            
            // Restaurar estado si hay error (se maneja en el catch del submit)
            setTimeout(() => {
                if (submitBtn.disabled) {
                    submitBtn.querySelector('span').textContent = originalText;
                    submitBtn.disabled = false;
                    submitBtn.setAttribute('aria-disabled', 'false');
                }
            }, 10000); // Timeout de 10 segundos
        }
    });
}

function getFieldDisplayName(fieldId) {
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

function isValidEmail(email) {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
}
