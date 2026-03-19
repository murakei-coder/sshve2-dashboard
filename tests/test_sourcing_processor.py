"""
Unit tests for the SourcingProcessor class.

Tests cover extraction of T30 GMS BAU, event flags, participation score calculation,
and aggregation by CID with various edge cases.
"""

import pytest
import pandas as pd
import numpy as np
from src.bridge_plan_generator.sourcing_processor import SourcingProcessor


class TestSourcingProcessor:
    """Test suite for SourcingProcessor class."""
    
    @pytest.fixture
    def processor(self):
        """Create a SourcingProcessor instance for testing."""
        return SourcingProcessor()
    
    @pytest.fixture
    def sample_sourcing_data(self):
        """Create sample sourcing data for testing."""
        return pd.DataFrame({
            'ASIN': ['A001', 'A002', 'A003', 'A004'],
            'CID': ['C001', 'C001', 'C002', 'C002'],
            'total_t30d_gms_BAU': [1000.0, 2000.0, 1500.0, 2500.0],
            'sshve1_flag': ['Y', 'N', 'Y', 'Y'],
            'fy26_mde2_flag': ['Y', 'Y', 'N', 'Y'],
            'nys26_flag': ['N', 'Y', 'Y', 'N'],
            'bf25_flag': ['N', 'N', 'Y', 'Y'],
            'fy25_mde4_flag': ['Y', 'N', 'N', 'N'],
            't365_flag': ['Y', 'Y', 'Y', 'N']
        })
    
    # Tests for extract_t30_gms_bau
    
    def test_extract_t30_gms_bau_basic(self, processor, sample_sourcing_data):
        """Test basic extraction of T30 GMS BAU values."""
        result = processor.extract_t30_gms_bau(sample_sourcing_data)
        
        assert 'ASIN' in result.columns
        assert 'CID' in result.columns
        assert 't30_gms_bau' in result.columns
        assert len(result) == 4
        assert result['t30_gms_bau'].tolist() == [1000.0, 2000.0, 1500.0, 2500.0]
    
    def test_extract_t30_gms_bau_missing_column(self, processor):
        """Test error handling when required columns are missing."""
        df = pd.DataFrame({
            'ASIN': ['A001'],
            'CID': ['C001']
            # Missing total_t30d_gms_BAU
        })
        
        with pytest.raises(KeyError) as exc_info:
            processor.extract_t30_gms_bau(df)
        assert 'total_t30d_gms_BAU' in str(exc_info.value)
    
    def test_extract_t30_gms_bau_numeric_coercion(self, processor):
        """Test that non-numeric values are coerced to NaN."""
        df = pd.DataFrame({
            'ASIN': ['A001', 'A002'],
            'CID': ['C001', 'C002'],
            'total_t30d_gms_BAU': ['1000.0', 'invalid']
        })
        
        result = processor.extract_t30_gms_bau(df)
        assert result['t30_gms_bau'].iloc[0] == 1000.0
        assert pd.isna(result['t30_gms_bau'].iloc[1])
    
    # Tests for extract_event_flags
    
    def test_extract_event_flags_basic(self, processor, sample_sourcing_data):
        """Test basic extraction of event participation flags."""
        result = processor.extract_event_flags(sample_sourcing_data)
        
        assert 'ASIN' in result.columns
        assert all(flag in result.columns for flag in processor.EVENT_FLAG_WEIGHTS.keys())
        assert len(result) == 4
        assert result.loc[result['ASIN'] == 'A001', 'sshve1_flag'].iloc[0] == 'Y'
        assert result.loc[result['ASIN'] == 'A002', 'sshve1_flag'].iloc[0] == 'N'
    
    def test_extract_event_flags_missing_column(self, processor):
        """Test error handling when event flag columns are missing."""
        df = pd.DataFrame({
            'ASIN': ['A001'],
            'sshve1_flag': ['Y']
            # Missing other flags
        })
        
        with pytest.raises(KeyError) as exc_info:
            processor.extract_event_flags(df)
        assert 'fy26_mde2_flag' in str(exc_info.value)
    
    # Tests for calculate_participation_score
    
    def test_calculate_participation_score_all_yes(self, processor):
        """Test participation score when all flags are Y."""
        flags = {
            'sshve1_flag': 'Y',
            'fy26_mde2_flag': 'Y',
            'nys26_flag': 'Y',
            'bf25_flag': 'Y',
            'fy25_mde4_flag': 'Y',
            't365_flag': 'Y'
        }
        
        score = processor.calculate_participation_score(flags)
        assert score == 1.0
    
    def test_calculate_participation_score_all_no(self, processor):
        """Test participation score when all flags are N."""
        flags = {
            'sshve1_flag': 'N',
            'fy26_mde2_flag': 'N',
            'nys26_flag': 'N',
            'bf25_flag': 'N',
            'fy25_mde4_flag': 'N',
            't365_flag': 'N'
        }
        
        score = processor.calculate_participation_score(flags)
        assert score == 0.0
    
    def test_calculate_participation_score_most_recent_only(self, processor):
        """Test participation score with only most recent flag set."""
        flags = {
            'sshve1_flag': 'Y',
            'fy26_mde2_flag': 'N',
            'nys26_flag': 'N',
            'bf25_flag': 'N',
            'fy25_mde4_flag': 'N',
            't365_flag': 'N'
        }
        
        score = processor.calculate_participation_score(flags)
        total_weight = sum(processor.EVENT_FLAG_WEIGHTS.values())
        expected = 1.0 / total_weight
        assert abs(score - expected) < 0.0001
    
    def test_calculate_participation_score_least_recent_only(self, processor):
        """Test participation score with only least recent flag set."""
        flags = {
            'sshve1_flag': 'N',
            'fy26_mde2_flag': 'N',
            'nys26_flag': 'N',
            'bf25_flag': 'N',
            'fy25_mde4_flag': 'N',
            't365_flag': 'Y'
        }
        
        score = processor.calculate_participation_score(flags)
        total_weight = sum(processor.EVENT_FLAG_WEIGHTS.values())
        expected = 0.1 / total_weight
        assert abs(score - expected) < 0.0001
    
    def test_calculate_participation_score_mixed(self, processor):
        """Test participation score with mixed flags."""
        flags = {
            'sshve1_flag': 'Y',  # 1.0
            'fy26_mde2_flag': 'Y',  # 0.8
            'nys26_flag': 'N',
            'bf25_flag': 'N',
            'fy25_mde4_flag': 'Y',  # 0.2
            't365_flag': 'N'
        }
        
        score = processor.calculate_participation_score(flags)
        total_weight = sum(processor.EVENT_FLAG_WEIGHTS.values())
        expected = (1.0 + 0.8 + 0.2) / total_weight
        assert abs(score - expected) < 0.0001
    
    def test_calculate_participation_score_missing_flags(self, processor):
        """Test participation score with missing flag entries."""
        flags = {
            'sshve1_flag': 'Y',
            'fy26_mde2_flag': 'Y'
            # Other flags missing
        }
        
        score = processor.calculate_participation_score(flags)
        total_weight = sum(processor.EVENT_FLAG_WEIGHTS.values())
        expected = (1.0 + 0.8) / total_weight
        assert abs(score - expected) < 0.0001
    
    def test_calculate_participation_score_recency_weighting(self, processor):
        """Test that more recent flags have higher impact on score."""
        recent_flags = {
            'sshve1_flag': 'Y',
            'fy26_mde2_flag': 'N',
            'nys26_flag': 'N',
            'bf25_flag': 'N',
            'fy25_mde4_flag': 'N',
            't365_flag': 'N'
        }
        
        old_flags = {
            'sshve1_flag': 'N',
            'fy26_mde2_flag': 'N',
            'nys26_flag': 'N',
            'bf25_flag': 'N',
            'fy25_mde4_flag': 'N',
            't365_flag': 'Y'
        }
        
        recent_score = processor.calculate_participation_score(recent_flags)
        old_score = processor.calculate_participation_score(old_flags)
        
        assert recent_score > old_score
    
    # Tests for aggregate_by_cid
    
    def test_aggregate_by_cid_basic(self, processor):
        """Test basic aggregation of T30 GMS BAU by CID."""
        df = pd.DataFrame({
            'CID': ['C001', 'C001', 'C002', 'C002'],
            't30_gms_bau': [1000.0, 2000.0, 1500.0, 2500.0]
        })
        
        result = processor.aggregate_by_cid(df)
        
        assert 'CID' in result.columns
        assert 't30_gms_bau_total' in result.columns
        assert len(result) == 2
        
        c001_total = result.loc[result['CID'] == 'C001', 't30_gms_bau_total'].iloc[0]
        c002_total = result.loc[result['CID'] == 'C002', 't30_gms_bau_total'].iloc[0]
        
        assert c001_total == 3000.0
        assert c002_total == 4000.0
    
    def test_aggregate_by_cid_single_asin_per_cid(self, processor):
        """Test aggregation when each CID has only one ASIN."""
        df = pd.DataFrame({
            'CID': ['C001', 'C002', 'C003'],
            't30_gms_bau': [1000.0, 2000.0, 3000.0]
        })
        
        result = processor.aggregate_by_cid(df)
        
        assert len(result) == 3
        assert result['t30_gms_bau_total'].tolist() == [1000.0, 2000.0, 3000.0]
    
    def test_aggregate_by_cid_with_nan_values(self, processor):
        """Test aggregation with NaN values."""
        df = pd.DataFrame({
            'CID': ['C001', 'C001', 'C002'],
            't30_gms_bau': [1000.0, np.nan, 2000.0]
        })
        
        result = processor.aggregate_by_cid(df)
        
        # pandas sum() ignores NaN by default
        c001_total = result.loc[result['CID'] == 'C001', 't30_gms_bau_total'].iloc[0]
        assert c001_total == 1000.0
    
    def test_aggregate_by_cid_missing_column(self, processor):
        """Test error handling when required columns are missing."""
        df = pd.DataFrame({
            'CID': ['C001', 'C002']
            # Missing t30_gms_bau
        })
        
        with pytest.raises(KeyError) as exc_info:
            processor.aggregate_by_cid(df)
        assert 't30_gms_bau' in str(exc_info.value)
    
    def test_aggregate_by_cid_empty_dataframe(self, processor):
        """Test aggregation with empty DataFrame."""
        df = pd.DataFrame({
            'CID': [],
            't30_gms_bau': []
        })
        
        result = processor.aggregate_by_cid(df)
        
        assert len(result) == 0
        assert 'CID' in result.columns
        assert 't30_gms_bau_total' in result.columns
    
    # Integration tests
    
    def test_full_workflow(self, processor, sample_sourcing_data):
        """Test complete workflow: extract → calculate scores → aggregate."""
        # Extract T30 GMS BAU
        t30_data = processor.extract_t30_gms_bau(sample_sourcing_data)
        
        # Extract event flags
        flags_data = processor.extract_event_flags(sample_sourcing_data)
        
        # Calculate participation scores for each ASIN
        scores = []
        for _, row in flags_data.iterrows():
            flags = {col: row[col] for col in processor.EVENT_FLAG_WEIGHTS.keys()}
            score = processor.calculate_participation_score(flags)
            scores.append(score)
        
        # Aggregate by CID
        aggregated = processor.aggregate_by_cid(t30_data)
        
        assert len(aggregated) == 2
        assert 'C001' in aggregated['CID'].values
        assert 'C002' in aggregated['CID'].values
