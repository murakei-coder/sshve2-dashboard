# Implementation Plan

- [x] 1. プロジェクト構造とコアインターフェースのセットアップ



  - [x] 1.1 新しいモジュールファイルの作成（discount_analyzer.py, discount_models.py, discount_constants.py）

    - src/discount_analyzer.py, src/discount_models.py, src/discount_constants.pyを作成
    - 必須カラム定義、価格帯定義を含める
    - _Requirements: 1.1, 3.1_
  - [x] 1.2 データモデルの定義


    - SegmentAnalysisResult, OptimalDiscountRecommendation, AnalysisResultsデータクラスを実装
    - _Requirements: 4.1, 5.1_

- [x] 2. データ読み込みとバリデーション機能の実装



  - [x] 2.1 DataLoaderクラスの実装
    - タブ区切りファイルの読み込み機能
    - 大容量ファイル対応（チャンク読み込み）

    - _Requirements: 1.1_
  - [x] 2.2 DataValidatorクラスの実装
    - 必須カラムの存在チェック
    - 数値カラムのバリデーション
    - 無効行の除外とログ記録
    - _Requirements: 1.2, 1.3, 1.4_
  - [ ]* 2.3 Property 9のプロパティテスト作成
    - **Property 9: Missing Column Detection**
    - **Validates: Requirements 1.2**
  - [ ]* 2.4 Property 2のプロパティテスト作成
    - **Property 2: Invalid Data Exclusion**
    - **Validates: Requirements 1.3, 1.4**

- [x] 3. 売上伸び率計算機能の実装

  - [x] 3.1 GrowthRateCalculatorクラスの実装

    - growth_rate = (promotion_ops / past_month_gms - 1) * 100 の計算
    - 小数点以下2桁への丸め
    - 外れ値フラグの設定（10000%以上）
    - _Requirements: 2.1, 2.2, 2.3_
  - [ ]* 3.2 Property 1のプロパティテスト作成
    - **Property 1: Growth Rate Calculation Correctness**
    - **Validates: Requirements 2.1, 2.2**
  - [ ]* 3.3 Property 4のプロパティテスト作成
    - **Property 4: Outlier Flagging**
    - **Validates: Requirements 2.3**



- [ ] 4. 価格帯分類機能の実装
  - [x] 4.1 PriceBandClassifierクラスの実装
    - 価格帯の分類ロジック（1~1000, 1001~2000, etc.）
    - 0以下・欠損値のUnknown分類
    - _Requirements: 3.1, 3.2_
  - [ ]* 4.2 Property 3のプロパティテスト作成
    - **Property 3: Price Band Classification Correctness**
    - **Validates: Requirements 3.1, 3.2**


- [x] 5. Checkpoint - テスト確認

  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. 統計分析機能の実装
  - [x] 6.1 DiscountAnalyzerクラスの実装
    - PF×価格帯ごとのグループ化
    - 相関係数の計算
    - 回帰分析（scipy.stats.linregress使用）
    - サンプル数チェック（10未満は除外）
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  - [ ]* 6.2 Property 5のプロパティテスト作成
    - **Property 5: Correlation Coefficient Range**

    - **Validates: Requirements 4.2**

  - [ ]* 6.3 Property 6のプロパティテスト作成
    - **Property 6: Sample Size Threshold**
    - **Validates: Requirements 4.4**

- [ ] 7. 最適割引率推定機能の実装
  - [x] 7.1 OptimalDiscountEstimatorクラスの実装
    - 回帰分析結果からの最適割引率推定
    - 0-50%範囲内への制約
    - 統計的有意性の判定（p値 > 0.05）
    - _Requirements: 5.1, 5.2, 5.3_
  - [ ]* 7.2 Property 7のプロパティテスト作成
    - **Property 7: Optimal Discount Rate Range**
    - **Validates: Requirements 5.2**


  - [ ]* 7.3 Property 8のプロパティテスト作成
    - **Property 8: Statistical Significance Reporting**
    - **Validates: Requirements 5.3**

- [x] 8. Checkpoint - テスト確認
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. HTMLレポート生成機能の実装

  - [x] 9.1 HTMLReportGeneratorクラスの実装

    - サマリーテーブルの生成
    - 散布図の生成（matplotlib/plotly使用）
    - 推奨割引率一覧テーブルの生成
    - HTMLテンプレートの作成
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  - [ ]* 9.2 Property 10のプロパティテスト作成
    - **Property 10: HTML Report Content Completeness**
    - **Validates: Requirements 6.2, 6.3, 6.4**



- [ ] 10. Excel出力機能の実装
  - [x] 10.1 ExcelExporterクラスの実装
    - openpyxlを使用したExcel生成
    - サマリーシートの作成
    - 詳細データシートの作成
    - 推奨割引率シートの作成
    - _Requirements: 7.1, 7.2, 7.3, 7.4_
  - [x]* 10.2 Property 11のプロパティテスト作成

    - **Property 11: Excel Sheet Completeness**

    - **Validates: Requirements 7.2, 7.3, 7.4**

- [ ] 11. シリアライズ機能の実装
  - [x] 11.1 JSONSerializerクラスの実装
    - AnalysisResultsのJSON変換
    - JSONからの復元
    - _Requirements: 8.1, 8.2, 8.3_
  - [ ]* 11.2 Property 12のプロパティテスト作成
    - **Property 12: Serialization Round Trip**
    - **Validates: Requirements 8.1, 8.2, 8.3**

- [x] 12. メインアプリケーションの統合




  - [x] 12.1 メイン実行スクリプトの作成

    - コマンドライン引数の処理
    - 全コンポーネントの統合
    - エラーハンドリング
    - _Requirements: 1.1, 6.1, 7.1_

  - [x] 12.2 バッチ実行スクリプトの更新

    - run_discount_analysis.batの作成
    - _Requirements: 1.1_

- [x] 13. Final Checkpoint - 全テスト確認
  - Ensure all tests pass, ask the user if questions arise.
