#!/usr/bin/env python3
"""
Script de prueba rápida para verificar configuración de Gmail
"""

import requests
import json

def test_email_configuration():
    """Prueba la configuración de email usando el endpoint de test."""

    url = "http://127.0.0.1:5000/api/test-email"

    # Email de prueba (tu email personal donde quieres recibir la prueba)
    test_data = {
        "email": "alangabrielsalva@gmail.com"
    }

    try:
        print("🧪 Probando configuración de email...")
        print(f"📧 Email de prueba: {test_data['email']}")
        print(f"🌐 URL: {url}")
        print("-" * 50)

        response = requests.post(url, json=test_data, timeout=30)

        if response.status_code == 200:
            data = response.json()

            print("✅ RESPUESTA EXITOSA:")
            print(f"📊 Configuración email: {'✅ Correcta' if data.get('email_configured') else '❌ Incorrecta'}")

            if data.get('configuration_issues'):
                print("⚠️  Problemas encontrados:")
                for issue in data['configuration_issues']:
                    print(f"   • {issue}")

            if 'test_email_sent' in data:
                print(f"📨 Email enviado: {'✅ Sí' if data['test_email_sent'] else '❌ No'}")

            print("\n📋 Detalles de configuración:")
            print(f"   • Servidor: {data.get('mail_server', 'No configurado')}")
            print(f"   • Puerto: {data.get('mail_port', 'No configurado')}")
            print(f"   • TLS: {'✅ Habilitado' if data.get('mail_use_tls') else '❌ Deshabilitado'}")
            print(f"   • Usuario: {data.get('mail_username', 'No configurado')}")

            if data.get('email_configured') and data.get('test_email_sent'):
                print("\n🎉 ¡EMAIL CONFIGURADO CORRECTAMENTE!")
                print("📬 Revisa tu bandeja de entrada para el email de confirmación.")
            else:
                print("\n⚠️  Hay problemas con la configuración de email.")

        else:
            print(f"❌ ERROR HTTP {response.status_code}:")
            try:
                error_data = response.json()
                print(f"   {error_data.get('error', 'Error desconocido')}")
            except:
                print(f"   {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se puede conectar al backend.")
        print("   Asegúrate de que el backend esté ejecutándose en el puerto 5000")

    except requests.exceptions.Timeout:
        print("⏱️  ERROR: Timeout al enviar email.")
        print("   El servidor SMTP puede estar tardando mucho en responder.")

    except Exception as e:
        print(f"❌ ERROR INESPERADO: {str(e)}")

if __name__ == "__main__":
    test_email_configuration()
