@echo off
REM Production startup script for Windows
REM Windows用の本番環境起動スクリプト

echo =========================================
echo SSHVE2 Dashboard - Production Mode
echo =========================================
echo.

REM Create logs directory if it doesn't exist
if not exist logs mkdir logs

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Install/update dependencies
echo Checking dependencies...
pip install -r requirements_production.txt

REM Start Gunicorn (Windows requires waitress instead)
echo.
echo Starting production server...
echo Access URL: http://YOUR_SERVER_IP:8000
echo.
echo To stop: Press Ctrl+C
echo =========================================
echo.

REM Use waitress for Windows (Gunicorn doesn't work on Windows)
pip install waitress
waitress-serve --host=0.0.0.0 --port=8000 --threads=4 wsgi:application
