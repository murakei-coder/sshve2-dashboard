"""
Discount Effectiveness Analyzer - Main analysis module.
Analyzes the relationship between discount rates and sales growth by PF × Price Band.
"""
import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple
from io import StringIO

import pandas as pd
import numpy as np
from scipy import stats

from src.discount_constants import (
    REQUIRED_COLUMNS, REQUIRED_COLUMNS_GL, NUMERIC_COLUMNS, 
    PRICE_BANDS, PRICE_BAND_ORDER, DISCOUNT_TIERS, DISCOUNT_TIER_ORDER,
    OUTLIER_THRESHOLD, MIN_SAMPLE_SIZE, SIGNIFICANCE_LEVEL,
    DISCOUNT_MIN, DISCOUNT_MAX
)
from src.discount_models import (
    SegmentAnalysisResult, OptimalDiscountRecommendation, AnalysisResults
)

logger = logging.getLogger(__name__)


class ParseError(Exception):
    """Exception raised when parsing fails."""
    pass


class ValidationError(Exception):
    """Exception raised when validation fails."""
    pass


@dataclass
class ValidationResult:
    """Result of data validation."""
    is_valid: bool
    missing_columns: List[str]
    invalid_rows_count: int
    error_messages: List[str]


class DataLoader:
    """Loads raw data files into DataFrame."""
    
    def load(self, file_path: str, encoding: str = 'utf-8') -> pd.DataFrame:
        """
        Load a tab-separated file into DataFrame.
        
        Args:
            file_path: Path to the input file
            encoding: File encoding (default: utf-8)
            
        Returns:
            DataFrame with loaded data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ParseError: If parsing fails
        """
        try:
            # Try tab-separated first
            df = pd.read_csv(file_path, sep='\t', encoding=encoding, low_memory=False)
            if len(df.columns) > 1:
                logger.info(f"Loaded {len(df)} records from {file_path}")
                return df
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                df = pd.read_csv(file_path, sep='\t', encoding='cp932', low_memory=False)
                if len(df.columns) > 1:
                    logger.info(f"Loaded {len(df)} records from {file_path} (cp932)")
                    return df
            except Exception:
                pass
        except FileNotFoundError:
            raise
        except Exception as e:
            logger.warning(f"Tab-separated parse failed: {e}")
        
        # Fallback to comma-separated
        try:
            df = pd.read_csv(file_path, sep=',', encoding=encoding, low_memory=False)
            logger.info(f"Loaded {len(df)} records from {file_path} (CSV)")
            return df
        except Exception as e:
            raise ParseError(f"データのパースに失敗しました: {e}")



class DataValidator:
    """Validates and cleans data for analysis."""
    
    def __init__(self, use_gl: bool = False):
        self.required_columns = REQUIRED_COLUMNS_GL if use_gl else REQUIRED_COLUMNS
        self.numeric_columns = NUMERIC_COLUMNS
        self.use_gl = use_gl
    
    def validate(self, df: pd.DataFrame) -> ValidationResult:
        """
        Validate DataFrame has required columns and valid data.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            ValidationResult with validation status
        """
        missing_columns = []
        error_messages = []
        
        # Check required columns
        for col in self.required_columns:
            if col not in df.columns:
                missing_columns.append(col)
        
        if missing_columns:
            error_messages.append(f"必須カラムが不足: {', '.join(missing_columns)}")
            return ValidationResult(
                is_valid=False,
                missing_columns=missing_columns,
                invalid_rows_count=0,
                error_messages=error_messages
            )
        
        # Count invalid rows (only past_month_gms <= 0)
        invalid_count = 0
        if 'past_month_gms' in df.columns:
            numeric_gms = pd.to_numeric(df['past_month_gms'], errors='coerce')
            invalid_gms = (numeric_gms <= 0) | numeric_gms.isna()
            invalid_count = int(invalid_gms.sum())
        
        return ValidationResult(
            is_valid=True,
            missing_columns=[],
            invalid_rows_count=invalid_count,
            error_messages=error_messages
        )
    
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean DataFrame by converting types and removing invalid rows.
        Only removes rows where past_month_gms <= 0 (required for growth rate calculation).
        
        Args:
            df: DataFrame to clean
            
        Returns:
            Cleaned DataFrame
        """
        df = df.copy()
        original_count = len(df)
        
        # Convert numeric columns (coerce errors to NaN but don't remove)
        for col in self.numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Fill NaN in numeric columns with 0 (except past_month_gms)
        for col in ['our_price', 'current_discount_percent', 'promotion_ops']:
            if col in df.columns:
                df[col] = df[col].fillna(0)
        
        # Only remove rows with past_month_gms <= 0 or NaN (can't calculate growth rate)
        if 'past_month_gms' in df.columns:
            df = df[df['past_month_gms'].notna() & (df['past_month_gms'] > 0)]
        
        removed_count = original_count - len(df)
        if removed_count > 0:
            logger.warning(f"{removed_count}行を除外しました（past_month_gms無効）")
        
        # Fill NaN in pf and gl with 'Unknown'
        if 'pf' in df.columns:
            df['pf'] = df['pf'].fillna('Unknown').astype(str)
        if 'gl' in df.columns:
            df['gl'] = df['gl'].fillna('Unknown').astype(str)
        
        return df.reset_index(drop=True)


class GrowthRateCalculator:
    """Calculates sales growth rate."""
    
    def __init__(self, outlier_threshold: float = OUTLIER_THRESHOLD):
        self.outlier_threshold = outlier_threshold
    
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate growth rate and flag outliers.
        
        growth_rate = (promotion_ops / past_month_gms - 1) * 100
        
        Args:
            df: DataFrame with past_month_gms and promotion_ops columns
            
        Returns:
            DataFrame with growth_rate and is_outlier columns added
        """
        df = df.copy()
        
        # Calculate growth rate (%)
        df['growth_rate'] = ((df['promotion_ops'] / df['past_month_gms']) - 1) * 100
        df['growth_rate'] = df['growth_rate'].round(2)
        
        # Flag outliers
        df['is_outlier'] = df['growth_rate'] >= self.outlier_threshold
        
        outlier_count = df['is_outlier'].sum()
        if outlier_count > 0:
            logger.info(f"{outlier_count}件の外れ値を検出（growth_rate >= {self.outlier_threshold}%）")
        
        return df



