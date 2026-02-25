@echo off
title DeepDive Catalog Assistant - Demo Launcher
color 0B

echo.
echo  ==================================================
echo     DEEPDIVE CATALOG ASSISTANT - CLIENT DEMO
echo  ==================================================
echo.
cd /d "%~dp0"
echo  [1/3] Checking System Environment...

:: Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  [X] Error: Python is not installed or not in your PATH.
    echo      Please install Python 3.10+ to run this demo.
    echo.
    pause
    exit
)

echo  [OK] Python found.

:: Setup Virtual Environment (Optional but recommended for clean run)
if not exist "venv" (
    echo.
    echo  [2/3] Setting up local environment (First run only)...
    python -m venv venv
    call venv\Scripts\activate
    echo        Installing dependencies...
    pip install -r requirements.txt -q
) else (
    echo  [2/3] Activating environment...
    call venv\Scripts\activate
)

echo  [OK] Ready to launch.

echo.
echo  [3/3] Starting Application...
echo        The app will open in your default browser.
echo.

:: Run Streamlit
streamlit run app_v2.py --server.headless=true --server.address=127.0.0.1 --server.port=8501
pause
