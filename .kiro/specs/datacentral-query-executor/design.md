# 設計書

## 概要

DataCentral Query Executorは、DataCentralからSQLクエリを取得し、日付を書き換えてローカルで実行し、結果をインタラクティブなWebダッシュボードで分析するツールです。このツールは、プロモーションデータの分析を自動化し、PF/GL/Seller/Team別の分析、OPS/T30 GMS係数の計算、OP2目標からのチーム割り当て、Suppression Status改善シミュレーションを提供します。

主要な機能：
- DataCentralからのクエリ取得と日付置換
- ローカルSQLiteデータベースでのクエリ実行
- Sellerマスタデータとの結合
- Webベースのインタラクティブダッシュボード
- 多次元フィルタリング（PF、GL、Seller、Team、Alias、Suppression Status）
- OPS/T30 GMS係数の計算と表示
- OP2目標からの必要T30 GMS計算とチーム割り当て
- Suppression改善によるIncremental OPS計算
- データのエクスポート機能

## アーキテクチャ

システムは以下のレイヤーで構成されます：

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                    │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Web Dashboard (Flask + HTML/JS)          │  │
│  │  - フィルタUI                                      │  │
│  │  - データテーブル表示                              │  │
│  │  - 係数表示                                        │  │
│  │  - 目標計算UI                                      │  │
│  │  - Suppressionシミュレーション                     │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    Business Logic Layer                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Coefficient  │  │    Team      │  │  Suppression │  │
│  │  Calculator  │  │  Allocator   │  │  Simulator   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │   Filter     │  │  Aggregator  │                    │
│  │   Engine     │  │              │                    │
│  └──────────────┘  └──────────────┘                    │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                      Data Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │    Query     │  │    Query     │  │   Seller     │  │
│  │   Fetcher    │  │   Executor   │  │   Mapper     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │    Date      │  │    Data      │                    │
│  │  Replacer    │  │   Exporter   │                    │
│  └──────────────┘  └──────────────┘                    │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    External Systems                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ DataCentral  │  │    SQLite    │  │    Excel     │  │
│  │     API      │  │   Database   │  │  Seller List │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## コンポーネントとインターフェース

### 1. Query Fetcher

DataCentralからSQLクエリを取得するコンポーネント。

```python
class QueryFetcher:
    def __init__(self, auth_config: Optional[Dict[str, str]] = None):
        """
        認証設定を初期化
        auth_config: 認証情報の辞書（環境変数から読み込み）
        """
        pass
    
    def fetch_query(self, url: str) -> str:
        """
        DataCentral URLからクエリを取得
        
        Parameters:
            url: DataCentral URL
        
        Returns:
            クエリテキスト
        
        Raises:
            ConnectionError: 接続失敗時
            AuthenticationError: 認証失敗時
            ValueError: 無効なURL時
        """
        pass
```

### 2. Date Replacer

クエリ内の日付を置換するコンポーネント。

```python
class DateReplacer:
    DATE_PATTERN = r'\d{4}-\d{2}-\d{2}'
    
    def replace_dates(self, query: str, target_date: str, 
                     start_line: int = 6, end_line: int = 11) -> str:
        """
        クエリの指定行範囲内の日付を置換
        
        Parameters:
            query: 元のクエリテキスト
            target_date: 置換する日付（'yyyy-mm-dd'形式）
            start_line: 開始行（1-indexed）
            end_line: 終了行（1-indexed）
        
        Returns:
            日付が置換されたクエリテキスト
        
        Raises:
            ValueError: 日付形式が不正な場合
        """
        pass
    
    def validate_date_format(self, date_str: str) -> bool:
        """
        日付形式を検証
        
        Parameters:
            date_str: 検証する日付文字列
        
        Returns:
            True if valid, False otherwise
        """
        pass
```

### 3. Query Executor

ローカルデータベースでクエリを実行するコンポーネント。

