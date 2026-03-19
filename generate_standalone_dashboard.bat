@echo off
chcp 65001 >nul

echo.
echo ========================================
echo スタンドアロンBridge Plan HTML生成
echo ========================================
echo.
echo 📂 Rawデータを読み込んで、配布用HTMLファイルを生成します
echo.
echo ⏱️  処理には数分かかる場合があります...
echo.

python src/generate_bridge_plan_html.py

echo.
echo ========================================
pause
