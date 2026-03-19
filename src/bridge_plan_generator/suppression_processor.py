"""
Suppression data processor module for the Bridge Plan Generator.

This module handles processing of suppression data including extraction of benchmark
percentages, validation of percentage sums, calculation of current suppression status,
and aggregation by CID and Product Family.
"""

import pandas as pd
from typing import Dict


class SuppressionProcessor:
    """Processes suppression data with benchmark and current status analysis."""
    
    # Suppression category mapping (1-5)
    SUPPRESSION_CATEGORIES = {
        1: "No suppression",
        2: "OOS",
        3: "VRP missing",
        4: "Price Error",
        5: "Others"
    }
    
    # Tolerance for percentage sum validation (1%)
    PERCENTAGE_SUM_TOLERANCE = 1.0
    
    def extract_benchmark_percentages(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Extract suppression reason percentages from benchmark data.
        
        Args:
            df: DataFrame containing benchmark suppression data with 'suppression_category' and 'percentage' columns
            
        Returns:
            Dictionary mapping suppression category names to their percentages
            
        Raises:
            KeyError: If required columns are missing
        """
        # Check for required columns
        required_cols = ['suppression_category', 'percentage']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise KeyError(f"Missing required columns: {', '.join(missing)}")
        
        # Extract percentages from the DataFrame
        if len(df) == 0:
            raise ValueError("Benchmark data is empty")
        
        # Build dictionary from suppression_category and percentage columns
        percentages = {}
        for _, row in df.iterrows():
            category = str(row['suppression_category']).strip()
            pct = float(row['percentage'])
            percentages[category] = pct
        
        return percentages
    
    def validate_percentage_sum(self, percentages: Dict[str, float]) -> bool:
        """
        Validate that suppression percentages sum to approximately 100% within tolerance.
        
        Args:
            percentages: Dictionary mapping category names to percentage values
            
        Returns:
            True if percentages sum to 100% within 1% tolerance, False otherwise
        """
        total = sum(percentages.values())
        return abs(total - 100.0) <= self.PERCENTAGE_SUM_TOLERANCE
    
    def calculate_current_suppression(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate current suppression percentages from ASIN suppression categories.
        
        Args:
            df: DataFrame containing ASIN data with 'suppression_category_large' column
            
        Returns:
            DataFrame with suppression category counts and percentages
            
        Raises:
            KeyError: If required columns are missing
        """
        required_cols = ['ASIN', 'suppression_category_large']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise KeyError(f"Missing required columns: {', '.join(missing)}")
        
        # Count ASINs in each suppression category
        category_counts = df['suppression_category_large'].value_counts()
        
        # Calculate total ASINs
        total_asins = len(df)
        
        # Build result DataFrame with all categories
        result_data = []
        for category_id, category_name in self.SUPPRESSION_CATEGORIES.items():
            count = category_counts.get(category_id, 0)
            percentage = (count / total_asins * 100.0) if total_asins > 0 else 0.0
            
            result_data.append({
                'suppression_category_id': category_id,
                'suppression_category_name': category_name,
                'asin_count': count,
                'percentage': percentage
            })
        
        result = pd.DataFrame(result_data)
        
        return result
    
    def aggregate_by_cid_pf(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate suppression data by CID and Product Family (PF).
        
        Calculate suppression percentages separately for each CID×PF combination.
        
        Args:
            df: DataFrame containing ASIN data with CID, PF, and suppression_category_large columns
            
        Returns:
            DataFrame with CID, PF, and suppression percentages for each category
            
        Raises:
            KeyError: If required columns are missing
        """
        required_cols = ['CID', 'PF', 'ASIN', 'suppression_category_large']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise KeyError(f"Missing required columns: {', '.join(missing)}")
        
        # Handle empty DataFrame
        if len(df) == 0:
            # Return empty DataFrame with proper column structure
            columns = ['CID', 'PF', 'total_asins']
            for category_name in self.SUPPRESSION_CATEGORIES.values():
                columns.append(f'{category_name}_count')
                columns.append(f'{category_name}_pct')
            return pd.DataFrame(columns=columns)
        
        # Group by CID and PF
        grouped = df.groupby(['CID', 'PF'])
        
        result_data = []
        
        for (cid, pf), group in grouped:
            # Count ASINs in each suppression category for this CID×PF
            category_counts = group['suppression_category_large'].value_counts()
            total_asins = len(group)
            
            # Build row with CID, PF, and percentages for each category
            row = {
                'CID': cid,
                'PF': pf,
                'total_asins': total_asins
            }
            
            for category_id, category_name in self.SUPPRESSION_CATEGORIES.items():
                count = category_counts.get(category_id, 0)
                percentage = (count / total_asins * 100.0) if total_asins > 0 else 0.0
                
                # Add both count and percentage columns
                row[f'{category_name}_count'] = count
                row[f'{category_name}_pct'] = percentage
            
            result_data.append(row)
        
        result = pd.DataFrame(result_data)
        
        return result
