"""
Unit tests for DataValidator class

Tests cover:
- Required column validation (Requirements 1.3, 5.1, 5.2, 5.3, 5.4)
- Empty DataFrame handling (Requirement 5.5)
- Data cleaning (Requirement 2.5)
"""

import pytest
import pandas as pd
from src.sourcing_aggregator import DataValidator, ValidationResult


class TestDataValidatorValidate:
    """Tests for DataValidator.validate() method"""
    
    def test_validate_with_all_required_columns(self):
        """Valid DataFrame with all required columns should pass validation"""
        df = pd.DataFrame({
            'mcid': ['M001', 'M002'],
            'total_t30d_gms_BAU': [1000, 2000],
            'SSHVE2_SourcedFlag': ['Y', 'N']
        })
        
        validator = DataValidator()
        result = validator.validate(df)
        
        assert result.is_valid is True
        assert len(result.missing_columns) == 0
        assert len(result.error_messages) == 0
        assert result.total_rows == 2
    
    def test_validate_with_missing_mcid_column(self):
        """DataFrame missing mcid column should fail validation"""
        df = pd.DataFrame({
            'total_t30d_gms_BAU': [1000, 2000],
            'SSHVE2_SourcedFlag': ['Y', 'N']
        })
        
        validator = DataValidator()
        result = validator.validate(df)
        
        assert result.is_valid is False
        assert 'mcid' in result.missing_columns
        assert any('mcid' in msg for msg in result.error_messages)
    
    def test_validate_with_missing_gms_column(self):
        """DataFrame missing total_t30d_gms_BAU column should fail validation"""
        df = pd.DataFrame({
            'mcid': ['M001', 'M002'],
            'SSHVE2_SourcedFlag': ['Y', 'N']
        })
        
        validator = DataValidator()
        result = validator.validate(df)
        
        assert result.is_valid is False
        assert 'total_t30d_gms_BAU' in result.missing_columns
        assert any('total_t30d_gms_BAU' in msg for msg in result.error_messages)
    
    def test_validate_with_missing_sourced_flag_column(self):
        """DataFrame missing SSHVE2_SourcedFlag column should fail validation"""
        df = pd.DataFrame({
            'mcid': ['M001', 'M002'],
            'total_t30d_gms_BAU': [1000, 2000]
        })
        
        validator = DataValidator()
        result = validator.validate(df)
        
        assert result.is_valid is False
        assert 'SSHVE2_SourcedFlag' in result.missing_columns
        assert any('SSHVE2_SourcedFlag' in msg for msg in result.error_messages)
    
    def test_validate_with_multiple_missing_columns(self):
        """DataFrame missing multiple columns should report all missing columns"""
        df = pd.DataFrame({
            'mcid': ['M001', 'M002']
        })
        
        validator = DataValidator()
        result = validator.validate(df)
        
        assert result.is_valid is False
        assert 'total_t30d_gms_BAU' in result.missing_columns
        assert 'SSHVE2_SourcedFlag' in result.missing_columns
        assert len(result.missing_columns) == 2
    
    def test_validate_with_empty_dataframe(self):
        """Empty DataFrame should fail validation"""
        df = pd.DataFrame({
            'mcid': [],
            'total_t30d_gms_BAU': [],
            'SSHVE2_SourcedFlag': []
        })
        
        validator = DataValidator()
        result = validator.validate(df)
        
        assert result.is_valid is False
        assert result.total_rows == 0
        assert any('データ行が存在しません' in msg for msg in result.error_messages)
    
    def test_validate_with_extra_columns(self):
        """DataFrame with extra columns should still pass validation"""
        df = pd.DataFrame({
            'mcid': ['M001'],
            'total_t30d_gms_BAU': [1000],
            'SSHVE2_SourcedFlag': ['Y'],
            'extra_column': ['extra_value']
        })
        
        validator = DataValidator()
        result = validator.validate(df)
        
        assert result.is_valid is True
        assert len(result.missing_columns) == 0


