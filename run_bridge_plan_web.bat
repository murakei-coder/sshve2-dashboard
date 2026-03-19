@echo off
chcp 65001 >nul

echo ========================================
echo Bridge Plan Generator - Web Application
echo ブリッジプラン生成ツール - Webアプリ
echo ========================================
echo.
echo 🚀 Webアプリケーションを起動しています...
echo.
echo ブラウザで以下のURLを開いてください:
echo    http://localhost:5000
echo.
echo ⚠️  終了するには Ctrl+C を押してください
echo ========================================
echo.

python src/bridge_plan_web_app.py

pause
