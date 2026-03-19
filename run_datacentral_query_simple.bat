@echo off
REM DataCentral Query Executor - 簡易実行バッチファイル
REM このファイルをダブルクリックするだけで実行できます

setlocal

REM ここにURLと日付を設定してください
set URL=https://datacentral.a2z.com/dw-platform/servlet/dwp/template/EtlViewExtractJobs.vm/job_profile_id/14164725
set DATE=2026-02-02

echo ================================================================================
echo DataCentral Query Executor
echo ================================================================================
echo URL: %URL%
echo 日付: %DATE%
echo ================================================================================
echo.

REM Pythonスクリプトを実行（HTMLレポート付き、ブラウザで自動的に開く）
python src\run_datacentral_query.py --url "%URL%" --date "%DATE%" --html --open-browser

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