```python
class QueryExecutor:
    def __init__(self, db_path: str = "database.sqlite"):
        """
        データベース接続を初期化
        
        Parameters:
            db_path: SQLiteデータベースファイルパス
        """
        pass
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """
        クエリを実行し、結果をDataFrameとして返す
        
        Parameters:
            query: 実行するSQLクエリ
        
        Returns:
            クエリ結果のDataFrame
        
        Raises:
            DatabaseError: データベース接続エラー
            SQLError: クエリ実行エラー
        """
        pass
    
    def close(self):
        """データベース接続を閉じる"""
        pass
```

### 4. Seller Mapper

Sellerマスタデータを読み込み、クエリ結果と結合するコンポーネント。

```python
class SellerMapper:
    def __init__(self, excel_path: str):
        """
        Sellerマスタデータを読み込む
        
        Parameters:
            excel_path: EITS_Seller_list.xlsxのパス
        
        Raises:
            FileNotFoundError: ファイルが存在しない場合
            ValueError: ファイル形式が不正な場合
        """
        pass
    
    def load_seller_master(self) -> pd.DataFrame:
        """
        Sellerマスタデータを読み込む
        
        Returns:
            Sellerマスタデータ（CID、Team、Aliasを含む）
        """
        pass
    
    def merge_with_query_result(self, query_result: pd.DataFrame) -> pd.DataFrame:
        """
        クエリ結果とSellerマスタを結合
        
        Parameters:
            query_result: クエリ実行結果
        
        Returns:
            TeamとAliasが追加された結合データ
        """
        pass
```

### 5. Filter Engine

データをフィルタリングするコンポーネント。

```python
class FilterEngine:
    def __init__(self, data: pd.DataFrame):
        """
        フィルタエンジンを初期化
        
        Parameters:
            data: フィルタリング対象のDataFrame
        """
        pass
    
    def apply_filters(self, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        複数のフィルタを適用
        
        Parameters:
            filters: フィルタ条件の辞書
                例: {
                    'pf': ['JP', 'US'],
                    'gl': ['Electronics'],
                    'team': ['Team A'],
                    'suppression_status': ['Active']
                }
        
        Returns:
            フィルタリングされたDataFrame
        """
        pass
```

### 6. Coefficient Calculator

OPS/T30 GMS係数を計算するコンポーネント。

```python
class CoefficientCalculator:
    def __init__(self, data: pd.DataFrame):
        """
        係数計算機を初期化
        
        Parameters:
            data: 計算対象のDataFrame
        """
        pass
    
    def calculate_by_gl(self) -> pd.DataFrame:
        """
        GL別のOPS/T30 GMS係数を計算
        
        Returns:
            GL別係数のDataFrame（gl、coefficient、sample_sizeを含む）
        """
        pass
    
    def calculate_by_suppression_status(self) -> pd.DataFrame:
        """
        Suppression Status別のOPS/T30 GMS係数を計算
        
        Returns:
            Suppression Status別係数のDataFrame
        """
        pass
    
    def calculate_overall_coefficient(self) -> float:
        """
        全体のOPS/T30 GMS係数を計算
        
        Returns:
            全体係数
        """
        pass
```

### 7. Aggregator

データを集計するコンポーネント。

```python
class Aggregator:
    def __init__(self, data: pd.DataFrame):
        """
        集計エンジンを初期化
        
        Parameters:
            data: 集計対象のDataFrame
        """
        pass
    
    def aggregate_by_seller(self) -> pd.DataFrame:
        """
        Seller（CID）別に集計
        
        Returns:
            Seller別集計データ
        """
        pass
    
    def aggregate_by_team(self) -> pd.DataFrame:
        """
        Team別に集計
        
        Returns:
            Team別集計データ
        """
        pass
    
    def aggregate_by_alias(self) -> pd.DataFrame:
        """
        Alias別に集計
        
        Returns:
            Alias別集計データ
        """
        pass
    
    def _calculate_metrics(self, group: pd.DataFrame) -> Dict[str, float]:
        """
        集計メトリクスを計算
        
        Returns:
            メトリクス辞書（asin_count、total_t30d_gms、total_promotion_ops等）
        """
        pass
```

### 8. Team Allocator

OP2目標からチーム割り当てを計算するコンポーネント。

