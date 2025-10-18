"""
Country Flags Utility
Functions for handling country flags and mappings
"""

# Mapping of countries to their flag emojis
COUNTRY_FLAGS = {
    'Argentina': '🇦🇷',
    'Bolivia': '🇧🇴',
    'Brasil': '🇧🇷',
    'Chile': '🇨🇱',
    'Colombia': '🇨🇴',
    'Costa Rica': '🇨🇷',
    'Cuba': '🇨🇺',
    'Ecuador': '🇪🇨',
    'El Salvador': '🇸🇻',
    'España': '🇪🇸',
    'Guatemala': '🇬🇹',
    'Honduras': '🇭🇳',
    'México': '🇲🇽',
    'Nicaragua': '🇳🇮',
    'Panamá': '🇵🇦',
    'Paraguay': '🇵🇾',
    'Perú': '🇵🇪',
    'República Dominicana': '🇩🇴',
    'Uruguay': '🇺🇾',
    'Venezuela': '🇻🇪',
    'Estados Unidos': '🇺🇸',
    'Canadá': '🇨🇦',
    'Francia': '🇫🇷',
    'Alemania': '🇩🇪',
    'Italia': '🇮🇹',
    'Portugal': '🇵🇹',
    'Reino Unido': '🇬🇧',
    'Australia': '🇦🇺',
    'Nueva Zelanda': '🇳🇿',
    'Otro': '🌍'
}

def get_country_flag(country_name: str) -> str:
    """
    Get the flag emoji for a given country name

    Args:
        country_name: Name of the country

    Returns:
        Flag emoji string, defaults to 🌍 if country not found
    """
    return COUNTRY_FLAGS.get(country_name, '🌍')

def get_all_countries() -> list:
    """
    Get list of all supported countries

    Returns:
        List of country names
    """
    return list(COUNTRY_FLAGS.keys())

def get_countries_with_flags() -> dict:
    """
    Get dictionary of all countries with their flags

    Returns:
        Dictionary mapping country names to flag emojis
    """
    return COUNTRY_FLAGS.copy()
