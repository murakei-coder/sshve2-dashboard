@echo off
chcp 65001 > nul
echo ========================================
echo Uplift交互作用分析ツール
echo ========================================
echo.

REM 仮想環境をアクティベート
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM 引数がない場合はデフォルトファイルを使用
if "%~1"=="" (
    echo 使用方法: run_uplift_analysis.bat ^<ファイルパス^> [出力ディレクトリ]
    echo.
    echo 例:
    echo   run_uplift_analysis.bat "C:\data\BF25_OPSByASIN.txt"
    echo   run_uplift_analysis.bat "C:\data\BF25_OPSByASIN.txt" "C:\output"
    echo.
    pause
    exit /b 1
)

REM 分析を実行
python src\run_uplift_analysis.py %*

echo.
pause
