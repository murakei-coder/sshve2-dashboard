"""
Promotion OPS Calculator for the Bridge Plan Generator.

This module calculates Promotion OPS (Operational Sales) targets and current values
based on suppression benchmarks and configurable coefficients.
"""

from typing import Dict


class PromotionOPSCalculator:
    """
    Calculator for Promotion OPS targets and current values.
    
    The calculator uses a weighted formula that considers suppression category
    distributions and their corresponding coefficients to estimate promotional
    sales potential.
    """
    
    def __init__(self, coefficients: Dict[str, float]):
        """
        Initialize the calculator with suppression coefficients.
        
        Args:
            coefficients: Dictionary mapping suppression categories to their
                         coefficients (e.g., {"No suppression": 0.5343, ...})
        """
        self.coefficients = coefficients
    
    def calculate_promotion_ops_target(
        self,
        t30_gms_target: float,
        benchmark_percentages: Dict[str, float]
    ) -> float:
        """
        Calculate Promotion OPS Target based on benchmark suppression distribution.
        
        Formula:
        Promotion_OPS_Target = T30_GMS_Target × Σ(benchmark_% × coefficient)
        
        Args:
            t30_gms_target: The T30 GMS target value
            benchmark_percentages: Dictionary mapping suppression categories to
                                  their benchmark percentages (e.g., {"No suppression": 45.0, ...})
        
        Returns:
            The calculated Promotion OPS Target value
        """
        promotion_ops = 0.0
        
        for category, benchmark_pct in benchmark_percentages.items():
            coefficient = self.coefficients.get(category, 0.0)
            # Convert percentage to decimal (e.g., 45.0 -> 0.45)
            promotion_ops += t30_gms_target * (benchmark_pct / 100.0) * coefficient
        
        return promotion_ops
    
    def calculate_current_promotion_ops(
        self,
        t30_gms_bau: float,
        current_percentages: Dict[str, float]
    ) -> float:
        """
        Calculate current Promotion OPS based on current suppression distribution.
        
        Formula:
        Current_Promotion_OPS = T30_GMS_BAU × Σ(current_% × coefficient)
        
        Args:
            t30_gms_bau: The current T30 GMS BAU (Business As Usual) value
            current_percentages: Dictionary mapping suppression categories to
                                their current percentages (e.g., {"No suppression": 40.0, ...})
        
        Returns:
            The calculated current Promotion OPS value
        """
        promotion_ops = 0.0
        
        for category, current_pct in current_percentages.items():
            coefficient = self.coefficients.get(category, 0.0)
            # Convert percentage to decimal (e.g., 40.0 -> 0.40)
            promotion_ops += t30_gms_bau * (current_pct / 100.0) * coefficient
        
        return promotion_ops
