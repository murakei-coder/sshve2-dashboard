@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
REM Bridge Plan Generator - Windows Batch Script

echo ========================================
echo Bridge Plan Generator
echo ブリッジプラン生成ツール
echo ========================================
echo.

if "%1"=="" (
    echo 集計レベルを選択してください / Select aggregation level:
    echo.
    echo 1. CID    - 個別セラーレベル / Individual seller level
    echo 2. Alias  - 営業担当者レベル / Sales representative level
    echo 3. Mgr    - マネージャーレベル / Manager level
    echo 4. Team   - チームレベル / Team level
    echo.
    set /p "choice=選択 (1-4): "
    
    if "!choice!"=="1" set LEVEL=CID
    if "!choice!"=="2" set LEVEL=Alias
    if "!choice!"=="3" set LEVEL=Mgr
    if "!choice!"=="4" set LEVEL=Team
    
    if not defined LEVEL (
        echo.
        echo ❌ 無効な選択です / Invalid selection
        echo.
        pause
        exit /b 1
    )
) else (
    set LEVEL=%1
)

echo.
echo 📊 集計レベル / Aggregation Level: !LEVEL!
echo 📁 設定ファイル / Config: config/bridge_config.json
echo 📁 出力先 / Output: output/
echo.
echo 処理を開始します... / Starting process...
echo.

python src/run_bridge_plan.py --level !LEVEL! --config config/bridge_config.json --output output/

echo.
echo ========================================
if %ERRORLEVEL% EQU 0 (
    echo ✅ 処理が完了しました / Process completed successfully
    echo 📁 結果は output/ フォルダに保存されました
    echo    Results saved to output/ folder
) else (
    echo ❌ エラーが発生しました / Error occurred
    echo    エラーコード / Error code: %ERRORLEVEL%
)
echo ========================================
echo.
pause
