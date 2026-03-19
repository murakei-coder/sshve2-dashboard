"""
Sourcing data processor module for the Bridge Plan Generator.

This module handles processing of sourcing data including extraction of T30 GMS BAU,
event participation flags, participation score calculation, and aggregation by CID.
"""

import pandas as pd
from typing import Dict


class SourcingProcessor:
    """Processes sourcing data with event participation history."""
    
    # Event flag weights ordered by recency (most recent to least recent)
    EVENT_FLAG_WEIGHTS = {
        'sshve1_flag': 1.0,      # Most recent
        'fy26_mde2_flag': 0.8,
        'nys26_flag': 0.6,
        'bf25_flag': 0.4,
        'fy25_mde4_flag': 0.2,
        't365_flag': 0.1         # Least recent
    }
    
    def extract_t30_gms_bau(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract T30 GMS BAU values from column T (total_t30d_gms_BAU) for each ASIN×CID combination.
        
        Args:
            df: DataFrame containing sourcing data with 'total_t30d_gms_BAU' column
            
        Returns:
            DataFrame with ASIN, CID, and t30_gms_bau columns
            
        Raises:
            KeyError: If required columns are missing
        """
        required_cols = ['ASIN', 'CID', 'total_t30d_gms_BAU']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise KeyError(f"Missing required columns: {', '.join(missing)}")
        
        result = df[['ASIN', 'CID', 'total_t30d_gms_BAU']].copy()
        result.rename(columns={'total_t30d_gms_BAU': 't30_gms_bau'}, inplace=True)
        
        # Convert to numeric, coercing errors to NaN
        result['t30_gms_bau'] = pd.to_numeric(result['t30_gms_bau'], errors='coerce')
        
        return result
    
    def extract_event_flags(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract all event participation flags for each ASIN.
        
        Args:
            df: DataFrame containing sourcing data with event flag columns
            
        Returns:
            DataFrame with ASIN and all event flag columns
            
        Raises:
            KeyError: If required columns are missing
        """
        required_cols = ['ASIN'] + list(self.EVENT_FLAG_WEIGHTS.keys())
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise KeyError(f"Missing required columns: {', '.join(missing)}")
        
        result = df[required_cols].copy()
        
        return result
    
    def calculate_participation_score(self, flags: Dict[str, str]) -> float:
        """
        Calculate participation likelihood score based on event flags with recency weighting.
        
        More recent event participation (Y values in earlier flag columns) results in higher scores.
        
        Args:
            flags: Dictionary mapping flag names to 'Y' or 'N' values
            
        Returns:
            Participation score normalized to 0-1 range
        """
        score = 0.0
        total_weight = sum(self.EVENT_FLAG_WEIGHTS.values())
        
        for flag_name, weight in self.EVENT_FLAG_WEIGHTS.items():
            if flags.get(flag_name) == 'Y':
                score += weight
        
        return score / total_weight
    
    def aggregate_by_cid(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate T30 GMS BAU values by CID, summing all ASINs belonging to each CID.
        
        Args:
            df: DataFrame with CID and t30_gms_bau columns
            
        Returns:
            DataFrame with CID and aggregated t30_gms_bau_total columns
            
        Raises:
            KeyError: If required columns are missing
        """
        required_cols = ['CID', 't30_gms_bau']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise KeyError(f"Missing required columns: {', '.join(missing)}")
        
        result = df.groupby('CID', as_index=False)['t30_gms_bau'].sum()
        result.rename(columns={'t30_gms_bau': 't30_gms_bau_total'}, inplace=True)
        
        return result
