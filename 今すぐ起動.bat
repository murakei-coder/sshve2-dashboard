@echo off
chcp 65001 > nul
echo ========================================
echo SSHVE2 Dashboard - 起動中...
echo ========================================
echo.
echo あなたのPCのIPアドレス:
ipconfig | findstr /i "IPv4"
echo.
echo アクセスURL: http://YOUR_IP:5001
echo 停止するには Ctrl+C を押してください
echo ========================================
echo.

cd /d "%~dp0"
python src/sshve2_dashboard_web_app.py

pause
