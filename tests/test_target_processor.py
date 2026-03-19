"""
Unit tests for the TargetProcessor class.

Tests cover extraction of T30 GMS targets, gap calculation (including negative gaps),
and identification of missing CIDs for data consistency checks.
"""

import pytest
import pandas as pd
import numpy as np
from src.bridge_plan_generator.target_processor import TargetProcessor


class TestTargetProcessor:
    """Test suite for TargetProcessor class."""
    
    @pytest.fixture
    def processor(self):
        """Create a TargetProcessor instance for testing."""
        return TargetProcessor()
    
    @pytest.fixture
    def sample_target_data(self):
        """Create sample target data for testing."""
        return pd.DataFrame({
            'CID': ['C001', 'C002', 'C003', 'C004'],
            'T30_GMS_Target': [5000.0, 8000.0, 3000.0, 10000.0]
        })
    
    @pytest.fixture
    def sample_current_data(self):
        """Create sample current performance data for testing."""
        return pd.DataFrame({
            'CID': ['C001', 'C002', 'C003', 'C005'],
            't30_gms_bau_total': [3000.0, 9000.0, 2000.0, 4000.0]
        })
    
    # Tests for extract_targets
    
    def test_extract_targets_basic(self, processor, sample_target_data):
        """Test basic extraction of T30 GMS Target values."""
        result = processor.extract_targets(sample_target_data)
        
        assert 'CID' in result.columns
        assert 't30_gms_target' in result.columns
        assert len(result) == 4
        assert result['t30_gms_target'].tolist() == [5000.0, 8000.0, 3000.0, 10000.0]
    
    def test_extract_targets_missing_column(self, processor):
        """Test error handling when required columns are missing."""
        df = pd.DataFrame({
            'CID': ['C001']
            # Missing T30_GMS_Target
        })
        
        with pytest.raises(KeyError) as exc_info:
            processor.extract_targets(df)
        assert 'T30_GMS_Target' in str(exc_info.value)
    
    def test_extract_targets_numeric_coercion(self, processor):
        """Test that non-numeric values are coerced to NaN."""
        df = pd.DataFrame({
            'CID': ['C001', 'C002'],
            'T30_GMS_Target': ['5000.0', 'invalid']
        })
        
        result = processor.extract_targets(df)
        assert result['t30_gms_target'].iloc[0] == 5000.0
        assert pd.isna(result['t30_gms_target'].iloc[1])
    
    def test_extract_targets_empty_dataframe(self, processor):
        """Test extraction with empty DataFrame."""
        df = pd.DataFrame({
            'CID': [],
            'T30_GMS_Target': []
        })
        
        result = processor.extract_targets(df)
        assert len(result) == 0
        assert 'CID' in result.columns
        assert 't30_gms_target' in result.columns
    
    # Tests for calculate_gaps
    
    def test_calculate_gaps_basic(self, processor, sample_current_data, sample_target_data):
        """Test basic gap calculation."""
        targets = processor.extract_targets(sample_target_data)
        result = processor.calculate_gaps(sample_current_data, targets)
        
        assert 'CID' in result.columns
        assert 't30_gms_bau_total' in result.columns
        assert 't30_gms_target' in result.columns
        assert 'gap' in result.columns
        
        # Check specific gap calculations
        c001_row = result[result['CID'] == 'C001'].iloc[0]
        assert c001_row['gap'] == 2000.0  # 5000 - 3000
        
        c002_row = result[result['CID'] == 'C002'].iloc[0]
        assert c002_row['gap'] == -1000.0  # 8000 - 9000 (negative gap, target achieved)
        
        c003_row = result[result['CID'] == 'C003'].iloc[0]
        assert c003_row['gap'] == 1000.0  # 3000 - 2000
    
    def test_calculate_gaps_negative_gap(self, processor):
        """Test gap calculation when target is already achieved (negative gap)."""
        current = pd.DataFrame({
            'CID': ['C001'],
            't30_gms_bau_total': [10000.0]
        })
        targets = pd.DataFrame({
            'CID': ['C001'],
            't30_gms_target': [8000.0]
        })
        
        result = processor.calculate_gaps(current, targets)
        
        assert result['gap'].iloc[0] == -2000.0
        assert result['gap'].iloc[0] < 0  # Verify it's negative
    
    def test_calculate_gaps_zero_gap(self, processor):
        """Test gap calculation when current equals target."""
        current = pd.DataFrame({
            'CID': ['C001'],
            't30_gms_bau_total': [5000.0]
        })
        targets = pd.DataFrame({
            'CID': ['C001'],
            't30_gms_target': [5000.0]
        })
        
        result = processor.calculate_gaps(current, targets)
        
        assert result['gap'].iloc[0] == 0.0
    
    def test_calculate_gaps_zero_target(self, processor):
        """Test gap calculation with zero target."""
        current = pd.DataFrame({
            'CID': ['C001'],
            't30_gms_bau_total': [1000.0]
        })
        targets = pd.DataFrame({
            'CID': ['C001'],
            't30_gms_target': [0.0]
        })
        
        result = processor.calculate_gaps(current, targets)
        
        assert result['gap'].iloc[0] == -1000.0
    
    def test_calculate_gaps_zero_current(self, processor):
        """Test gap calculation with zero current performance."""
        current = pd.DataFrame({
            'CID': ['C001'],
            't30_gms_bau_total': [0.0]
        })
        targets = pd.DataFrame({
            'CID': ['C001'],
            't30_gms_target': [5000.0]
        })
        
        result = processor.calculate_gaps(current, targets)
        
        assert result['gap'].iloc[0] == 5000.0
    
    def test_calculate_gaps_missing_in_targets(self, processor):
        """Test gap calculation when CID exists in current but not in targets."""
        current = pd.DataFrame({
            'CID': ['C001', 'C002'],
            't30_gms_bau_total': [3000.0, 4000.0]
        })
        targets = pd.DataFrame({
            'CID': ['C001'],
            't30_gms_target': [5000.0]
        })
        
        result = processor.calculate_gaps(current, targets)
        
        # C002 should be in result with NaN target and gap
        assert len(result) == 2
        c002_row = result[result['CID'] == 'C002'].iloc[0]
        assert pd.isna(c002_row['t30_gms_target'])
        assert pd.isna(c002_row['gap'])
    
    def test_calculate_gaps_missing_in_current(self, processor):
        """Test gap calculation when CID exists in targets but not in current."""
        current = pd.DataFrame({
            'CID': ['C001'],
            't30_gms_bau_total': [3000.0]
        })
        targets = pd.DataFrame({
            'CID': ['C001', 'C002'],
            't30_gms_target': [5000.0, 8000.0]
        })
        
        result = processor.calculate_gaps(current, targets)
        
        # C002 should be in result with NaN current and gap
        assert len(result) == 2
        c002_row = result[result['CID'] == 'C002'].iloc[0]
        assert pd.isna(c002_row['t30_gms_bau_total'])
        assert pd.isna(c002_row['gap'])
    
    def test_calculate_gaps_missing_column_current(self, processor):
        """Test error handling when current data is missing required columns."""
        current = pd.DataFrame({
            'CID': ['C001']
            # Missing t30_gms_bau_total
        })
        targets = pd.DataFrame({
            'CID': ['C001'],
            't30_gms_target': [5000.0]
        })
        
        with pytest.raises(KeyError) as exc_info:
            processor.calculate_gaps(current, targets)
        assert 't30_gms_bau_total' in str(exc_info.value)
    
    def test_calculate_gaps_missing_column_targets(self, processor):
        """Test error handling when targets data is missing required columns."""
        current = pd.DataFrame({
            'CID': ['C001'],
            't30_gms_bau_total': [3000.0]
        })
        targets = pd.DataFrame({
            'CID': ['C001']
            # Missing t30_gms_target
        })
        
        with pytest.raises(KeyError) as exc_info:
            processor.calculate_gaps(current, targets)
        assert 't30_gms_target' in str(exc_info.value)
    
    def test_calculate_gaps_empty_dataframes(self, processor):
        """Test gap calculation with empty DataFrames."""
        current = pd.DataFrame({
            'CID': [],
            't30_gms_bau_total': []
        })
        targets = pd.DataFrame({
            'CID': [],
            't30_gms_target': []
        })
        
        result = processor.calculate_gaps(current, targets)
        
        assert len(result) == 0
        assert 'CID' in result.columns
        assert 'gap' in result.columns
    
    def test_calculate_gaps_with_nan_values(self, processor):
        """Test gap calculation with NaN values in input data."""
        current = pd.DataFrame({
            'CID': ['C001', 'C002'],
            't30_gms_bau_total': [3000.0, np.nan]
        })
        targets = pd.DataFrame({
            'CID': ['C001', 'C002'],
            't30_gms_target': [5000.0, 8000.0]
        })
        
        result = processor.calculate_gaps(current, targets)
        
        # C001 should have valid gap
        c001_row = result[result['CID'] == 'C001'].iloc[0]
        assert c001_row['gap'] == 2000.0
        
        # C002 should have NaN gap due to NaN current
        c002_row = result[result['CID'] == 'C002'].iloc[0]
        assert pd.isna(c002_row['gap'])
    
    # Tests for identify_missing_targets
    
    def test_identify_missing_targets_basic(self, processor):
        """Test identification of CIDs missing from target data."""
        sourcing_cids = {'C001', 'C002', 'C003', 'C004'}
        target_cids = {'C001', 'C002'}
        
        missing = processor.identify_missing_targets(sourcing_cids, target_cids)
        
        assert len(missing) == 2
        assert 'C003' in missing
        assert 'C004' in missing
        assert missing == ['C003', 'C004']  # Should be sorted
    
    def test_identify_missing_targets_none_missing(self, processor):
        """Test when all sourcing CIDs have targets."""
        sourcing_cids = {'C001', 'C002', 'C003'}
        target_cids = {'C001', 'C002', 'C003', 'C004'}
        
        missing = processor.identify_missing_targets(sourcing_cids, target_cids)
        
        assert len(missing) == 0
        assert missing == []
    
    def test_identify_missing_targets_all_missing(self, processor):
        """Test when no sourcing CIDs have targets."""
        sourcing_cids = {'C001', 'C002', 'C003'}
        target_cids = {'C004', 'C005'}
        
        missing = processor.identify_missing_targets(sourcing_cids, target_cids)
        
        assert len(missing) == 3
        assert set(missing) == {'C001', 'C002', 'C003'}
    
    def test_identify_missing_targets_empty_sourcing(self, processor):
        """Test with empty sourcing CIDs."""
        sourcing_cids = set()
        target_cids = {'C001', 'C002'}
        
        missing = processor.identify_missing_targets(sourcing_cids, target_cids)
        
        assert len(missing) == 0
        assert missing == []
    
    def test_identify_missing_targets_empty_targets(self, processor):
        """Test with empty target CIDs."""
        sourcing_cids = {'C001', 'C002', 'C003'}
        target_cids = set()
        
        missing = processor.identify_missing_targets(sourcing_cids, target_cids)
        
        assert len(missing) == 3
        assert set(missing) == {'C001', 'C002', 'C003'}
    
    def test_identify_missing_targets_sorted_output(self, processor):
        """Test that output is sorted alphabetically."""
        sourcing_cids = {'C005', 'C001', 'C003', 'C002'}
        target_cids = {'C001'}
        
        missing = processor.identify_missing_targets(sourcing_cids, target_cids)
        
        assert missing == ['C002', 'C003', 'C005']
    
    # Integration tests
    
    def test_full_workflow(self, processor, sample_current_data, sample_target_data):
        """Test complete workflow: extract targets → calculate gaps → identify missing."""
        # Extract targets
        targets = processor.extract_targets(sample_target_data)
        
        # Calculate gaps
        gaps = processor.calculate_gaps(sample_current_data, targets)
        
        # Identify missing targets
        sourcing_cids = set(sample_current_data['CID'])
        target_cids = set(sample_target_data['CID'])
        missing = processor.identify_missing_targets(sourcing_cids, target_cids)
        
        # Verify results
        assert len(gaps) == 5  # 4 from targets + 1 from current only (C005)
        assert len(missing) == 1
        assert 'C005' in missing
    
    def test_workflow_with_negative_gaps(self, processor):
        """Test workflow including CIDs with negative gaps (target already achieved)."""
        current = pd.DataFrame({
            'CID': ['C001', 'C002', 'C003'],
            't30_gms_bau_total': [10000.0, 5000.0, 3000.0]
        })
        targets = pd.DataFrame({
            'CID': ['C001', 'C002', 'C003'],
            'T30_GMS_Target': [8000.0, 5000.0, 4000.0]
        })
        
        extracted_targets = processor.extract_targets(targets)
        gaps = processor.calculate_gaps(current, extracted_targets)
        
        # C001: negative gap (target achieved)
        c001_gap = gaps[gaps['CID'] == 'C001']['gap'].iloc[0]
        assert c001_gap == -2000.0
        
        # C002: zero gap (exactly at target)
        c002_gap = gaps[gaps['CID'] == 'C002']['gap'].iloc[0]
        assert c002_gap == 0.0
        
        # C003: positive gap (needs improvement)
        c003_gap = gaps[gaps['CID'] == 'C003']['gap'].iloc[0]
        assert c003_gap == 1000.0
