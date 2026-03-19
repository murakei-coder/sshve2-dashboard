@echo off
REM スタンドアロンダッシュボード生成

echo ================================================================================
echo スタンドアロンダッシュボード生成
echo ================================================================================
echo.
echo データを埋め込んだHTMLファイルを生成します。
echo 生成されたHTMLファイルは、Pythonなしで他の人と共有できます。
echo.
echo ================================================================================

python src\generate_standalone_dashboard.py "C:\Users\murakei\Desktop\3PEITS_AI\Opp_Dashboard\raw\Sourcing&Suppression_Sample.txt" "C:\Users\murakei\Desktop\3PEITS_AI\Opp_Dashboard\raw\EITS_Seller_list.xlsx" "C:\Users\murakei\Downloads\3P_E&ITS_SS HVE#1_Top40K_Tracking_v6.xlsx"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo エラーが発生しました。
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo 処理が完了しました。
echo standalone_dashboard.html を他の人に共有してください。
pause
