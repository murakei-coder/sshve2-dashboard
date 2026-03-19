# Bridge Plan Generator

Bridge Plan Generatorは、Amazon販売担当者が売上目標を達成するための戦略的なブリッジプランを作成するAI搭載アプリケーションです。

## 概要

このシステムは、販売データ、イベント参加履歴、抑制パターンを分析し、2つの主要な最適化アプローチを通じて実行可能な推奨事項を生成します：

1. **ソーシング最適化**: イベント参加のための高ポテンシャルASINの特定
2. **抑制最適化**: 販売を妨げる運用上の問題（OOS、価格エラー、VRP欠落）の削減

## 機能

- ✅ 複数の集計レベルでのブリッジプラン生成（CID、Alias、Mgr、Team）
- ✅ 3つのパターン生成（ソーシング重視、抑制重視、バランス型）
- ✅ CSV/Excel形式でのレポートエクスポート
- ✅ 日本語サポート
- ✅ 設定可能な抑制係数とイベントパラメータ

## インストール

### 必要要件

- Python 3.8以上
- pip（Pythonパッケージマネージャー）

### セットアップ

1. リポジトリをクローン：
```bash
git clone <repository-url>
cd <repository-directory>
```

2. 必要なパッケージをインストール：
```bash
pip install -r requirements.txt
```

## 使用方法

### 方法1: Webアプリケーション（推奨）

営業担当が簡単に使える、ブラウザベースのインターフェースです。

1. `run_bridge_plan_web.bat` をダブルクリック
2. ブラウザで `http://localhost:5000` を開く
3. 画面の指示に従って操作：
   - ステップ1: データを読み込む
   - ステップ2: 集計レベルを選択（CID/Alias/Mgr/Team）
   - ステップ3: 対象を選択（オプション）
   - ステップ4: プランを生成
4. 結果が画面に表示され、`output/`フォルダにファイルが保存されます

### 方法2: コマンドライン

#### バッチファイルを使用（対話式）

```bash
run_bridge_plan.bat
```

ダブルクリックすると、集計レベルを選択するメニューが表示されます。

#### Pythonコマンドを直接実行

```bash
python src/run_bridge_plan.py --level <LEVEL> --config <CONFIG_FILE> --output <OUTPUT_DIR>
```

### パラメータ

- `--level`: 集計レベル（必須）
  - `CID`: 個別セラーレベル
  - `Alias`: 個別営業担当者レベル
  - `Mgr`: マネージャーレベル
  - `Team`: チームレベル

- `--config`: 設定JSONファイルのパス（必須）

- `--output`: レポート出力ディレクトリ（必須）

- `--entity`: 特定のエンティティIDのみ生成（オプション）

### 使用例

#### CIDレベルでプランを生成
```bash
python src/run_bridge_plan.py --level CID --config config/bridge_config.json --output output/
```

#### Aliasレベルでプランを生成
```bash
python src/run_bridge_plan.py --level Alias --config config/bridge_config.json --output output/
```

#### 特定のマネージャーのプランを生成
```bash
python src/run_bridge_plan.py --level Mgr --config config/bridge_config.json --output output/ --entity "山田マネージャー"
```

#### Teamレベルでプランを生成
```bash
python src/run_bridge_plan.py --level Team --config config/bridge_config.json --output output/
```

## 設定ファイル

設定ファイル（`config/bridge_config.json`）には以下の情報を含めます：

```json
{
  "sourcing_data_path": "data/sample_sourcing_data.csv",
  "target_data_path": "data/sample_target_data.csv",
  "suppression_benchmark_path": "data/sample_suppression_benchmark.csv",
  "cid_mapping_path": "data/sample_cid_mapping.xlsx",
  "cid_mapping_sheet": "Sheet1",
  "suppression_coefficients": {
    "No suppression": 0.5343,
    "OOS": 0.2807,
    "VRP missing": 0.0963,
    "Price Error": 0.275,
    "Others": 0.1801
  },
  "event_flag_priority": [
    "sshve1_flag",
    "fy26_mde2_flag",
    "nys26_flag",
    "bf25_flag",
    "fy25_mde4_flag",
    "t365_flag"
  ]
}
```

### 設定パラメータの説明

