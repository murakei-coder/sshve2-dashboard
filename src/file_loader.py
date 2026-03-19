"""
File Loader module for Deal Sourcing Analyzer.
Handles loading txt files from the data directory.
"""
from pathlib import Path
from typing import List, Dict, Any, Union

import pandas as pd


class FileLoader:
    """Loads txt files from the specified data directory."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
    
    def load_file(self, filename: str, chunksize: int = None, aggregate_mode: bool = False) -> Union[pd.DataFrame, Dict[str, Any]]:
        """
        Load a txt file.
        
        Args:
            filename: Name of the file to load
            chunksize: Chunk size for reading (ignored if aggregate_mode=False)
            aggregate_mode: If True, return aggregated results instead of DataFrame
            
        Returns:
            DataFrame or dict with aggregated results
        """
        file_path = self.data_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
        
        if aggregate_mode:
            return self._load_aggregated(file_path, chunksize or 100000)
        else:
            return self._load_normal(file_path)
    
    def _load_normal(self, file_path: Path) -> pd.DataFrame:
        """Load file normally into DataFrame."""
        dtype_map = {
            'paid-flag': 'category',
            'price&pointsdealflag': 'category',
            'priceband': 'category',
            'asintenure': 'category',
            'gms': 'float32',
            'units': 'float32',
            'our_price': 'float32',
            'asin_tenure_days': 'float32'
        }
        
        try:
            df = pd.read_csv(file_path, sep='\t', encoding='utf-8',
                           dtype=dtype_map, low_memory=True, on_bad_lines='skip')
            return df
        except Exception:
            df = pd.read_csv(file_path, sep=',', encoding='utf-8',
                           dtype=dtype_map, low_memory=True, on_bad_lines='skip')
            return df
    
    def _load_aggregated(self, file_path: Path, chunksize: int) -> Dict[str, Any]:
        """Load file in chunks and return aggregated results."""
        usecols = ['paid-flag', 'price&pointsdealflag', 'priceband', 'asintenure', 
                   'gms', 'our_price', 'asin_tenure_days']
        
        dtype_map = {
            'paid-flag': 'str',
            'price&pointsdealflag': 'str',
            'priceband': 'str',
            'asintenure': 'str',
            'gms': 'float32',
            'our_price': 'float32',
            'asin_tenure_days': 'float32'
        }
        
        paid_agg = {}
        priceband_agg = {}
        tenure_agg = {}
        price_samples = {'Sourced': [], 'NonSourced': []}
        tenure_samples = {'Sourced': [], 'NonSourced': []}
        sample_limit = 50000
        total_rows = 0
        
        chunk_iter = pd.read_csv(file_path, sep='\t', encoding='utf-8',
                                chunksize=chunksize, usecols=usecols,
                                dtype=dtype_map, low_memory=True, on_bad_lines='skip')
        
        for chunk in chunk_iter:
            total_rows += len(chunk)
            
            for (paid, status), group in chunk.groupby(['paid-flag', 'price&pointsdealflag']):
                key = (paid, status)
                if key not in paid_agg:
                    paid_agg[key] = {'gms_sum': 0, 'count': 0}
                paid_agg[key]['gms_sum'] += group['gms'].sum()
                paid_agg[key]['count'] += len(group)
            
            for (band, status), group in chunk.groupby(['priceband', 'price&pointsdealflag']):
                key = (band, status)
                if key not in priceband_agg:
                    priceband_agg[key] = {'gms_sum': 0, 'count': 0}
                priceband_agg[key]['gms_sum'] += group['gms'].sum()
                priceband_agg[key]['count'] += len(group)
            
            for (tenure, status), group in chunk.groupby(['asintenure', 'price&pointsdealflag']):
                key = (tenure, status)
                if key not in tenure_agg:
                    tenure_agg[key] = {'gms_sum': 0, 'count': 0}
                tenure_agg[key]['gms_sum'] += group['gms'].sum()
                tenure_agg[key]['count'] += len(group)
            
            for status in ['Sourced', 'NonSourced']:
                status_data = chunk[chunk['price&pointsdealflag'] == status]
                if len(price_samples[status]) < sample_limit and len(status_data) > 0:
                    remaining = sample_limit - len(price_samples[status])
                    sample_size = min(remaining, len(status_data))
                    sampled = status_data.head(sample_size)
                    price_samples[status].extend(sampled['our_price'].dropna().tolist())
                    tenure_samples[status].extend(sampled['asin_tenure_days'].dropna().tolist())
        
        return {
            'paid_agg': paid_agg,
            'priceband_agg': priceband_agg,
            'tenure_agg': tenure_agg,
            'price_samples': price_samples,
            'tenure_samples': tenure_samples,
            'total_rows': total_rows
        }
    
    def list_available_files(self) -> List[str]:
        """List all available txt files in the data directory."""
        if not self.data_dir.exists():
            return []
        return [f.name for f in self.data_dir.glob("*.txt")]
