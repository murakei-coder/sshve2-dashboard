"""
Property-based tests for FileLoader.
**Feature: deal-sourcing-analyzer, Property 1: File Loading Consistency**
**Validates: Requirements 1.1, 1.2**
"""
import os
import tempfile
from pathlib import Path

import pandas as pd
import pytest
from hypothesis import given, strategies as st, settings

from src.file_loader import FileLoader
from src.constants import REQUIRED_COLUMNS


# Strategy for generating valid data rows
@st.composite
def valid_row_data(draw):
    """Generate a single valid row of data."""
    return {
        'asin': draw(st.text(alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', min_size=5, max_size=10)),
        'MERCHANT_CUSTOMER_ID': draw(st.text(alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', min_size=5, max_size=15)),
        'pf': draw(st.sampled_from(['PF1', 'PF2', 'PF3'])),
        'gl': draw(st.sampled_from(['GL1', 'GL2', 'GL3'])),
        'Paid-Flag': draw(st.sampled_from(['Y', 'N'])),
        'DealFlag': draw(st.sampled_from(['Deal', 'NoDeal'])),
        'PointsDealFlag': draw(st.sampled_from(['Points', 'NoPoints'])),
        'Price&PointsDealFlag': draw(st.sampled_from(['Sourced', 'NonSourced'])),
        'RetailFlag': draw(st.sampled_from(['Y', 'N'])),
        'DomesticOOCFlag': draw(st.sampled_from(['Y', 'N'])),
        'PriceBand': draw(st.sampled_from(['1~1000', '1001~2000', '2001~3000'])),
        'ASINTenure': draw(st.sampled_from(['1.0-30 days', '2.31-90 days', '3.91-180 days'])),
        'GMS': draw(st.floats(min_value=0, max_value=1000000, allow_nan=False, allow_infinity=False)),
        'UNITS': draw(st.integers(min_value=0, max_value=10000)),
    }


@st.composite
def valid_dataframe(draw):
    """Generate a valid DataFrame with all required columns."""
    n_rows = draw(st.integers(min_value=1, max_value=50))
    rows = [draw(valid_row_data()) for _ in range(n_rows)]
    return pd.DataFrame(rows)


class TestFileLoaderProperty:
    """Property-based tests for FileLoader."""
    
    @given(df=valid_dataframe())
    @settings(max_examples=100)
    def test_file_loading_consistency(self, df: pd.DataFrame):
        """
        **Feature: deal-sourcing-analyzer, Property 1: File Loading Consistency**
        
        For any valid txt file in the data folder, loading the file should return
        a DataFrame containing all 14 required columns with the correct data types.
        
        **Validates: Requirements 1.1, 1.2**
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write the DataFrame to a temp file
            test_file = Path(tmpdir) / "test_data.txt"
            df.to_csv(test_file, sep='\t', index=False)
            
            # Load the file using FileLoader
            loader = FileLoader(data_dir=tmpdir)
            loaded_df = loader.load_file("test_data.txt")
            
            # Property: All required columns should be present
            for col in REQUIRED_COLUMNS:
                assert col in loaded_df.columns, f"Missing column: {col}"
            
            # Property: Row count should match
            assert len(loaded_df) == len(df), "Row count mismatch"
            
            # Property: Data should be consistent (check a few key columns)
            assert loaded_df['Paid-Flag'].isin(['Y', 'N']).all(), "Invalid Paid-Flag values"
            assert loaded_df['Price&PointsDealFlag'].isin(['Sourced', 'NonSourced']).all(), "Invalid Price&PointsDealFlag values"


class TestFileLoaderUnit:
    """Unit tests for FileLoader edge cases."""
    
    def test_file_not_found(self):
        """Test that FileNotFoundError is raised for missing files."""
        loader = FileLoader(data_dir="nonexistent_dir")
        with pytest.raises(FileNotFoundError):
            loader.load_file("nonexistent.txt")
    
    def test_list_available_files_empty_dir(self):
        """Test listing files in empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = FileLoader(data_dir=tmpdir)
            files = loader.list_available_files()
            assert files == []
    
    def test_list_available_files_with_txt(self):
        """Test listing txt files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some test files
            (Path(tmpdir) / "test1.txt").touch()
            (Path(tmpdir) / "test2.txt").touch()
            (Path(tmpdir) / "other.csv").touch()  # Should not be listed
            
            loader = FileLoader(data_dir=tmpdir)
            files = loader.list_available_files()
            
            assert len(files) == 2
            assert "test1.txt" in files
            assert "test2.txt" in files
            assert "other.csv" not in files
