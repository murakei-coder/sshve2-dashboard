@echo off
chcp 65001 >nul

echo ========================================
echo Bridge Plan Generator
echo スタンドアロン実行ファイル作成
echo ========================================
echo.
echo 📦 このスクリプトは以下を実行します:
echo    1. PyInstallerのインストール
echo    2. 単一の.exeファイルの作成
echo    3. 配布用パッケージの作成
echo.
echo ⏱️  処理には5-10分かかる場合があります
echo.
pause

echo.
echo [1/4] PyInstallerをインストールしています...
pip install pyinstaller
if %ERRORLEVEL% NEQ 0 (
    echo ❌ PyInstallerのインストールに失敗しました
    pause
    exit /b 1
)

echo.
echo [2/4] 実行ファイルをビルドしています...
echo       （これには数分かかります）
python -m PyInstaller bridge_plan_app.spec --clean
if %ERRORLEVEL% NEQ 0 (
    echo ❌ ビルドに失敗しました
    pause
    exit /b 1
)

echo.
echo [3/4] 配布用パッケージを作成しています...

REM Create distribution package
set DIST_DIR=BridgePlanGenerator_配布用
if exist %DIST_DIR% rmdir /s /q %DIST_DIR%
mkdir %DIST_DIR%

REM Copy executable
copy dist\BridgePlanGenerator.exe %DIST_DIR%\

REM Copy data files
xcopy /E /I /Y config %DIST_DIR%\config
xcopy /E /I /Y data %DIST_DIR%\data

REM Create simple launcher
(
echo @echo off
echo chcp 65001 ^>nul
echo.
echo echo ========================================
echo echo Bridge Plan Generator
echo echo ブリッジプラン生成ツール
echo echo ========================================
echo echo.
echo echo 🚀 アプリケーションを起動しています...
echo echo.
echo echo 数秒後にブラウザで以下のURLを開いてください:
echo echo    http://localhost:5000
echo echo.
echo echo ⚠️  終了するには、このウィンドウを閉じてください
echo echo ========================================
echo echo.
echo.
echo start http://localhost:5000
echo BridgePlanGenerator.exe
) > %DIST_DIR%\起動.bat

REM Create user guide
(
echo ========================================
echo Bridge Plan Generator - 使い方
echo ========================================
echo.
echo ■ 起動方法
echo.
echo 1. 「起動.bat」をダブルクリック
echo 2. 自動的にブラウザが開きます
echo    （開かない場合は http://localhost:5000 を手動で開く）
echo.
echo ■ 使い方
echo.
echo 1. ブラウザで集計レベルを選択（CID/Alias/Mgr/Team）
echo 2. 対象を選択（オプション）
echo 3. 「プランを生成」ボタンをクリック
echo 4. 結果が画面に表示され、Excelファイルが生成されます
echo.
echo ■ 出力ファイル
echo.
echo 生成されたファイルは「output」フォルダに保存されます:
echo - bridge_plan_summary_*.csv : サマリー
echo - bridge_plan_detailed_*.xlsx : 詳細レポート
echo.
echo ■ データファイルの更新
echo.
echo 「config\bridge_config.json」を編集して、
echo データファイルのパスを変更できます。
echo.
echo ■ トラブルシューティング
echo.
echo Q: ブラウザが開かない
echo A: 手動で http://localhost:5000 を開いてください
echo.
echo Q: エラーが表示される
echo A: データファイルのパスを確認してください
echo    （config\bridge_config.json）
echo.
echo Q: 終了方法
echo A: コマンドプロンプトウィンドウを閉じてください
echo.
echo ========================================
echo.
echo ■ 必要な環境
echo.
echo - Windows 10/11
echo - ブラウザ（Chrome, Edge, Firefoxなど）
echo - Excel（結果ファイルを開く場合）
echo.
echo ※ Pythonのインストールは不要です
echo.
echo ========================================
) > %DIST_DIR%\使い方.txt

echo.
echo [4/4] ZIPファイルを作成しています...

REM Create ZIP using PowerShell
powershell -command "Compress-Archive -Path '%DIST_DIR%' -DestinationPath 'BridgePlanGenerator_配布用.zip' -Force"

echo.
echo ========================================
echo ✅ 完了しました！
echo ========================================
echo.
echo 📁 配布用ファイル:
echo    BridgePlanGenerator_配布用.zip
echo.
echo 📦 ZIPファイルの中身:
echo    - BridgePlanGenerator.exe （実行ファイル）
echo    - 起動.bat （簡単起動用）
echo    - config\ （設定ファイル）
echo    - data\ （サンプルデータ）
echo    - 使い方.txt （ユーザーガイド）
echo.
echo 💡 営業担当への配布方法:
echo    1. BridgePlanGenerator_配布用.zip を配布
echo    2. 営業担当は解凍後、「起動.bat」をダブルクリック
echo    3. ブラウザで操作
echo.
echo ✨ Pythonのインストールは不要です！
echo ========================================
echo.
pause
