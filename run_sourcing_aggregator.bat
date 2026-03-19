@echo off
chcp 65001 > nul
echo ========================================
echo ソーシングデータ集約ツール
echo ========================================

REM Activate virtual environment if exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Prompt for input file path if not provided
if "%~1"=="" (
    echo.
    set /p INPUT_FILE="入力CSVファイルのパスを入力してください: "
) else (
    set INPUT_FILE=%~1
)

REM Check if input file path is empty
if "%INPUT_FILE%"=="" (
    echo.
    echo エラー: 入力ファイルパスが指定されていません。
    echo.
    pause
    exit /b 1
)

REM Set default output directory
set DEFAULT_OUTPUT_DIR=C:\Users\murakei\Desktop\SSHVE2\Sourcing\Tracking

REM Run aggregation
echo.
echo 処理を開始します...
if "%~2"=="" (
    python -m src.run_sourcing_aggregator "%INPUT_FILE%" -o "%DEFAULT_OUTPUT_DIR%"
) else (
    python -m src.run_sourcing_aggregator "%INPUT_FILE%" -o "%~2"
)

echo.
echo 処理が完了しました。
pause
