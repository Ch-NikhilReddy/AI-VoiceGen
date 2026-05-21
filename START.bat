@echo off
title VoiceLab - AI Voice Generator
color 0A
cls

echo.
echo  =====================================================
echo     VoiceLab - AI Voice Generator  ^|  One-Click Setup
echo  =====================================================
echo.

:: ─── Step 1: Check Python ────────────────────────────────────────────────────
echo  [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo  ERROR: Python is not installed or not in PATH.
    echo  Please download and install Python 3.10 or higher from:
    echo  https://www.python.org/downloads/
    echo.
    echo  IMPORTANT: During install, check "Add Python to PATH"
    echo.
    pause
    start https://www.python.org/downloads/
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo  Found: %%i
echo.

:: ─── Step 2: Create Virtual Environment ──────────────────────────────────────
echo  [2/5] Setting up virtual environment...
if not exist "venv\" (
    echo  Creating new virtual environment...
    python -m venv venv
    echo  Virtual environment created!
) else (
    echo  Virtual environment already exists. Skipping...
)
echo.

:: ─── Step 3: Install Dependencies ────────────────────────────────────────────
echo  [3/5] Installing required packages (first time may take 5-10 minutes)...
echo  Please wait - downloading PyTorch, TTS engine and other libraries...
echo.

call venv\Scripts\activate.bat

:: Upgrade pip silently
python -m pip install --upgrade pip --quiet

:: Install CPU PyTorch first (smaller, no CUDA needed)
echo  Installing PyTorch (CPU version)...
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu --quiet
if %errorlevel% neq 0 (
    color 0C
    echo  ERROR: Failed to install PyTorch. Check your internet connection.
    pause
    exit /b 1
)
echo  PyTorch installed!

:: Install remaining packages
echo  Installing remaining packages...
pip install flask flask-cors coqui-tts soundfile numpy librosa "transformers==4.49.0" --quiet
if %errorlevel% neq 0 (
    color 0C
    echo  ERROR: Failed to install required packages. Check your internet connection.
    pause
    exit /b 1
)
echo  All packages installed!
echo.

:: ─── Step 4: Create required folders ─────────────────────────────────────────
echo  [4/5] Preparing workspace folders...
if not exist "outputs\" mkdir outputs
if not exist "voices\" mkdir voices
echo  Folders ready!
echo.

:: ─── Step 5: Launch Server + Open Chrome ─────────────────────────────────────
echo  [5/5] Starting VoiceLab server...
echo.
echo  =====================================================
echo   The app will open in your browser automatically.
echo   If it does not open, go to: http://localhost:5050
echo.
echo   NOTE: First launch downloads the AI voice model
echo   (~1.87 GB). This only happens ONCE.
echo   Subsequent launches will start in seconds!
echo.
echo   To stop the server, close this window or press
echo   CTRL+C in this window.
echo  =====================================================
echo.

:: Wait 3 seconds then open browser
start /b cmd /c "timeout /t 4 /nobreak >nul && start chrome http://localhost:5050 2>nul || start msedge http://localhost:5050 2>nul || start http://localhost:5050"

:: Start the Flask app
python App.py

:: If server stops, pause so user can read error
echo.
echo  Server has stopped. Press any key to exit.
pause >nul
