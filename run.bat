@echo off

REM Image Drive startup script for Windows

echo ================================
echo Image Drive - Startup Script
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    echo Virtual environment created!
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
if not exist ".requirements_installed" (
    echo Installing requirements...
    pip install -r requirements.txt
    type nul > .requirements_installed
    echo Requirements installed!
)

REM Check if database is initialized
if not exist "image_drive.db" (
    echo.
    echo Database not found. Initializing...
    python init_database.py
)

REM Start the application
echo.
echo Starting Image Drive...
echo Access the application at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python app.py

pause
