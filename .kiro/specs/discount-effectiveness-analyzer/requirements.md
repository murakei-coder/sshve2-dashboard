# Requirements Document

## Introduction

本機能は、ブラックフライデー等のプロモーションイベントにおける割引効果を分析するPythonアプリケーションである。過去の売上（past_month_gms）からプロモーション当日の売上（promotion_ops）への伸び率を対象に、PF（プラットフォーム）×価格帯ごとに最適な割引率を統計的に試算する。分析結果はHTMLレポートとExcelファイルの両形式で出力される。

## Glossary

- **Discount_Effectiveness_Analyzer**: 割引効果分析システム
- **PF (Platform)**: プラットフォーム区分（商品カテゴリ分類）
- **past_month_gms**: 過去1ヶ月の売上金額（ベースライン）
- **promotion_ops**: プロモーション当日の売上金額
- **current_discount_percent**: 現在の割引率（%）
- **our_price**: 割引前価格（定価）
- **growth_rate**: 売上伸び率（promotion_ops / past_month_gms）
- **price_band**: 価格帯区分（例：1~1000円、1001~2000円等）
- **optimal_discount_rate**: 統計的に算出された最適割引率

## Requirements

### Requirement 1

**User Story:** As a データアナリスト, I want to Rawデータファイルを読み込んで分析用データフレームに変換する, so that 割引効果分析の基礎データを準備できる.

#### Acceptance Criteria

1. WHEN ユーザーがタブ区切りのRawデータファイルパスを指定する THEN Discount_Effectiveness_Analyzer SHALL ファイルを読み込みDataFrameに変換する
2. WHEN DataFrameに必須カラム（asin, pf, our_price, current_discount_percent, past_month_gms, promotion_ops）が存在しない THEN Discount_Effectiveness_Analyzer SHALL 不足カラム名を含むエラーメッセージを返す
3. WHEN 数値カラム（our_price, current_discount_percent, past_month_gms, promotion_ops）に非数値データが含まれる THEN Discount_Effectiveness_Analyzer SHALL 該当行を除外してログに記録する
4. WHEN past_month_gmsが0または負の値である THEN Discount_Effectiveness_Analyzer SHALL 該当行を除外する（伸び率計算不可のため）

### Requirement 2

**User Story:** As a データアナリスト, I want to 売上伸び率を計算する, so that 割引効果を定量的に評価できる.

#### Acceptance Criteria

1. WHEN 有効なpast_month_gmsとpromotion_opsが存在する THEN Discount_Effectiveness_Analyzer SHALL growth_rate = (promotion_ops / past_month_gms - 1) * 100 として伸び率（%）を計算する
2. WHEN growth_rateを計算する THEN Discount_Effectiveness_Analyzer SHALL 結果を小数点以下2桁で丸める
3. WHEN growth_rateが異常値（例：10000%以上）である THEN Discount_Effectiveness_Analyzer SHALL 該当データを外れ値としてフラグ付けする

### Requirement 3

**User Story:** As a データアナリスト, I want to 価格帯を自動分類する, so that 価格帯別の分析ができる.

#### Acceptance Criteria

1. WHEN our_priceが存在する THEN Discount_Effectiveness_Analyzer SHALL 以下の価格帯に分類する：1~1000, 1001~2000, 2001~3000, 3001~5000, 5001~10000, 10001~50000, 50001以上
2. WHEN our_priceが0以下または欠損値である THEN Discount_Effectiveness_Analyzer SHALL 価格帯を「Unknown」として分類する

### Requirement 4

**User Story:** As a データアナリスト, I want to PF×価格帯ごとに割引率と売上伸び率の関係を分析する, so that 最適な割引戦略を立案できる.

#### Acceptance Criteria

1. WHEN 分析を実行する THEN Discount_Effectiveness_Analyzer SHALL PFと価格帯の組み合わせごとにデータをグループ化する
2. WHEN グループ化されたデータに対して THEN Discount_Effectiveness_Analyzer SHALL 割引率（current_discount_percent）と売上伸び率（growth_rate）の相関係数を計算する
3. WHEN グループ化されたデータに対して THEN Discount_Effectiveness_Analyzer SHALL 回帰分析を実行して割引率が売上伸び率に与える影響係数を算出する
4. WHEN サンプル数が10未満のグループが存在する THEN Discount_Effectiveness_Analyzer SHALL 該当グループを「サンプル不足」としてマークし統計分析から除外する

### Requirement 5

**User Story:** As a データアナリスト, I want to PF×価格帯ごとに最適割引率を試算する, so that 具体的な割引率の推奨値を得られる.

#### Acceptance Criteria

1. WHEN 回帰分析結果が存在する THEN Discount_Effectiveness_Analyzer SHALL 売上伸び率を最大化する割引率を推定する
2. WHEN 最適割引率を計算する THEN Discount_Effectiveness_Analyzer SHALL 割引率の実用範囲（0%~50%）内で推奨値を算出する
3. WHEN 統計的に有意な関係が見られない場合（p値 > 0.05） THEN Discount_Effectiveness_Analyzer SHALL 「統計的に有意な関係なし」と報告する

### Requirement 6

**User Story:** As a データアナリスト, I want to 分析結果をHTMLレポートとして出力する, so that ブラウザで視覚的に確認できる.

#### Acceptance Criteria

1. WHEN 分析が完了する THEN Discount_Effectiveness_Analyzer SHALL HTMLファイルを生成する
2. WHEN HTMLレポートを生成する THEN Discount_Effectiveness_Analyzer SHALL PF×価格帯ごとの分析サマリーテーブルを含める
3. WHEN HTMLレポートを生成する THEN Discount_Effectiveness_Analyzer SHALL 割引率と売上伸び率の散布図をPF×価格帯ごとに含める
4. WHEN HTMLレポートを生成する THEN Discount_Effectiveness_Analyzer SHALL 最適割引率の推奨値一覧テーブルを含める

### Requirement 7

**User Story:** As a データアナリスト, I want to 分析結果をExcelファイルとして出力する, so that 詳細データを加工・共有できる.

#### Acceptance Criteria

1. WHEN 分析が完了する THEN Discount_Effectiveness_Analyzer SHALL Excelファイル（.xlsx）を生成する
2. WHEN Excelファイルを生成する THEN Discount_Effectiveness_Analyzer SHALL 「サマリー」シートにPF×価格帯ごとの統計値を出力する
3. WHEN Excelファイルを生成する THEN Discount_Effectiveness_Analyzer SHALL 「詳細データ」シートに全レコードと計算結果を出力する
4. WHEN Excelファイルを生成する THEN Discount_Effectiveness_Analyzer SHALL 「推奨割引率」シートに最適割引率の推奨値を出力する

### Requirement 8

**User Story:** As a データアナリスト, I want to 分析結果をシリアライズして保存・読み込みする, so that 分析結果を再利用できる.

#### Acceptance Criteria

1. WHEN 分析結果を保存する THEN Discount_Effectiveness_Analyzer SHALL JSON形式でシリアライズする
2. WHEN JSON形式で保存した分析結果を読み込む THEN Discount_Effectiveness_Analyzer SHALL 元の分析結果オブジェクトを復元する
3. WHEN シリアライズ後にデシリアライズする THEN Discount_Effectiveness_Analyzer SHALL 元のデータと同一の値を保持する（ラウンドトリップ整合性）
