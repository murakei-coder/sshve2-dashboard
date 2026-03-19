"""
Unit tests for the HierarchyProcessor class.

Tests cover hierarchy map building, aggregation at different levels,
and handling of unmapped CIDs.
"""

import pytest
import pandas as pd
from src.bridge_plan_generator.hierarchy_processor import HierarchyProcessor
from src.bridge_models import HierarchyMap


class TestHierarchyProcessor:
    """Test suite for HierarchyProcessor class."""
    
    @pytest.fixture
    def processor(self):
        """Create a HierarchyProcessor instance."""
        return HierarchyProcessor()
    
    @pytest.fixture
    def sample_hierarchy_df(self):
        """Create a sample hierarchy DataFrame."""
        return pd.DataFrame({
            'CID': ['C001', 'C002', 'C003', 'C004', 'C005'],
            'Alias': ['alice', 'alice', 'bob', 'bob', 'charlie'],
            'Mgr': ['mgr1', 'mgr1', 'mgr1', 'mgr1', 'mgr2'],
            'Team': ['team_a', 'team_a', 'team_a', 'team_a', 'team_b']
        })
    
    @pytest.fixture
    def sample_data_df(self):
        """Create a sample data DataFrame with metrics."""
        return pd.DataFrame({
            'CID': ['C001', 'C002', 'C003', 'C004', 'C005', 'C999'],
            'sales': [100.0, 200.0, 150.0, 250.0, 300.0, 500.0],
            'units': [10, 20, 15, 25, 30, 50]
        })
    
    def test_build_hierarchy_map_success(self, processor, sample_hierarchy_df):
        """Test successful hierarchy map building."""
        hierarchy = processor.build_hierarchy_map(sample_hierarchy_df)
        
        assert isinstance(hierarchy, HierarchyMap)
        assert hierarchy.cid_to_alias == {
            'C001': 'alice',
            'C002': 'alice',
            'C003': 'bob',
            'C004': 'bob',
            'C005': 'charlie'
        }
        assert hierarchy.alias_to_manager == {
            'alice': 'mgr1',
            'bob': 'mgr1',
            'charlie': 'mgr2'
        }
        assert hierarchy.manager_to_team == {
            'mgr1': 'team_a',
            'mgr2': 'team_b'
        }
    
    def test_build_hierarchy_map_missing_columns(self, processor):
        """Test error handling when required columns are missing."""
        df = pd.DataFrame({
            'CID': ['C001'],
            'Alias': ['alice']
            # Missing Mgr and Team columns
        })
        
        with pytest.raises(KeyError) as exc_info:
            processor.build_hierarchy_map(df)
        
        assert "Missing required columns" in str(exc_info.value)
        assert "Mgr" in str(exc_info.value)
        assert "Team" in str(exc_info.value)
    
    def test_build_hierarchy_map_with_whitespace(self, processor):
        """Test that whitespace is properly stripped from values."""
        df = pd.DataFrame({
            'CID': [' C001 ', 'C002'],
            'Alias': ['alice ', ' bob'],
            'Mgr': [' mgr1', 'mgr1 '],
            'Team': ['team_a ', ' team_a']
        })
        
        hierarchy = processor.build_hierarchy_map(df)
        
        assert hierarchy.cid_to_alias == {'C001': 'alice', 'C002': 'bob'}
        assert hierarchy.alias_to_manager == {'alice': 'mgr1', 'bob': 'mgr1'}
        assert hierarchy.manager_to_team == {'mgr1': 'team_a'}
    
    def test_aggregate_by_alias_success(self, processor, sample_data_df, sample_hierarchy_df):
        """Test successful aggregation by Alias."""
        hierarchy = processor.build_hierarchy_map(sample_hierarchy_df)
        result = processor.aggregate_by_alias(sample_data_df, hierarchy)
        
        # Check structure
        assert 'Alias' in result.columns
        assert 'sales' in result.columns
        assert 'units' in result.columns
        
        # Check aggregation correctness
        alice_row = result[result['Alias'] == 'alice'].iloc[0]
        assert alice_row['sales'] == 300.0  # 100 + 200
        assert alice_row['units'] == 30  # 10 + 20
        
        bob_row = result[result['Alias'] == 'bob'].iloc[0]
        assert bob_row['sales'] == 400.0  # 150 + 250
        assert bob_row['units'] == 40  # 15 + 25
        
        charlie_row = result[result['Alias'] == 'charlie'].iloc[0]
        assert charlie_row['sales'] == 300.0
        assert charlie_row['units'] == 30
        
        # C999 should be excluded (unmapped)
        assert len(result) == 3
    
    def test_aggregate_by_alias_unmapped_cids_excluded(self, processor, sample_hierarchy_df):
        """Test that unmapped CIDs are excluded from aggregation."""
        hierarchy = processor.build_hierarchy_map(sample_hierarchy_df)
        
        # Data with only unmapped CIDs
        data = pd.DataFrame({
            'CID': ['C999', 'C888'],
            'sales': [100.0, 200.0]
        })
        
        result = processor.aggregate_by_alias(data, hierarchy)
        
        # Should return empty DataFrame with expected columns
        assert len(result) == 0
        assert 'Alias' in result.columns
    
    def test_aggregate_by_alias_missing_cid_column(self, processor, sample_hierarchy_df):
        """Test error handling when CID column is missing."""
        hierarchy = processor.build_hierarchy_map(sample_hierarchy_df)
        
        data = pd.DataFrame({
            'sales': [100.0, 200.0]
        })
        
        with pytest.raises(KeyError) as exc_info:
            processor.aggregate_by_alias(data, hierarchy)
        
        assert "Missing required column: CID" in str(exc_info.value)
    
    def test_aggregate_by_manager_success(self, processor, sample_data_df, sample_hierarchy_df):
        """Test successful aggregation by Manager."""
        hierarchy = processor.build_hierarchy_map(sample_hierarchy_df)
        result = processor.aggregate_by_manager(sample_data_df, hierarchy)
        
        # Check structure
        assert 'Mgr' in result.columns
        assert 'sales' in result.columns
        assert 'units' in result.columns
        
        # Check aggregation correctness
        mgr1_row = result[result['Mgr'] == 'mgr1'].iloc[0]
        assert mgr1_row['sales'] == 700.0  # 100 + 200 + 150 + 250
        assert mgr1_row['units'] == 70  # 10 + 20 + 15 + 25
        
        mgr2_row = result[result['Mgr'] == 'mgr2'].iloc[0]
        assert mgr2_row['sales'] == 300.0
        assert mgr2_row['units'] == 30
        
        # C999 should be excluded (unmapped)
        assert len(result) == 2
    
    def test_aggregate_by_manager_unmapped_cids_excluded(self, processor, sample_hierarchy_df):
        """Test that unmapped CIDs are excluded from manager aggregation."""
        hierarchy = processor.build_hierarchy_map(sample_hierarchy_df)
        
        # Data with only unmapped CIDs
        data = pd.DataFrame({
            'CID': ['C999', 'C888'],
            'sales': [100.0, 200.0]
        })
        
        result = processor.aggregate_by_manager(data, hierarchy)
        
        # Should return empty DataFrame with expected columns
        assert len(result) == 0
        assert 'Mgr' in result.columns
    
    def test_aggregate_by_team_success(self, processor, sample_data_df, sample_hierarchy_df):
        """Test successful aggregation by Team."""
        hierarchy = processor.build_hierarchy_map(sample_hierarchy_df)
        result = processor.aggregate_by_team(sample_data_df, hierarchy)
        
        # Check structure
        assert 'Team' in result.columns
        assert 'sales' in result.columns
        assert 'units' in result.columns
        
        # Check aggregation correctness
        team_a_row = result[result['Team'] == 'team_a'].iloc[0]
        assert team_a_row['sales'] == 700.0  # 100 + 200 + 150 + 250
        assert team_a_row['units'] == 70  # 10 + 20 + 15 + 25
        
        team_b_row = result[result['Team'] == 'team_b'].iloc[0]
        assert team_b_row['sales'] == 300.0
        assert team_b_row['units'] == 30
        
        # C999 should be excluded (unmapped)
        assert len(result) == 2
    
    def test_aggregate_by_team_unmapped_cids_excluded(self, processor, sample_hierarchy_df):
        """Test that unmapped CIDs are excluded from team aggregation."""
        hierarchy = processor.build_hierarchy_map(sample_hierarchy_df)
        
        # Data with only unmapped CIDs
        data = pd.DataFrame({
            'CID': ['C999', 'C888'],
            'sales': [100.0, 200.0]
        })
        
        result = processor.aggregate_by_team(data, hierarchy)
        
        # Should return empty DataFrame with expected columns
        assert len(result) == 0
        assert 'Team' in result.columns
    
    def test_multi_level_aggregation_consistency(self, processor, sample_data_df, sample_hierarchy_df):
        """Test that aggregation is consistent across multiple levels."""
        hierarchy = processor.build_hierarchy_map(sample_hierarchy_df)
        
        # Aggregate at each level
        alias_result = processor.aggregate_by_alias(sample_data_df, hierarchy)
        mgr_result = processor.aggregate_by_manager(sample_data_df, hierarchy)
        team_result = processor.aggregate_by_team(sample_data_df, hierarchy)
        
        # Sum of all aliases should equal sum of all managers
        assert alias_result['sales'].sum() == mgr_result['sales'].sum()
        assert alias_result['units'].sum() == mgr_result['units'].sum()
        
        # Sum of all managers should equal sum of all teams
        assert mgr_result['sales'].sum() == team_result['sales'].sum()
        assert mgr_result['units'].sum() == team_result['units'].sum()
        
        # Total should be 1000 (excluding unmapped C999 with 500)
        assert team_result['sales'].sum() == 1000.0
        assert team_result['units'].sum() == 100
    
    def test_aggregate_with_empty_dataframe(self, processor, sample_hierarchy_df):
        """Test aggregation with empty input DataFrame."""
        hierarchy = processor.build_hierarchy_map(sample_hierarchy_df)
        
        empty_df = pd.DataFrame(columns=['CID', 'sales', 'units'])
        
        result = processor.aggregate_by_alias(empty_df, hierarchy)
        assert len(result) == 0
        assert 'Alias' in result.columns
        
        result = processor.aggregate_by_manager(empty_df, hierarchy)
        assert len(result) == 0
        assert 'Mgr' in result.columns
        
        result = processor.aggregate_by_team(empty_df, hierarchy)
        assert len(result) == 0
        assert 'Team' in result.columns
    
    def test_aggregate_with_single_cid(self, processor):
        """Test aggregation with a single CID."""
        hierarchy_df = pd.DataFrame({
            'CID': ['C001'],
            'Alias': ['alice'],
            'Mgr': ['mgr1'],
            'Team': ['team_a']
        })
        
        data_df = pd.DataFrame({
            'CID': ['C001'],
            'sales': [100.0],
            'units': [10]
        })
        
        hierarchy = processor.build_hierarchy_map(hierarchy_df)
        
        alias_result = processor.aggregate_by_alias(data_df, hierarchy)
        assert len(alias_result) == 1
        assert alias_result.iloc[0]['sales'] == 100.0
        
        mgr_result = processor.aggregate_by_manager(data_df, hierarchy)
        assert len(mgr_result) == 1
        assert mgr_result.iloc[0]['sales'] == 100.0
        
        team_result = processor.aggregate_by_team(data_df, hierarchy)
        assert len(team_result) == 1
        assert team_result.iloc[0]['sales'] == 100.0
    
    def test_aggregate_with_multiple_metrics(self, processor, sample_hierarchy_df):
        """Test aggregation with multiple numeric columns."""
        hierarchy = processor.build_hierarchy_map(sample_hierarchy_df)
        
        data = pd.DataFrame({
            'CID': ['C001', 'C002'],
            'metric1': [100.0, 200.0],
            'metric2': [50.0, 75.0],
            'metric3': [10, 20],
            'text_col': ['a', 'b']  # Non-numeric column
        })
        
        result = processor.aggregate_by_alias(data, hierarchy)
        
        # All numeric columns should be aggregated
        assert 'metric1' in result.columns
        assert 'metric2' in result.columns
        assert 'metric3' in result.columns
        
        # Text column should not be in result
        assert 'text_col' not in result.columns
        
        # Check aggregation
        alice_row = result[result['Alias'] == 'alice'].iloc[0]
        assert alice_row['metric1'] == 300.0
        assert alice_row['metric2'] == 125.0
        assert alice_row['metric3'] == 30
