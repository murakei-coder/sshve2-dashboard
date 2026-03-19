"""
Uplift Interaction Analyzer - Data Processor

データクレンジングと前処理機能
- 割引率文字列のパース
- 欠損値・異常値の処理
"""

import pandas as pd
import re
from typing import Optional, Union
import numpy as np


class DataProcessor:
    """データの前処理を行うクラス"""
    
    def parse_discount_percent(self, value: Union[str, float, None]) -> Optional[float]:
        """
        割引率文字列を数値に変換
        
        対応形式:
        - 数値: 20.01 -> 20.01
        - パーセント付き: "20.01%" -> 20.01
        - 範囲形式: "5.20%~25%" -> 5.20（先頭の数値を採用）
        - Unknown: None
        
        Args:
            value: 割引率の値（文字列または数値）
            
        Returns:
            float: パースした数値、変換できない場合はNone
        """
        if value is None:
            return None
        
        if isinstance(value, (int, float)):
            if pd.isna(value):
                return None
            return float(value)
        
        if not isinstance(value, str):
            return None
        
        value = value.strip()
        
        # "Unknown" や空文字列の処理
        if value.lower() == 'unknown' or value == '':
            return None
        
        # 数値パターンを抽出（先頭の数値を取得）
        match = re.match(r'^(-?\d+\.?\d*)', value)
        if match:
            return float(match.group(1))
        
        return None
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        データクレンジングを実行
        
        - current_discount_percentを数値に変換
        - our_priceを数値に変換（Unknownは除外）
        - promotion_ops, past_month_gmsを数値に変換
        
        Args:
            df: 入力DataFrame
            
        Returns:
            pd.DataFrame: クレンジング後のDataFrame
        """
        df = df.copy()
        
        # current_discount_percentのパース（Unknownは None になる）
        if 'current_discount_percent' in df.columns:
            df['discount_percent_numeric'] = df['current_discount_percent'].apply(
                self.parse_discount_percent
            )
        
        # our_priceを数値に変換（Unknownや文字列はNaNになる）
        if 'our_price' in df.columns:
            # 文字列の "Unknown" を明示的に除外
            df['our_price'] = df['our_price'].replace(['Unknown', 'unknown', 'UNKNOWN', ''], np.nan)
            df['our_price'] = pd.to_numeric(df['our_price'], errors='coerce')
        
        # promotion_opsを数値に変換
        if 'promotion_ops' in df.columns:
            df['promotion_ops'] = pd.to_numeric(df['promotion_ops'], errors='coerce')
        
        # past_month_gmsを数値に変換
        if 'past_month_gms' in df.columns:
            df['past_month_gms'] = pd.to_numeric(df['past_month_gms'], errors='coerce')
        
        return df
    
    def remove_invalid_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        分析に使用できない行を除外
        
        - our_priceがNULLまたは0以下
        - discount_percent_numericがNULL
        - promotion_opsがNULL
        - past_month_gmsがNULLまたは0以下
        
        Args:
            df: 入力DataFrame
            
        Returns:
            pd.DataFrame: 有効な行のみのDataFrame
        """
        df = df.copy()
        
        # 条件に基づいてフィルタリング
        valid_mask = (
            df['our_price'].notna() & 
            (df['our_price'] > 0) &
            df['discount_percent_numeric'].notna() &
            df['promotion_ops'].notna() &
            df['past_month_gms'].notna() &
            (df['past_month_gms'] > 0)
        )
        
        return df[valid_mask].reset_index(drop=True)
    
    def remove_outliers(self, df: pd.DataFrame, column: str, method: str = 'iqr', 
                        lower_percentile: float = 1, upper_percentile: float = 99) -> pd.DataFrame:
        """
        外れ値を除外
        
        Args:
            df: 入力DataFrame
            column: 外れ値を検出するカラム名
            method: 'iqr'（四分位範囲法）または 'percentile'（パーセンタイル法）
            lower_percentile: 下限パーセンタイル（percentile法の場合）
            upper_percentile: 上限パーセンタイル（percentile法の場合）
            
        Returns:
            pd.DataFrame: 外れ値除外後のDataFrame
        """
        df = df.copy()
        
        if method == 'iqr':
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
        elif method == 'percentile':
            lower_bound = df[column].quantile(lower_percentile / 100)
            upper_bound = df[column].quantile(upper_percentile / 100)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        mask = (df[column] >= lower_bound) & (df[column] <= upper_bound)
        return df[mask].reset_index(drop=True)
