@echo off
echo ========================================
echo SSHVE2 Dashboard - 常時起動モード
echo ========================================
echo.
echo あなたのPCのIPアドレス:
ipconfig | findstr "IPv4"
echo.
echo 停止するには Ctrl+C を押してください
echo ========================================
echo.

cd /d "%~dp0"
python src/sshve2_dashboard_web_app.py

pause
