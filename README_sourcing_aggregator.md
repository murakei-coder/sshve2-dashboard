# ソーシングデータ集約ツール

## 概要

このツールは、毎日更新されるソーシングデータCSVファイルを読み込み、MCID（Merchant/Category ID）単位で集約してレポートを生成します。Python初心者でも簡単に使えるよう、バッチファイルをダブルクリックするだけで実行できます。

**主な機能：**
- CSVファイルからソーシングデータを自動読み込み
- MCID単位でのデータ集約（Total GMS、Sourced GMS、Sourced GMS %を計算）
- 見やすいHTMLレポートの生成
- Excelファイルへのエクスポート
- 日本語での進捗表示とエラーメッセージ

## 使い方

### 基本的な使用方法

1. **`run_sourcing_aggregator.bat` をダブルクリック**
2. **入力CSVファイルのパスを入力**（例: `C:\data\sourcing_data.csv`）
3. **Enterキーを押す**
4. 処理が完了すると、HTMLレポートとExcelファイルが生成されます

### 出力ファイル

処理が完了すると、入力ファイルと同じフォルダに以下のファイルが生成されます：

- `sourcing_aggregation_YYYYMMDD_HHMMSS.html` - HTMLレポート
- `sourcing_aggregation_YYYYMMDD_HHMMSS.xlsx` - Excelファイル

**例：**
```
入力: C:\data\sourcing_data.csv
出力: C:\data\sourcing_aggregation_20250117_143022.html
      C:\data\sourcing_aggregation_20250117_143022.xlsx
```

### 出力先を指定する場合

バッチファイルに引数を渡すことで、出力先を指定できます：

```cmd
run_sourcing_aggregator.bat "C:\data\sourcing_data.csv" "C:\output"
```

### コマンドラインから実行する場合

```bash
# 基本的な使用（入力ファイルと同じフォルダに出力）
python -m src.run_sourcing_aggregator "C:\data\sourcing_data.csv"

# 出力先を指定
python -m src.run_sourcing_aggregator "C:\data\sourcing_data.csv" -o "C:\output"
```

## 入力ファイルの要件

### 必須カラム

CSVファイルには以下の3つのカラムが必須です：

| カラム名 | 説明 | データ型 |
|---------|------|---------|
| `mcid` | Merchant/Category ID | 文字列 |
| `total_t30d_gms_BAU` | 30日間のGMS（Gross Merchandise Sales） | 数値 |
| `SSHVE2_SourcedFlag` | ソーシングフラグ（"Y" または "N"） | 文字列 |

### ファイル形式

- **エンコーディング**: UTF-8（自動的にcp932も試行）
- **形式**: CSV（カンマ区切り）
- **ヘッダー行**: 必須

### データ例

```csv
mcid,total_t30d_gms_BAU,SSHVE2_SourcedFlag
MC001,150000.50,Y
MC001,80000.25,N
MC002,200000.00,Y
MC003,50000.00,N
```

## 出力ファイルの説明

### HTMLレポート

視覚的に見やすいHTMLレポートが生成されます：

- **タイトル**: Sourcing Data Aggregation Report
- **メタデータ**: 生成日時、ソースファイル名
- **集約結果テーブル**: MCID、Total GMS、Sourced GMS、Sourced GMS %

**テーブルの列：**

| 列名 | 説明 |
|-----|------|
| MCID | Merchant/Category ID |
| Total GMS | MCID単位の合計GMS（カンマ区切り、小数点2桁） |
| Sourced GMS | ソーシングフラグが"Y"の行の合計GMS |
| Sourced GMS % | Sourced GMSの割合（小数点2桁） |

### Excelファイル

同じデータがExcel形式で出力されます：

- **シート名**: 集約結果
- **フォーマット**: 
  - 数値列: カンマ区切り、小数点2桁
  - パーセンテージ列: パーセンテージ形式（0.00%）
  - ヘッダー: 太字、背景色付き

## 集約ロジック

各MCIDに対して以下の計算を実行します：

