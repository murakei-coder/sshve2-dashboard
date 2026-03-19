"""
Tests for the PromotionOPSCalculator class.

This module contains unit tests for the Promotion OPS calculation functionality.
"""

import pytest
from src.bridge_plan_generator.promotion_ops_calculator import PromotionOPSCalculator


class TestPromotionOPSCalculator:
    """Test suite for PromotionOPSCalculator."""
    
    @pytest.fixture
    def default_coefficients(self):
        """Default suppression coefficients from the design document."""
        return {
            "No suppression": 0.5343,
            "OOS": 0.2807,
            "VRP missing": 0.0963,
            "Price Error": 0.2750,
            "Others": 0.1801
        }
    
    @pytest.fixture
    def calculator(self, default_coefficients):
        """Create a calculator with default coefficients."""
        return PromotionOPSCalculator(default_coefficients)
    
    def test_calculate_promotion_ops_target_basic(self, calculator):
        """Test basic Promotion OPS Target calculation."""
        t30_gms_target = 1000.0
        benchmark_percentages = {
            "No suppression": 50.0,
            "OOS": 20.0,
            "VRP missing": 10.0,
            "Price Error": 15.0,
            "Others": 5.0
        }
        
        # Expected: 1000 * (0.50*0.5343 + 0.20*0.2807 + 0.10*0.0963 + 0.15*0.2750 + 0.05*0.1801)
        # = 1000 * (0.26715 + 0.05614 + 0.00963 + 0.04125 + 0.009005)
        # = 1000 * 0.383175
        # = 383.175
        expected = 383.175
        result = calculator.calculate_promotion_ops_target(t30_gms_target, benchmark_percentages)
        
        assert abs(result - expected) < 0.01, f"Expected {expected}, got {result}"
    
    def test_calculate_promotion_ops_target_zero_target(self, calculator):
        """Test Promotion OPS Target calculation with zero target."""
        t30_gms_target = 0.0
        benchmark_percentages = {
            "No suppression": 50.0,
            "OOS": 20.0,
            "VRP missing": 10.0,
            "Price Error": 15.0,
            "Others": 5.0
        }
        
        result = calculator.calculate_promotion_ops_target(t30_gms_target, benchmark_percentages)
        assert result == 0.0
    
    def test_calculate_promotion_ops_target_all_no_suppression(self, calculator):
        """Test Promotion OPS Target with 100% no suppression."""
        t30_gms_target = 1000.0
        benchmark_percentages = {
            "No suppression": 100.0,
            "OOS": 0.0,
            "VRP missing": 0.0,
            "Price Error": 0.0,
            "Others": 0.0
        }
        
        # Expected: 1000 * (1.0 * 0.5343) = 534.3
        expected = 534.3
        result = calculator.calculate_promotion_ops_target(t30_gms_target, benchmark_percentages)
        
        assert abs(result - expected) < 0.01
    
    def test_calculate_promotion_ops_target_missing_category(self, calculator):
        """Test Promotion OPS Target with missing category (should use 0.0 coefficient)."""
        t30_gms_target = 1000.0
        benchmark_percentages = {
            "No suppression": 50.0,
            "Unknown Category": 50.0  # Not in coefficients
        }
        
        # Expected: 1000 * (0.50 * 0.5343 + 0.50 * 0.0) = 267.15
        expected = 267.15
        result = calculator.calculate_promotion_ops_target(t30_gms_target, benchmark_percentages)
        
        assert abs(result - expected) < 0.01
    
    def test_calculate_current_promotion_ops_basic(self, calculator):
        """Test basic current Promotion OPS calculation."""
        t30_gms_bau = 800.0
        current_percentages = {
            "No suppression": 40.0,
            "OOS": 30.0,
            "VRP missing": 10.0,
            "Price Error": 15.0,
            "Others": 5.0
        }
        
        # Expected: 800 * (0.40*0.5343 + 0.30*0.2807 + 0.10*0.0963 + 0.15*0.2750 + 0.05*0.1801)
        # = 800 * (0.21372 + 0.08421 + 0.00963 + 0.04125 + 0.009005)
        # = 800 * 0.357815
        # = 286.252
        expected = 286.252
        result = calculator.calculate_current_promotion_ops(t30_gms_bau, current_percentages)
        
        assert abs(result - expected) < 0.01, f"Expected {expected}, got {result}"
    
    def test_calculate_current_promotion_ops_zero_bau(self, calculator):
        """Test current Promotion OPS calculation with zero BAU."""
        t30_gms_bau = 0.0
        current_percentages = {
            "No suppression": 40.0,
            "OOS": 30.0,
            "VRP missing": 10.0,
            "Price Error": 15.0,
            "Others": 5.0
        }
        
        result = calculator.calculate_current_promotion_ops(t30_gms_bau, current_percentages)
        assert result == 0.0
    
    def test_calculate_current_promotion_ops_all_suppressed(self, calculator):
        """Test current Promotion OPS with 100% OOS (worst case)."""
        t30_gms_bau = 1000.0
        current_percentages = {
            "No suppression": 0.0,
            "OOS": 100.0,
            "VRP missing": 0.0,
            "Price Error": 0.0,
            "Others": 0.0
        }
        
        # Expected: 1000 * (1.0 * 0.2807) = 280.7
        expected = 280.7
        result = calculator.calculate_current_promotion_ops(t30_gms_bau, current_percentages)
        
        assert abs(result - expected) < 0.01
    
    def test_custom_coefficients(self):
        """Test calculator with custom coefficients."""
        custom_coefficients = {
            "No suppression": 0.6,
            "OOS": 0.3,
            "VRP missing": 0.1,
            "Price Error": 0.2,
            "Others": 0.15
        }
        calculator = PromotionOPSCalculator(custom_coefficients)
        
        t30_gms_target = 1000.0
        benchmark_percentages = {
            "No suppression": 50.0,
            "OOS": 50.0
        }
        
        # Expected: 1000 * (0.50 * 0.6 + 0.50 * 0.3) = 1000 * 0.45 = 450.0
        expected = 450.0
        result = calculator.calculate_promotion_ops_target(t30_gms_target, benchmark_percentages)
        
        assert abs(result - expected) < 0.01
    
    def test_coefficient_update_propagation(self, default_coefficients):
        """Test that updating coefficients affects calculations."""
        # Create calculator with initial coefficients
        calculator1 = PromotionOPSCalculator(default_coefficients)
        
        t30_gms_target = 1000.0
        benchmark_percentages = {"No suppression": 100.0}
        
        result1 = calculator1.calculate_promotion_ops_target(t30_gms_target, benchmark_percentages)
        
        # Create new calculator with updated coefficients
        updated_coefficients = default_coefficients.copy()
        updated_coefficients["No suppression"] = 0.7
        calculator2 = PromotionOPSCalculator(updated_coefficients)
        
        result2 = calculator2.calculate_promotion_ops_target(t30_gms_target, benchmark_percentages)
        
        # Results should be different
        assert result1 != result2
        assert abs(result1 - 534.3) < 0.01  # Original coefficient
        assert abs(result2 - 700.0) < 0.01  # Updated coefficient
    
    def test_empty_percentages(self, calculator):
        """Test calculation with empty percentages dictionary."""
        t30_gms_target = 1000.0
        benchmark_percentages = {}
        
        result = calculator.calculate_promotion_ops_target(t30_gms_target, benchmark_percentages)
        assert result == 0.0
    
    def test_large_values(self, calculator):
        """Test calculation with large values."""
        t30_gms_target = 1_000_000.0
        benchmark_percentages = {
            "No suppression": 50.0,
            "OOS": 20.0,
            "VRP missing": 10.0,
            "Price Error": 15.0,
            "Others": 5.0
        }
        
        result = calculator.calculate_promotion_ops_target(t30_gms_target, benchmark_percentages)
        
        # Should scale linearly
        assert result > 0
        assert result < t30_gms_target  # Should be less than target due to coefficients < 1
    
    def test_formula_consistency(self, calculator):
        """Test that target and current calculations use the same formula."""
        value = 1000.0
        percentages = {
            "No suppression": 50.0,
            "OOS": 20.0,
            "VRP missing": 10.0,
            "Price Error": 15.0,
            "Others": 5.0
        }
        
        # Both methods should produce the same result with the same inputs
        result_target = calculator.calculate_promotion_ops_target(value, percentages)
        result_current = calculator.calculate_current_promotion_ops(value, percentages)
        
        assert abs(result_target - result_current) < 0.0001
