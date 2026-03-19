"""
Data Parser module for Deal Sourcing Analyzer.
Handles parsing and validation of loaded data.
"""
from dataclasses import dataclass
from typing import List, Optional

import pandas as pd

from src.constants import REQUIRED_COLUMNS


@dataclass
class ValidationResult:
    """Result of data validation."""
    is_valid: bool
    missing_columns: List[str]
    invalid_columns: List[str]
    error_message: Optional[str] = None


class ParseError(Exception):
    """Exception raised when parsing fails."""
    pass


class ValidationError(Exception):
    """Exception raised when validation fails."""
    pass


class DataParser:
    """
    Parses and validates data for Deal Sourcing Analyzer.
    
    Validates that all required columns are present and have correct data types.
    """
    
    def __init__(self):
        """Initialize DataParser."""
        self.required_columns = REQUIRED_COLUMNS
    
    def parse(self, raw_data: str) -> pd.DataFrame:
        """
        Parse raw string data into a DataFrame.
        
        Args:
            raw_data: Raw string data (tab or comma separated)
            
        Returns:
            Parsed DataFrame
            
        Raises:
            ParseError: If parsing fails
        """
        from io import StringIO
        
        try:
            # Try tab-separated first
            df = pd.read_csv(StringIO(raw_data), sep='\t')
            if len(df.columns) > 1:
                return df
        except Exception:
            pass
        
        try:
            # Fallback to comma-separated
            df = pd.read_csv(StringIO(raw_data), sep=',')
            return df
        except Exception as e:
            raise ParseError(f"データのパースに失敗しました: {e}")
    
    def validate(self, df: pd.DataFrame) -> ValidationResult:
        """
        Validate that DataFrame has all required columns and correct data types.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            ValidationResult with validation status and details
        """
        missing_columns = []
        invalid_columns = []
        
        # Check for missing columns
        for col in self.required_columns:
            if col not in df.columns:
                missing_columns.append(col)
        
        if missing_columns:
            return ValidationResult(
                is_valid=False,
                missing_columns=missing_columns,
                invalid_columns=[],
                error_message=f"必須カラムが不足しています: {', '.join(missing_columns)}"
            )
        
        # Validate data types and values
        # Check paid-flag values
        if not df['paid-flag'].isin(['Y', 'N']).all():
            invalid_values = df[~df['paid-flag'].isin(['Y', 'N'])]['paid-flag'].unique()
            invalid_columns.append(f"paid-flag (無効な値: {invalid_values})")
        
        # Check price&pointsdealflag values
        if not df['price&pointsdealflag'].isin(['Sourced', 'NonSourced']).all():
            invalid_values = df[~df['price&pointsdealflag'].isin(['Sourced', 'NonSourced'])]['price&pointsdealflag'].unique()
            invalid_columns.append(f"price&pointsdealflag (無効な値: {invalid_values})")
        
        # Check gms is numeric
        try:
            pd.to_numeric(df['gms'], errors='raise')
        except (ValueError, TypeError):
            invalid_columns.append("gms (数値ではありません)")
        
        # Check units is numeric
        try:
            pd.to_numeric(df['units'], errors='raise')
        except (ValueError, TypeError):
            invalid_columns.append("units (数値ではありません)")
        
        if invalid_columns:
            return ValidationResult(
                is_valid=False,
                missing_columns=[],
                invalid_columns=invalid_columns,
                error_message=f"データ型が不正です: {'; '.join(invalid_columns)}"
            )
        
        return ValidationResult(
            is_valid=True,
            missing_columns=[],
            invalid_columns=[]
        )
    
    def parse_and_validate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate DataFrame and raise exception if invalid.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Validated DataFrame with correct data types
            
        Raises:
            ValidationError: If validation fails
        """
        result = self.validate(df)
        
        if not result.is_valid:
            raise ValidationError(result.error_message)
        
        # Convert data types
        df = df.copy()
        df['gms'] = pd.to_numeric(df['gms'], errors='coerce').fillna(0)
        df['units'] = pd.to_numeric(df['units'], errors='coerce').fillna(0).astype(int)
        
        return df
