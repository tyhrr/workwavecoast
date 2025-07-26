#!/usr/bin/env python3
"""
Script para instalar todas las dependencias necesarias
"""

import subprocess
import sys
import os

def install_package(package):
    """Instalar un paquete usando pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} instalado correctamente")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Error instalando {package}")
        return False

def main():
    """Función principal"""
    print("🔧 Instalando dependencias para WorkWave Coast...")
    
    # Lista de dependencias para el backend completo
    packages = [
        "Flask>=3.0.0",
        "Flask-CORS>=4.0.0", 
        "pymongo>=4.6.0",
        "cloudinary>=1.36.0",
        "python-dotenv>=1.0.0",
        "Werkzeug>=3.0.0",
        "gunicorn>=21.2.0",
        "pandas>=2.2.0",
        "openpyxl>=3.1.2"
    ]
    
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 Resultado: {success_count}/{len(packages)} paquetes instalados")
    
    if success_count == len(packages):
        print("✅ Todas las dependencias se instalaron correctamente")
        print("\n🚀 Ahora puedes ejecutar:")
        print("   python server.py  (versión local con CSV)")
        print("   python backend/app.py  (versión con MongoDB + Cloudinary)")
    else:
        print("❌ Algunos paquetes no se pudieron instalar")
        print("Ejecuta manualmente: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
