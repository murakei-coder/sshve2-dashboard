# Requirements Document

## Introduction

本システムは、プロモーションデータを分析し、価格（our_price）と割引率（current_discount_percent）がUplift（promotion_ops÷past_month_gms - 100%）に与える影響を視覚的・統計的に明らかにするツールである。特に、価格と割引率の交互作用効果（両方が高い場合にUpliftがさらに大きくなるか）を検証することを目的とする。

## Glossary

- **Uplift**: プロモーション効果を示す指標。計算式: (promotion_ops ÷ past_month_gms - 1) × 100%
- **our_price**: 商品の通常価格
- **current_discount_percent**: 現在適用されている割引率
- **交互作用効果（Interaction Effect）**: 2つの変数が組み合わさった時に、個別の効果の合計以上（または以下）の効果が生じる現象
- **OPS**: Ordered Product Sales（注文商品売上）
- **GMS**: Gross Merchandise Sales（総商品売上）
- **回帰分析**: 変数間の関係を数学的にモデル化する統計手法

## Requirements

### Requirement 1

**User Story:** As a データアナリスト, I want to タブ区切りファイルからデータを読み込む, so that 分析に必要なデータを取得できる

#### Acceptance Criteria

1. WHEN ユーザーがファイルパスを指定する THEN THE システム SHALL タブ区切りファイルを読み込み、DataFrameとして返す
2. WHEN ファイルに必要なカラム（our_price, current_discount_percent, promotion_ops, past_month_gms）が存在しない THEN THE システム SHALL エラーメッセージを表示し処理を中断する
3. WHEN current_discount_percentが文字列形式（例: "20.01"や"5.20%~25%"）である THEN THE システム SHALL 数値に変換する

### Requirement 2

**User Story:** As a データアナリスト, I want to Upliftを計算する, so that プロモーション効果を定量化できる

#### Acceptance Criteria

1. WHEN データが読み込まれる THEN THE システム SHALL Uplift = (promotion_ops / past_month_gms - 1) × 100 を計算する
2. WHEN past_month_gmsが0またはNULLである THEN THE システム SHALL 該当レコードをUplift計算から除外する
3. WHEN Upliftが計算される THEN THE システム SHALL 結果を新しいカラムとしてDataFrameに追加する

### Requirement 3

**User Story:** As a データアナリスト, I want to 価格と割引率のUpliftへの影響を視覚化する, so that 傾向を直感的に理解できる

#### Acceptance Criteria

1. WHEN 分析が実行される THEN THE システム SHALL our_priceをX軸、Upliftを Y軸とした散布図を生成する
2. WHEN 分析が実行される THEN THE システム SHALL current_discount_percentをX軸、UpliftをY軸とした散布図を生成する
3. WHEN 分析が実行される THEN THE システム SHALL our_priceとcurrent_discount_percentの組み合わせによるUpliftのヒートマップを生成する
4. WHEN ヒートマップを生成する THEN THE システム SHALL 価格帯と割引率帯でデータをビニングし、各セルの平均Upliftを表示する

### Requirement 4

**User Story:** As a データアナリスト, I want to 統計的に交互作用効果を検証する, so that 仮説を数値的に証明できる

#### Acceptance Criteria

1. WHEN 統計分析が実行される THEN THE システム SHALL 重回帰分析を実行し、our_price、current_discount_percent、および交互作用項（our_price × current_discount_percent）の係数を算出する
2. WHEN 回帰分析が完了する THEN THE システム SHALL 各係数のp値を計算し、統計的有意性を判定する
3. WHEN 回帰分析が完了する THEN THE システム SHALL R²値（決定係数）を算出し、モデルの説明力を評価する
4. WHEN 交互作用項の係数が正かつp値が0.05未満である THEN THE システム SHALL 「価格と割引率の交互作用効果は統計的に有意」と結論付ける

### Requirement 5

**User Story:** As a データアナリスト, I want to 分析結果をレポートとして出力する, so that 結果を共有・保存できる

#### Acceptance Criteria

1. WHEN 分析が完了する THEN THE システム SHALL 統計サマリー（係数、p値、R²）をコンソールに表示する
2. WHEN 分析が完了する THEN THE システム SHALL 生成したグラフをPNGファイルとして保存する
3. WHEN 分析が完了する THEN THE システム SHALL 分析結果をJSON形式でも出力する
