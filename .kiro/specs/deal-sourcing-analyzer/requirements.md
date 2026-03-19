# Requirements Document

## Introduction

Deal Sourcing Analyzerは、3Pセラーのディール（Deal）エントリー状況を分析するアプリケーションである。txtファイルからASIN×セラーデータを読み込み、Paid/Non-Paidセラー別、Price Band別、ASIN Tenure別にSourced率とOpportunityを可視化し、効率的なディールエントリー戦略の立案を支援する。

## Glossary

- **Deal_Sourcing_Analyzer**: 本分析アプリケーションの名称
- **Sourced**: Price&PointsDealFlagが"Sourced"の状態。ディールにエントリーできているASIN×セラーの組み合わせ
- **NonSourced**: Price&PointsDealFlagが"NonSourced"の状態。ディールにエントリーできていないASIN×セラーの組み合わせ
- **Opportunity**: NonSourcedのASIN×セラーの組み合わせが持つ潜在的なGMS/ASIN数
- **Paid_Seller**: Paid-Flagが"Y"のセラー
- **Non_Paid_Seller**: Paid-Flagが"N"のセラー
- **Price_Band**: 価格帯区分（1~1000, 1001~2000等）
- **ASIN_Tenure**: ASINの出品期間区分（0-30 days, 31-90 days等）
- **GMS**: Gross Merchandise Sales（総売上）
- **ASIN_Count**: ユニークASIN数
- **GMS_per_ASIN**: GMS÷ASIN_Countで算出される1ASINあたりの売上

## Requirements

### Requirement 1

**User Story:** As a 分析担当者, I want to 指定したtxtファイルを読み込む, so that 分析対象データを取得できる

#### Acceptance Criteria

1. WHEN ユーザーがファイル名を指定して読み込みを実行する THEN Deal_Sourcing_Analyzer SHALL 指定されたtxtファイルをdataフォルダから読み込む
2. WHEN txtファイルが正常に読み込まれる THEN Deal_Sourcing_Analyzer SHALL 以下のカラムを含むデータとしてパースする: asin, MERCHANT_CUSTOMER_ID, pf, gl, Paid-Flag, DealFlag, PointsDealFlag, Price&PointsDealFlag, RetailFlag, DomesticOOCFlag, PriceBand, ASINTenure, GMS, UNITS
3. IF 指定されたファイルが存在しない THEN Deal_Sourcing_Analyzer SHALL エラーメッセージを表示してユーザーに通知する
4. IF ファイルのフォーマットが不正である THEN Deal_Sourcing_Analyzer SHALL パースエラーの詳細を表示してユーザーに通知する

### Requirement 2

**User Story:** As a 分析担当者, I want to Paid/Non-PaidセラーごとのSourced状況を分析する, so that セラータイプ別のOpportunityを把握できる

#### Acceptance Criteria

1. WHEN データが読み込まれる THEN Deal_Sourcing_Analyzer SHALL Paid_SellerとNon_Paid_Sellerそれぞれについて、Sourced/NonSourcedの集計を行う
2. WHEN 集計が完了する THEN Deal_Sourcing_Analyzer SHALL 各セラータイプについてGMS合計、ASIN_Count、GMS_per_ASINを算出する
3. WHEN 分析結果を表示する THEN Deal_Sourcing_Analyzer SHALL Sourced率（Sourced ASIN数÷全ASIN数）を百分率で表示する
4. WHEN 分析結果を表示する THEN Deal_Sourcing_Analyzer SHALL NonSourcedのGMS合計をOpportunityとして表示する

### Requirement 3

**User Story:** As a 分析担当者, I want to Price Band別のSourced状況を分析する, so that 価格帯ごとのOpportunityを特定できる

#### Acceptance Criteria

1. WHEN データが読み込まれる THEN Deal_Sourcing_Analyzer SHALL 各Price_Bandについて、Sourced/NonSourcedの集計を行う
2. WHEN 集計が完了する THEN Deal_Sourcing_Analyzer SHALL 各Price_BandについてGMS合計、ASIN_Count、GMS_per_ASIN、Sourced率を算出する
3. WHEN 分析結果を表示する THEN Deal_Sourcing_Analyzer SHALL Price_Bandを価格順にソートして表示する
4. WHEN 分析結果を表示する THEN Deal_Sourcing_Analyzer SHALL 各Price_BandのNonSourced GMS（Opportunity）と全体に占める割合を表示する

### Requirement 4

**User Story:** As a 分析担当者, I want to ASIN Tenure別のSourced状況を分析する, so that 出品期間ごとのOpportunityを特定できる

#### Acceptance Criteria

1. WHEN データが読み込まれる THEN Deal_Sourcing_Analyzer SHALL 各ASIN_Tenureについて、Sourced/NonSourcedの集計を行う
2. WHEN 集計が完了する THEN Deal_Sourcing_Analyzer SHALL 各ASIN_TenureについてGMS合計、ASIN_Count、GMS_per_ASIN、Sourced率を算出する
3. WHEN 分析結果を表示する THEN Deal_Sourcing_Analyzer SHALL ASIN_Tenureを期間順にソートして表示する
4. WHEN 分析結果を表示する THEN Deal_Sourcing_Analyzer SHALL 各ASIN_TenureのNonSourced GMS（Opportunity）と全体に占める割合を表示する

### Requirement 5

**User Story:** As a 分析担当者, I want to Opportunity優先度を判断する, so that 効率的なディールエントリー戦略を立案できる

#### Acceptance Criteria

1. WHEN 分析結果を表示する THEN Deal_Sourcing_Analyzer SHALL 各セグメント（Price_Band/ASIN_Tenure）のSourced率が高い場合（80%以上）は「Opportunity少」と表示する
2. WHEN 分析結果を表示する THEN Deal_Sourcing_Analyzer SHALL NonSourced GMS÷全体GMS比率が高いセグメントを「高Opportunity」としてハイライト表示する
3. WHEN 分析結果を表示する THEN Deal_Sourcing_Analyzer SHALL GMS_per_ASINが高いセグメントを「強いASIN」として識別表示する

### Requirement 6

**User Story:** As a 分析担当者, I want to 分析結果をダッシュボード形式で閲覧する, so that 全体像を素早く把握できる

#### Acceptance Criteria

1. WHEN アプリケーションを起動する THEN Deal_Sourcing_Analyzer SHALL Webブラウザでアクセス可能なダッシュボードを表示する
2. WHEN ダッシュボードを表示する THEN Deal_Sourcing_Analyzer SHALL サマリー（全体Sourced率、総GMS、総Opportunity）を画面上部に表示する
3. WHEN ダッシュボードを表示する THEN Deal_Sourcing_Analyzer SHALL Paid/Non-Paid比較、Price Band分析、ASIN Tenure分析を個別セクションとして表示する
4. WHEN ダッシュボードを表示する THEN Deal_Sourcing_Analyzer SHALL グラフ（棒グラフ/円グラフ）を用いて視覚的に分析結果を表示する
