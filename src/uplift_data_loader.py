"""
Uplift Interaction Analyzer - Data Loader

タブ区切りファイルの読み込みとカラム検証機能
"""

import pandas as pd
from typing import List, Optional
from pathlib import Path


class MissingColumnError(Exception):
    """必要なカラムが存在しない場合のエラー"""
    def __init__(self, missing_columns: List[str]):
        self.missing_columns = missing_columns
        super().__init__(f"必要なカラムが見つかりません: {', '.join(missing_columns)}")


class DataLoader:
    """タブ区切りファイルを読み込み、検証するクラス"""
    
    REQUIRED_COLUMNS = [
        'our_price',
        'current_discount_percent',
        'promotion_ops',
        'past_month_gms'
    ]
    
    def __init__(self, required_columns: Optional[List[str]] = None):
        """
        Args:
            required_columns: 必要なカラムのリスト（省略時はデフォルト）
        """
        self.required_columns = required_columns or self.REQUIRED_COLUMNS
    
    def load_file(self, file_path: str) -> pd.DataFrame:
        """
        タブ区切りファイルを読み込む
        
        Args:
            file_path: ファイルパス
            
        Returns:
            pd.DataFrame: 読み込んだデータ
            
        Raises:
            FileNotFoundError: ファイルが存在しない場合
            MissingColumnError: 必要なカラムが存在しない場合
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
        
        # タブ区切りファイルを読み込み
        df = pd.read_csv(file_path, sep='\t', encoding='utf-8')
        
        # カラム検証
        if not self.validate_columns(df, self.required_columns):
            missing = self.get_missing_columns(df, self.required_columns)
            raise MissingColumnError(missing)
        
        return df
    
    def validate_columns(self, df: pd.DataFrame, required_columns: List[str]) -> bool:
        """
        必要なカラムの存在を検証
        
        Args:
            df: DataFrame
            required_columns: 必要なカラムのリスト
            
        Returns:
            bool: すべてのカラムが存在する場合True
        """
        return all(col in df.columns for col in required_columns)
    
    def get_missing_columns(self, df: pd.DataFrame, required_columns: List[str]) -> List[str]:
        """
        不足しているカラムのリストを取得
        
        Args:
            df: DataFrame
            required_columns: 必要なカラムのリスト
            
        Returns:
            List[str]: 不足しているカラム名のリスト
        """
        return [col for col in required_columns if col not in df.columns]
