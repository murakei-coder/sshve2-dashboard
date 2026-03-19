@echo off
REM DataCentral Query Executor - バッチファイル
REM 使用例: run_datacentral_query.bat "https://datacentral.a2z.com/..." "2026-02-02"

setlocal

REM 引数チェック
if "%~1"=="" (
    echo 使用方法: run_datacentral_query.bat [URL] [日付]
    echo.
    echo 例: run_datacentral_query.bat "https://datacentral.a2z.com/dw-platform/servlet/dwp/template/EtlViewExtractJobs.vm/job_profile_id/14164725" "2026-02-02"
    echo.
    pause
    exit /b 1
)

if "%~2"=="" (
    echo 使用方法: run_datacentral_query.bat [URL] [日付]
    echo.
    echo 例: run_datacentral_query.bat "https://datacentral.a2z.com/dw-platform/servlet/dwp/template/EtlViewExtractJobs.vm/job_profile_id/14164725" "2026-02-02"
    echo.
    pause
    exit /b 1
)

REM Pythonスクリプトを実行（HTMLレポート付き、ブラウザで自動的に開く）
python src\run_datacentral_query.py --url "%~1" --date "%~2" --html --open-browser

REM エラーコードをチェック
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo エラーが発生しました。
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo 処理が完了しました。
pause