- **sourcing_data_path**: ソーシングデータCSVファイルのパス
- **target_data_path**: ターゲットデータCSVファイルのパス
- **suppression_benchmark_path**: 抑制ベンチマークCSVファイルのパス
- **cid_mapping_path**: CIDマッピングExcelファイルのパス
- **cid_mapping_sheet**: Excelシート名
- **suppression_coefficients**: 各抑制カテゴリの売上影響係数
- **event_flag_priority**: イベント参加フラグの優先順位（新しい順）

## 入力データ形式

### 1. ソーシングデータ（CSV）

必須列：
- `ASIN`: 商品識別子
- `CID`: セラー識別子
- `total_t30d_gms_BAU`: 過去30日間のGMS（通常時）
- `suppression_category_large`: 抑制カテゴリ（1-5）
- イベント参加フラグ: `sshve1_flag`, `fy26_mde2_flag`, `nys26_flag`, `bf25_flag`, `fy25_mde4_flag`, `t365_flag`

### 2. ターゲットデータ（CSV）

必須列：
- `CID`: セラー識別子
- `t30_gms_target`: T30 GMS目標値

### 3. 抑制ベンチマーク（CSV）

必須列：
- `suppression_category`: 抑制カテゴリ名
- `percentage`: ベンチマーク割合

### 4. CIDマッピング（Excel）

必須列：
- `CID`: セラー識別子
- `Alias`: 営業担当者名
- `Mgr`: マネージャー名
- `Team`: チーム名

## 出力ファイル

アプリケーションは以下のファイルを生成します：

1. **bridge_plan_summary_{LEVEL}.csv**: 全パターンのサマリー
2. **bridge_plan_detailed_{LEVEL}.xlsx**: 詳細レポート（複数シート）
   - Summary: パターン概要
   - Sourcing Details: ASIN推奨詳細
   - Suppression Details: 抑制改善機会詳細
3. **bridge_plan_sourcing_{LEVEL}.csv**: ソーシング推奨詳細
4. **bridge_plan_suppression_{LEVEL}.csv**: 抑制改善詳細

## ブリッジプランパターン

### パターン1: ソーシング重視
高ポテンシャルASINの募集を通じて主に目標を達成します。

**適用条件**: ソーシングでギャップの50%以上をクローズできる場合

### パターン2: 抑制重視
抑制問題の削減を通じて主に目標を達成します。

**適用条件**: 抑制最適化でギャップの50%以上をクローズできる場合

### パターン3: バランス型
ソーシングと抑制最適化の組み合わせで目標を達成します。

**適用条件**: 両方のアプローチが実行可能で、合計でギャップの70%以上をクローズできる場合

## トラブルシューティング

### エラー: "File not found"
- 設定ファイルのパスが正しいか確認してください
- データファイルが指定された場所に存在するか確認してください

### エラー: "Missing required columns"
- データファイルに必須列が含まれているか確認してください
- 列名が正確に一致しているか確認してください（大文字小文字を区別）

### エラー: "Configuration validation failed"
- 設定ファイルのJSON形式が正しいか確認してください
- すべての必須パラメータが含まれているか確認してください
- 抑制係数が0-1の範囲内にあるか確認してください

### 日本語文字が正しく表示されない
- ファイルがUTF-8エンコーディングで保存されているか確認してください
- Excelで開く場合、UTF-8対応のバージョンを使用してください

## サンプルデータ

サンプルデータファイルは`data/`ディレクトリに含まれています：

- `sample_sourcing_data.csv`: 50件のASIN×CIDレコード
- `sample_target_data.csv`: 10件のCIDターゲット
- `sample_suppression_benchmark.csv`: 抑制ベンチマークデータ
- `sample_cid_mapping.xlsx`: 10件のCIDマッピング（日本語名含む）

サンプルデータを使用してアプリケーションをテストできます：

```bash
python src/run_bridge_plan.py --level CID --config config/bridge_config.json --output output/
```

## 技術仕様

### アーキテクチャ

```
┌─────────────────┐
│  Data Loaders   │ → CSVとExcelファイルの読み込みと検証
└────────┬────────┘
         │
┌────────▼────────┐
│  Data Processors│ → データの変換、集計、エンリッチ
└────────┬────────┘
         │
┌────────▼────────┐
│ Bridge Plan     │ → ソーシングと抑制プランの生成
│ Generator       │
└────────┬────────┘
         │
┌────────▼────────┐
│ Report Generator│ → 可視化とレポートのエクスポート
└─────────────────┘
```