class TestDataValidatorClean:
    """Tests for DataValidator.clean() method"""
    
    def test_clean_converts_numeric_gms_values(self):
        """Numeric string values in total_t30d_gms_BAU should be converted to float"""
        df = pd.DataFrame({
            'mcid': ['M001', 'M002'],
            'total_t30d_gms_BAU': ['1000.5', '2000.75'],
            'SSHVE2_SourcedFlag': ['Y', 'N']
        })
        
        validator = DataValidator()
        cleaned = validator.clean(df)
        
        assert cleaned['total_t30d_gms_BAU'].dtype in [float, 'float64']
        assert cleaned['total_t30d_gms_BAU'].iloc[0] == 1000.5
        assert cleaned['total_t30d_gms_BAU'].iloc[1] == 2000.75
    
    def test_clean_converts_invalid_gms_to_zero(self):
        """Non-numeric values in total_t30d_gms_BAU should be converted to 0"""
        df = pd.DataFrame({
            'mcid': ['M001', 'M002', 'M003'],
            'total_t30d_gms_BAU': ['1000', 'invalid', 'N/A'],
            'SSHVE2_SourcedFlag': ['Y', 'N', 'Y']
        })
        
        validator = DataValidator()
        cleaned = validator.clean(df)
        
        assert cleaned['total_t30d_gms_BAU'].iloc[0] == 1000.0
        assert cleaned['total_t30d_gms_BAU'].iloc[1] == 0.0
        assert cleaned['total_t30d_gms_BAU'].iloc[2] == 0.0
    
    def test_clean_converts_sourced_flag_to_string(self):
        """SSHVE2_SourcedFlag should be converted to string type"""
        df = pd.DataFrame({
            'mcid': ['M001', 'M002'],
            'total_t30d_gms_BAU': [1000, 2000],
            'SSHVE2_SourcedFlag': ['Y', 'N']
        })
        
        validator = DataValidator()
        cleaned = validator.clean(df)
        
        assert cleaned['SSHVE2_SourcedFlag'].dtype == object
        assert isinstance(cleaned['SSHVE2_SourcedFlag'].iloc[0], str)
    
    def test_clean_removes_rows_with_missing_mcid(self):
        """Rows with missing mcid should be removed"""
        df = pd.DataFrame({
            'mcid': ['M001', None, 'M003', pd.NA],
            'total_t30d_gms_BAU': [1000, 2000, 3000, 4000],
            'SSHVE2_SourcedFlag': ['Y', 'N', 'Y', 'N']
        })
        
        validator = DataValidator()
        cleaned = validator.clean(df)
        
        assert len(cleaned) == 2
        assert 'M001' in cleaned['mcid'].values
        assert 'M003' in cleaned['mcid'].values
    
    def test_clean_does_not_modify_original_dataframe(self):
        """Cleaning should not modify the original DataFrame"""
        df = pd.DataFrame({
            'mcid': ['M001', None],
            'total_t30d_gms_BAU': ['1000', 'invalid'],
            'SSHVE2_SourcedFlag': ['Y', 'N']
        })
        
        original_len = len(df)
        original_gms_type = df['total_t30d_gms_BAU'].dtype
        
        validator = DataValidator()
        cleaned = validator.clean(df)
        
        # Original DataFrame should remain unchanged
        assert len(df) == original_len
        assert df['total_t30d_gms_BAU'].dtype == original_gms_type
        
        # Cleaned DataFrame should be different
        assert len(cleaned) != len(df)
        assert cleaned['total_t30d_gms_BAU'].dtype != original_gms_type
    
    def test_clean_handles_empty_dataframe(self):
        """Cleaning an empty DataFrame should return an empty DataFrame"""
        df = pd.DataFrame({
            'mcid': [],
            'total_t30d_gms_BAU': [],
            'SSHVE2_SourcedFlag': []
        })
        
        validator = DataValidator()
        cleaned = validator.clean(df)
        
        assert len(cleaned) == 0
        assert list(cleaned.columns) == list(df.columns)
    
    def test_clean_handles_all_valid_data(self):
        """Cleaning valid data should preserve all rows"""
        df = pd.DataFrame({
            'mcid': ['M001', 'M002', 'M003'],
            'total_t30d_gms_BAU': [1000.0, 2000.0, 3000.0],
            'SSHVE2_SourcedFlag': ['Y', 'N', 'Y']
        })
        
        validator = DataValidator()
        cleaned = validator.clean(df)
        
        assert len(cleaned) == 3
        assert list(cleaned['mcid']) == ['M001', 'M002', 'M003']