class PriceBandClassifier:
    """Classifies prices into price bands."""
    
    def __init__(self, price_bands: List[Tuple] = None, discount_tiers: List[Tuple] = None):
        self.price_bands = price_bands or PRICE_BANDS
        self.discount_tiers = discount_tiers or DISCOUNT_TIERS
    
    def classify(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Classify our_price into price bands and discount into tiers.
        
        Args:
            df: DataFrame with our_price column
            
        Returns:
            DataFrame with price_band and discount_tier columns added
        """
        df = df.copy()
        
        def get_price_band(price):
            if pd.isna(price) or price <= 0:
                return 'Unknown'
            for min_p, max_p, label in self.price_bands:
                if min_p <= price <= max_p:
                    return label
            return 'Unknown'
        
        def get_discount_tier(discount):
            if pd.isna(discount) or discount < 0:
                return 'Unknown'
            for min_d, max_d, label in self.discount_tiers:
                if min_d <= discount < max_d:
                    return label
            return 'Unknown'
        
        df['price_band'] = df['our_price'].apply(get_price_band)
        df['discount_tier'] = df['current_discount_percent'].apply(get_discount_tier)
        
        # Log distribution
        band_counts = df['price_band'].value_counts()
        logger.info(f"価格帯分布: {band_counts.to_dict()}")
        
        return df


class DiscountAnalyzer:
    """Performs statistical analysis on discount effectiveness."""
    
    def __init__(
        self,
        min_sample_size: int = MIN_SAMPLE_SIZE,
        significance_level: float = SIGNIFICANCE_LEVEL
    ):
        self.min_sample_size = min_sample_size
        self.significance_level = significance_level
    
    def analyze(self, df: pd.DataFrame, group_by: str = 'pf') -> List[SegmentAnalysisResult]:
        """
        Analyze discount effectiveness by PF or GL × Price Band.
        
        Args:
            df: DataFrame with pf/gl, price_band, current_discount_percent, growth_rate
            group_by: 'pf' or 'gl' for grouping
            
        Returns:
            List of SegmentAnalysisResult for each segment
        """
        results = []
        
        # Exclude outliers for analysis
        analysis_df = df[~df['is_outlier']].copy()
        
        # Group by specified column and Price Band
        grouped = analysis_df.groupby([group_by, 'price_band'])
        
        for (category, price_band), group in grouped:
            result = self._analyze_segment(str(category), price_band, group, group_by)
            results.append(result)
        
        logger.info(f"{len(results)}セグメントの分析を完了 (by {group_by})")
        return results
    
    def analyze_by_gl_price_discount(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze average growth rate by GL × Price Band × Discount Tier.
        
        Args:
            df: DataFrame with gl, price_band, discount_tier, growth_rate
            
        Returns:
            DataFrame with aggregated statistics
        """
        # Exclude outliers
        analysis_df = df[~df['is_outlier']].copy()
        
        # Group by GL, Price Band, and Discount Tier
        grouped = analysis_df.groupby(['gl', 'price_band', 'discount_tier']).agg({
            'growth_rate': ['mean', 'std', 'count'],
            'current_discount_percent': 'mean',
            'promotion_ops': 'sum',
            'past_month_gms': 'sum'
        }).reset_index()
        
        # Flatten column names
        grouped.columns = ['gl', 'price_band', 'discount_tier', 
                          'avg_growth_rate', 'std_growth_rate', 'sample_count',
                          'avg_discount', 'total_promotion_ops', 'total_past_gms']
        
        # Round values
        grouped['avg_growth_rate'] = grouped['avg_growth_rate'].round(2)
        grouped['std_growth_rate'] = grouped['std_growth_rate'].round(2)
        grouped['avg_discount'] = grouped['avg_discount'].round(2)
        
        return grouped
    
    def _analyze_segment(
        self, category: str, price_band: str, group: pd.DataFrame, group_by: str = 'pf'
    ) -> SegmentAnalysisResult:
        """Analyze a single segment."""
        sample_count = len(group)
        
        # Basic statistics
        mean_discount = group['current_discount_percent'].mean()
        mean_growth_rate = group['growth_rate'].mean()
        std_discount = group['current_discount_percent'].std()
        std_growth_rate = group['growth_rate'].std()
        
        # Get GL value if available
        gl_value = group['gl'].iloc[0] if 'gl' in group.columns else ''
        
        result = SegmentAnalysisResult(
            pf=str(category) if group_by == 'pf' else '',
            price_band=str(price_band),
            sample_count=sample_count,
            mean_discount=round(mean_discount, 2) if not pd.isna(mean_discount) else 0.0,
            mean_growth_rate=round(mean_growth_rate, 2) if not pd.isna(mean_growth_rate) else 0.0,
            std_discount=round(std_discount, 2) if not pd.isna(std_discount) else 0.0,
            std_growth_rate=round(std_growth_rate, 2) if not pd.isna(std_growth_rate) else 0.0,
            gl=str(category) if group_by == 'gl' else gl_value
        )
        
        # Check sample size
        if sample_count < self.min_sample_size:
            result.is_insufficient_sample = True
            return result
        
        # Correlation analysis
        x = group['current_discount_percent'].values
        y = group['growth_rate'].values
        
        # Check for variance
        if np.std(x) == 0 or np.std(y) == 0:
            result.is_insufficient_sample = True
            return result
        
        try:
            # Correlation
            correlation, _ = stats.pearsonr(x, y)
            result.correlation = round(correlation, 4)
            
            # Linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            result.regression_coef = round(slope, 4)
            result.regression_intercept = round(intercept, 4)
            result.r_squared = round(r_value ** 2, 4)
            result.p_value = round(p_value, 4)
            result.is_significant = p_value <= self.significance_level
            
        except Exception as e:
            logger.warning(f"統計計算エラー ({category} × {price_band}): {e}")
        
        return result



class OptimalDiscountEstimator:
    """Estimates optimal discount rates based on analysis results."""
    
    def __init__(
        self,
        discount_min: float = DISCOUNT_MIN,
        discount_max: float = DISCOUNT_MAX
    ):
        self.discount_min = discount_min
        self.discount_max = discount_max
    
    def estimate(
        self, analysis_results: List[SegmentAnalysisResult]
    ) -> List[OptimalDiscountRecommendation]:
        """
        Estimate optimal discount rates for each segment.
        
        Args:
            analysis_results: List of segment analysis results
            
        Returns:
            List of optimal discount recommendations
        """
        recommendations = []
        
        for result in analysis_results:
            recommendation = self._estimate_segment(result)
            recommendations.append(recommendation)
        
        return recommendations
    
    def _estimate_segment(
        self, result: SegmentAnalysisResult
    ) -> OptimalDiscountRecommendation:
        """Estimate optimal discount for a single segment."""
        
        # Handle insufficient sample
        if result.is_insufficient_sample:
            return OptimalDiscountRecommendation(
                pf=result.pf,
                price_band=result.price_band,
                optimal_discount_rate=result.mean_discount,
                expected_growth_rate=result.mean_growth_rate,
                confidence_level='低',
                note='サンプル数不足のため統計分析不可'
            )
        
        # Handle non-significant relationship
        if not result.is_significant:
            return OptimalDiscountRecommendation(
                pf=result.pf,
                price_band=result.price_band,
                optimal_discount_rate=result.mean_discount,
                expected_growth_rate=result.mean_growth_rate,
                confidence_level='低',
                note='統計的に有意な関係なし'
            )
        
        # Calculate optimal discount based on regression
        coef = result.regression_coef or 0
        intercept = result.regression_intercept or 0
        
        # If positive coefficient, higher discount = higher growth
        # Recommend max discount within range
        if coef > 0:
            optimal_discount = self.discount_max
            confidence = '高' if result.r_squared and result.r_squared > 0.3 else '中'
        # If negative coefficient, lower discount = higher growth
        elif coef < 0:
            optimal_discount = self.discount_min
            confidence = '高' if result.r_squared and result.r_squared > 0.3 else '中'
        else:
            optimal_discount = result.mean_discount
            confidence = '低'
        
        # Ensure within bounds
        optimal_discount = max(self.discount_min, min(self.discount_max, optimal_discount))
        
        # Calculate expected growth rate
        expected_growth = intercept + coef * optimal_discount
        
        # Determine note
        if coef > 0:
            note = f'割引率を上げると売上伸び率が向上（係数: {coef:.2f}）'
        elif coef < 0:
            note = f'割引率を下げると売上伸び率が向上（係数: {coef:.2f}）'
        else:
            note = '割引率と売上伸び率に明確な関係なし'
        
        return OptimalDiscountRecommendation(
            pf=result.pf,
            price_band=result.price_band,
            optimal_discount_rate=round(optimal_discount, 2),
            expected_growth_rate=round(expected_growth, 2),
            confidence_level=confidence,
            note=note
        )