```python
class TeamAllocator:
    def __init__(self, data: pd.DataFrame, coefficient_calculator: CoefficientCalculator):
        """
        チーム割り当て計算機を初期化
        
        Parameters:
            data: 計算対象のDataFrame
            coefficient_calculator: 係数計算機
        """
        pass
    
    def calculate_required_t30_gms(self, op2_ops_target: float) -> float:
        """
        OP2 OPS目標から必要なT30 GMSを計算
        
        Parameters:
            op2_ops_target: OP2 OPS目標値
        
        Returns:
            必要なT30 GMS
        """
        pass
    
    def breakdown_by_segment(self, required_t30_gms: float) -> Dict[str, float]:
        """
        必要T30 GMSをTop 20K/40K/その他に分解
        
        Parameters:
            required_t30_gms: 必要なT30 GMS
        
        Returns:
            セグメント別必要T30 GMS
        """
        pass
    
    def breakdown_by_gl(self, required_t30_gms: float) -> pd.DataFrame:
        """
        必要T30 GMSをGL別に分解
        
        Parameters:
            required_t30_gms: 必要なT30 GMS
        
        Returns:
            GL別必要T30 GMSのDataFrame
        """
        pass
    
    def allocate_to_teams(self, required_t30_gms: float) -> pd.DataFrame:
        """
        必要T30 GMSをTeam別に割り当て
        
        Parameters:
            required_t30_gms: 必要なT30 GMS
        
        Returns:
            Team別割り当てのDataFrame（team、current_t30_gms、required_t30_gms、achievement_rateを含む）
        """
        pass
```

### 9. Suppression Simulator

Suppression改善によるIncremental OPSを計算するコンポーネント。

```python
class SuppressionSimulator:
    def __init__(self, data: pd.DataFrame, coefficient_calculator: CoefficientCalculator):
        """
        Suppressionシミュレータを初期化
        
        Parameters:
            data: シミュレーション対象のDataFrame
            coefficient_calculator: 係数計算機
        """
        pass
    
    def calculate_suppression_rate(self, entity_type: str, entity_id: str) -> float:
        """
        Seller/TeamのSuppression Rateを計算
        
        Parameters:
            entity_type: 'seller' または 'team'
            entity_id: SellerのCIDまたはTeam名
        
        Returns:
            Suppression Rate（0.0～1.0）
        """
        pass
    
    def simulate_improvement(self, entity_type: str, entity_id: str,
                           current_rate: float, target_rate: float) -> float:
        """
        Suppression改善によるIncremental OPSを計算
        
        Parameters:
            entity_type: 'seller' または 'team'
            entity_id: SellerのCIDまたはTeam名
            current_rate: 現在のSuppression Rate
            target_rate: 目標Suppression Rate
        
        Returns:
            Incremental OPS
        """
        pass
    
    def batch_simulate(self, simulations: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        複数のSuppression改善シミュレーションを一括実行
        
        Parameters:
            simulations: シミュレーション設定のリスト
        
        Returns:
            シミュレーション結果のDataFrame
        """
        pass
```

### 10. Data Exporter

データをエクスポートするコンポーネント。

```python
class DataExporter:
    def export_to_csv(self, data: pd.DataFrame, file_path: str):
        """
        DataFrameをCSVファイルとしてエクスポート
        
        Parameters:
            data: エクスポートするDataFrame
            file_path: 出力ファイルパス
        """
        pass
    
    def export_to_excel(self, data: pd.DataFrame, file_path: str):
        """
        DataFrameをExcelファイルとしてエクスポート
        
        Parameters:
            data: エクスポートするDataFrame
            file_path: 出力ファイルパス
        """
        pass
    
    def export_to_json(self, data: Dict[str, Any], file_path: str):
        """
        辞書をJSONファイルとしてエクスポート
        
        Parameters:
            data: エクスポートする辞書
            file_path: 出力ファイルパス
        """
        pass
```

### 11. Dashboard (Flask Application)

Webダッシュボードを提供するFlaskアプリケーション。

