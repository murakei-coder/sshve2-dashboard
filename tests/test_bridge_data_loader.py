"""
Unit tests for the DataLoader class.

Tests cover loading CSV and Excel files, error handling for missing files,
encoding issues, and column validation.
"""

import pytest
import pandas as pd
import tempfile
import os
from src.bridge_plan_generator.data_loader import DataLoader


class TestDataLoader:
    """Test suite for DataLoader class."""
    
    @pytest.fixture
    def data_loader(self):
        """Create a DataLoader instance for testing."""
        return DataLoader()
    
    @pytest.fixture
    def temp_csv_file(self):
        """Create a temporary CSV file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
            f.write("col1,col2,col3\n")
            f.write("value1,value2,value3\n")
            f.write("value4,value5,value6\n")
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)
    
    @pytest.fixture
    def temp_csv_with_japanese(self):
        """Create a temporary CSV file with Japanese characters."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
            f.write("名前,値,カテゴリ\n")
            f.write("テスト1,100,カテゴリA\n")
            f.write("テスト2,200,カテゴリB\n")
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)
    
    @pytest.fixture
    def temp_excel_file(self):
        """Create a temporary Excel file for testing."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as f:
            temp_path = f.name
        
        # Create a simple Excel file
        df = pd.DataFrame({
            'CID': ['CID001', 'CID002'],
            'Alias': ['Alias1', 'Alias2'],
            'Mgr': ['Manager1', 'Manager1'],
            'Team': ['TeamA', 'TeamA']
        })
        df.to_excel(temp_path, sheet_name='Sheet1', index=False, engine='openpyxl')
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)
    
    def test_load_sourcing_data_success(self, data_loader, temp_csv_file):
        """Test successful loading of sourcing data from CSV."""
        df = data_loader.load_sourcing_data(temp_csv_file)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert list(df.columns) == ['col1', 'col2', 'col3']
    
    def test_load_target_data_success(self, data_loader, temp_csv_file):
        """Test successful loading of target data from CSV."""
        df = data_loader.load_target_data(temp_csv_file)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert list(df.columns) == ['col1', 'col2', 'col3']
    
    def test_load_suppression_benchmark_success(self, data_loader, temp_csv_file):
        """Test successful loading of suppression benchmark from CSV."""
        df = data_loader.load_suppression_benchmark(temp_csv_file)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert list(df.columns) == ['col1', 'col2', 'col3']
    
    def test_load_cid_mapping_success(self, data_loader, temp_excel_file):
        """Test successful loading of CID mapping from Excel."""
        df = data_loader.load_cid_mapping(temp_excel_file, sheet_name='Sheet1')
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert 'CID' in df.columns
        assert 'Alias' in df.columns
        assert 'Mgr' in df.columns
        assert 'Team' in df.columns
    
    def test_load_japanese_characters(self, data_loader, temp_csv_with_japanese):
        """Test loading CSV file with Japanese characters."""
        df = data_loader.load_sourcing_data(temp_csv_with_japanese)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert '名前' in df.columns
        assert '値' in df.columns
        assert 'カテゴリ' in df.columns
        assert df.iloc[0]['名前'] == 'テスト1'
    
    def test_load_sourcing_data_file_not_found(self, data_loader):
        """Test error handling when sourcing data file is missing."""
        with pytest.raises(FileNotFoundError) as exc_info:
            data_loader.load_sourcing_data('nonexistent_file.csv')
        
        assert 'File not found' in str(exc_info.value)
        assert 'nonexistent_file.csv' in str(exc_info.value)
    
    def test_load_target_data_file_not_found(self, data_loader):
        """Test error handling when target data file is missing."""
        with pytest.raises(FileNotFoundError) as exc_info:
            data_loader.load_target_data('nonexistent_file.csv')
        
        assert 'File not found' in str(exc_info.value)
        assert 'nonexistent_file.csv' in str(exc_info.value)
    
    def test_load_suppression_benchmark_file_not_found(self, data_loader):
        """Test error handling when suppression benchmark file is missing."""
        with pytest.raises(FileNotFoundError) as exc_info:
            data_loader.load_suppression_benchmark('nonexistent_file.csv')
        
        assert 'File not found' in str(exc_info.value)
        assert 'nonexistent_file.csv' in str(exc_info.value)
    
    def test_load_cid_mapping_file_not_found(self, data_loader):
        """Test error handling when CID mapping file is missing."""
        with pytest.raises(FileNotFoundError) as exc_info:
            data_loader.load_cid_mapping('nonexistent_file.xlsx')
        
        assert 'File not found' in str(exc_info.value)
        assert 'nonexistent_file.xlsx' in str(exc_info.value)
    
    def test_validate_required_columns_all_present(self, data_loader):
        """Test column validation when all required columns are present."""
        df = pd.DataFrame({
            'col1': [1, 2],
            'col2': [3, 4],
            'col3': [5, 6]
        })
        
        is_valid, error_msg = data_loader.validate_required_columns(
            df, ['col1', 'col2', 'col3'], 'test_file.csv'
        )
        
        assert is_valid is True
        assert error_msg is None
    
    def test_validate_required_columns_some_missing(self, data_loader):
        """Test column validation when some required columns are missing."""
        df = pd.DataFrame({
            'col1': [1, 2],
            'col2': [3, 4]
        })
        
        is_valid, error_msg = data_loader.validate_required_columns(
            df, ['col1', 'col2', 'col3', 'col4'], 'test_file.csv'
        )
        
        assert is_valid is False
        assert error_msg is not None
        assert 'Missing required columns' in error_msg
        assert 'test_file.csv' in error_msg
        assert 'col3' in error_msg
        assert 'col4' in error_msg
    
    def test_validate_required_columns_all_missing(self, data_loader):
        """Test column validation when all required columns are missing."""
        df = pd.DataFrame({
            'col1': [1, 2],
            'col2': [3, 4]
        })
        
        is_valid, error_msg = data_loader.validate_required_columns(
            df, ['col5', 'col6'], 'test_file.csv'
        )
        
        assert is_valid is False
        assert error_msg is not None
        assert 'Missing required columns' in error_msg
        assert 'col5' in error_msg
        assert 'col6' in error_msg
    
    def test_validate_required_columns_empty_dataframe(self, data_loader):
        """Test column validation with an empty DataFrame."""
        df = pd.DataFrame()
        
        is_valid, error_msg = data_loader.validate_required_columns(
            df, ['col1', 'col2'], 'test_file.csv'
        )
        
        assert is_valid is False
        assert error_msg is not None
        assert 'Missing required columns' in error_msg
