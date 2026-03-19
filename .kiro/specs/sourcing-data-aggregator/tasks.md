# Implementation Plan: Sourcing Data Aggregator

## Overview

このプランは、CSVファイルからソーシングデータを読み込み、MCID単位で集約してHTMLとExcelレポートを生成するシンプルなツールを実装する。既存のプロジェクト構造に従い、src/ディレクトリにスクリプトを配置し、バッチファイルで実行できるようにする。

## Tasks

- [x] 1. プロジェクト構造とデータモデルのセットアップ
  - src/sourcing_aggregator.py を作成
  - データクラス（AggregatedResult, ValidationResult）を定義
  - 必要な定数（REQUIRED_COLUMNS）を定義
  - _Requirements: 7.1_

- [ ] 2. CSVLoader の実装
  - [x] 2.1 CSVLoader クラスを実装
    - load() メソッドを実装（UTF-8エンコーディング、失敗時はcp932フォールバック）
    - FileNotFoundError と UnicodeDecodeError のハンドリング
    - _Requirements: 1.1, 1.4, 1.5_
  
  - [ ]* 2.2 CSVLoader のプロパティテストを作成
    - **Property 1: CSV Loading with UTF-8**
    - **Validates: Requirements 1.1**
  
  - [ ]* 2.3 CSVLoader のユニットテストを作成
    - ファイルが存在しない場合のテスト
    - エンコーディングフォールバックのテスト
    - _Requirements: 1.4, 1.5_

- [ ] 3. DataValidator の実装
  - [x] 3.1 DataValidator クラスを実装
    - validate() メソッドを実装（必須カラムチェック）
    - clean() メソッドを実装（数値変換、欠損値除外）
    - _Requirements: 1.2, 1.3, 2.5, 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ]* 3.2 DataValidator のプロパティテストを作成
    - **Property 2: Complete Row Loading**
    - **Property 3: Missing Column Detection**
    - **Validates: Requirements 1.2, 1.3, 5.1, 5.2, 5.3, 5.4**
  
  - [ ]* 3.3 DataValidator のユニットテストを作成
    - 空のDataFrameのテスト
    - 非数値データのクリーニングテスト
    - _Requirements: 2.5, 5.5_

- [ ] 4. MCIDAggregator の実装
  - [x] 4.1 MCIDAggregator クラスを実装
    - aggregate() メソッドを実装（MCID単位でグループ化と集約）
    - _calculate_sourced_gms() ヘルパーメソッドを実装
    - _calculate_percentage() ヘルパーメソッドを実装（ゼロ除算対応）
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.6_
  
  - [ ]* 4.2 MCIDAggregator のプロパティテストを作成
    - **Property 4: MCID Grouping Completeness**
    - **Property 5: Aggregation Calculation Correctness**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.6**
  
  - [ ]* 4.3 MCIDAggregator のユニットテストを作成
    - ゼロ除算のエッジケーステスト
    - 複数MCIDの集約テスト
    - _Requirements: 2.6_

- [x] 5. Checkpoint - コア機能の動作確認
  - すべてのテストが通ることを確認し、質問があればユーザーに確認する

- [ ] 6. HTMLReportGenerator の実装
  - [x] 6.1 HTMLReportGenerator クラスを実装
    - generate() メソッドを実装（HTMLテーブル生成）
    - _format_number() ヘルパーメソッドを実装（カンマ区切り）
    - _format_percentage() ヘルパーメソッドを実装（小数点2桁）
    - タイムスタンプとソースファイル名を含める
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_
  
  - [ ]* 6.2 HTMLReportGenerator のプロパティテストを作成
    - **Property 6: HTML Table Structure**
    - **Property 7: Number Formatting in HTML**
    - **Property 8: HTML Timestamp Presence**
    - **Property 9: Timestamped Filename Generation**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7**
  
  - [ ]* 6.3 HTMLReportGenerator のユニットテストを作成
    - 大きな数値のフォーマットテスト
    - パーセンテージフォーマットテスト
    - _Requirements: 3.4, 3.5_

- [ ] 7. ExcelExporter の実装
  - [x] 7.1 ExcelExporter クラスを実装
    - export() メソッドを実装（Excelファイル生成）
    - 数値フォーマットとパーセンテージフォーマットを適用
    - ヘッダーのスタイリング（太字、背景色）
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [ ]* 7.2 ExcelExporter のプロパティテストを作成
    - **Property 13: Excel File Generation with Formatting**
    - **Property 14: Consistent Output Filenames**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5**
  
  - [ ]* 7.3 ExcelExporter のユニットテストを作成
    - Excelファイルの読み込みと検証
    - フォーマットの確認
    - _Requirements: 6.3, 6.4_

- [ ] 8. メインスクリプトの実装
  - [x] 8.1 run_sourcing_aggregator.py を作成
    - コマンドライン引数の解析（input_file, output_dir）
    - ロギング設定（日本語メッセージ）
    - 各コンポーネントの統合
    - エラーハンドリング（日本語エラーメッセージ）
    - 進捗ログの出力
    - 出力ファイルパスの表示
    - _Requirements: 4.3, 4.4, 4.5, 7.4, 7.5, 7.6_
  
  - [ ]* 8.2 メインスクリプトのプロパティテストを作成
    - **Property 10: Progress Logging**
    - **Property 11: Output Location Display**
    - **Property 12: Japanese Error Messages**
    - **Property 15: Default Output Location**
    - **Property 16: Custom Output Location**
    - **Validates: Requirements 4.3, 4.4, 4.5, 7.5, 7.6**
  
  - [ ]* 8.3 メインスクリプトの統合テストを作成
    - エンドツーエンドの処理フロー
    - エラーケースの統合テスト
    - _Requirements: 4.3, 4.4, 4.5_

- [ ] 9. バッチファイルの作成
  - [x] 9.1 run_sourcing_aggregator.bat を作成
    - UTF-8コードページ設定
    - 仮想環境のアクティベーション（存在する場合）
    - 入力ファイルパスのプロンプト
    - Pythonスクリプトの実行
    - 完了メッセージの表示
    - 最後にpauseを追加
    - _Requirements: 4.1, 4.2, 4.6_

- [ ] 10. ドキュメントとREADMEの作成
  - [x] 10.1 README_sourcing_aggregator.md を作成
    - ツールの概要説明（日本語）
    - 使用方法（バッチファイルの実行手順）
    - 入力ファイルの要件
    - 出力ファイルの説明
    - トラブルシューティング
    - _Requirements: 4.1, 4.2_

- [x] 11. 最終チェックポイント
  - すべてのテストが通ることを確認
  - サンプルCSVファイルで動作確認
  - 質問があればユーザーに確認する

## Notes

- `*` マークのタスクはオプションで、より早いMVPのためにスキップ可能
- 各タスクは特定の要件を参照してトレーサビリティを確保
- チェックポイントで段階的な検証を実施
- プロパティテストは普遍的な正確性を検証
- ユニットテストは特定の例とエッジケースを検証
- すべてのメッセージとドキュメントは日本語で記述
