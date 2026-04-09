@echo off
echo =======================================================
echo Starting Web Based Electronic Store System Locally
echo =======================================================

cd /d "%~dp0"

IF NOT EXIST ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r code\backend\requirements.txt

echo.
echo =======================================================
echo Server is starting... 
echo Please visit http://127.0.0.0:5000 in your browser.
echo =======================================================
echo.

cd code\backend
python app.py
