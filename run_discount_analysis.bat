@echo off
chcp 65001 > nul
echo ========================================
echo 割引効果分析ツール
echo ========================================

REM Activate virtual environment if exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Check if input file is provided
if "%~1"=="" (
    echo.
    echo 使用方法: run_discount_analysis.bat ^<入力ファイルパス^> [出力ディレクトリ]
    echo.
    echo 例: run_discount_analysis.bat "C:\data\BF25_OPSByASIN T30GMS.txt"
    echo 例: run_discount_analysis.bat "C:\data\BF25_OPSByASIN T30GMS.txt" "C:\output"
    echo.
    pause
    exit /b 1
)

REM Run analysis
if "%~2"=="" (
    python -m src.run_discount_analysis "%~1"
) else (
    python -m src.run_discount_analysis "%~1" -o "%~2"
)

echo.
echo 処理が完了しました。
pause
