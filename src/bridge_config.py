"""
Configuration management for the Bridge Plan Generator.

This module handles loading, saving, and validating configuration settings
including file paths, suppression coefficients, and event parameters.
"""

import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional


@dataclass
class Config:
    """Configuration settings for the Bridge Plan Generator."""
    
    # File paths
    sourcing_data_path: str = ""
    target_data_path: str = ""
    suppression_benchmark_path: str = ""
    cid_mapping_path: str = ""
    cid_mapping_sheet: str = "Sheet1"
    
    # Suppression coefficients (default values from design doc)
    suppression_coefficients: Dict[str, float] = field(default_factory=lambda: {
        "No suppression": 0.5343,
        "OOS": 0.2807,
        "VRP missing": 0.0963,
        "Price Error": 0.2750,
        "Others": 0.1801
    })
    
    # Event participation flags in order of recency (most recent first)
    event_flag_priority: List[str] = field(default_factory=lambda: [
        "sshve1_flag",
        "fy26_mde2_flag",
        "nys26_flag",
        "bf25_flag",
        "fy25_mde4_flag",
        "t365_flag"
    ])
    
    @classmethod
    def load_from_file(cls, config_path: str) -> 'Config':
        """
        Load configuration from a JSON file.
        
        Args:
            config_path: Path to the configuration JSON file
            
        Returns:
            Config object with loaded settings
            
        Raises:
            FileNotFoundError: If the config file doesn't exist
            json.JSONDecodeError: If the config file is not valid JSON
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls(**data)
    
    def save_to_file(self, config_path: str) -> None:
        """
        Save configuration to a JSON file.
        
        Args:
            config_path: Path where the configuration should be saved
        """
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate that all required configuration parameters are present and valid.
        
        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if configuration is valid, False otherwise
            - error_message: Description of validation error, or None if valid
        """
        # Check required file paths
        required_paths = {
            'sourcing_data_path': self.sourcing_data_path,
            'target_data_path': self.target_data_path,
            'suppression_benchmark_path': self.suppression_benchmark_path,
            'cid_mapping_path': self.cid_mapping_path
        }
        
        for param_name, param_value in required_paths.items():
            if not param_value or not isinstance(param_value, str):
                return False, f"Missing required configuration: {param_name}"
        
        # Check cid_mapping_sheet
        if not self.cid_mapping_sheet or not isinstance(self.cid_mapping_sheet, str):
            return False, "Missing required configuration: cid_mapping_sheet"
        
        # Check suppression coefficients
        if not self.suppression_coefficients:
            return False, "Missing required configuration: suppression_coefficients"
        
        required_categories = ["No suppression", "OOS", "VRP missing", "Price Error", "Others"]
        for category in required_categories:
            if category not in self.suppression_coefficients:
                return False, f"Missing suppression coefficient for category: {category}"
            
            coefficient = self.suppression_coefficients[category]
            if not isinstance(coefficient, (int, float)) or coefficient < 0 or coefficient > 1:
                return False, f"Invalid suppression coefficient for {category}: {coefficient}. Must be between 0 and 1."
        
        # Check event flag priority
        if not self.event_flag_priority or not isinstance(self.event_flag_priority, list):
            return False, "Missing required configuration: event_flag_priority"
        
        return True, None
