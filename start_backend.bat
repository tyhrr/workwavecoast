@echo off
echo Starting WorkWave Coast Backend...
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Check if .env file exists
if not exist "backend\.env" (
    echo .env file not found in backend directory.
    echo Please copy backend\env.example to backend\.env and configure your settings.
    pause
    exit /b 1
)

REM Change to backend directory
cd backend

REM Start the Flask application
echo Starting Flask server...
python app.py

pause
