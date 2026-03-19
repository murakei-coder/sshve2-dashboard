"""
Large File Loader for Deal Sourcing Analyzer.
Handles loading large txt files with streaming aggregation.
"""
from pathlib import Path
from typing import Dict, Any

import pandas as pd


def load_large_file(file_path: str, chunksize: int = 100000) -> Dict[str, Any]:
    """
    Load a large file and return pre-aggregated results.
    Processes file in chunks to avoid memory issues.
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"ファイルが見つかりません: {path}")
    
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
    
    chunk_iter = pd.read_csv(path, sep='\t', encoding='utf-8',
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
