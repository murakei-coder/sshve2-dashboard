"""
Unit tests for the discount analyzer DataLoader class.
Tests cover tab-delimited file loading and chunk reading for large files.
"""
import pytest
import pandas as pd
import tempfile
import os
from src.discount_analyzer import DataLoader, ParseError


class TestDiscountDataLoader:
    """Test suite for discount analyzer DataLoader class."""
    
    @pytest.fixture
    def data_loader(self):
        """Create a DataLoader instance for testing."""
        return DataLoader()
    
    @pytest.fixture
    def sample_tsv_file(self):
        """Create a temporary TSV file for testing."""
        data = """asin\tpf\tour_price\tcurrent_discount_percent\tpast_month_gms\tpromotion_ops
B001\tBooks\t1500\t10\t50000\t75000
B002\tElectronics\t25000\t20\t100000\t150000
B003\tFashion\t3000\t15\t30000\t45000
B004\tHome\t8000\t25\t60000\t90000
B005\tBooks\t2000\t5\t40000\t50000"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            f.write(data)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)
    
    @pytest.fixture
    def large_tsv_file(self):
        """Create a larger temporary TSV file for chunk reading test."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            # Write header
            f.write("asin\tpf\tour_price\tcurrent_discount_percent\tpast_month_gms\tpromotion_ops\n")
            
            # Write 1000 rows
            for i in range(1000):
                pf = ['Books', 'Electronics', 'Fashion', 'Home'][i % 4]
                price = 1000 + (i * 10)
                discount = 5 + (i % 45)
                past_gms = 10000 + (i * 100)
                promo_ops = past_gms * (1 + discount / 100)
                f.write(f"B{i:04d}\t{pf}\t{price}\t{discount}\t{past_gms}\t{promo_ops}\n")
            
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)
    
    def test_load_basic_tsv(self, data_loader, sample_tsv_file):
        """Test loading a basic tab-separated file."""
        df = data_loader.load(sample_tsv_file)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5
        assert 'asin' in df.columns
        assert 'pf' in df.columns
        assert 'our_price' in df.columns
        assert 'current_discount_percent' in df.columns
        assert 'past_month_gms' in df.columns
        assert 'promotion_ops' in df.columns
    
    def test_load_with_chunks(self, data_loader, large_tsv_file):
        """Test loading a file with chunk reading."""
        # Load with chunks
        df_chunked = data_loader.load(large_tsv_file, chunksize=100)
        
        # Load without chunks for comparison
        df_normal = data_loader.load(large_tsv_file)
        
        assert isinstance(df_chunked, pd.DataFrame)
        assert len(df_chunked) == len(df_normal)
        assert len(df_chunked) == 1000
        assert list(df_chunked.columns) == list(df_normal.columns)
        
        # Verify data integrity
        pd.testing.assert_frame_equal(df_chunked, df_normal)
    
    def test_load_nonexistent_file(self, data_loader):
        """Test loading a file that doesn't exist."""
        with pytest.raises(FileNotFoundError):
            data_loader.load('nonexistent_file.txt')
    
    def test_load_with_different_encoding(self, data_loader):
        """Test loading a file with cp932 encoding."""
        # Create a file with Japanese characters in cp932 encoding
        data = "asin\tpf\tour_price\tcurrent_discount_percent\tpast_month_gms\tpromotion_ops\n"
        data += "B001\t書籍\t1500\t10\t50000\t75000\n"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='cp932') as f:
            f.write(data)
            temp_path = f.name
        
        try:
            # Should automatically detect and use cp932 encoding
            df = data_loader.load(temp_path)
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 1
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_chunk_size_parameter(self, data_loader, large_tsv_file):
        """Test that different chunk sizes produce the same result."""
        df_chunk_50 = data_loader.load(large_tsv_file, chunksize=50)
        df_chunk_200 = data_loader.load(large_tsv_file, chunksize=200)
        df_no_chunk = data_loader.load(large_tsv_file)
        
        assert len(df_chunk_50) == len(df_chunk_200) == len(df_no_chunk)
        pd.testing.assert_frame_equal(df_chunk_50, df_no_chunk)
        pd.testing.assert_frame_equal(df_chunk_200, df_no_chunk)
