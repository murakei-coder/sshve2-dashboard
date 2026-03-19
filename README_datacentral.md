# DataCentral Query Executor

DataCentralからSQLクエリを取得し、日付を書き換えてローカルで実行し、結果をtxtファイルに保存するツールです。

## 機能

- DataCentral URLからクエリを自動取得
- クエリの6～11行目の日付を指定した日付に置換
- ローカルSQLiteデータベースでクエリを実行
- 結果をテキストファイルに保存

## インストール

必要なライブラリをインストール：

```bash
pip install -r requirements.txt
```

## 使用方法

### コマンドライン

```bash
# テキストファイルのみ
python src/run_datacentral_query.py --url "https://datacentral.a2z.com/..." --date 2026-02-02

# HTMLレポート付き
python src/run_datacentral_query.py --url "https://datacentral.a2z.com/..." --date 2026-02-02 --html
```

### バッチファイル（Windows）

```cmd
run_datacentral_query.bat "https://datacentral.a2z.com/..." "2026-02-02"
```

バッチファイルは自動的にHTMLレポートも生成します。

### オプション

- `--url`: DataCentral URL（必須）
- `--date`: 置換する日付（yyyy-mm-dd形式、必須）
- `--output`: 結果を保存するテキストファイルパス（オプション、デフォルト: query_result_YYYYMMDD_HHMMSS.txt）
- `--html`: HTMLレポートを生成する（オプション）
- `--html-output`: HTMLレポートの出力パス（オプション、デフォルト: query_result_YYYYMMDD_HHMMSS.html）
- `--db`: SQLiteデータベースファイルパス（オプション、デフォルト: database.sqlite）
- `--start-line`: 日付置換の開始行（オプション、デフォルト: 6）
- `--end-line`: 日付置換の終了行（オプション、デフォルト: 11）

### 使用例

```bash
# 基本的な使用（テキストファイルのみ）
python src/run_datacentral_query.py --url "https://datacentral.a2z.com/dw-platform/servlet/dwp/template/EtlViewExtractJobs.vm/job_profile_id/14164725" --date 2026-02-02

# HTMLレポート付き
python src/run_datacentral_query.py --url "https://datacentral.a2z.com/..." --date 2026-02-02 --html

# 出力ファイルを指定
python src/run_datacentral_query.py --url "https://datacentral.a2z.com/..." --date 2026-02-02 --output results.txt --html --html-output report.html

# カスタムデータベースを使用
python src/run_datacentral_query.py --url "https://datacentral.a2z.com/..." --date 2026-02-02 --db custom.sqlite --html

# 日付置換の行範囲を変更
python src/run_datacentral_query.py --url "https://datacentral.a2z.com/..." --date 2026-02-02 --start-line 5 --end-line 10 --html
```

## 認証設定

DataCentralへのアクセスに認証が必要な場合、以下の環境変数を設定してください：

### トークン認証

```bash
set DATACENTRAL_TOKEN=your_token_here
```

### ユーザー名/パスワード認証

```bash
set DATACENTRAL_USERNAME=your_username
set DATACENTRAL_PASSWORD=your_password
```

## 出力ファイル形式

### テキストファイル

結果はテキストファイルに以下の形式で保存されます：

```
================================================================================
DataCentral Query Executor - 実行結果
================================================================================
実行日時: 2026-02-17 17:30:00
URL: https://datacentral.a2z.com/...
置換日付: 2026-02-02
データベース: database.sqlite
結果行数: 100
結果列数: 10
================================================================================

【実行したクエリ】
--------------------------------------------------------------------------------
SELECT ...
--------------------------------------------------------------------------------

【実行結果】
--------------------------------------------------------------------------------
column1  column2  column3
value1   value2   value3
...
--------------------------------------------------------------------------------
```

### HTMLレポート

`--html`オプションを指定すると、視覚的に見やすいHTMLレポートが生成されます：

- 📊 データサマリー（行数、列数、統計情報）
- 🔍 実行したクエリの表示
- 📋 インタラクティブなデータテーブル
- 🔎 テーブル内検索機能
- 📈 グラデーションデザインで見やすい表示

HTMLレポートはブラウザで開いて閲覧できます。

## エラーハンドリング

ツールは以下のエラーを適切に処理します：

- **DataCentralエラー**: URL無効、接続失敗、認証失敗
- **データ検証エラー**: 日付形式が不正
- **クエリ実行エラー**: データベース接続失敗、SQL構文エラー

エラーが発生した場合、詳細なエラーメッセージが表示され、ゼロ以外の終了コードが返されます。

## プロジェクト構造

```
src/
  datacentral/
    __init__.py           # パッケージ初期化
    exceptions.py         # カスタム例外クラス
    query_fetcher.py      # クエリ取得コンポーネント
    date_replacer.py      # 日付置換コンポーネント
    query_executor.py     # クエリ実行コンポーネント
    html_report.py        # HTMLレポート生成
  run_datacentral_query.py  # メインCLIスクリプト
run_datacentral_query.bat   # Windowsバッチファイル
README_datacentral.md       # このファイル
```

## トラブルシューティング

### クエリが取得できない

- URLが正しいか確認してください
- 認証情報が設定されているか確認してください
- DataCentralにアクセスできるか確認してください

### データベース接続エラー

- データベースファイルが存在するか確認してください
- データベースファイルのパスが正しいか確認してください

### 日付形式エラー

- 日付が`yyyy-mm-dd`形式（例: 2026-02-02）であることを確認してください
- 日付が有効な日付であることを確認してください

## ライセンス

このツールは内部使用のために開発されました。
