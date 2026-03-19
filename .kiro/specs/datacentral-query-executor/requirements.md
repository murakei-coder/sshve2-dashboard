# 要件定義書

## はじめに

DataCentralからSQLクエリを取得し、日付を書き換えてローカルで実行し、結果をインタラクティブなダッシュボードで分析するツールです。このツールは、プロモーションデータの分析を自動化し、PF/GL/Seller/Team別のOPS/T30 GMS係数の計算、Suppression Status分析、OP2目標からのチーム割り当てまでを一貫して実行します。

## 用語集

- **DataCentral**: Amazon社内のデータウェアハウスプラットフォーム
- **Query_Executor**: SQLクエリを実行するシステムコンポーネント
- **Date_Replacer**: クエリ内の日付文字列を置換するコンポーネント
- **Query_Fetcher**: DataCentralからクエリを取得するコンポーネント
- **Dashboard**: データをインタラクティブに表示・フィルタリングするUIコンポーネント
- **Coefficient_Calculator**: OPS/T30 GMS係数を計算するコンポーネント
- **Team_Allocator**: OP2目標をチームに割り当てるコンポーネント
- **Seller_Mapper**: CIDとTeam/Aliasを紐付けるコンポーネント
- **CLI**: コマンドラインインターフェース
- **PF**: プラットフォーム（例：Marketplace）
- **GL**: 商品カテゴリ（例：Electronics, Apparel）
- **OPS**: Ordered Product Sales（注文商品売上）
- **T30 GMS**: 過去30日間のGross Merchandise Sales（総商品販売額）
- **CID**: Customer ID（Seller ID）
- **Suppression Status**: 商品の抑制状態（検索結果に表示されない状態）
- **OP2**: Operating Plan 2（年間事業計画の第2四半期目標）
- **Top 20K/40K**: 売上上位20,000/40,000のSeller

## 要件

### 要件1: DataCentralからのクエリ取得

**ユーザーストーリー:** データアナリストとして、DataCentralのURLを指定してSQLクエリを自動的に取得したい。これにより、手動でクエリをコピー＆ペーストする手間を省くことができる。

#### 受入基準

1. WHEN ユーザーがDataCentralのURL（例：https://datacentral.a2z.com/dw-platform/servlet/dwp/template/EtlViewExtractJobs.vm/job_profile_id/14164725）を指定した場合、THE Query_Fetcher SHALL そのURLからSQLクエリテキストを取得する
2. IF DataCentralへの接続が認証を必要とする場合、THEN THE Query_Fetcher SHALL 適切な認証情報を使用してアクセスする
3. IF URLが無効またはアクセスできない場合、THEN THE Query_Fetcher SHALL 明確なエラーメッセージを返す
4. WHEN クエリの取得に成功した場合、THE Query_Fetcher SHALL クエリテキスト全体を文字列として返す

### 要件2: クエリ内の日付置換

**ユーザーストーリー:** データアナリストとして、取得したクエリの特定行の日付を指定した日付に自動的に書き換えたい。これにより、異なる日付でのデータ分析を効率的に実行できる。

#### 受入基準

1. WHEN ユーザーが日付（'yyyy-mm-dd'形式、例：'2026-02-02'）を指定した場合、THE Date_Replacer SHALL クエリの6行目から11行目に含まれる日付文字列を指定された日付に置換する
2. THE Date_Replacer SHALL 'yyyy-mm-dd'形式の日付パターンを正確に識別する
3. WHEN 6～11行目に複数の日付が存在する場合、THE Date_Replacer SHALL すべての日付を指定された日付に置換する
4. WHEN 6～11行目に日付が存在しない場合、THE Date_Replacer SHALL クエリを変更せずに返す
5. IF 指定された日付が'yyyy-mm-dd'形式に従っていない場合、THEN THE Date_Replacer SHALL エラーメッセージを返す

### 要件3: ローカルでのクエリ実行

**ユーザーストーリー:** データアナリストとして、書き換えたクエリをローカルPCのデータベースに対して実行したい。これにより、DataCentral上で直接実行するよりも柔軟にデータを取得できる。

#### 受入基準

1. WHEN 書き換えられたクエリが提供された場合、THE Query_Executor SHALL ローカルデータベース接続を使用してクエリを実行する
2. THE Query_Executor SHALL SQLiteデータベース（database.sqlite）に接続する
3. IF データベース接続が失敗した場合、THEN THE Query_Executor SHALL 接続エラーの詳細を含むエラーメッセージを返す
4. IF クエリ実行が失敗した場合、THEN THE Query_Executor SHALL SQLエラーの詳細を含むエラーメッセージを返す
5. WHEN クエリ実行が成功した場合、THE Query_Executor SHALL すべての結果行を返す

