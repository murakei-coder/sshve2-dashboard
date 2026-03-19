"""
Target data processor module for the Bridge Plan Generator.

This module handles processing of target data including extraction of T30 GMS targets,
gap calculation, and identification of missing targets for data consistency checks.
"""

import pandas as pd
from typing import Set, List


class TargetProcessor:
    """Processes target data and calculates gaps between current and target performance."""
    
    def extract_targets(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract T30 GMS Target values for each CID.
        
        Args:
            df: DataFrame containing target data with 'CID' and 'T30_GMS_Target' columns
            
        Returns:
            DataFrame with CID and t30_gms_target columns
            
        Raises:
            KeyError: If required columns are missing
        """
        required_cols = ['CID', 't30_gms_target']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise KeyError(f"Missing required columns: {', '.join(missing)}")
        
        result = df[['CID', 't30_gms_target']].copy()
        
        # Convert to numeric, coercing errors to NaN
        result['t30_gms_target'] = pd.to_numeric(result['t30_gms_target'], errors='coerce')
        
        return result
    
    def calculate_gaps(self, current: pd.DataFrame, targets: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the gap between T30 GMS Target and current T30 GMS BAU for each CID.
        
        Gap = Target - Current
        Negative gap means target is already achieved.
        
        Args:
            current: DataFrame with CID and t30_gms_bau_total columns (current performance)
            targets: DataFrame with CID and t30_gms_target columns (target performance)
            
        Returns:
            DataFrame with CID, t30_gms_bau_total, t30_gms_target, and gap columns
            
        Raises:
            KeyError: If required columns are missing
        """
        # Validate current DataFrame
        if 't30_gms_bau_total' not in current.columns:
            raise KeyError("Missing required column in current data: t30_gms_bau_total")
        if 'CID' not in current.columns:
            raise KeyError("Missing required column in current data: CID")
        
        # Validate targets DataFrame
        if 't30_gms_target' not in targets.columns:
            raise KeyError("Missing required column in targets data: t30_gms_target")
        if 'CID' not in targets.columns:
            raise KeyError("Missing required column in targets data: CID")
        
        # Merge current and targets on CID
        result = pd.merge(
            current[['CID', 't30_gms_bau_total']],
            targets[['CID', 't30_gms_target']],
            on='CID',
            how='outer'
        )
        
        # Calculate gap: target - current
        result['gap'] = result['t30_gms_target'] - result['t30_gms_bau_total']
        
        return result
    
    def identify_missing_targets(self, sourcing_cids: Set[str], target_cids: Set[str]) -> List[str]:
        """
        Identify CIDs that exist in sourcing data but not in target data.
        
        This is a data consistency check to flag potential data quality issues.
        
        Args:
            sourcing_cids: Set of CIDs from sourcing data
            target_cids: Set of CIDs from target data
            
        Returns:
            List of CIDs that are in sourcing but missing from targets
        """
        missing = sourcing_cids - target_cids
        return sorted(list(missing))
