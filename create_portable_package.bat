@echo off
chcp 65001 >nul

echo ========================================
echo Bridge Plan Generator
echo ポータブルパッケージ作成
echo ========================================
echo.

echo 📦 ポータブルパッケージを作成しています...
echo.

REM Create package directory
set PACKAGE_DIR=BridgePlanGenerator_Portable
if exist %PACKAGE_DIR% rmdir /s /q %PACKAGE_DIR%
mkdir %PACKAGE_DIR%

echo ✅ パッケージディレクトリを作成しました
echo.

REM Copy necessary files
echo 📂 ファイルをコピーしています...
xcopy /E /I /Y src %PACKAGE_DIR%\src
xcopy /E /I /Y templates %PACKAGE_DIR%\templates
xcopy /E /I /Y config %PACKAGE_DIR%\config
xcopy /E /I /Y data %PACKAGE_DIR%\data
copy /Y requirements.txt %PACKAGE_DIR%\
copy /Y run_bridge_plan_web.bat %PACKAGE_DIR%\

echo ✅ ファイルのコピーが完了しました
echo.

REM Create simplified launcher
echo 🚀 起動スクリプトを作成しています...
(
echo @echo off
echo chcp 65001 ^>nul
echo.
echo echo ========================================
echo echo Bridge Plan Generator
echo echo ブリッジプラン生成ツール
echo echo ========================================
echo echo.
echo echo 🔍 Python環境を確認しています...
echo.
echo python --version ^>nul 2^>^&1
echo if %%ERRORLEVEL%% NEQ 0 ^(
echo     echo ❌ Pythonがインストールされていません
echo     echo.
echo     echo 📥 Pythonをインストールしてください:
echo     echo    https://www.python.org/downloads/
echo     echo.
echo     echo インストール時に「Add Python to PATH」にチェックを入れてください
echo     echo.
echo     pause
echo     exit /b 1
echo ^)
echo.
echo echo ✅ Python環境が見つかりました
echo echo.
echo echo 📦 必要なパッケージをインストールしています...
echo pip install -r requirements.txt ^>nul 2^>^&1
echo.
echo echo ✅ パッケージのインストールが完了しました
echo echo.
echo echo 🚀 Webアプリケーションを起動しています...
echo echo.
echo echo ブラウザで以下のURLを開いてください:
echo echo    http://localhost:5000
echo echo.
echo echo ⚠️  終了するには Ctrl+C を押してください
echo echo ========================================
echo echo.
echo.
echo python src/bridge_plan_web_app.py
echo.
echo pause
) > %PACKAGE_DIR%\起動.bat

echo ✅ 起動スクリプトを作成しました
echo.

REM Create README
echo 📝 READMEを作成しています...
(
echo # Bridge Plan Generator - ポータブル版
echo.
echo ## 初回セットアップ
echo.
echo 1. Pythonをインストール（まだの場合）
echo    - https://www.python.org/downloads/ からダウンロード
echo    - インストール時に「Add Python to PATH」にチェック
echo.
echo 2. 「起動.bat」をダブルクリック
echo    - 初回起動時に必要なパッケージが自動インストールされます
echo.
echo ## 使い方
echo.
echo 1. 「起動.bat」をダブルクリック
echo 2. ブラウザで http://localhost:5000 を開く
echo 3. 画面の指示に従って操作
echo.
echo ## データファイルの更新
echo.
echo `config/bridge_config.json` でデータファイルのパスを設定できます。
echo.
echo ## トラブルシューティング
echo.
echo ### エラー: Pythonが見つかりません
echo - Pythonをインストールしてください
echo - インストール時に「Add Python to PATH」にチェックを入れてください
echo.
echo ### エラー: データファイルが見つかりません
echo - `config/bridge_config.json` のパスを確認してください
echo - データファイルが正しい場所にあるか確認してください
) > %PACKAGE_DIR%\README.txt

echo ✅ READMEを作成しました
echo.

echo ========================================
echo ✅ ポータブルパッケージの作成が完了しました！
echo.
echo 📁 パッケージの場所:
echo    %PACKAGE_DIR%\
echo.
echo 📦 配布方法:
echo    1. %PACKAGE_DIR% フォルダ全体をZIP圧縮
echo    2. 営業担当に配布
echo    3. 営業担当は解凍後、「起動.bat」をダブルクリック
echo.
echo 💡 初回起動時に自動的に必要なパッケージがインストールされます
echo ========================================
echo.
pause