### 要件4: Sellerマスタデータの読み込み

**ユーザーストーリー:** データアナリストとして、CIDとTeam/Aliasの紐付けデータを読み込みたい。これにより、Seller別、Team別、Alias別の分析が可能になる。

#### 受入基準

1. THE Seller_Mapper SHALL Excelファイル（C:\Users\murakei\Desktop\3PEITS_AI\Opp_Dashboard\raw\EITS_Seller_list.xlsx）からSellerマスタデータを読み込む
2. THE Seller_Mapper SHALL CID（merchant_customer_id）、Team、Aliasのマッピングを保持する
3. IF Excelファイルが存在しない場合、THEN THE Seller_Mapper SHALL ファイルパスを含むエラーメッセージを返す
4. IF Excelファイルの形式が不正な場合、THEN THE Seller_Mapper SHALL 期待される形式を説明するエラーメッセージを返す
5. WHEN マスタデータの読み込みが成功した場合、THE Seller_Mapper SHALL 読み込まれたSeller数を確認メッセージとして返す

### 要件5: クエリ結果とSellerマスタの結合

**ユーザーストーリー:** データアナリストとして、クエリ結果にTeamとAliasの情報を追加したい。これにより、組織構造に基づいた分析が可能になる。

#### 受入基準

1. WHEN クエリ結果とSellerマスタデータが利用可能な場合、THE Seller_Mapper SHALL merchant_customer_idをキーとして両データを結合する
2. THE Seller_Mapper SHALL 結合後のデータにteamカラムとaliasカラムを追加する
3. WHEN merchant_customer_idがマスタデータに存在しない場合、THE Seller_Mapper SHALL teamとaliasをNULLまたは"Unknown"として設定する
4. THE Seller_Mapper SHALL 元のクエリ結果のすべてのカラムを保持する

### 要件6: インタラクティブダッシュボードの表示

**ユーザーストーリー:** データアナリストとして、データをインタラクティブに表示・フィルタリングできるダッシュボードを使用したい。これにより、様々な切り口でデータを分析できる。

#### 受入基準

1. THE Dashboard SHALL Webブラウザでアクセス可能なインターフェースを提供する
2. THE Dashboard SHALL 結合されたデータをテーブル形式で表示する
3. THE Dashboard SHALL PF（プラットフォーム）でフィルタリング機能を提供する
4. THE Dashboard SHALL GL（商品カテゴリ）でフィルタリング機能を提供する
5. THE Dashboard SHALL Seller（CID）でフィルタリング機能を提供する
6. THE Dashboard SHALL Teamでフィルタリング機能を提供する
7. THE Dashboard SHALL Aliasでフィルタリング機能を提供する
8. THE Dashboard SHALL Suppression Statusでフィルタリング機能を提供する
9. THE Dashboard SHALL Top 20K/40Kステータスでフィルタリング機能を提供する
10. WHEN 複数のフィルタが適用された場合、THE Dashboard SHALL すべてのフィルタ条件を満たすデータのみを表示する

### 要件7: OPS/T30 GMS係数の計算と表示

**ユーザーストーリー:** データアナリストとして、GL別、Suppression Status別のOPS/T30 GMS係数を確認したい。これにより、各セグメントの効率性を理解できる。

#### 受入基準

1. THE Coefficient_Calculator SHALL GL別にOPS/T30 GMS係数を計算する
2. THE Coefficient_Calculator SHALL Suppression Status別にOPS/T30 GMS係数を計算する
3. THE Coefficient_Calculator SHALL 係数を「total_promotion_ops / total_t30d_gms」として計算する
4. WHEN total_t30d_gmsがゼロの場合、THE Coefficient_Calculator SHALL 係数をNULLまたは無限大として扱う
5. THE Dashboard SHALL GL別係数を専用のセクションまたはテーブルで表示する
6. THE Dashboard SHALL Suppression Status別係数を専用のセクションまたはテーブルで表示する
7. THE Dashboard SHALL 各係数に対応するデータ件数とサンプルサイズを表示する

### 要件8: Seller/Team/Alias別の集計表示

**ユーザーストーリー:** データアナリストとして、Seller別、Team別、Alias別の集計データを確認したい。これにより、個別のパフォーマンスを評価できる。

#### 受入基準

1. THE Dashboard SHALL Seller（CID）別の集計テーブルを表示する
2. THE Dashboard SHALL Team別の集計テーブルを表示する
3. THE Dashboard SHALL Alias別の集計テーブルを表示する
4. WHEN 集計を表示する場合、THE Dashboard SHALL 以下のメトリクスを含める：
   - ASIN数（asin_count）
   - 合計T30 GMS（total_t30d_gms）
   - 合計T30 Units（total_t30d_units）
   - 合計Promotion OPS（total_promotion_ops）
   - 合計Promotion Units（total_promotion_units）
   - OPS/T30 GMS係数
