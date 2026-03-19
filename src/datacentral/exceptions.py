"""カスタム例外クラス"""


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