```python
class Dashboard:
    def __init__(self, data: pd.DataFrame, seller_mapper: SellerMapper):
        """
        ダッシュボードを初期化
        
        Parameters:
            data: 表示するDataFrame
            seller_mapper: Sellerマッパー
        """
        pass
    
    def run(self, host: str = '127.0.0.1', port: int = 5000):
        """
        ダッシュボードサーバーを起動
        
        Parameters:
            host: ホストアドレス
            port: ポート番号
        """
        pass
```

エンドポイント：
- `GET /`: ダッシュボードのメインページ
- `POST /api/filter`: フィルタを適用してデータを取得
- `GET /api/coefficients`: 係数データを取得
- `GET /api/aggregations`: 集計データを取得
- `POST /api/allocate`: OP2目標からチーム割り当てを計算
- `POST /api/simulate_suppression`: Suppression改善をシミュレート
- `POST /api/export`: データをエクスポート

## データモデル

### Query Result Schema

クエリ実行結果の基本スキーマ：

```python
{
    'pf': str,                          # プラットフォーム
    'gl': str,                          # 商品カテゴリ
    'dom_ooc': str,                     # Domestic/OOC
    'merchant_customer_id': str,        # Seller CID
    'is_top_20k': bool,                 # Top 20Kフラグ
    'is_top_40k': bool,                 # Top 40Kフラグ
    'deal_registered': bool,            # Deal登録フラグ
    'suppression_status': str,          # Suppression状態
    'asin_count': int,                  # ASIN数
    'total_t30d_gms': float,           # 合計T30 GMS
    'total_t30d_units': int,           # 合計T30 Units
    'total_promotion_ops_before_discount': float,  # 割引前OPS
    'total_promotion_ops': float,      # プロモーションOPS
    'total_promotion_units': int       # プロモーションUnits
}
```

### Enriched Data Schema

Sellerマスタと結合後のスキーマ：

```python
{
    # Query Result Schemaのすべてのフィールド +
    'team': str,                        # チーム名
    'alias': str                        # Alias
}
```

### Coefficient Schema

係数データのスキーマ：

```python
{
    'dimension': str,                   # 'gl' または 'suppression_status'
    'value': str,                       # GLまたはSuppression Statusの値
    'coefficient': float,               # OPS/T30 GMS係数
    'sample_size': int,                 # サンプル数
    'total_ops': float,                 # 合計OPS
    'total_t30_gms': float             # 合計T30 GMS
}
```

### Allocation Schema

チーム割り当てのスキーマ：

```python
{
    'team': str,                        # チーム名
    'current_t30_gms': float,          # 現在のT30 GMS
    'required_t30_gms': float,         # 必要なT30 GMS
    'gap': float,                       # ギャップ
    'achievement_rate': float,          # 達成率（current/required）
    'composition_ratio': float          # 構成比
}
```

### Suppression Simulation Schema

Suppressionシミュレーション結果のスキーマ：

```python
{
    'entity_type': str,                 # 'seller' または 'team'
    'entity_id': str,                   # CIDまたはTeam名
    'current_suppression_rate': float,  # 現在のSuppression Rate
    'target_suppression_rate': float,   # 目標Suppression Rate
    'improvement': float,               # 改善幅
    'current_t30_gms': float,          # 現在のT30 GMS
    'incremental_ops': float            # Incremental OPS
}
```

## 正確性プロパティ

正確性プロパティは、システムがすべての有効な実行において真であるべき特性や動作を定義します。これらは人間が読める仕様と機械で検証可能な正確性保証の橋渡しとなります。


### クエリ取得と日付置換のプロパティ

Property 1: クエリ取得の成功
*すべての*有効なDataCentral URLに対して、Query_Fetcherはクエリテキストを文字列として取得できる
**検証: 要件 1.1**

Property 2: 無効URL時のエラーハンドリング
*すべての*無効または到達不可能なURLに対して、Query_Fetcherは明確なエラーメッセージを返す
**検証: 要件 1.3**

Property 3: 日付置換の正確性
*すべての*クエリテキストと有効な日付（'yyyy-mm-dd'形式）の組み合わせに対して、Date_Replacerは6～11行目のすべての日付を指定された日付に置換する
**検証: 要件 2.1**