5. THE Dashboard SHALL 集計テーブルをメトリクスでソート可能にする

### 要件9: OP2目標からのT30 GMS必要量計算

**ユーザーストーリー:** マネージャーとして、OP2のOPS目標を入力し、必要なT30 GMSを計算したい。これにより、目標達成に必要なアクション量を把握できる。

#### 受入基準

1. THE Dashboard SHALL OP2 OPS目標を入力するフィールドを提供する
2. WHEN OP2 OPS目標が入力された場合、THE Team_Allocator SHALL 全体のOPS/T30 GMS係数を使用して必要なT30 GMSを計算する
3. THE Team_Allocator SHALL 必要なT30 GMSを「OP2 OPS目標 / OPS/T30 GMS係数」として計算する
4. THE Dashboard SHALL 計算された必要T30 GMSを表示する
5. IF OPS/T30 GMS係数がゼロまたは利用不可の場合、THEN THE Team_Allocator SHALL エラーメッセージを表示する

### 要件10: Top 20K/40K/その他別の目標分解

**ユーザーストーリー:** マネージャーとして、必要なT30 GMSをTop 20K、Top 40K、その他のセグメント別に分解したい。これにより、各セグメントの貢献度を理解できる。

#### 受入基準

1. THE Team_Allocator SHALL 現在のデータからTop 20K、Top 40K、その他の各セグメントのT30 GMS構成比を計算する
2. WHEN 必要T30 GMSが計算された場合、THE Team_Allocator SHALL 構成比を使用して各セグメントの必要T30 GMSを計算する
3. THE Dashboard SHALL Top 20K、Top 40K、その他別の必要T30 GMSを表示する
4. THE Dashboard SHALL 各セグメントの構成比（パーセンテージ）を表示する

### 要件11: GL別の目標分解

**ユーザーストーリー:** マネージャーとして、必要なT30 GMSをGL（商品カテゴリ）別に分解したい。これにより、どのカテゴリに注力すべきかを理解できる。

#### 受入基準

1. THE Team_Allocator SHALL 現在のデータから各GLのT30 GMS構成比を計算する
2. WHEN 必要T30 GMSが計算された場合、THE Team_Allocator SHALL 構成比を使用して各GLの必要T30 GMSを計算する
3. THE Dashboard SHALL GL別の必要T30 GMSをテーブルまたはチャートで表示する
4. THE Dashboard SHALL 各GLの構成比（パーセンテージ）を表示する
5. THE Dashboard SHALL GL別の必要T30 GMSを降順でソートする

### 要件12: Team別の目標割り当て

**ユーザーストーリー:** マネージャーとして、必要なT30 GMSを各Teamに割り当てたい。これにより、各チームの目標を明確にできる。

#### 受入基準

1. THE Team_Allocator SHALL 現在のデータから各TeamのT30 GMS構成比を計算する
2. WHEN 必要T30 GMSが計算された場合、THE Team_Allocator SHALL 構成比を使用して各Teamの必要T30 GMSを計算する
3. THE Dashboard SHALL Team別の割り当てT30 GMSをテーブルで表示する
4. THE Dashboard SHALL 各Teamの現在のT30 GMSと必要T30 GMSを並べて表示する
5. THE Dashboard SHALL 各Teamの達成率（現在/必要）を表示する
6. THE Dashboard SHALL Team別の割り当てをCSVまたはExcelファイルとしてエクスポート可能にする

### 要件13: Suppression Status改善によるIncremental OPS計算

**ユーザーストーリー:** アカウントマネージャーとして、Suppression Statusを改善した場合のIncremental OPSを計算したい。これにより、Suppression解消の優先順位を決定できる。

#### 受入基準

1. THE Dashboard SHALL Seller別の現在のSuppression Rate（抑制されているASINの割合）を表示する
2. THE Dashboard SHALL Team別の現在のSuppression Rateを表示する
3. THE Dashboard SHALL Suppression Rate改善シミュレーション機能を提供する
4. WHEN ユーザーがSeller/TeamとSuppression Rate改善目標（例：30%→20%）を入力した場合、THE Coefficient_Calculator SHALL Incremental OPSを計算する
5. THE Coefficient_Calculator SHALL Incremental OPSを「(改善前Rate - 改善後Rate) × T30 GMS × Suppression別OPS/T30 GMS係数」として計算する
6. THE Dashboard SHALL 計算されたIncremental OPSを表示する
7. THE Dashboard SHALL 複数のSeller/Teamに対するSuppression改善シミュレーションを一括実行可能にする

### 要件14: データの永続化とエクスポート

