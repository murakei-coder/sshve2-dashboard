"""
Unit tests for the SuppressionProcessor class.

Tests cover extraction of benchmark percentages, validation of percentage sums,
calculation of current suppression status, and aggregation by CID×PF with various edge cases.
"""

import pytest
import pandas as pd
import numpy as np
from src.bridge_plan_generator.suppression_processor import SuppressionProcessor


class TestSuppressionProcessor:
    """Test suite for SuppressionProcessor class."""
    
    @pytest.fixture
    def processor(self):
        """Create a SuppressionProcessor instance for testing."""
        return SuppressionProcessor()
    
    @pytest.fixture
    def sample_benchmark_data(self):
        """Create sample benchmark suppression data for testing."""
        return pd.DataFrame({
            'event_name': ['BF25'],
            'no_suppression_pct': [45.0],
            'oos_pct': [25.0],
            'vrp_missing_pct': [10.0],
            'price_error_pct': [15.0],
            'others_pct': [5.0]
        })
    
    @pytest.fixture
    def sample_asin_data(self):
        """Create sample ASIN data with suppression categories for testing."""
        return pd.DataFrame({
            'ASIN': ['A001', 'A002', 'A003', 'A004', 'A005', 'A006', 'A007', 'A008'],
            'CID': ['C001', 'C001', 'C001', 'C001', 'C002', 'C002', 'C002', 'C002'],
            'PF': ['Electronics', 'Electronics', 'Home', 'Home', 'Electronics', 'Electronics', 'Home', 'Home'],
            'suppression_category_large': [1, 1, 2, 3, 1, 4, 5, 2]
        })
    
    # Tests for extract_benchmark_percentages
    
    def test_extract_benchmark_percentages_basic(self, processor, sample_benchmark_data):
        """Test basic extraction of benchmark percentages."""
        result = processor.extract_benchmark_percentages(sample_benchmark_data)
        
        assert isinstance(result, dict)
        assert len(result) == 5
        assert result["No suppression"] == 45.0
        assert result["OOS"] == 25.0
        assert result["VRP missing"] == 10.0
        assert result["Price Error"] == 15.0
        assert result["Others"] == 5.0
    
    def test_extract_benchmark_percentages_missing_column(self, processor):
        """Test error handling when required columns are missing."""
        df = pd.DataFrame({
            'event_name': ['BF25'],
            'no_suppression_pct': [45.0],
            'oos_pct': [25.0]
            # Missing other percentage columns
        })
        
        with pytest.raises(KeyError) as exc_info:
            processor.extract_benchmark_percentages(df)
        assert 'vrp_missing_pct' in str(exc_info.value)
    
    def test_extract_benchmark_percentages_empty_dataframe(self, processor):
        """Test error handling with empty DataFrame."""
        df = pd.DataFrame({
            'no_suppression_pct': [],
            'oos_pct': [],
            'vrp_missing_pct': [],
            'price_error_pct': [],
            'others_pct': []
        })
        
        with pytest.raises(ValueError) as exc_info:
            processor.extract_benchmark_percentages(df)
        assert 'empty' in str(exc_info.value).lower()
    
    def test_extract_benchmark_percentages_multiple_rows(self, processor):
        """Test extraction uses first row when multiple rows present."""
        df = pd.DataFrame({
            'event_name': ['BF25', 'BF24'],
            'no_suppression_pct': [45.0, 50.0],
            'oos_pct': [25.0, 20.0],
            'vrp_missing_pct': [10.0, 12.0],
            'price_error_pct': [15.0, 13.0],
            'others_pct': [5.0, 5.0]
        })
        
        result = processor.extract_benchmark_percentages(df)
        
        # Should use first row
        assert result["No suppression"] == 45.0
        assert result["OOS"] == 25.0
    
    # Tests for validate_percentage_sum
    
    def test_validate_percentage_sum_exact_100(self, processor):
        """Test validation with percentages summing to exactly 100%."""
        percentages = {
            "No suppression": 45.0,
            "OOS": 25.0,
            "VRP missing": 10.0,
            "Price Error": 15.0,
            "Others": 5.0
        }
        
        assert processor.validate_percentage_sum(percentages) is True
    
    def test_validate_percentage_sum_within_tolerance(self, processor):
        """Test validation with percentages within 1% tolerance."""
        percentages = {
            "No suppression": 45.5,
            "OOS": 25.0,
            "VRP missing": 10.0,
            "Price Error": 15.0,
            "Others": 4.8
        }
        
        # Sum = 100.3, within 1% tolerance
        assert processor.validate_percentage_sum(percentages) is True
    
    def test_validate_percentage_sum_at_tolerance_boundary(self, processor):
        """Test validation at exactly 1% tolerance boundary."""
        percentages = {
            "No suppression": 46.0,
            "OOS": 25.0,
            "VRP missing": 10.0,
            "Price Error": 15.0,
            "Others": 5.0
        }
        
        # Sum = 101.0, exactly at 1% tolerance
        assert processor.validate_percentage_sum(percentages) is True
    
    def test_validate_percentage_sum_outside_tolerance(self, processor):
        """Test validation with percentages outside 1% tolerance."""
        percentages = {
            "No suppression": 50.0,
            "OOS": 25.0,
            "VRP missing": 10.0,
            "Price Error": 15.0,
            "Others": 5.0
        }
        
        # Sum = 105.0, outside 1% tolerance
        assert processor.validate_percentage_sum(percentages) is False
    
    def test_validate_percentage_sum_below_100(self, processor):
        """Test validation with percentages summing below 100%."""
        percentages = {
            "No suppression": 40.0,
            "OOS": 20.0,
            "VRP missing": 10.0,
            "Price Error": 15.0,
            "Others": 5.0
        }
        
        # Sum = 90.0, outside tolerance
        assert processor.validate_percentage_sum(percentages) is False
    
    def test_validate_percentage_sum_empty_dict(self, processor):
        """Test validation with empty dictionary."""
        percentages = {}
        
        # Sum = 0, outside tolerance
        assert processor.validate_percentage_sum(percentages) is False
    
    # Tests for calculate_current_suppression
    
    def test_calculate_current_suppression_basic(self, processor, sample_asin_data):
        """Test basic calculation of current suppression percentages."""
        result = processor.calculate_current_suppression(sample_asin_data)
        
        assert 'suppression_category_id' in result.columns
        assert 'suppression_category_name' in result.columns
        assert 'asin_count' in result.columns
        assert 'percentage' in result.columns
        assert len(result) == 5  # All 5 categories should be present
        
        # Verify counts (8 total ASINs)
        # Category 1 (No suppression): A001, A002, A005 = 3
        # Category 2 (OOS): A003, A008 = 2
        # Category 3 (VRP missing): A004 = 1
        # Category 4 (Price Error): A006 = 1
        # Category 5 (Others): A007 = 1
        
        cat1 = result[result['suppression_category_id'] == 1].iloc[0]
        assert cat1['asin_count'] == 3
        assert abs(cat1['percentage'] - 37.5) < 0.01
        
        cat2 = result[result['suppression_category_id'] == 2].iloc[0]
        assert cat2['asin_count'] == 2
        assert abs(cat2['percentage'] - 25.0) < 0.01
    
    def test_calculate_current_suppression_all_same_category(self, processor):
        """Test calculation when all ASINs are in the same category."""
        df = pd.DataFrame({
            'ASIN': ['A001', 'A002', 'A003'],
            'suppression_category_large': [1, 1, 1]
        })
        
        result = processor.calculate_current_suppression(df)
        
        cat1 = result[result['suppression_category_id'] == 1].iloc[0]
        assert cat1['asin_count'] == 3
        assert abs(cat1['percentage'] - 100.0) < 0.01
        
        # Other categories should have 0
        for cat_id in [2, 3, 4, 5]:
            cat = result[result['suppression_category_id'] == cat_id].iloc[0]
            assert cat['asin_count'] == 0
            assert cat['percentage'] == 0.0
    
    def test_calculate_current_suppression_missing_column(self, processor):
        """Test error handling when required columns are missing."""
        df = pd.DataFrame({
            'ASIN': ['A001', 'A002']
            # Missing suppression_category_large
        })
        
        with pytest.raises(KeyError) as exc_info:
            processor.calculate_current_suppression(df)
        assert 'suppression_category_large' in str(exc_info.value)
    
    def test_calculate_current_suppression_empty_dataframe(self, processor):
        """Test calculation with empty DataFrame."""
        df = pd.DataFrame({
            'ASIN': [],
            'suppression_category_large': []
        })
        
        result = processor.calculate_current_suppression(df)
        
        # Should return all categories with 0 count and 0%
        assert len(result) == 5
        assert all(result['asin_count'] == 0)
        assert all(result['percentage'] == 0.0)
    
    def test_calculate_current_suppression_invalid_category(self, processor):
        """Test calculation with invalid suppression category values."""
        df = pd.DataFrame({
            'ASIN': ['A001', 'A002', 'A003'],
            'suppression_category_large': [1, 2, 99]  # 99 is invalid
        })
        
        result = processor.calculate_current_suppression(df)
        
        # Valid categories should still be counted
        cat1 = result[result['suppression_category_id'] == 1].iloc[0]
        assert cat1['asin_count'] == 1
        
        cat2 = result[result['suppression_category_id'] == 2].iloc[0]
        assert cat2['asin_count'] == 1
    
    # Tests for aggregate_by_cid_pf
    
    def test_aggregate_by_cid_pf_basic(self, processor, sample_asin_data):
        """Test basic aggregation by CID and Product Family."""
        result = processor.aggregate_by_cid_pf(sample_asin_data)
        
        assert 'CID' in result.columns
        assert 'PF' in result.columns
        assert 'total_asins' in result.columns
        
        # Should have 4 combinations: C001×Electronics, C001×Home, C002×Electronics, C002×Home
        assert len(result) == 4
        
        # Check C001×Electronics (A001, A002): categories 1, 1
        c001_elec = result[(result['CID'] == 'C001') & (result['PF'] == 'Electronics')].iloc[0]
        assert c001_elec['total_asins'] == 2
        assert c001_elec['No suppression_count'] == 2
        assert abs(c001_elec['No suppression_pct'] - 100.0) < 0.01
        
        # Check C001×Home (A003, A004): categories 2, 3
        c001_home = result[(result['CID'] == 'C001') & (result['PF'] == 'Home')].iloc[0]
        assert c001_home['total_asins'] == 2
        assert c001_home['OOS_count'] == 1
        assert abs(c001_home['OOS_pct'] - 50.0) < 0.01
        assert c001_home['VRP missing_count'] == 1
        assert abs(c001_home['VRP missing_pct'] - 50.0) < 0.01
    
    def test_aggregate_by_cid_pf_single_asin_per_group(self, processor):
        """Test aggregation when each CID×PF has only one ASIN."""
        df = pd.DataFrame({
            'ASIN': ['A001', 'A002', 'A003'],
            'CID': ['C001', 'C002', 'C003'],
            'PF': ['Electronics', 'Home', 'Electronics'],
            'suppression_category_large': [1, 2, 3]
        })
        
        result = processor.aggregate_by_cid_pf(df)
        
        assert len(result) == 3
        assert all(result['total_asins'] == 1)
    
    def test_aggregate_by_cid_pf_missing_column(self, processor):
        """Test error handling when required columns are missing."""
        df = pd.DataFrame({
            'ASIN': ['A001', 'A002'],
            'CID': ['C001', 'C002']
            # Missing PF and suppression_category_large
        })
        
        with pytest.raises(KeyError) as exc_info:
            processor.aggregate_by_cid_pf(df)
        assert 'PF' in str(exc_info.value)
    
    def test_aggregate_by_cid_pf_empty_dataframe(self, processor):
        """Test aggregation with empty DataFrame."""
        df = pd.DataFrame({
            'ASIN': [],
            'CID': [],
            'PF': [],
            'suppression_category_large': []
        })
        
        result = processor.aggregate_by_cid_pf(df)
        
        assert len(result) == 0
        assert 'CID' in result.columns
        assert 'PF' in result.columns
    
    def test_aggregate_by_cid_pf_all_categories_present(self, processor):
        """Test aggregation with all suppression categories present in a group."""
        df = pd.DataFrame({
            'ASIN': ['A001', 'A002', 'A003', 'A004', 'A005'],
            'CID': ['C001', 'C001', 'C001', 'C001', 'C001'],
            'PF': ['Electronics', 'Electronics', 'Electronics', 'Electronics', 'Electronics'],
            'suppression_category_large': [1, 2, 3, 4, 5]
        })
        
        result = processor.aggregate_by_cid_pf(df)
        
        assert len(result) == 1
        row = result.iloc[0]
        
        assert row['total_asins'] == 5
        assert row['No suppression_count'] == 1
        assert row['OOS_count'] == 1
        assert row['VRP missing_count'] == 1
        assert row['Price Error_count'] == 1
        assert row['Others_count'] == 1
        
        # Each category should be 20%
        assert abs(row['No suppression_pct'] - 20.0) < 0.01
        assert abs(row['OOS_pct'] - 20.0) < 0.01
        assert abs(row['VRP missing_pct'] - 20.0) < 0.01
        assert abs(row['Price Error_pct'] - 20.0) < 0.01
        assert abs(row['Others_pct'] - 20.0) < 0.01
    
    def test_aggregate_by_cid_pf_percentage_calculation(self, processor):
        """Test that percentages are calculated correctly."""
        df = pd.DataFrame({
            'ASIN': ['A001', 'A002', 'A003', 'A004', 'A005', 'A006', 'A007', 'A008', 'A009', 'A010'],
            'CID': ['C001'] * 10,
            'PF': ['Electronics'] * 10,
            'suppression_category_large': [1, 1, 1, 1, 1, 1, 1, 2, 2, 3]
        })
        
        result = processor.aggregate_by_cid_pf(df)
        
        row = result.iloc[0]
        assert row['total_asins'] == 10
        assert row['No suppression_count'] == 7
        assert abs(row['No suppression_pct'] - 70.0) < 0.01
        assert row['OOS_count'] == 2
        assert abs(row['OOS_pct'] - 20.0) < 0.01
        assert row['VRP missing_count'] == 1
        assert abs(row['VRP missing_pct'] - 10.0) < 0.01
    
    # Integration tests
    
    def test_full_workflow(self, processor, sample_benchmark_data, sample_asin_data):
        """Test complete workflow: extract benchmark → validate → calculate current → aggregate."""
        # Extract benchmark percentages
        benchmark = processor.extract_benchmark_percentages(sample_benchmark_data)
        
        # Validate benchmark percentages
        is_valid = processor.validate_percentage_sum(benchmark)
        assert is_valid is True
        
        # Calculate current suppression
        current = processor.calculate_current_suppression(sample_asin_data)
        assert len(current) == 5
        
        # Aggregate by CID×PF
        aggregated = processor.aggregate_by_cid_pf(sample_asin_data)
        assert len(aggregated) == 4
        
        # Verify all CID×PF combinations are present
        assert ('C001', 'Electronics') in zip(aggregated['CID'], aggregated['PF'])
        assert ('C001', 'Home') in zip(aggregated['CID'], aggregated['PF'])
        assert ('C002', 'Electronics') in zip(aggregated['CID'], aggregated['PF'])
        assert ('C002', 'Home') in zip(aggregated['CID'], aggregated['PF'])
