"""
Uplift Interaction Analyzer - Uplift Calculator

Uplift計算機能
- Uplift = (promotion_ops / past_month_gms - 1) × 100
- past_month_gms=0またはNULLのレコード除外
"""

import pandas as pd
import numpy as np
from typing import Optional


class UpliftCalculator:
    """Upliftを計算するクラス"""
    
    def calculate_uplift(self, promotion_ops: float, past_month_gms: float) -> Optional[float]:
        """
        単一レコードのUpliftを計算
        
        Uplift = (promotion_ops / past_month_gms - 1) × 100
        
        Args:
            promotion_ops: プロモーション期間のOPS
            past_month_gms: 過去1ヶ月のGMS
            
        Returns:
            float: Uplift値（%）、計算できない場合はNone
        """
        if past_month_gms is None or past_month_gms == 0:
            return None
        if promotion_ops is None:
            return None
        if pd.isna(past_month_gms) or pd.isna(promotion_ops):
            return None
        
        return (promotion_ops / past_month_gms - 1) * 100
    
    def add_uplift_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        DataFrameにUpliftカラムを追加
        
        - past_month_gmsが0またはNULLのレコードは除外
        - 元のカラムはすべて保持
        
        Args:
            df: 入力DataFrame（promotion_ops, past_month_gmsカラムが必要）
            
        Returns:
            pd.DataFrame: upliftカラムが追加されたDataFrame
        """
        df = df.copy()
        
        # past_month_gmsが0またはNULLのレコードを除外
        valid_mask = (
            df['past_month_gms'].notna() & 
            (df['past_month_gms'] != 0)
        )
        df = df[valid_mask].copy()
        
        # Upliftを計算
        df['uplift'] = df.apply(
            lambda row: self.calculate_uplift(
                row['promotion_ops'], 
                row['past_month_gms']
            ),
            axis=1
        )
        
        # Upliftが計算できなかった行を除外
        df = df[df['uplift'].notna()].reset_index(drop=True)
        
        return df