**ユーザーストーリー:** データアナリストとして、分析結果を保存し、他のツールで使用したい。これにより、レポート作成や追加分析が可能になる。

#### 受入基準

1. THE Dashboard SHALL 現在表示されているデータをCSVファイルとしてエクスポート可能にする
2. THE Dashboard SHALL 現在表示されているデータをExcelファイルとしてエクスポート可能にする
3. THE Dashboard SHALL 計算された係数と目標割り当てをJSON形式で保存可能にする
4. WHEN ユーザーがエクスポートを実行した場合、THE Dashboard SHALL ファイルをダウンロードまたは指定の場所に保存する
5. THE Dashboard SHALL エクスポートファイルに実行日時とフィルタ条件を含める

### 要件15: コマンドラインインターフェース

**ユーザーストーリー:** データアナリストとして、コマンドラインまたはバッチファイルからツールを実行したい。これにより、既存のワークフローに統合し、自動化スクリプトから呼び出すことができる。

#### 受入基準

1. THE CLI SHALL コマンドライン引数としてDataCentral URLを受け取る
2. THE CLI SHALL コマンドライン引数として置換する日付（'yyyy-mm-dd'形式）を受け取る
3. WHERE データベース接続情報が必要な場合、THE CLI SHALL コマンドライン引数またはオプションとしてデータベースパスを受け取る
4. WHERE Sellerマスタファイルパスが必要な場合、THE CLI SHALL コマンドライン引数またはオプションとしてファイルパスを受け取る
5. THE CLI SHALL ダッシュボードモードを起動するオプションを提供する
6. WHEN 必須引数が不足している場合、THE CLI SHALL 使用方法を説明するヘルプメッセージを表示する
7. THE CLI SHALL Windowsコマンドプロンプト（cmd.exe）から実行可能である
8. THE CLI SHALL バッチファイル（.bat）から呼び出し可能である
9. WHEN ダッシュボードモードで起動された場合、THE CLI SHALL ローカルWebサーバーを起動し、ブラウザでダッシュボードを開く

### 要件16: エラーハンドリングとユーザーフィードバック

**ユーザーストーリー:** データアナリストとして、ツールの実行中に問題が発生した場合、明確なエラーメッセージを受け取りたい。これにより、問題を迅速に特定し、修正できる。

#### 受入基準

1. WHEN 任意の処理ステップでエラーが発生した場合、THE CLI SHALL エラーの種類と原因を説明する明確なメッセージを表示する
2. THE CLI SHALL エラーメッセージを標準エラー出力（stderr）に出力する
3. WHEN エラーが発生した場合、THE CLI SHALL ゼロ以外の終了コードを返す
4. WHEN すべての処理が成功した場合、THE CLI SHALL 終了コード0を返す
5. THE CLI SHALL 各主要ステップ（取得、置換、実行、結合、ダッシュボード起動）の進行状況を標準出力（stdout）に表示する
6. THE Dashboard SHALL エラーが発生した場合、ユーザーフレンドリーなエラーメッセージをUI上に表示する

### 要件17: 認証とセキュリティ

**ユーザーストーリー:** データアナリストとして、DataCentralへのアクセスに必要な認証情報を安全に提供したい。これにより、セキュリティを維持しながらツールを使用できる。

#### 受入基準

1. WHERE DataCentralが認証を必要とする場合、THE Query_Fetcher SHALL 環境変数または設定ファイルから認証情報を読み取る
2. THE Query_Fetcher SHALL 認証情報をコマンドライン引数として受け取らない（セキュリティのため）
3. IF 認証情報が見つからない場合、THEN THE Query_Fetcher SHALL 認証情報の設定方法を説明するエラーメッセージを返す
4. THE Query_Fetcher SHALL HTTPSを使用してDataCentralと通信する
5. THE Dashboard SHALL ローカルホスト（127.0.0.1）でのみアクセス可能にする（外部アクセスを防ぐ）

### 要件18: 既存プロジェクト構造との統合

**ユーザーストーリー:** データアナリストとして、既存のプロジェクト構造とワークフローに一貫性のある方法でツールを統合したい。これにより、他の分析ツールと同じ方法で使用できる。

#### 受入基準

1. THE CLI SHALL Pythonスクリプトとしてsrc/ディレクトリに配置される
2. THE CLI SHALL 既存のバッチファイル（run_discount_analysis.bat、run_uplift_analysis.batなど）と同様のパターンで実行可能なバッチファイルを持つ
3. THE CLI SHALL requirements.txtに必要な依存関係を記載する
4. THE CLI SHALL 既存のプロジェクトと同じPython環境で実行可能である
5. THE Dashboard SHALL 既存の分析ツール（discount_analyzer、uplift_analyzer）と一貫性のあるUI/UXパターンを使用する
