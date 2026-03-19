# Implementation Plan

- [x] 1. プロジェクト構造とデータモデルの作成





  - [ ] 1.1 データモデルクラスを作成する
    - RegressionCoefficient, RegressionResult, AnalysisInterpretation, AnalysisResult をdataclassで定義
    - src/uplift_models.py に配置
    - _Requirements: 4.1, 4.2, 4.3, 4.4_




  - [ ]* 1.2 Property Test: JSON出力のラウンドトリップ
    - **Property 10: JSON出力のラウンドトリップ**
    - **Validates: Requirements 5.3**

- [ ] 2. データ読み込みと前処理の実装
  - [x] 2.1 DataLoaderクラスを実装する


    - タブ区切りファイルの読み込み機能
    - 必要カラムの存在検証機能
    - src/uplift_data_loader.py に配置
    - _Requirements: 1.1, 1.2_
  - [ ]* 2.2 Property Test: カラム検証の正確性
    - **Property 1: カラム検証の正確性**




    - **Validates: Requirements 1.2**
  - [ ] 2.3 DataProcessorクラスを実装する
    - 割引率文字列のパース機能（"20.01", "5.20%~25%" → 数値）
    - データクレンジング機能
    - src/uplift_data_processor.py に配置
    - _Requirements: 1.3_
  - [ ]* 2.4 Property Test: 割引率パースの正確性
    - **Property 2: 割引率パースの正確性**
    - **Validates: Requirements 1.3**

- [ ] 3. Uplift計算の実装
  - [ ] 3.1 UpliftCalculatorクラスを実装する
    - Uplift = (promotion_ops / past_month_gms - 1) × 100 の計算

    - past_month_gms=0またはNULLのレコード除外
    - DataFrameへのupliftカラム追加
    - src/uplift_calculator.py に配置




    - _Requirements: 2.1, 2.2, 2.3_
  - [ ]* 3.2 Property Test: Uplift計算の正確性
    - **Property 3: Uplift計算の正確性**
    - **Validates: Requirements 2.1**
  - [ ]* 3.3 Property Test: ゼロ・NULL除外の正確性
    - **Property 4: ゼロ・NULL除外の正確性**
    - **Validates: Requirements 2.2**
  - [ ]* 3.4 Property Test: Upliftカラム追加の不変性
    - **Property 5: Upliftカラム追加の不変性**
    - **Validates: Requirements 2.3**

- [ ] 4. Checkpoint - テストが全て通ることを確認
  - Ensure all tests pass, ask the user if questions arise.





- [ ] 5. 統計分析の実装
  - [ ] 5.1 StatisticalAnalyzerクラスを実装する
    - statsmodelsを使用した重回帰分析（our_price, discount_percent, 交互作用項）
    - 係数、p値、R²の算出
    - 結果の解釈と結論導出
    - src/uplift_statistical_analyzer.py に配置




    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  - [ ]* 5.2 Property Test: 有意性判定の正確性
    - **Property 7: 有意性判定の正確性**


    - **Validates: Requirements 4.2**
  - [ ]* 5.3 Property Test: R²値の範囲
    - **Property 8: R²値の範囲**




    - **Validates: Requirements 4.3**
  - [ ]* 5.4 Property Test: 交互作用効果の結論ロジック
    - **Property 9: 交互作用効果の結論ロジック**
    - **Validates: Requirements 4.4**

- [ ] 6. 視覚化の実装
  - [ ] 6.1 Visualizerクラスを実装する
    - 散布図生成（price vs uplift, discount vs uplift）
    - ヒートマップ生成（price × discount のUplift平均）
    - PNG保存機能
    - src/uplift_visualizer.py に配置
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  - [ ]* 6.2 Property Test: ビニング処理の正確性
    - **Property 6: ビニング処理の正確性**
    - **Validates: Requirements 3.4**

- [ ] 7. レポート生成と統合
  - [ ] 7.1 ReportGeneratorクラスを実装する
    - コンソールへのサマリー表示
    - JSON出力機能
    - src/uplift_report_generator.py に配置
    - _Requirements: 5.1, 5.2, 5.3_
  - [ ] 7.2 メインスクリプトを作成する
    - 全コンポーネントを統合
    - コマンドライン引数でファイルパスを受け取る
    - src/run_uplift_analysis.py に配置
    - _Requirements: 1.1, 5.1, 5.2, 5.3_
  - [ ] 7.3 バッチファイルを作成する
    - run_uplift_analysis.bat を作成
    - _Requirements: 1.1_

- [ ] 8. Final Checkpoint - 全テストが通ることを確認
  - Ensure all tests pass, ask the user if questions arise.
