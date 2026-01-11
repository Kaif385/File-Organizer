@echo off
REM ============================================================
REM Smart File Organizer Pro - Windows Launcher
REM ============================================================
SETLOCAL ENABLEDELAYEDEXPANSION

REM Get the directory where this script is located
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ============================================================
    echo ERROR: Python is not installed or not in PATH
    echo ============================================================
    echo.
    echo Please ensure Python 3.8+ is installed and added to PATH
    echo Download from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Upgrade pip
echo [*] Upgrading pip...
python -m pip install --upgrade pip -q

REM Install dependencies
echo [*] Installing required dependencies...
echo     - streamlit
echo     - pandas
echo     - scikit-learn
python -m pip install -r requirements.txt

echo.
echo [OK] Dependencies installed successfully
echo.
echo [*] Starting Smart File Organizer Pro...
echo.

REM Launch the application
python launcher.py

echo.
echo [!] Application closed
pause

