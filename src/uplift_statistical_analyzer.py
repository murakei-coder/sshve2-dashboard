"""
Uplift Interaction Analyzer - Statistical Analyzer

重回帰分析と統計検定機能
- our_price, discount_percent, 交互作用項の係数算出
- p値、R²の計算
- 結果の解釈と結論導出
"""

import pandas as pd
import numpy as np
from typing import Optional
import statsmodels.api as sm
from statsmodels.regression.linear_model import RegressionResultsWrapper

from uplift_models import (
    RegressionCoefficient,
    RegressionResult,
    AnalysisInterpretation,
    DescriptiveStats
)


class StatisticalAnalyzer:
    """統計分析を行うクラス"""
    
    def __init__(self, significance_level: float = 0.05):
        """
        Args:
            significance_level: 有意水準（デフォルト: 0.05）
        """
        self.significance_level = significance_level
    
    def is_significant(self, p_value: float) -> bool:
        """p値が有意水準未満かどうかを判定"""
        return p_value < self.significance_level
    
    def run_regression(self, df: pd.DataFrame) -> RegressionResult:
        """
        重回帰分析を実行（交互作用項を含む）
        
        モデル: Uplift ~ our_price + discount_percent + our_price × discount_percent
        
        Args:
            df: 入力DataFrame（our_price, discount_percent_numeric, upliftカラムが必要）
            
        Returns:
            RegressionResult: 回帰分析結果
        """
        # 説明変数の準備
        X = df[['our_price', 'discount_percent_numeric']].copy()
        X.columns = ['price', 'discount']
        
        # 交互作用項を追加
        X['interaction'] = X['price'] * X['discount']
        
        # 定数項を追加
        X = sm.add_constant(X)
        
        # 目的変数
        y = df['uplift']
        
        # 回帰分析を実行
        model = sm.OLS(y, X)
        results = model.fit()
        
        # 係数を抽出
        coefficients = []
        param_names = ['const', 'price', 'discount', 'interaction']
        display_names = ['定数項', 'our_price', 'discount_percent', '交互作用項']
        
        for param, display in zip(param_names, display_names):
            coef = RegressionCoefficient(
                name=display,
                coefficient=results.params[param],
                std_error=results.bse[param],
                t_value=results.tvalues[param],
                p_value=results.pvalues[param]
            )
            coefficients.append(coef)
        
        return RegressionResult(
            coefficients=coefficients,
            r_squared=results.rsquared,
            adj_r_squared=results.rsquared_adj,
            f_statistic=results.fvalue,
            f_p_value=results.f_pvalue,
            n_observations=int(results.nobs)
        )

    
    def interpret_results(self, result: RegressionResult) -> AnalysisInterpretation:
        """
        回帰分析結果を解釈し、仮説検証の結論を導出
        
        Args:
            result: 回帰分析結果
            
        Returns:
            AnalysisInterpretation: 分析結果の解釈
        """
        # 各係数を取得
        price_coef = next((c for c in result.coefficients if c.name == 'our_price'), None)
        discount_coef = next((c for c in result.coefficients if c.name == 'discount_percent'), None)
        interaction_coef = next((c for c in result.coefficients if c.name == '交互作用項'), None)
        
        # 価格の効果を解釈
        if price_coef:
            if price_coef.is_significant:
                direction = "正" if price_coef.coefficient > 0 else "負"
                price_effect = f"価格はUpliftに統計的に有意な{direction}の影響を与えています（係数: {price_coef.coefficient:.4f}, p値: {price_coef.p_value:.4f}）"
            else:
                price_effect = f"価格のUpliftへの影響は統計的に有意ではありません（p値: {price_coef.p_value:.4f}）"
        else:
            price_effect = "価格の係数が見つかりません"
        
        # 割引率の効果を解釈
        if discount_coef:
            if discount_coef.is_significant:
                direction = "正" if discount_coef.coefficient > 0 else "負"
                discount_effect = f"割引率はUpliftに統計的に有意な{direction}の影響を与えています（係数: {discount_coef.coefficient:.4f}, p値: {discount_coef.p_value:.4f}）"
            else:
                discount_effect = f"割引率のUpliftへの影響は統計的に有意ではありません（p値: {discount_coef.p_value:.4f}）"
        else:
            discount_effect = "割引率の係数が見つかりません"
        
        # 交互作用効果を解釈
        hypothesis_supported = False
        if interaction_coef:
            if interaction_coef.is_significant and interaction_coef.coefficient > 0:
                interaction_effect = f"価格と割引率の交互作用効果は統計的に有意です（係数: {interaction_coef.coefficient:.6f}, p値: {interaction_coef.p_value:.4f}）。価格と割引率が両方高い場合、Upliftへの影響はさらに大きくなります。"
                hypothesis_supported = True
            elif interaction_coef.is_significant and interaction_coef.coefficient < 0:
                interaction_effect = f"価格と割引率の交互作用効果は統計的に有意ですが、負の方向です（係数: {interaction_coef.coefficient:.6f}, p値: {interaction_coef.p_value:.4f}）。"
            else:
                interaction_effect = f"価格と割引率の交互作用効果は統計的に有意ではありません（p値: {interaction_coef.p_value:.4f}）"
        else:
            interaction_effect = "交互作用項の係数が見つかりません"
        
        # 総合的な結論
        if hypothesis_supported:
            conclusion = f"仮説は支持されました。価格と割引率が組み合わさると、Upliftへの影響はさらに大きくなります。モデルの説明力（R²）は{result.r_squared:.4f}です。"
        else:
            conclusion = f"仮説は支持されませんでした。価格と割引率の交互作用効果は統計的に有意ではないか、負の方向です。モデルの説明力（R²）は{result.r_squared:.4f}です。"
        
        return AnalysisInterpretation(
            price_effect=price_effect,
            discount_effect=discount_effect,
            interaction_effect=interaction_effect,
            hypothesis_supported=hypothesis_supported,
            conclusion=conclusion
        )
    
    def calculate_descriptive_stats(self, df: pd.DataFrame) -> list:
        """
        記述統計を計算
        
        Args:
            df: 入力DataFrame
            
        Returns:
            list: DescriptiveStatsのリスト
        """
        stats_list = []
        
        for col in ['our_price', 'discount_percent_numeric', 'uplift']:
            if col in df.columns:
                data = df[col].dropna()
                stats = DescriptiveStats(
                    variable=col,
                    count=len(data),
                    mean=float(data.mean()),
                    std=float(data.std()),
                    min_val=float(data.min()),
                    max_val=float(data.max()),
                    median=float(data.median())
                )
                stats_list.append(stats)
        
        return stats_list
