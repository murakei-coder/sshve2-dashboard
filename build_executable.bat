@echo off
chcp 65001 >nul

echo ========================================
echo Bridge Plan Generator
echo スタンドアロン実行ファイル作成
echo ========================================
echo.

echo 📦 PyInstallerをインストールしています...
pip install pyinstaller

echo.
echo 🔨 実行ファイルをビルドしています...
echo    （数分かかる場合があります）
echo.

pyinstaller --name="BridgePlanGenerator" ^
    --onefile ^
    --windowed ^
    --add-data "templates;templates" ^
    --add-data "config;config" ^
    --add-data "data;data" ^
    --hidden-import=flask ^
    --hidden-import=pandas ^
    --hidden-import=openpyxl ^
    --icon=NONE ^
    src/bridge_plan_web_app.py

echo.
echo ========================================
if %ERRORLEVEL% EQU 0 (
    echo ✅ ビルド完了！
    echo.
    echo 📁 実行ファイルの場所:
    echo    dist\BridgePlanGenerator.exe
    echo.
    echo 💡 使い方:
    echo    1. dist\BridgePlanGenerator.exe をダブルクリック
    echo    2. ブラウザで http://localhost:5000 を開く
    echo.
    echo 📦 配布方法:
    echo    以下のフォルダを営業担当に配布してください:
    echo    - dist\BridgePlanGenerator.exe
    echo    - config\bridge_config.json
    echo    - data\ フォルダ（データファイル）
) else (
    echo ❌ ビルドに失敗しました
    echo    エラーコード: %ERRORLEVEL%
)
echo ========================================
echo.
pause
