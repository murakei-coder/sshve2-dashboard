"""
Analyzer module for Deal Sourcing Analyzer.
Contains the main analysis logic for Sourced/NonSourced data.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
import numpy as np

import pandas as pd

from src.constants import PRICE_BAND_ORDER, TENURE_ORDER


@dataclass
class SummaryResult:
    """Overall summary of the analysis."""
    total_gms: float
    total_asin_count: int
    sourced_asin_count: int
    nonsourced_asin_count: int
    overall_sourced_rate: float
    overall_sourced_rate_gms_weighted: float
    total_opportunity_gms: float


class Analyzer:
    """
    Main analysis engine for Deal Sourcing data.
    Supports both DataFrame mode (small files) and aggregated mode (large files).
    """
    
    def __init__(self, data):
        """
        Initialize Analyzer with data.
        
        Args:
            data: Either a DataFrame (small files) or dict with aggregated results (large files)
        """
        # Check if data is aggregated (dict with 'paid_agg' key)
        if isinstance(data, dict) and 'paid_agg' in data:
            # Aggregated mode for large files
            self.mode = 'aggregated'
            self.agg_data = data
            self.df = None
        else:
            # DataFrame mode for small files
            self.mode = 'dataframe'
            self.df = data
            self.agg_data = None
    
    def get_summary(self) -> SummaryResult:
        """Get overall summary statistics."""
        if self.mode == 'aggregated':
            return self._get_summary_aggregated()
        else:
            return self._get_summary_dataframe()
    
    def _get_summary_aggregated(self) -> SummaryResult:
        """Get summary from aggregated data."""
        paid_agg = self.agg_data['paid_agg']
        
        total_gms = 0
        total_count = 0
        sourced_gms = 0
        sourced_count = 0
        
        for (paid, status), vals in paid_agg.items():
            total_gms += vals['gms_sum']
            total_count += vals['count']
            if status == 'Sourced':
                sourced_gms += vals['gms_sum']
                sourced_count += vals['count']
        
        nonsourced_gms = total_gms - sourced_gms
        nonsourced_count = total_count - sourced_count
        
        return SummaryResult(
            total_gms=total_gms,
            total_asin_count=total_count,
            sourced_asin_count=sourced_count,
            nonsourced_asin_count=nonsourced_count,
            overall_sourced_rate=sourced_count / total_count if total_count > 0 else 0,
            overall_sourced_rate_gms_weighted=sourced_gms / total_gms if total_gms > 0 else 0,
            total_opportunity_gms=nonsourced_gms
        )
    
    def _get_summary_dataframe(self) -> SummaryResult:
        """Get summary from DataFrame."""
        total_gms = self.df['gms'].sum()
        total_asin_count = len(self.df)
        
        gms_by_status = self.df.groupby('price&pointsdealflag')['gms'].sum()
        count_by_status = self.df.groupby('price&pointsdealflag').size()
        
        sourced_gms = gms_by_status.get('Sourced', 0)
        nonsourced_gms = gms_by_status.get('NonSourced', 0)
        sourced_asin_count = count_by_status.get('Sourced', 0)
        nonsourced_asin_count = count_by_status.get('NonSourced', 0)
        
        return SummaryResult(
            total_gms=total_gms,
            total_asin_count=total_asin_count,
            sourced_asin_count=int(sourced_asin_count),
            nonsourced_asin_count=int(nonsourced_asin_count),
            overall_sourced_rate=sourced_asin_count / total_asin_count if total_asin_count > 0 else 0,
            overall_sourced_rate_gms_weighted=sourced_gms / total_gms if total_gms > 0 else 0,
            total_opportunity_gms=nonsourced_gms
        )
    
    def analyze_by_paid_flag(self) -> pd.DataFrame:
        """Analyze data grouped by Paid-Flag (Y/N)."""
        if self.mode == 'aggregated':
            return self._analyze_by_paid_flag_aggregated()
        else:
            return self._analyze_by_paid_flag_dataframe()
    
    def _analyze_by_paid_flag_aggregated(self) -> pd.DataFrame:
        """Analyze by paid flag from aggregated data."""
        paid_agg = self.agg_data['paid_agg']
        results = []
        
        for paid_flag in ['Y', 'N']:
            sourced_key = (paid_flag, 'Sourced')
            nonsourced_key = (paid_flag, 'NonSourced')
            
            sourced_gms = paid_agg.get(sourced_key, {}).get('gms_sum', 0)
            nonsourced_gms = paid_agg.get(nonsourced_key, {}).get('gms_sum', 0)
            sourced_count = paid_agg.get(sourced_key, {}).get('count', 0)
            nonsourced_count = paid_agg.get(nonsourced_key, {}).get('count', 0)
            
            total_gms = sourced_gms + nonsourced_gms
            total_count = sourced_count + nonsourced_count
            
            if total_count == 0:
                continue
            
            results.append({
                'paid-flag': paid_flag,
                'total_gms': total_gms,
                'sourced_gms': sourced_gms,
                'nonsourced_gms': nonsourced_gms,
                'total_asin_count': total_count,
                'sourced_asin_count': sourced_count,
                'nonsourced_asin_count': nonsourced_count,
                'sourced_rate': sourced_count / total_count if total_count > 0 else 0,
                'sourced_rate_gms_weighted': sourced_gms / total_gms if total_gms > 0 else 0,
                'gms_per_asin': total_gms / total_count if total_count > 0 else 0,
                'opportunity_gms': nonsourced_gms
            })
        
        return pd.DataFrame(results)
    
    def _analyze_by_paid_flag_dataframe(self) -> pd.DataFrame:
        """Analyze by paid flag from DataFrame."""
        grouped = self.df.groupby(['paid-flag', 'price&pointsdealflag']).agg(
            gms_sum=('gms', 'sum'),
            count=('gms', 'size')
        ).reset_index()
        
        results = []
        for paid_flag in ['Y', 'N']:
            flag_data = grouped[grouped['paid-flag'] == paid_flag]
            if len(flag_data) == 0:
                continue
            
            sourced_row = flag_data[flag_data['price&pointsdealflag'] == 'Sourced']
            nonsourced_row = flag_data[flag_data['price&pointsdealflag'] == 'NonSourced']
            
            sourced_gms = sourced_row['gms_sum'].sum() if len(sourced_row) > 0 else 0
            nonsourced_gms = nonsourced_row['gms_sum'].sum() if len(nonsourced_row) > 0 else 0
            sourced_count = int(sourced_row['count'].sum()) if len(sourced_row) > 0 else 0
            nonsourced_count = int(nonsourced_row['count'].sum()) if len(nonsourced_row) > 0 else 0
            
            total_gms = sourced_gms + nonsourced_gms
            total_count = sourced_count + nonsourced_count
            
            results.append({
                'paid-flag': paid_flag,
                'total_gms': total_gms,
                'sourced_gms': sourced_gms,
                'nonsourced_gms': nonsourced_gms,
                'total_asin_count': total_count,
                'sourced_asin_count': sourced_count,
                'nonsourced_asin_count': nonsourced_count,
                'sourced_rate': sourced_count / total_count if total_count > 0 else 0,
                'sourced_rate_gms_weighted': sourced_gms / total_gms if total_gms > 0 else 0,
                'gms_per_asin': total_gms / total_count if total_count > 0 else 0,
                'opportunity_gms': nonsourced_gms
            })
        
        return pd.DataFrame(results)

    def analyze_by_price_band(self) -> pd.DataFrame:
        """Analyze data grouped by PriceBand."""
        if self.mode == 'aggregated':
            return self._analyze_by_segment_aggregated(self.agg_data['priceband_agg'], 'priceband', PRICE_BAND_ORDER)
        else:
            return self._analyze_by_segment_dataframe('priceband', PRICE_BAND_ORDER)
    
    def analyze_by_tenure(self) -> pd.DataFrame:
        """Analyze data grouped by ASINTenure."""
        if self.mode == 'aggregated':
            return self._analyze_by_segment_aggregated(self.agg_data['tenure_agg'], 'asintenure', TENURE_ORDER)
        else:
            return self._analyze_by_segment_dataframe('asintenure', TENURE_ORDER)
    
    def _analyze_by_segment_aggregated(self, agg_data: Dict, col_name: str, order: list) -> pd.DataFrame:
        """Generic segment analysis from aggregated data."""
        # Calculate total GMS for opportunity ratio
        total_gms_all = sum(v['gms_sum'] for v in agg_data.values())
        
        results = []
        for segment in order:
            sourced_key = (segment, 'Sourced')
            nonsourced_key = (segment, 'NonSourced')
            
            sourced_gms = agg_data.get(sourced_key, {}).get('gms_sum', 0)
            nonsourced_gms = agg_data.get(nonsourced_key, {}).get('gms_sum', 0)
            sourced_count = agg_data.get(sourced_key, {}).get('count', 0)
            nonsourced_count = agg_data.get(nonsourced_key, {}).get('count', 0)
            
            total_gms = sourced_gms + nonsourced_gms
            total_count = sourced_count + nonsourced_count
            
            if total_count == 0:
                continue
            
            results.append({
                col_name: segment,
                'total_gms': total_gms,
                'sourced_gms': sourced_gms,
                'nonsourced_gms': nonsourced_gms,
                'total_asin_count': total_count,
                'sourced_asin_count': sourced_count,
                'nonsourced_asin_count': nonsourced_count,
                'sourced_rate': sourced_count / total_count if total_count > 0 else 0,
                'sourced_rate_gms_weighted': sourced_gms / total_gms if total_gms > 0 else 0,
                'gms_per_asin': total_gms / total_count if total_count > 0 else 0,
                'opportunity_gms': nonsourced_gms,
                'opportunity_ratio': nonsourced_gms / total_gms_all if total_gms_all > 0 else 0
            })
        
        return pd.DataFrame(results)
    
    def _analyze_by_segment_dataframe(self, col_name: str, order: list) -> pd.DataFrame:
        """Generic segment analysis from DataFrame."""
        total_gms_all = self.df['gms'].sum()
        
        grouped = self.df.groupby([col_name, 'price&pointsdealflag']).agg(
            gms_sum=('gms', 'sum'),
            count=('gms', 'size')
        ).reset_index()
        
        results = []
        for segment in order:
            seg_data = grouped[grouped[col_name] == segment]
            if len(seg_data) == 0:
                continue
            
            sourced_row = seg_data[seg_data['price&pointsdealflag'] == 'Sourced']
            nonsourced_row = seg_data[seg_data['price&pointsdealflag'] == 'NonSourced']
            
            sourced_gms = sourced_row['gms_sum'].sum() if len(sourced_row) > 0 else 0
            nonsourced_gms = nonsourced_row['gms_sum'].sum() if len(nonsourced_row) > 0 else 0
            sourced_count = int(sourced_row['count'].sum()) if len(sourced_row) > 0 else 0
            nonsourced_count = int(nonsourced_row['count'].sum()) if len(nonsourced_row) > 0 else 0
            
            total_gms = sourced_gms + nonsourced_gms
            total_count = sourced_count + nonsourced_count
            
            results.append({
                col_name: segment,
                'total_gms': total_gms,
                'sourced_gms': sourced_gms,
                'nonsourced_gms': nonsourced_gms,
                'total_asin_count': total_count,
                'sourced_asin_count': sourced_count,
                'nonsourced_asin_count': nonsourced_count,
                'sourced_rate': sourced_count / total_count if total_count > 0 else 0,
                'sourced_rate_gms_weighted': sourced_gms / total_gms if total_gms > 0 else 0,
                'gms_per_asin': total_gms / total_count if total_count > 0 else 0,
                'opportunity_gms': nonsourced_gms,
                'opportunity_ratio': nonsourced_gms / total_gms_all if total_gms_all > 0 else 0
            })
        
        return pd.DataFrame(results)

    def calculate_opportunity_score(self, segment_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate opportunity scores for each segment."""
        result = segment_df.copy()
        
        def get_opportunity_level(row):
            if row['sourced_rate'] >= 0.8:
                return '低'
            elif row['opportunity_ratio'] >= result['opportunity_ratio'].quantile(0.75):
                return '高'
            else:
                return '中'
        
        result['opportunity_level'] = result.apply(get_opportunity_level, axis=1)
        
        if len(result) > 0:
            gms_per_asin_threshold = result['gms_per_asin'].quantile(0.75)
            result['strong_asin'] = result['gms_per_asin'] >= gms_per_asin_threshold
        else:
            result['strong_asin'] = False
        
        return result

    def get_price_statistics(self) -> pd.DataFrame:
        """Get detailed price statistics."""
        if self.mode == 'aggregated':
            return self._get_price_statistics_aggregated()
        else:
            return self._get_price_statistics_dataframe()
    
    def _get_price_statistics_aggregated(self) -> pd.DataFrame:
        """Get price statistics from sampled data."""
        price_samples = self.agg_data['price_samples']
        results = []
        
        for status in ['Sourced', 'NonSourced']:
            samples = price_samples.get(status, [])
            if len(samples) == 0:
                continue
            
            arr = np.array(samples)
            results.append({
                'status': status,
                'count': len(samples),
                'price_mean': np.mean(arr),
                'price_median': np.median(arr),
                'price_std': np.std(arr),
                'price_min': np.min(arr),
                'price_max': np.max(arr),
                'price_25pct': np.percentile(arr, 25),
                'price_75pct': np.percentile(arr, 75),
            })
        
        return pd.DataFrame(results)
    
    def _get_price_statistics_dataframe(self) -> pd.DataFrame:
        """Get price statistics from DataFrame."""
        results = []
        
        for status in ['Sourced', 'NonSourced']:
            mask = self.df['price&pointsdealflag'] == status
            count = mask.sum()
            
            if count == 0:
                continue
            
            price_col = pd.to_numeric(self.df.loc[mask, 'our_price'], errors='coerce').dropna()
            
            if len(price_col) > 0:
                results.append({
                    'status': status,
                    'count': count,
                    'price_mean': price_col.mean(),
                    'price_median': price_col.median(),
                    'price_std': price_col.std(),
                    'price_min': price_col.min(),
                    'price_max': price_col.max(),
                    'price_25pct': price_col.quantile(0.25),
                    'price_75pct': price_col.quantile(0.75),
                })
        
        return pd.DataFrame(results)
    
    def get_tenure_statistics(self) -> pd.DataFrame:
        """Get detailed tenure statistics."""
        if self.mode == 'aggregated':
            return self._get_tenure_statistics_aggregated()
        else:
            return self._get_tenure_statistics_dataframe()
    
    def _get_tenure_statistics_aggregated(self) -> pd.DataFrame:
        """Get tenure statistics from sampled data."""
        tenure_samples = self.agg_data['tenure_samples']
        results = []
        
        for status in ['Sourced', 'NonSourced']:
            samples = tenure_samples.get(status, [])
            if len(samples) == 0:
                continue
            
            arr = np.array(samples)
            results.append({
                'status': status,
                'count': len(samples),
                'tenure_mean': np.mean(arr),
                'tenure_median': np.median(arr),
                'tenure_std': np.std(arr),
                'tenure_min': np.min(arr),
                'tenure_max': np.max(arr),
                'tenure_25pct': np.percentile(arr, 25),
                'tenure_75pct': np.percentile(arr, 75),
            })
        
        return pd.DataFrame(results)
    
    def _get_tenure_statistics_dataframe(self) -> pd.DataFrame:
        """Get tenure statistics from DataFrame."""
        results = []
        
        for status in ['Sourced', 'NonSourced']:
            mask = self.df['price&pointsdealflag'] == status
            count = mask.sum()
            
            if count == 0:
                continue
            
            tenure_col = pd.to_numeric(self.df.loc[mask, 'asin_tenure_days'], errors='coerce').dropna()
            
            if len(tenure_col) > 0:
                results.append({
                    'status': status,
                    'count': count,
                    'tenure_mean': tenure_col.mean(),
                    'tenure_median': tenure_col.median(),
                    'tenure_std': tenure_col.std(),
                    'tenure_min': tenure_col.min(),
                    'tenure_max': tenure_col.max(),
                    'tenure_25pct': tenure_col.quantile(0.25),
                    'tenure_75pct': tenure_col.quantile(0.75),
                })
        
        return pd.DataFrame(results)
    
    def get_correlation_analysis(self, sample_size: int = 100000) -> dict:
        """Analyze correlations between price, tenure, and GMS."""
        if self.mode == 'aggregated':
            # Use sampled data for correlation
            price_samples = self.agg_data['price_samples']
            tenure_samples = self.agg_data['tenure_samples']
            
            # Combine samples
            all_prices = price_samples.get('Sourced', []) + price_samples.get('NonSourced', [])
            all_tenures = tenure_samples.get('Sourced', []) + tenure_samples.get('NonSourced', [])
            
            if len(all_prices) < 2 or len(all_tenures) < 2:
                return {'price_gms_corr': 0, 'tenure_gms_corr': 0, 'price_tenure_corr': 0}
            
            # For aggregated mode, we can only compute price-tenure correlation
            min_len = min(len(all_prices), len(all_tenures))
            prices = np.array(all_prices[:min_len])
            tenures = np.array(all_tenures[:min_len])
            
            price_tenure_corr = np.corrcoef(prices, tenures)[0, 1] if min_len > 1 else 0
            
            return {
                'price_gms_corr': 0,  # Cannot compute without raw GMS data
                'tenure_gms_corr': 0,
                'price_tenure_corr': price_tenure_corr if not np.isnan(price_tenure_corr) else 0
            }
        else:
            cols = ['our_price', 'asin_tenure_days', 'gms']
            df_subset = self.df[cols].copy()
            
            df_subset['our_price'] = pd.to_numeric(df_subset['our_price'], errors='coerce')
            df_subset['asin_tenure_days'] = pd.to_numeric(df_subset['asin_tenure_days'], errors='coerce')
            df_subset['gms'] = pd.to_numeric(df_subset['gms'], errors='coerce')
            
            valid_df = df_subset.dropna()
            
            if len(valid_df) < 2:
                return {'price_gms_corr': 0, 'tenure_gms_corr': 0, 'price_tenure_corr': 0}
            
            if len(valid_df) > sample_size:
                valid_df = valid_df.sample(n=sample_size, random_state=42)
            
            return {
                'price_gms_corr': valid_df['our_price'].corr(valid_df['gms']),
                'tenure_gms_corr': valid_df['asin_tenure_days'].corr(valid_df['gms']),
                'price_tenure_corr': valid_df['our_price'].corr(valid_df['asin_tenure_days'])
            }
