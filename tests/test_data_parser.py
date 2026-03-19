"""
Unit tests for DataParser.
**Validates: Requirements 1.2, 1.3, 1.4**
"""
import pandas as pd
import pytest

from src.data_parser import DataParser, ValidationError, ParseError
from src.constants import REQUIRED_COLUMNS


def create_valid_dataframe(n_rows: int = 5) -> pd.DataFrame:
    """Create a valid DataFrame for testing."""
    return pd.DataFrame({
        'asin': [f'ASIN{i}' for i in range(n_rows)],
        'MERCHANT_CUSTOMER_ID': [f'MID{i}' for i in range(n_rows)],
        'pf': ['PF1'] * n_rows,
        'gl': ['GL1'] * n_rows,
        'Paid-Flag': ['Y', 'N'] * (n_rows // 2) + ['Y'] * (n_rows % 2),
        'DealFlag': ['Deal'] * n_rows,
        'PointsDealFlag': ['Points'] * n_rows,
        'Price&PointsDealFlag': ['Sourced', 'NonSourced'] * (n_rows // 2) + ['Sourced'] * (n_rows % 2),
        'RetailFlag': ['Y'] * n_rows,
        'DomesticOOCFlag': ['N'] * n_rows,
        'PriceBand': ['1~1000'] * n_rows,
        'ASINTenure': ['1.0-30 days'] * n_rows,
        'GMS': [1000.0 * i for i in range(n_rows)],
        'UNITS': [10 * i for i in range(n_rows)],
    })


class TestDataParserValidation:
    """Unit tests for DataParser validation."""
    
    def test_validate_valid_data(self):
        """Test validation passes for valid data."""
        parser = DataParser()
        df = create_valid_dataframe()
        
        result = parser.validate(df)
        
        assert result.is_valid is True
        assert result.missing_columns == []
        assert result.invalid_columns == []
    
    def test_validate_missing_columns(self):
        """Test validation fails when required columns are missing."""
        parser = DataParser()
        df = pd.DataFrame({
            'asin': ['ASIN1'],
            'MERCHANT_CUSTOMER_ID': ['MID1'],
            # Missing other required columns
        })
        
        result = parser.validate(df)
        
        assert result.is_valid is False
        assert len(result.missing_columns) > 0
        assert 'Paid-Flag' in result.missing_columns
    
    def test_validate_invalid_paid_flag(self):
        """Test validation fails for invalid Paid-Flag values."""
        parser = DataParser()
        df = create_valid_dataframe()
        df.loc[0, 'Paid-Flag'] = 'INVALID'
        
        result = parser.validate(df)
        
        assert result.is_valid is False
        assert any('Paid-Flag' in col for col in result.invalid_columns)
    
    def test_validate_invalid_price_points_deal_flag(self):
        """Test validation fails for invalid Price&PointsDealFlag values."""
        parser = DataParser()
        df = create_valid_dataframe()
        df.loc[0, 'Price&PointsDealFlag'] = 'INVALID'
        
        result = parser.validate(df)
        
        assert result.is_valid is False
        assert any('Price&PointsDealFlag' in col for col in result.invalid_columns)


class TestDataParserParseAndValidate:
    """Unit tests for parse_and_validate method."""
    
    def test_parse_and_validate_success(self):
        """Test parse_and_validate returns validated DataFrame."""
        parser = DataParser()
        df = create_valid_dataframe()
        
        result = parser.parse_and_validate(df)
        
        assert len(result) == len(df)
        assert result['GMS'].dtype in ['float64', 'int64']
    
    def test_parse_and_validate_raises_on_invalid(self):
        """Test parse_and_validate raises ValidationError for invalid data."""
        parser = DataParser()
        df = pd.DataFrame({
            'asin': ['ASIN1'],
            # Missing required columns
        })
        
        with pytest.raises(ValidationError):
            parser.parse_and_validate(df)


class TestDataParserParse:
    """Unit tests for parse method."""
    
    def test_parse_tab_separated(self):
        """Test parsing tab-separated data."""
        parser = DataParser()
        raw_data = "col1\tcol2\nval1\tval2"
        
        df = parser.parse(raw_data)
        
        assert 'col1' in df.columns
        assert 'col2' in df.columns
        assert df.loc[0, 'col1'] == 'val1'
    
    def test_parse_comma_separated(self):
        """Test parsing comma-separated data."""
        parser = DataParser()
        raw_data = "col1,col2\nval1,val2"
        
        df = parser.parse(raw_data)
        
        assert 'col1' in df.columns
        assert 'col2' in df.columns
