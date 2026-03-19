"""
Unit tests for bridge plan configuration management.
"""

import pytest
import json
import tempfile
import os
from src.bridge_config import Config


def test_config_creation_with_defaults():
    """Test creating a Config instance with default values."""
    config = Config()
    
    assert config.sourcing_data_path == ""
    assert config.cid_mapping_sheet == "Sheet1"
    assert "No suppression" in config.suppression_coefficients
    assert config.suppression_coefficients["No suppression"] == 0.5343
    assert len(config.event_flag_priority) == 6
    assert config.event_flag_priority[0] == "sshve1_flag"


def test_config_creation_with_custom_values():
    """Test creating a Config instance with custom values."""
    config = Config(
        sourcing_data_path="data/sourcing.csv",
        target_data_path="data/target.csv",
        suppression_benchmark_path="data/benchmark.csv",
        cid_mapping_path="data/mapping.xlsx"
    )
    
    assert config.sourcing_data_path == "data/sourcing.csv"
    assert config.target_data_path == "data/target.csv"


def test_config_validation_success():
    """Test validation of a valid configuration."""
    config = Config(
        sourcing_data_path="data/sourcing.csv",
        target_data_path="data/target.csv",
        suppression_benchmark_path="data/benchmark.csv",
        cid_mapping_path="data/mapping.xlsx"
    )
    
    is_valid, error_message = config.validate()
    assert is_valid is True
    assert error_message is None


def test_config_validation_missing_path():
    """Test validation fails when required path is missing."""
    config = Config(
        sourcing_data_path="",
        target_data_path="data/target.csv",
        suppression_benchmark_path="data/benchmark.csv",
        cid_mapping_path="data/mapping.xlsx"
    )
    
    is_valid, error_message = config.validate()
    assert is_valid is False
    assert "sourcing_data_path" in error_message


def test_config_validation_invalid_coefficient():
    """Test validation fails when coefficient is out of range."""
    config = Config(
        sourcing_data_path="data/sourcing.csv",
        target_data_path="data/target.csv",
        suppression_benchmark_path="data/benchmark.csv",
        cid_mapping_path="data/mapping.xlsx",
        suppression_coefficients={
            "No suppression": 1.5,  # Invalid: > 1
            "OOS": 0.2807,
            "VRP missing": 0.0963,
            "Price Error": 0.2750,
            "Others": 0.1801
        }
    )
    
    is_valid, error_message = config.validate()
    assert is_valid is False
    assert "No suppression" in error_message
    assert "between 0 and 1" in error_message


def test_config_validation_missing_coefficient():
    """Test validation fails when a required coefficient is missing."""
    config = Config(
        sourcing_data_path="data/sourcing.csv",
        target_data_path="data/target.csv",
        suppression_benchmark_path="data/benchmark.csv",
        cid_mapping_path="data/mapping.xlsx",
        suppression_coefficients={
            "No suppression": 0.5343,
            "OOS": 0.2807
            # Missing other coefficients
        }
    )
    
    is_valid, error_message = config.validate()
    assert is_valid is False
    assert "coefficient" in error_message.lower()


def test_config_save_and_load():
    """Test saving and loading configuration from file."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = f.name
    
    try:
        # Create and save config
        original_config = Config(
            sourcing_data_path="data/sourcing.csv",
            target_data_path="data/target.csv",
            suppression_benchmark_path="data/benchmark.csv",
            cid_mapping_path="data/mapping.xlsx",
            cid_mapping_sheet="TestSheet"
        )
        original_config.save_to_file(temp_path)
        
        # Load config
        loaded_config = Config.load_from_file(temp_path)
        
        # Verify all fields match
        assert loaded_config.sourcing_data_path == original_config.sourcing_data_path
        assert loaded_config.target_data_path == original_config.target_data_path
        assert loaded_config.suppression_benchmark_path == original_config.suppression_benchmark_path
        assert loaded_config.cid_mapping_path == original_config.cid_mapping_path
        assert loaded_config.cid_mapping_sheet == original_config.cid_mapping_sheet
        assert loaded_config.suppression_coefficients == original_config.suppression_coefficients
        assert loaded_config.event_flag_priority == original_config.event_flag_priority
        
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_config_load_nonexistent_file():
    """Test loading from a nonexistent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        Config.load_from_file("nonexistent_config.json")


def test_config_save_preserves_japanese_characters():
    """Test that saving and loading preserves Japanese characters."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8') as f:
        temp_path = f.name
    
    try:
        # Create config with Japanese path
        original_config = Config(
            sourcing_data_path="データ/ソーシング.csv",
            target_data_path="data/target.csv",
            suppression_benchmark_path="data/benchmark.csv",
            cid_mapping_path="data/mapping.xlsx"
        )
        original_config.save_to_file(temp_path)
        
        # Load and verify
        loaded_config = Config.load_from_file(temp_path)
        assert loaded_config.sourcing_data_path == "データ/ソーシング.csv"
        
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