### 主要コンポーネント

- **DataLoader**: データファイルの読み込みと検証
- **SourcingProcessor**: ソーシングデータの処理
- **TargetProcessor**: ターゲットデータとギャップ計算
- **SuppressionProcessor**: 抑制データの処理
- **HierarchyProcessor**: 組織階層のマッピングと集計
- **PromotionOPSCalculator**: プロモーションOPS目標の計算
- **SourcingPlanGenerator**: ソーシングベースのプラン生成
- **SuppressionPlanGenerator**: 抑制ベースのプラン生成
- **BridgePlanOrchestrator**: 複数パターンの生成とオーケストレーション
- **ReportGenerator**: レポート生成とエクスポート

## ライセンス

[ライセンス情報をここに記載]

## サポート

問題や質問がある場合は、[サポート連絡先]までお問い合わせください。

---

# Bridge Plan Generator (English)

The Bridge Plan Generator is an AI-powered application designed to help Amazon sales representatives create strategic Bridge Plans to achieve their sales targets.

## Overview

This system analyzes sales data, event participation history, and suppression patterns to generate actionable recommendations through two primary optimization approaches:

1. **Sourcing Optimization**: Identifying high-potential ASINs for event participation
2. **Suppression Optimization**: Reducing operational issues (OOS, Price Error, VRP missing) that prevent sales

## Features

- ✅ Generate bridge plans at multiple aggregation levels (CID, Alias, Mgr, Team)
- ✅ Three pattern generation (Sourcing-Focused, Suppression-Focused, Balanced)
- ✅ Export reports in CSV/Excel formats
- ✅ Japanese language support
- ✅ Configurable suppression coefficients and event parameters

## Installation

### Requirements

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-directory>
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python src/run_bridge_plan.py --level <LEVEL> --config <CONFIG_FILE> --output <OUTPUT_DIR>
```

### Parameters

- `--level`: Aggregation level (required)
  - `CID`: Individual seller level
  - `Alias`: Individual sales representative level
  - `Mgr`: Manager level
  - `Team`: Team level

- `--config`: Path to configuration JSON file (required)

- `--output`: Output directory for reports (required)

- `--entity`: Generate for specific entity ID only (optional)

### Examples

#### Generate plans at CID level
```bash
python src/run_bridge_plan.py --level CID --config config/bridge_config.json --output output/
```

#### Generate plans at Alias level
```bash
python src/run_bridge_plan.py --level Alias --config config/bridge_config.json --output output/
```

#### Generate plans for specific manager
```bash
python src/run_bridge_plan.py --level Mgr --config config/bridge_config.json --output output/ --entity "山田マネージャー"
```

#### Generate plans at Team level
```bash
python src/run_bridge_plan.py --level Team --config config/bridge_config.json --output output/
```

## Configuration File

The configuration file (`config/bridge_config.json`) should contain:

```json
{
  "sourcing_data_path": "data/sample_sourcing_data.csv",
  "target_data_path": "data/sample_target_data.csv",
  "suppression_benchmark_path": "data/sample_suppression_benchmark.csv",
  "cid_mapping_path": "data/sample_cid_mapping.xlsx",
  "cid_mapping_sheet": "Sheet1",
  "suppression_coefficients": {
    "No suppression": 0.5343,
    "OOS": 0.2807,
    "VRP missing": 0.0963,
    "Price Error": 0.275,
    "Others": 0.1801
  },
  "event_flag_priority": [
    "sshve1_flag",
    "fy26_mde2_flag",
    "nys26_flag",
    "bf25_flag",
    "fy25_mde4_flag",
    "t365_flag"
  ]
}
```

## Sample Data

Sample data files are included in the `data/` directory. You can test the application using:

```bash
python src/run_bridge_plan.py --level CID --config config/bridge_config.json --output output/
```

## Output Files

The application generates:

1. **bridge_plan_summary_{LEVEL}.csv**: Summary of all patterns
2. **bridge_plan_detailed_{LEVEL}.xlsx**: Detailed report with multiple sheets
3. **bridge_plan_sourcing_{LEVEL}.csv**: Sourcing recommendations details
4. **bridge_plan_suppression_{LEVEL}.csv**: Suppression improvement details

## Support

For issues or questions, please contact [support contact].
