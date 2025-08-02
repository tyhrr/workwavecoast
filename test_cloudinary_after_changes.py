#!/usr/bin/env python3
"""
Script para probar URLs de Cloudinary después de cambios de configuración
"""

import requests
import time

def test_cloudinary_access():
    """Prueba el acceso a archivos de Cloudinary después de cambios de configuración"""

    # URLs de prueba basadas en tu verificación anterior
    test_urls = [
        "https://res.cloudinary.com/dde3kelit/raw/upload/v1754152195/workwave_coast/cv_zcxbqm.pdf",
        "https://res.cloudinary.com/dde3kelit/image/upload/v1754139168/workwave_coast/documentos_pukbww.pdf"
    ]

    print("🧪 PROBANDO ACCESO A ARCHIVOS CLOUDINARY")
    print("=" * 50)
    print("📅 Ejecuta este script DESPUÉS de hacer los cambios en tu dashboard")
    print("⏰ Espera 2-3 minutos después de guardar cambios antes de ejecutar")
    print()

    for i, url in enumerate(test_urls, 1):
        print(f"🔗 Prueba {i}: {url[:60]}...")

        try:
            # Hacer petición HEAD para verificar acceso sin descargar
            response = requests.head(url, timeout=10)

            if response.status_code == 200:
                print(f"   ✅ ÉXITO: Archivo accesible públicamente")
                print(f"   📊 Código: {response.status_code}")
                print(f"   📏 Tamaño: {response.headers.get('Content-Length', 'Desconocido')} bytes")
                print(f"   📄 Tipo: {response.headers.get('Content-Type', 'Desconocido')}")
            elif response.status_code == 401:
                print(f"   ❌ FALLO: Aún requiere autenticación (401)")
                print(f"   💡 Sugerencia: Verificar que se guardaron los cambios en dashboard")
            elif response.status_code == 404:
                print(f"   ⚠️  ADVERTENCIA: Archivo no encontrado (404)")
            else:
                print(f"   ⚠️  INESPERADO: Código {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"   ❌ ERROR DE RED: {str(e)}")

        print()

    print("📋 RESUMEN:")
    print("   Si ves ✅ ÉXITO: ¡Los cambios funcionaron!")
    print("   Si ves ❌ FALLO: Espera unos minutos más o verifica configuración")
    print("   Si ves ⚠️ ADVERTENCIA: Puede ser problema de URL específica")

if __name__ == "__main__":
    test_cloudinary_access()
