# Bridge Plan Generator - 営業担当向けガイド

## 🎯 このツールについて

Bridge Plan Generatorは、売上目標を達成するためのブリッジプランを自動生成するツールです。

**特徴:**
- ✅ Pythonのインストール不要
- ✅ ブラウザで簡単操作
- ✅ 自動的にExcelファイルを生成
- ✅ CID/Alias/Mgr/Teamレベルで分析可能

---

## 📦 初回セットアップ（1回だけ）

### ステップ1: ZIPファイルを解凍

受け取った `BridgePlanGenerator_配布用.zip` を右クリック → 「すべて展開」

### ステップ2: フォルダの中身を確認

解凍したフォルダには以下のファイルがあります：

```
BridgePlanGenerator_配布用/
├── 起動.bat                    ← これをダブルクリック！
├── BridgePlanGenerator.exe     ← 本体
├── config/                     ← 設定ファイル
│   └── bridge_config.json
├── data/                       ← データファイル
└── 使い方.txt                  ← このガイド
```

---

## 🚀 使い方

### 1. アプリを起動

`起動.bat` をダブルクリック

→ 黒い画面（コマンドプロンプト）が表示されます

**⚠️ 重要: この黒い画面は閉じないでください！**

### 2. ブラウザを開く

自動的にブラウザが開きます。

開かない場合は、ブラウザで以下を入力：
```
http://localhost:5000
```

### 3. 画面で操作

#### ステップ1: データ読み込み状況を確認
- 自動的にデータが読み込まれます
- CID、Alias、Mgr、Teamの件数が表示されます

#### ステップ2: 集計レベルを選択
- **CID**: 個別セラーレベル
- **Alias**: 営業担当者レベル
- **Mgr**: マネージャーレベル
- **Team**: チームレベル

#### ステップ3: 対象を選択（オプション）
- 「すべて」を選択すると全体のプランを生成
- 特定の対象を選択すると、その対象のみ生成

#### ステップ4: プランを生成
- 「プランを生成」ボタンをクリック
- 数分待つと結果が表示されます

### 4. 結果を確認

画面に結果が表示され、以下のファイルが自動生成されます：

```
output/
├── bridge_plan_summary_CID_20260317_143022.csv      ← サマリー
├── bridge_plan_detailed_CID_20260317_143022.xlsx   ← 詳細レポート
├── bridge_plan_sourcing_CID_20260317_143022.csv    ← ソーシング詳細
└── bridge_plan_suppression_CID_20260317_143022.csv ← 抑制詳細
```

Excelで開いて確認できます。

---

## ⚠️ 重要な注意事項

### アプリを終了する方法

**黒い画面（コマンドプロンプト）を閉じてください**

ブラウザのタブを閉じるだけでは終了しません。

### 再度使用する場合

もう一度 `起動.bat` をダブルクリックするだけです。

---

## 🔧 データファイルの変更方法

### 自分のデータを使用する場合

1. `config\bridge_config.json` をメモ帳で開く
2. データファイルのパスを変更

**例:**
```json
{
  "sourcing_data_path": "C:\\Users\\yourname\\Desktop\\my_data.csv",
  "target_data_path": "C:\\Users\\yourname\\Desktop\\target.csv",
  ...
}
```

**注意:** パスの区切りは `\\` （バックスラッシュ2つ）を使用

### 必要なデータファイル

1. **ソーシングデータ** (CSV)
   - 必須列: ASIN, CID, total_t30d_gms_BAU, suppression_category_large
   - イベント参加フラグ: sshve1_flag, fy26_mde2_flag, nys26_flag, bf25_flag, fy25_mde4_flag, t365_flag

2. **ターゲットデータ** (CSV)
   - 必須列: CID, t30_gms_target

3. **抑制ベンチマーク** (CSV)
   - 必須列: suppression_category, percentage

4. **CIDマッピング** (Excel)
   - 必須列: CID, Alias, Mgr, Team

---

## ❓ トラブルシューティング

### Q: ブラウザが自動で開かない

**A:** ブラウザを手動で開いて、以下を入力
```
http://localhost:5000
```

### Q: エラーが表示される

**A:** データファイルのパスを確認してください
- `config\bridge_config.json` を開く
- パスが正しいか確認
- ファイルが存在するか確認

### Q: 「ポート5000は既に使用されています」エラー

**A:** 前回起動したアプリが終了していません

1. タスクマネージャーを開く（Ctrl + Shift + Esc）
2. `BridgePlanGenerator.exe` を探す
3. 右クリック → 「タスクの終了」

### Q: データ読み込みエラー

**A:** 以下を確認してください
- データファイルが存在するか
- ファイルが他のプログラムで開かれていないか
- ファイルの形式が正しいか（CSV/Excel）
- 必須列が含まれているか

### Q: 処理が遅い

**A:** データ量によっては数分かかる場合があります
- CIDレベル: 数分
- Teamレベル: 10分以上かかる場合も

---

## 📞 サポート

問題が解決しない場合は、以下の情報を添えて連絡してください：

1. 表示されたエラーメッセージ（スクリーンショット）
2. 黒い画面に表示されている内容
3. 使用しているWindowsのバージョン
4. 使用しているブラウザ

---

## ✅ 必要な環境

- **OS**: Windows 10 または Windows 11
- **ブラウザ**: Chrome、Edge、Firefoxなど
- **Excel**: 結果ファイルを開く場合

**※ Pythonのインストールは不要です！**

---

## 📊 出力ファイルの見方

### 1. サマリーCSV (`bridge_plan_summary_*.csv`)

全パターンの概要が記載されています。

**主な列:**
- `entity_id`: 対象ID（CID、Aliasなど）
- `pattern_name`: パターン名（Sourcing-Focused、Suppression-Focused、Balanced）
- `current_t30_gms`: 現在のGMS
- `target_t30_gms`: 目標GMS
- `gap`: ギャップ
- `feasibility_score`: 実現可能性スコア

### 2. 詳細Excel (`bridge_plan_detailed_*.xlsx`)

複数のシートに分かれています：

- **Summary**: パターン概要
- **Sourcing Details**: ASIN推奨詳細
- **Suppression Details**: 抑制改善機会詳細

### 3. ソーシング詳細CSV (`bridge_plan_sourcing_*.csv`)

推奨ASINの詳細情報

### 4. 抑制詳細CSV (`bridge_plan_suppression_*.csv`)

抑制改善の詳細情報

---

## 🎓 用語説明

- **CID**: セラーID
- **Alias**: 営業担当者
- **Mgr**: マネージャー
- **Team**: チーム
- **T30 GMS**: 過去30日間のGMS（売上）
- **ソーシング**: ASINの募集による売上増加
- **抑制**: OOS、価格エラーなどの運用問題の削減
- **Feasibility Score**: 実現可能性スコア（高いほど実現しやすい）

---

## 📝 更新履歴

- 2026-03-17: 初版リリース

---

**質問や問題がある場合は、遠慮なく連絡してください！**
