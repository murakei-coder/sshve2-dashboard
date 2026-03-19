# SSHVE2 Opportunity Dashboard 使い方ガイド

## 📋 目次
1. [概要](#概要)
2. [ダッシュボードの目的](#ダッシュボードの目的)
3. [基本的な使い方（SOP）](#基本的な使い方sop)
4. [各指標の説明](#各指標の説明)
5. [Action Focusの判定基準](#action-focusの判定基準)
6. [入力方法と計算ロジック](#入力方法と計算ロジック)
7. [よくある質問（FAQ）](#よくある質問faq)

---

## 概要

SSHVE2 Opportunity Dashboardは、セラーごとのPromotion OPS（Ordered Product Sales）のギャップを可視化し、Bridge Planを作成するためのツールです。

**主な機能**:
- セラーごとのOPS現状と目標の比較
- Sourcing/Suppression施策の優先順位付け
- 改善施策のシミュレーション
- ASIN単位のRawデータへのアクセス

---

## ダッシュボードの目的

このダッシュボードは、**Target OPSとの差分を埋めるためのBridge Plan作成**を支援します。

### Bridge Planとは？
Target OPSを達成するために必要な施策を具体化した計画です：
- **Sourcing施策**: 新規ASINの追加、既存ASINのGMS拡大
- **Suppression施策**: OOS削減、Price Error削減、その他Suppression削減

---

## 基本的な使い方（SOP）

### ステップ1: 担当範囲にフィルターをかける

1. **フィルターセクション**で自分の担当範囲を選択
   - Team / Mgr / Alias / MCID / Merchant Name から選択
   - 例: Team = "BITS SA&M" を選択

2. **🔍 検索ボタン**をクリック
   - 該当するセラーのリストが表示されます
   - Team Summaryで全体像を確認できます

### ステップ2: Promotion OPS vs Targetで昇順ソート

1. **Promotion OPS**セクションの**vs Target**カラムヘッダーをクリック
   - 昇順（▲）にソート
   - マイナスが大きいセラー（ギャップが大きい）が上位に表示されます

2. **優先度の高いセラーから対応**
   - vs Targetがマイナスのセラーは目標未達
   - マイナス幅が大きいほど優先度が高い

### ステップ3: Action Focusを確認

各セラーの**Action Focus**カラムで推奨アクションを確認：

| アイコン | 意味 | 対応方針 |
|---------|------|---------|
| 🎯 Sourcing | Sourcing施策が必要 | 新規ASIN追加、既存ASIN拡大 |
| 🔧 Suppression | Suppression施策が必要 | OOS削減、Price Error削減 |
| 📊 Both | 両方の施策が必要 | Sourcing + Suppression |
| ✅ Maintain | 現状維持でOK | 特別な施策不要 |

### ステップ4: 改善施策を入力してシミュレーション

1. **黄色のセル**をクリックして改善幅を入力

   **入力項目**:
   - **Sourcing改善幅**: 金額で入力（例: `10000` = 1万円の改善）
   - **OOS改善率**: %の数値のみ（例: `20` = 20%改善）
   - **Price Error削減率**: %の数値のみ（例: `15` = 15%削減）
   - **その他Suppression削減率**: %の数値のみ（例: `10` = 10%削減）

2. **Enter**キーを押すと自動計算
   - **Projected OPS**: 改善後の予測OPS
   - **Incremental OPS**: 改善によるOPS増分
   - **vs Target**: 改善後の目標との差分

3. **一括入力機能**も利用可能
   - 複数セラーに同じ改善幅を適用したい場合
   - 一括入力セクションで値を入力 → ✅ 一括適用ボタン

### ステップ5: Bridge Planに反映

1. **Projected OPS**と**Incremental OPS**を確認
   - Target OPSに到達できるか確認
   - 到達できない場合は追加施策を検討

2. **CSV出力**で結果を保存
   - 📥 CSV出力ボタンをクリック
   - Excel等で開いてBridge Planに転記

3. **ASIN単位の詳細確認**（必要に応じて）
   - 上部の**📊 QuickSight**リンクをクリック
   - またはCIDをクリックしてQuickSightで詳細データを確認

---

## 各指標の説明

### Sourced GMS
- **Act**: 現在のSourced GMS（SSHVE2でSourcedフラグがYのASINのGMS合計）
- **vs Target**: 現在のGMSと目標GMSの差分
- **Target**: 目標GMS（Target T30 GMS）
- **Total GMS**: Act + 過去参加ASIN（SSHVE1 + T365）

### SSHVE1 Suppression
- 前回イベント（SSHVE1）のSuppression状況
- **灰色ハイライト**: データがないセラーはPF平均値を使用
- Target OPSの計算に使用

### SSHVE2 Suppression
- 今回イベント（SSHVE2）の現在のSuppression状況
- Forecast OPSの計算に使用

### Promotion OPS
- **Forecast OPS**: 現在のGMSとSSHVE2 Suppressionから算出される予測OPS
  - 計算式: `Σ(Current GMS × SSHVE2% × 係数)`
- **vs Target**: Forecast OPS - Target OPS
- **Target OPS**: Target GMSとSSHVE1 Suppressionから算出される目標OPS
  - 計算式: `Σ(Target GMS × SSHVE1% × 係数)`

### 改善施策入力（黄色セル）
- **Sourcing改善幅**: GMSの増加額（金額）
- **OOS改善率**: OOS%の削減率（%）
- **Price Error削減率**: Price Error%の削減率（%）
- **その他Suppression削減率**: その他Suppression%の削減率（%）

### 改善後の予測（青色セル）
- **Suppression改善幅**: Suppression削減によるOPS増分
- **Projected OPS**: 改善施策適用後の予測OPS
  - 計算式: `Σ(Improved GMS × Improved SSHVE2% × 係数)`
- **Incremental OPS**: Projected OPS - Forecast OPS
- **vs Target**: Projected OPS - Target OPS

---

## Action Focusの判定基準

Action Focusは以下の3つの条件で自動判定されます：

### 判定条件
1. **Promotion OPS vs Target**: Projected OPS - Target OPS
2. **Sourced GMS vs Target**: Current GMS - Target GMS
3. **No Suppression比較**: SSHVE2 No Supp% - SSHVE1 No Supp%

### 判定ロジック

| Action Focus | 条件 |
|-------------|------|
| ✅ **Maintain** | OPS vs Target ≥ 0 **かつ** GMS vs Target ≥ 0 **かつ** No Supp ≥ SSHVE1 |
| 🔧 **Suppression** | GMS vs Target ≥ 0 **だが** No Supp < SSHVE1 |
| 🎯 **Sourcing** | GMS vs Target < 0 **だが** No Supp ≥ SSHVE1 |
| 📊 **Both** | GMS vs Target < 0 **かつ** No Supp < SSHVE1 |

### 対応方針

#### 🎯 Sourcing
**状況**: GMSが不足しているが、Suppressionは改善している
**施策**:
- 新規ASINの追加
- 既存ASINのGMS拡大
- Deal強化

#### 🔧 Suppression
**状況**: GMSは十分だが、Suppressionが悪化している
**施策**:
- OOS削減（在庫管理改善）
- Price Error削減（価格設定の最適化）
- その他Suppression削減

#### 📊 Both
**状況**: GMSもSuppressionも両方課題がある
**施策**:
- Sourcing施策とSuppression施策の両方を実施
- 優先度を付けて段階的に対応

#### ✅ Maintain
**状況**: 目標達成済み、または達成見込み
**施策**:
- 現状維持
- 必要に応じて更なる改善を検討

---

## 入力方法と計算ロジック

### 入力方法

#### 個別入力
1. 黄色のセルをクリック
2. 数値を入力
   - **Sourcing改善幅**: 金額（例: `10000`）
   - **改善率/削減率**: %の数値のみ（例: `20` = 20%）
3. Enterキーで確定
4. 自動的に再計算されます

#### 一括入力
1. 一括入力セクションで値を入力
2. ✅ 一括適用ボタンをクリック
3. 表示中の全セラーに適用されます

### 計算ロジック

#### Suppression Category係数
| Category | 係数 |
|----------|------|
| No suppression | 0.5343 |
| OOS | 0.0000 |
| VRP Missing | 0.0000 |
| Price Error | 0.2750 |
| Others | 0.1801 |

**注**: OOSとVRP Missingの係数は0に設定されています

#### Improved SSHVE2%の計算

改善施策を入力すると、SSHVE2のSuppression比率が以下のように変化します：

1. **OOS改善**:
   - Improved OOS% = OOS% × (1 - OOS改善率% / 100)
   - 削減分はNo suppressionに加算

2. **Price Error削減**:
   - Improved Price Error% = Price Error% × (1 - Price Error削減率% / 100)
   - 削減分はNo suppressionに加算

3. **その他Suppression削減**:
   - Improved Others% = Others% × (1 - その他削減率% / 100)
   - Improved VRP% = VRP% × (1 - その他削減率% / 100)
   - 削減分はNo suppressionに加算

4. **No suppression**:
   - Improved No Supp% = 元のNo Supp% + 各削減分の合計

#### Projected OPSの計算

```
Improved GMS = Current GMS + Sourcing改善幅

Projected OPS = Σ(Improved GMS × Improved SSHVE2% × 係数)
              = (Improved GMS × Improved No Supp% / 100 × 0.5343)
              + (Improved GMS × Improved OOS% / 100 × 0.0000)
              + (Improved GMS × Improved VRP% / 100 × 0.0000)
              + (Improved GMS × Improved Price Error% / 100 × 0.2750)
              + (Improved GMS × Improved Others% / 100 × 0.1801)
```

---

## よくある質問（FAQ）

### Q1: フィルターをかけてもデータが表示されない
**A**: 以下を確認してください：
- フィルター条件が正しく選択されているか
- 🔍 検索ボタンをクリックしたか
- ブラウザのコンソールにエラーが出ていないか（F12キーで確認）

### Q2: 20%改善したい場合、何を入力すればいい？
**A**: `20`と入力してください（`0.2`ではありません）
- 例: OOS改善率に`20`と入力 → 20%改善

### Q3: Sourcing改善幅はどう決めればいい？
**A**: 以下を参考に決定してください：
- 新規ASIN追加の見込みGMS
- 既存ASINのGMS拡大見込み
- Deal強化による増加見込み
- QuickSightでASIN単位のデータを確認して積み上げ

### Q4: SSHVE1 Suppressionが灰色になっているのはなぜ？
**A**: そのセラーのSSHVE1データが存在しないため、PF平均値を使用しています
- 灰色セルにマウスを乗せると「PF平均値を使用」と表示されます

### Q5: Action Focusが「Both」のセラーはどう対応すればいい？
**A**: Sourcing施策とSuppression施策の両方が必要です：
1. まずギャップの大きい方から着手
2. QuickSightでASIN単位のデータを確認
3. 優先度を付けて段階的に対応

### Q6: CSV出力したデータの文字化けを防ぐには？
**A**: UTF-8 BOMで出力されているため、Excelで開いても文字化けしません
- そのままExcelで開いてください

### Q7: Team Summaryの数値は何を表している？
**A**: 
- **Sellers**: セラー数
- **Current/Target GMS**: GMS合計
- **Gap**: Current GMS - Target GMS
- **No Supp%等**: GMS加重平均
- **Sourcing/Suppression/Both/Maintain**: 各Action Focusに該当するセラー数

### Q8: QuickSightで何が確認できる？
**A**: ASIN単位の詳細データを確認できます：
- ASIN別のGMS、OPS
- Suppression Category別の内訳
- 時系列推移
- より詳細な分析が可能

### Q9: 一括入力を取り消したい
**A**: 
- 個別に値を修正するか
- ページをリロードして最初からやり直してください
- CSV出力前であれば、ブラウザの戻るボタンでも可

### Q10: Projected OPSがTarget OPSに届かない場合は？
**A**: 以下を検討してください：
1. Sourcing改善幅を増やす（新規ASIN追加等）
2. Suppression削減率を上げる（より積極的な施策）
3. 両方の施策を強化
4. 現実的な目標値かどうかを再検討

---

## サポート

質問や不具合がある場合は、ダッシュボード管理者に連絡してください。

**最終更新**: 2026年3月19日
