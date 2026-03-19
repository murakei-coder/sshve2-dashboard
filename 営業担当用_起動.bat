@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo.
echo ========================================
echo    統合ダッシュボード
echo    Unified Analytics Dashboard
echo ========================================
echo.
echo 🚀 アプリケーションを起動しています...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Pythonがインストールされていません
    echo.
    echo 📥 以下の手順でPythonをインストールしてください:
    echo    1. https://www.python.org/downloads/ を開く
    echo    2. 「Download Python」をクリック
    echo    3. インストール時に「Add Python to PATH」にチェック
    echo.
    pause
    exit /b 1
)

echo ✅ Python環境が見つかりました
echo.

REM Check if required packages are installed
echo 📦 必要なパッケージを確認しています...
python -c "import flask" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo    Flaskをインストールしています...
    pip install flask >nul 2>&1
)

python -c "import pandas" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo    Pandasをインストールしています...
    pip install pandas >nul 2>&1
)

python -c "import openpyxl" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo    Openpyxlをインストールしています...
    pip install openpyxl >nul 2>&1
)

echo ✅ パッケージの確認が完了しました
echo.
echo 🌐 ブラウザが自動的に開きます...
echo    （開かない場合は http://localhost:5000 を手動で開いてください）
echo.
echo ⚠️  終了するには、このウィンドウを閉じてください
echo ========================================
echo.

REM Start the unified dashboard
python src/unified_dashboard.py

pause
