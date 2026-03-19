"""
Hierarchy mapping and aggregation processor module for the Bridge Plan Generator.

This module handles processing of organizational hierarchy data including CID to Alias,
Alias to Manager, and Manager to Team mappings, and provides aggregation functionality
at different organizational levels.
"""

import pandas as pd
from typing import Dict
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_path = Path(__file__).parent.parent
if str(parent_path) not in sys.path:
    sys.path.insert(0, str(parent_path))

import bridge_models


class HierarchyProcessor:
    """Processes organizational hierarchy data and performs multi-level aggregations."""
    
    def build_hierarchy_map(self, df: pd.DataFrame) -> 'bridge_models.HierarchyMap':
        """
        Create CID→Alias→Mgr→Team mappings from the hierarchy data.
        
        Args:
            df: DataFrame containing CID, Alias, Mgr, and Team columns
            
        Returns:
            HierarchyMap object with the three mapping dictionaries
            
        Raises:
            KeyError: If required columns are missing
        """
        required_cols = ['CID', 'Alias', 'Mgr', 'Team']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise KeyError(f"Missing required columns: {', '.join(missing)}")
        
        # Build CID to Alias mapping
        cid_to_alias = {}
        for _, row in df.iterrows():
            cid = str(row['CID']).strip()
            alias = str(row['Alias']).strip()
            if cid and alias:
                cid_to_alias[cid] = alias
        
        # Build Alias to Manager mapping
        alias_to_manager = {}
        for _, row in df.iterrows():
            alias = str(row['Alias']).strip()
            manager = str(row['Mgr']).strip()
            if alias and manager:
                alias_to_manager[alias] = manager
        
        # Build Manager to Team mapping
        manager_to_team = {}
        for _, row in df.iterrows():
            manager = str(row['Mgr']).strip()
            team = str(row['Team']).strip()
            if manager and team:
                manager_to_team[manager] = team
        
        return bridge_models.HierarchyMap(
            cid_to_alias=cid_to_alias,
            alias_to_manager=alias_to_manager,
            manager_to_team=manager_to_team
        )
    
    def aggregate_by_alias(self, data: pd.DataFrame, hierarchy: 'bridge_models.HierarchyMap') -> pd.DataFrame:
        """
        Sum all metrics for CIDs assigned to each Alias.
        
        Unmapped CIDs (not in hierarchy) are excluded from aggregation.
        
        Args:
            data: DataFrame with CID column and numeric metric columns to aggregate
            hierarchy: HierarchyMap containing CID to Alias mappings
            
        Returns:
            DataFrame with Alias and aggregated metric columns
            
        Raises:
            KeyError: If CID column is missing
        """
        if 'CID' not in data.columns:
            raise KeyError("Missing required column: CID")
        
        # Add Alias column based on hierarchy mapping
        data_with_alias = data.copy()
        data_with_alias['Alias'] = data_with_alias['CID'].astype(str).map(hierarchy.cid_to_alias)
        
        # Filter out unmapped CIDs (where Alias is NaN)
        mapped_data = data_with_alias[data_with_alias['Alias'].notna()].copy()
        
        if mapped_data.empty:
            # Return empty DataFrame with expected structure
            return pd.DataFrame(columns=['Alias'])
        
        # Identify numeric columns to aggregate
        numeric_cols = mapped_data.select_dtypes(include=['number']).columns.tolist()
        
        # Group by Alias and sum numeric columns
        result = mapped_data.groupby('Alias', as_index=False)[numeric_cols].sum()
        
        return result
    
    def aggregate_by_manager(self, data: pd.DataFrame, hierarchy: 'bridge_models.HierarchyMap') -> pd.DataFrame:
        """
        Sum all metrics for Aliases assigned to each Manager.
        
        Unmapped CIDs (not in hierarchy) are excluded from aggregation.
        
        Args:
            data: DataFrame with CID column and numeric metric columns to aggregate
            hierarchy: HierarchyMap containing CID to Alias and Alias to Manager mappings
            
        Returns:
            DataFrame with Mgr and aggregated metric columns
            
        Raises:
            KeyError: If CID column is missing
        """
        if 'CID' not in data.columns:
            raise KeyError("Missing required column: CID")
        
        # Add Alias and Manager columns based on hierarchy mapping
        data_with_hierarchy = data.copy()
        data_with_hierarchy['Alias'] = data_with_hierarchy['CID'].astype(str).map(hierarchy.cid_to_alias)
        data_with_hierarchy['Mgr'] = data_with_hierarchy['Alias'].map(hierarchy.alias_to_manager)
        
        # Filter out unmapped CIDs (where Mgr is NaN)
        mapped_data = data_with_hierarchy[data_with_hierarchy['Mgr'].notna()].copy()
        
        if mapped_data.empty:
            # Return empty DataFrame with expected structure
            return pd.DataFrame(columns=['Mgr'])
        
        # Identify numeric columns to aggregate
        numeric_cols = mapped_data.select_dtypes(include=['number']).columns.tolist()
        
        # Group by Mgr and sum numeric columns
        result = mapped_data.groupby('Mgr', as_index=False)[numeric_cols].sum()
        
        return result
    
    def aggregate_by_team(self, data: pd.DataFrame, hierarchy: 'bridge_models.HierarchyMap') -> pd.DataFrame:
        """
        Sum all metrics for all members of each Team.
        
        Unmapped CIDs (not in hierarchy) are excluded from aggregation.
        
        Args:
            data: DataFrame with CID column and numeric metric columns to aggregate
            hierarchy: HierarchyMap containing full hierarchy mappings
            
        Returns:
            DataFrame with Team and aggregated metric columns
            
        Raises:
            KeyError: If CID column is missing
        """
        if 'CID' not in data.columns:
            raise KeyError("Missing required column: CID")
        
        # Add Alias, Manager, and Team columns based on hierarchy mapping
        data_with_hierarchy = data.copy()
        data_with_hierarchy['Alias'] = data_with_hierarchy['CID'].astype(str).map(hierarchy.cid_to_alias)
        data_with_hierarchy['Mgr'] = data_with_hierarchy['Alias'].map(hierarchy.alias_to_manager)
        data_with_hierarchy['Team'] = data_with_hierarchy['Mgr'].map(hierarchy.manager_to_team)
        
        # Filter out unmapped CIDs (where Team is NaN)
        mapped_data = data_with_hierarchy[data_with_hierarchy['Team'].notna()].copy()
        
        if mapped_data.empty:
            # Return empty DataFrame with expected structure
            return pd.DataFrame(columns=['Team'])
        
        # Identify numeric columns to aggregate
        numeric_cols = mapped_data.select_dtypes(include=['number']).columns.tolist()
        
        # Group by Team and sum numeric columns
        result = mapped_data.groupby('Team', as_index=False)[numeric_cols].sum()
        
        return result
