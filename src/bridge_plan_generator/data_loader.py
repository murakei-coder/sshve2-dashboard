"""
Data loader module for the Bridge Plan Generator.

This module handles loading and validating CSV and Excel files containing
sourcing data, target data, suppression benchmarks, and CID mappings.
"""

import pandas as pd
from typing import Tuple, Optional, List


class DataLoader:
    """Handles loading and validation of all input data files."""
    
    def load_sourcing_data(self, file_path: str) -> pd.DataFrame:
        """
        Load sourcing data from a CSV file.
        
        Args:
            file_path: Path to the sourcing data CSV file
            
        Returns:
            DataFrame containing sourcing data
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            pd.errors.ParserError: If the file cannot be parsed
            UnicodeDecodeError: If encoding issues occur
        """
        try:
            # Try UTF-8 encoding first
            df = pd.read_csv(file_path, encoding='utf-8')
            return df
        except UnicodeDecodeError:
            # Fall back to UTF-8-sig for files with BOM
            try:
                df = pd.read_csv(file_path, encoding='utf-8-sig')
                return df
            except UnicodeDecodeError as e:
                raise UnicodeDecodeError(
                    e.encoding,
                    e.object,
                    e.start,
                    e.end,
                    f"Encoding error in {file_path}. Please ensure the file is UTF-8 encoded."
                )
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}. Please check the configuration.")
        except pd.errors.ParserError:
            raise pd.errors.ParserError(f"Unable to parse {file_path}. Please ensure the file format is correct.")
    
    def load_target_data(self, file_path: str) -> pd.DataFrame:
        """
        Load target data from a CSV file.
        
        Args:
            file_path: Path to the target data CSV file
            
        Returns:
            DataFrame containing target data
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            pd.errors.ParserError: If the file cannot be parsed
            UnicodeDecodeError: If encoding issues occur
        """
        try:
            # Try UTF-8 encoding first
            df = pd.read_csv(file_path, encoding='utf-8')
            return df
        except UnicodeDecodeError:
            # Fall back to UTF-8-sig for files with BOM
            try:
                df = pd.read_csv(file_path, encoding='utf-8-sig')
                return df
            except UnicodeDecodeError as e:
                raise UnicodeDecodeError(
                    e.encoding,
                    e.object,
                    e.start,
                    e.end,
                    f"Encoding error in {file_path}. Please ensure the file is UTF-8 encoded."
                )
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}. Please check the configuration.")
        except pd.errors.ParserError:
            raise pd.errors.ParserError(f"Unable to parse {file_path}. Please ensure the file format is correct.")

    def load_suppression_benchmark(self, file_path: str) -> pd.DataFrame:
        """
        Load suppression benchmark data from a CSV file.
        
        Args:
            file_path: Path to the suppression benchmark CSV file
            
        Returns:
            DataFrame containing suppression benchmark data
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            pd.errors.ParserError: If the file cannot be parsed
            UnicodeDecodeError: If encoding issues occur
        """
        try:
            # Try UTF-8 encoding first
            df = pd.read_csv(file_path, encoding='utf-8')
            return df
        except UnicodeDecodeError:
            # Fall back to UTF-8-sig for files with BOM
            try:
                df = pd.read_csv(file_path, encoding='utf-8-sig')
                return df
            except UnicodeDecodeError as e:
                raise UnicodeDecodeError(
                    e.encoding,
                    e.object,
                    e.start,
                    e.end,
                    f"Encoding error in {file_path}. Please ensure the file is UTF-8 encoded."
                )
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}. Please check the configuration.")
        except pd.errors.ParserError:
            raise pd.errors.ParserError(f"Unable to parse {file_path}. Please ensure the file format is correct.")
    
    def load_cid_mapping(self, file_path: str, sheet_name: str = "Sheet1") -> pd.DataFrame:
        """
        Load CID mapping data from an Excel file.
        
        Args:
            file_path: Path to the CID mapping Excel file
            sheet_name: Name of the sheet to read (default: "Sheet1")
            
        Returns:
            DataFrame containing CID mapping data
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            Exception: If the file cannot be read or sheet doesn't exist
        """
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
            return df
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}. Please check the configuration.")
        except Exception as e:
            raise Exception(f"Unable to read Excel file {file_path}: {str(e)}")
    
    def validate_required_columns(
        self, 
        df: pd.DataFrame, 
        required_columns: List[str], 
        file_name: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that all required columns are present in the DataFrame.
        
        Args:
            df: DataFrame to validate
            required_columns: List of column names that must be present
            file_name: Name of the file being validated (for error messages)
            
        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if all columns are present, False otherwise
            - error_message: Description of missing columns, or None if valid
        """
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            missing_str = ", ".join(missing_columns)
            return False, f"Missing required columns in {file_name}: {missing_str}"
        
        return True, None