Property 4: 日付パターン認識
*すべての*'yyyy-mm-dd'形式の日付文字列に対して、Date_Replacerは正確に識別できる
**検証: 要件 2.2**

Property 5: 日付不在時の不変性
*すべての*6～11行目に日付を含まないクエリに対して、Date_Replacerは元のクエリを変更せずに返す
**検証: 要件 2.4**

Property 6: 無効日付形式のエラーハンドリング
*すべての*'yyyy-mm-dd'形式に従わない日付文字列に対して、Date_Replacerはエラーメッセージを返す
**検証: 要件 2.5**

### クエリ実行のプロパティ

Property 7: クエリ実行の成功
*すべての*有効なSQLクエリに対して、Query_Executorはローカルデータベースでクエリを実行し、結果をDataFrameとして返す
**検証: 要件 3.1**

Property 8: 無効クエリのエラーハンドリング
*すべての*無効なSQLクエリに対して、Query_ExecutorはSQLエラーの詳細を含むエラーメッセージを返す
**検証: 要件 3.4**

### Sellerマスタ結合のプロパティ

Property 9: Sellerマスタ読み込み
*すべての*有効なExcelファイル（CID、Team、Aliasを含む）に対して、Seller_Mapperは正しくデータを読み込める
**検証: 要件 4.1**

Property 10: データ結合の正確性
*すべての*クエリ結果とSellerマスタデータの組み合わせに対して、Seller_Mapperはmerchant_customer_idをキーとして正しく結合し、teamとaliasカラムを追加する
**検証: 要件 5.1**

Property 11: 結合時のカラム保持
*すべての*結合操作に対して、Seller_Mapperは元のクエリ結果のすべてのカラムを保持する（カラム数は増加のみ）
**検証: 要件 5.4**

### 係数計算のプロパティ

Property 12: GL別係数計算
*すべての*データセットに対して、Coefficient_CalculatorはGL別にOPS/T30 GMS係数を「total_promotion_ops / total_t30d_gms」として正確に計算する
**検証: 要件 7.1, 7.3**

Property 13: Suppression Status別係数計算
*すべての*データセットに対して、Coefficient_CalculatorはSuppression Status別にOPS/T30 GMS係数を「total_promotion_ops / total_t30d_gms」として正確に計算する
**検証: 要件 7.2, 7.3**

### 集計のプロパティ

Property 14: Seller/Team/Alias別集計
*すべての*データセットに対して、AggregatorはSeller、Team、Alias別に正しく集計し、各メトリクス（asin_count、total_t30d_gms、total_promotion_ops等）を計算する
**検証: 要件 8.1, 8.2, 8.3, 8.4**

### 目標計算と割り当てのプロパティ

Property 15: 必要T30 GMS計算
*すべての*OP2 OPS目標値に対して、Team_Allocatorは「OP2 OPS目標 / OPS/T30 GMS係数」として必要なT30 GMSを正確に計算する
**検証: 要件 9.2, 9.3**

Property 16: セグメント別分解の構成比
*すべての*必要T30 GMS値に対して、Team_AllocatorがTop 20K、Top 40K、その他に分解した際、各セグメントの合計は元の必要T30 GMSと一致する
**検証: 要件 10.2**

Property 17: GL別分解の構成比
*すべての*必要T30 GMS値に対して、Team_AllocatorがGL別に分解した際、各GLの合計は元の必要T30 GMSと一致する
**検証: 要件 11.2**

Property 18: Team別割り当ての合計一致
*すべての*必要T30 GMS値に対して、Team_AllocatorがTeam別に割り当てた際、各Teamの割り当ての合計は元の必要T30 GMSと一致する
**検証: 要件 12.2**

### Suppressionシミュレーションのプロパティ

Property 19: Suppression改善によるIncremental OPS計算
*すべての*Seller/TeamとSuppression Rate改善目標の組み合わせに対して、Suppression_SimulatorはIncremental OPSを正確に計算する
**検証: 要件 13.4, 13.5**

### データエクスポートのプロパティ