1. **Total GMS** = `total_t30d_gms_BAU` の合計
2. **Sourced GMS** = `SSHVE2_SourcedFlag` が "Y" の行の `total_t30d_gms_BAU` の合計
3. **Sourced GMS %** = (Sourced GMS / Total GMS) × 100

**注意事項：**
- Total GMSが0の場合、Sourced GMS %は0%として計算されます
- 非数値データは0として扱われます
- MCIDが欠損している行は除外されます

## 必要な環境

### Python環境

- Python 3.7以上
- 必要なライブラリ:
  - pandas
  - openpyxl

### インストール

```bash
pip install pandas openpyxl
```

または、プロジェクトの `requirements.txt` を使用：

```bash
pip install -r requirements.txt
```

## トラブルシューティング

### Q: バッチファイルを実行してもエラーが出る

**A:** 以下を確認してください：
- Pythonがインストールされているか
- 必要なライブラリがインストールされているか（`pip install pandas openpyxl`）
- 仮想環境を使用している場合、`venv\Scripts\activate.bat` が存在するか

### Q: 「ファイルが見つかりません」エラー

**A:** 以下を確認してください：
- 入力ファイルのパスが正しいか
- ファイルが実際に存在するか
- パスにスペースが含まれている場合、ダブルクォートで囲んでいるか

### Q: 「必須カラムが不足しています」エラー

**A:** CSVファイルに以下のカラムが含まれているか確認してください：
- `mcid`
- `total_t30d_gms_BAU`
- `SSHVE2_SourcedFlag`

カラム名は大文字小文字を区別します。

### Q: 「エンコーディングエラー」が表示される

**A:** CSVファイルの文字コードを確認してください：
- UTF-8またはcp932（Shift-JIS）に対応しています
- それ以外のエンコーディングの場合、UTF-8に変換してください

### Q: 出力ファイルが生成されない

**A:** 以下を確認してください：
- 出力先フォルダへの書き込み権限があるか
- ディスクの空き容量が十分にあるか
- 同名のファイルが開かれていないか

### Q: データが正しく集約されない

**A:** 以下を確認してください：
- `total_t30d_gms_BAU` が数値として認識されているか
- `SSHVE2_SourcedFlag` が "Y" または "N" になっているか（大文字小文字を区別）
- MCIDに欠損値がないか

### Q: 処理が遅い

**A:** 大量のデータを処理する場合、時間がかかることがあります：
- 数十万行のデータでも数秒～数十秒で処理できます
- それ以上かかる場合、ファイルサイズやデータの品質を確認してください

## プロジェクト構造

```
src/
  sourcing_aggregator.py      # コアロジック（CSVLoader、DataValidator、MCIDAggregator、HTMLReportGenerator、ExcelExporter）
  run_sourcing_aggregator.py  # メインスクリプト
run_sourcing_aggregator.bat   # Windowsバッチファイル
README_sourcing_aggregator.md # このファイル
```

## 処理の流れ

1. **CSVファイル読み込み** - UTF-8エンコーディングで読み込み（失敗時はcp932を試行）
2. **データバリデーション** - 必須カラムの存在確認
3. **データクリーニング** - 非数値データの変換、欠損値の除外
4. **MCID単位で集約** - Total GMS、Sourced GMS、Sourced GMS %を計算
5. **レポート生成** - HTMLレポートとExcelファイルを出力

各ステップで進捗状況が日本語で表示されます。

## 技術仕様

### データ処理

- **グループ化**: pandasの `groupby` を使用してMCID単位で集約
- **数値変換**: `pd.to_numeric` で非数値データを0に変換
- **ゼロ除算対策**: Total GMSが0の場合、Sourced GMS %を0%として計算

### 出力フォーマット

- **数値**: カンマ区切り、小数点2桁（例: 1,234,567.89）
- **パーセンテージ**: 小数点2桁（例: 45.67%）
- **タイムスタンプ**: YYYYMMDD_HHMMSS形式（例: 20250117_143022）

## サポート

問題が発生した場合や質問がある場合は、開発チームにお問い合わせください。

---

**バージョン**: 1.0  
**最終更新**: 2025年1月
