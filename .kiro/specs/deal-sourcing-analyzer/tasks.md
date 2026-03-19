# Implementation Plan

- [x] 1. プロジェクト構造とセットアップ






  - [x] 1.1 プロジェクトディレクトリ構造を作成

    - src/フォルダ配下にfile_loader.py, data_parser.py, analyzer.py, app.pyを配置
    - tests/フォルダを作成
    - requirements.txtを作成（streamlit, pandas, pytest, hypothesis）
    - _Requirements: 1.1_

  - [x] 1.2 定数とデータモデルを定義


    - constants.pyにREQUIRED_COLUMNS, PRICE_BAND_ORDER, TENURE_ORDERを定義
    - models.pyにSegmentAnalysisデータクラスを定義
    - _Requirements: 3.3, 4.3_

- [x] 2. FileLoaderの実装



  - [x] 2.1 FileLoaderクラスを実装


    - data_dir指定での初期化
    - load_file()メソッド：txtファイルを読み込みDataFrameを返す
    - list_available_files()メソッド：利用可能なファイル一覧を返す
    - _Requirements: 1.1_


  - [x] 2.2 FileLoaderのプロパティテストを作成

    - **Property 1: File Loading Consistency**
    - **Validates: Requirements 1.1, 1.2**

- [x] 3. DataParserの実装




  - [x] 3.1 DataParserクラスを実装

    - parse()メソッド：生データをDataFrameに変換
    - validate()メソッド：必須カラムとデータ型を検証
    - エラー時は詳細メッセージを含む例外をスロー
    - _Requirements: 1.2, 1.3, 1.4_


  - [x] 3.2 DataParserのユニットテストを作成

    - 正常データのパーステスト
    - 不正フォーマットのエラーハンドリングテスト
    - _Requirements: 1.2, 1.3, 1.4_

- [x] 4. Checkpoint - テスト確認




  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Analyzerの実装（基本集計）




  - [x] 5.1 Analyzerクラスの基本構造を実装

    - DataFrameを受け取る初期化
    - get_summary()メソッド：全体サマリーを返す
    - _Requirements: 2.1_


  - [x] 5.2 analyze_by_paid_flag()メソッドを実装

    - Paid-FlagでグループしてGMS、ASIN数、GMS/ASIN、Sourced率を集計
    - NonSourced GMSをOpportunityとして算出
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 5.3 Paid-Flag分析のプロパティテストを作成


    - **Property 2: Group Aggregation Accuracy**
    - **Property 3: Metric Calculation Consistency**
    - **Property 4: Sourced Rate Calculation**
    - **Property 5: Opportunity Equals NonSourced GMS**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4**

- [x] 6. Analyzerの実装（Price Band分析）



  - [x] 6.1 analyze_by_price_band()メソッドを実装
    - PriceBandでグループして集計
    - PRICE_BAND_ORDER順にソート
    - _Requirements: 3.1, 3.2, 3.3, 3.4_


  - [x] 6.2 Price Band分析のプロパティテストを作成

    - **Property 6: Price Band Sort Order**
    - **Validates: Requirements 3.3**

- [x] 7. Analyzerの実装（ASIN Tenure分析）



  - [x] 7.1 analyze_by_tenure()メソッドを実装
    - ASINTenureでグループして集計
    - TENURE_ORDER順にソート
    - _Requirements: 4.1, 4.2, 4.3, 4.4_


  - [x] 7.2 ASIN Tenure分析のプロパティテストを作成

    - **Property 7: ASIN Tenure Sort Order**
    - **Validates: Requirements 4.3**

- [x] 8. Opportunity判定ロジックの実装


  - [x] 8.1 calculate_opportunity_score()メソッドを実装


    - Sourced率80%以上は「低」Opportunity
    - NonSourced GMS比率が高いセグメントを「高」Opportunity
    - GMS/ASINが高いセグメントを「強いASIN」として識別
    - _Requirements: 5.1, 5.2, 5.3_


  - [x] 8.2 Opportunity判定のプロパティテストを作成

    - **Property 8: Opportunity Level Classification**
    - **Property 9: High Opportunity Identification**
    - **Validates: Requirements 5.1, 5.2**

- [x] 9. Checkpoint - テスト確認



  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Streamlitダッシュボードの実装



  - [x] 10.1 app.pyの基本構造を実装
    - ファイル選択UI（selectbox）
    - 分析開始ボタン
    - _Requirements: 6.1_



  - [x] 10.2 サマリーセクションを実装
    - 全体Sourced率、総GMS、総Opportunityを表示
    - st.metricを使用した見やすい表示
    - _Requirements: 6.2_



  - [x] 10.3 Paid/Non-Paid分析セクションを実装
    - 比較テーブルの表示
    - 棒グラフでの可視化
    - _Requirements: 6.3, 6.4_



  - [x] 10.4 Price Band分析セクションを実装
    - 価格帯別テーブルの表示
    - Opportunity判定のハイライト表示
    - 棒グラフでの可視化
    - _Requirements: 6.3, 6.4_



  - [x] 10.5 ASIN Tenure分析セクションを実装

    - 期間別テーブルの表示
    - Opportunity判定のハイライト表示
    - 棒グラフでの可視化
    - _Requirements: 6.3, 6.4_

- [x] 11. Final Checkpoint - 最終テスト確認
  - Ensure all tests pass, ask the user if questions arise.