Property 20: エクスポートのラウンドトリップ
*すべての*DataFrameに対して、CSV/Excelにエクスポートしてから再読み込みした場合、元のデータと同等のデータが得られる
**検証: 要件 14.1, 14.2**

## エラーハンドリング

### エラーの分類

1. **接続エラー**
   - DataCentral接続失敗
   - データベース接続失敗
   - ファイルアクセスエラー

2. **検証エラー**
   - 無効なURL形式
   - 無効な日付形式
   - 無効なSQL構文
   - 無効なExcelファイル形式

3. **計算エラー**
   - ゼロ除算（T30 GMSがゼロの場合）
   - データ不足（サンプルサイズが小さすぎる場合）

4. **システムエラー**
   - メモリ不足
   - ディスク容量不足
   - 予期しない例外

### エラーハンドリング戦略

すべてのコンポーネントは以下のパターンに従います：

```python
try:
    # 処理
    result = perform_operation()
    return result
except SpecificError as e:
    # 具体的なエラーメッセージを生成
    error_msg = f"Operation failed: {str(e)}"
    logger.error(error_msg)
    raise CustomException(error_msg) from e
except Exception as e:
    # 予期しないエラー
    error_msg = f"Unexpected error: {str(e)}"
    logger.error(error_msg)
    raise SystemError(error_msg) from e
```

### カスタム例外クラス

```python
class DataCentralError(Exception):
    """DataCentral関連のエラー"""
    pass

class QueryExecutionError(Exception):
    """クエリ実行エラー"""
    pass

class DataValidationError(Exception):
    """データ検証エラー"""
    pass

class CalculationError(Exception):
    """計算エラー"""
    pass
```

## テスト戦略

### デュアルテストアプローチ

このプロジェクトでは、ユニットテストとプロパティベーステストの両方を使用します：

- **ユニットテスト**: 特定の例、エッジケース、エラー条件を検証
- **プロパティベーステスト**: すべての入力に対して成り立つ普遍的な性質を検証

両者は補完的であり、包括的なカバレッジに必要です。

### プロパティベーステスト

Pythonの`hypothesis`ライブラリを使用してプロパティベーステストを実装します。

**設定**:
- 各プロパティテストは最低100回の反復を実行
- 各テストは設計書のプロパティを参照するタグを含む
- タグ形式: `# Feature: datacentral-query-executor, Property {number}: {property_text}`

**例**:

```python
from hypothesis import given, strategies as st
import hypothesis

@given(
    url=st.text(min_size=10),
    query_text=st.text(min_size=1)
)
@hypothesis.settings(max_examples=100)
def test_property_1_query_fetch_success(url, query_text):
    """
    Feature: datacentral-query-executor, Property 1: クエリ取得の成功
    すべての有効なDataCentral URLに対して、Query_Fetcherはクエリテキストを文字列として取得できる
    """
    # モックサーバーをセットアップ
    with mock_datacentral_server(url, query_text):
        fetcher = QueryFetcher()
        result = fetcher.fetch_query(url)
        assert isinstance(result, str)
        assert len(result) > 0
```

### ユニットテスト

ユニットテストは以下に焦点を当てます：

1. **特定の例**: 実際のDataCentral URLとクエリを使用した統合テスト
2. **エッジケース**: 
   - 空のクエリ結果
   - マスタデータに存在しないCID
   - T30 GMSがゼロの場合
3. **エラー条件**:
   - 無効なURL
   - 無効な日付形式
   - データベース接続エラー
   - ファイルが存在しない

### テストカバレッジ目標

- コードカバレッジ: 80%以上
- プロパティテスト: 設計書の各プロパティに対して1つのテスト
- ユニットテスト: 各コンポーネントの主要な機能とエラーパス

### テストデータ

テストには以下のデータを使用します：

1. **モックDataCentralサーバー**: `responses`ライブラリを使用
2. **テスト用SQLiteデータベース**: インメモリデータベース
3. **テスト用Excelファイル**: `openpyxl`で生成
4. **ランダムデータ生成**: `hypothesis`のストラテジーを使用

### 継続的インテグレーション

- すべてのテストはコミット前に実行
- CIパイプラインで自動実行
- テスト失敗時はマージをブロック
