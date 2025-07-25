@echo off
echo 🏖️ WorkWave Coast - Iniciando servidor...
echo.
echo Verificando dependencias de Python...

python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado o no está en el PATH
    echo Instala Python desde https://python.org
    pause
    exit /b 1
)

echo ✅ Python encontrado

if not exist "requirements.txt" (
    echo ❌ Archivo requirements.txt no encontrado
    pause
    exit /b 1
)

echo.
echo Instalando dependencias...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Error instalando dependencias
    pause
    exit /b 1
)

echo.
echo ✅ Dependencias instaladas
echo.
echo 🚀 Iniciando servidor...
echo.
echo 🌐 El servidor estará disponible en:
echo    - http://localhost:5000
echo    - http://127.0.0.1:5000
echo.
echo ⚡ Para detener el servidor presiona Ctrl+C
echo.

python server.py

pause
