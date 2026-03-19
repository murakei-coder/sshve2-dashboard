"""
Suppression plan generator module for the Bridge Plan Generator.

This module generates suppression-based bridge plans by identifying opportunities
to improve sales through reducing operational issues (OOS, Price Error, VRP missing).
"""

import pandas as pd
from typing import Dict, List
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_path = Path(__file__).parent.parent
if str(parent_path) not in sys.path:
    sys.path.insert(0, str(parent_path))

import bridge_models


class SuppressionPlanGenerator:
    """Generates suppression-based bridge plans to close sales gaps."""
    
    def __init__(self, coefficients: Dict[str, float]):
        """
        Initialize the suppression plan generator.
        
        Args:
            coefficients: Dictionary mapping suppression categories to their sales impact coefficients
        """
        self.coefficients = coefficients
    
    def identify_improvement_opportunities(
        self, 
        current: Dict[str, float], 
        benchmark: Dict[str, float]
    ) -> List['bridge_models.SuppressionOpportunity']:
        """
        Identify suppression improvement opportunities by comparing current vs benchmark.
        
        Prioritizes reducing Price Error and increasing No suppression percentages.
        
        Args:
            current: Current suppression percentages by category
            benchmark: Benchmark suppression percentages by category
            
        Returns:
            List of SuppressionOpportunity objects, sorted by expected impact (highest first)
        """
        opportunities = []
        
        # Categories to improve (reduce these)
        reduce_categories = ["Price Error", "OOS", "VRP missing", "Others"]
        
        for category in reduce_categories:
            current_pct = current.get(category, 0.0)
            benchmark_pct = benchmark.get(category, 0.0)
            
            # If current is higher than benchmark, there's opportunity to reduce
            if current_pct > benchmark_pct:
                # Target is to match or beat benchmark
                target_pct = benchmark_pct
                reduction = current_pct - target_pct
                
                # Calculate expected impact: moving ASINs from this category to "No suppression"
                # Impact = reduction_percentage × (no_suppression_coef - current_category_coef)
                no_suppression_coef = self.coefficients.get("No suppression", 0.5343)
                category_coef = self.coefficients.get(category, 0.0)
                
                # Expected impact as a multiplier on T30 GMS Target
                impact_multiplier = (reduction / 100.0) * (no_suppression_coef - category_coef)
                
                # Generate recommended actions
                actions = self._generate_actions(category, current_pct, target_pct)
                
                opportunity = bridge_models.SuppressionOpportunity(
                    category=category,
                    current_percentage=current_pct,
                    target_percentage=target_pct,
                    expected_impact=impact_multiplier,
                    recommended_actions=actions
                )
                opportunities.append(opportunity)
        
        # Sort by expected impact (highest first)
        opportunities.sort(key=lambda x: x.expected_impact, reverse=True)
        
        return opportunities
    
    def _generate_actions(self, category: str, current_pct: float, target_pct: float) -> List[str]:
        """
        Generate specific recommended actions for reducing a suppression category.
        
        Args:
            category: Suppression category name
            current_pct: Current percentage
            target_pct: Target percentage
            
        Returns:
            List of actionable recommendations
        """
        reduction = current_pct - target_pct
        
        actions = []
        
        if category == "Price Error":
            actions.append(f"Reduce Price Error from {current_pct:.1f}% to {target_pct:.1f}%")
            actions.append("Review and fix pricing for ASINs with price errors")
            actions.append("Ensure prices are competitive and within event guidelines")
        elif category == "OOS":
            actions.append(f"Reduce OOS from {current_pct:.1f}% to {target_pct:.1f}%")
            actions.append("Work with sellers to improve inventory management")
            actions.append("Identify ASINs at risk of going OOS and proactively restock")
        elif category == "VRP missing":
            actions.append(f"Reduce VRP missing from {current_pct:.1f}% to {target_pct:.1f}%")
            actions.append("Ensure all ASINs have valid VRP (Vendor Retail Price) set")
            actions.append("Contact sellers to update missing VRP information")
        elif category == "Others":
            actions.append(f"Reduce Others from {current_pct:.1f}% to {target_pct:.1f}%")
            actions.append("Investigate and resolve miscellaneous suppression issues")
            actions.append("Review suppression logs for specific error details")
        
        return actions
    
    def calculate_impact_of_reduction(
        self, 
        category: str, 
        reduction_percentage: float, 
        t30_gms_target: float
    ) -> float:
        """
        Calculate the sales impact of reducing a suppression category by a given percentage.
        
        Args:
            category: Suppression category to reduce
            reduction_percentage: Percentage points to reduce (e.g., 5.0 for 5%)
            t30_gms_target: T30 GMS Target value
            
        Returns:
            Expected sales impact in absolute currency units
        """
        no_suppression_coef = self.coefficients.get("No suppression", 0.5343)
        category_coef = self.coefficients.get(category, 0.0)
        
        # Impact = T30_GMS_Target × reduction_percentage × (no_suppression_coef - category_coef)
        impact = t30_gms_target * (reduction_percentage / 100.0) * (no_suppression_coef - category_coef)
        
        return impact
    
    def generate_plan(
        self, 
        gap: float, 
        current_suppression: Dict[str, float], 
        benchmark: Dict[str, float],
        t30_gms_target: float
    ) -> 'bridge_models.SuppressionPlan':
        """
        Generate a suppression-based bridge plan to close the sales gap.
        
        Args:
            gap: Sales gap to close (target - current)
            current_suppression: Current suppression percentages by category
            benchmark: Benchmark suppression percentages by category
            t30_gms_target: T30 GMS Target value for impact calculation
            
        Returns:
            SuppressionPlan with opportunities and expected gap closure
        """
        # Identify improvement opportunities
        opportunities = self.identify_improvement_opportunities(current_suppression, benchmark)
        
        # Calculate total potential impact
        total_impact = 0.0
        for opp in opportunities:
            reduction = opp.current_percentage - opp.target_percentage
            impact = self.calculate_impact_of_reduction(opp.category, reduction, t30_gms_target)
            total_impact += impact
        
        # Determine how much of the gap can be closed
        gap_closable = min(total_impact, gap)
        remaining_gap = gap - gap_closable
        
        # Ensure recommended percentages sum to 100%
        self._validate_percentage_sum(current_suppression, opportunities)
        
        return bridge_models.SuppressionPlan(
            total_gap=gap,
            gap_closable_by_suppression=gap_closable,
            opportunities=opportunities,
            remaining_gap=remaining_gap
        )
    
    def _validate_percentage_sum(
        self, 
        current: Dict[str, float], 
        opportunities: List['bridge_models.SuppressionOpportunity']
    ) -> None:
        """
        Validate that recommended suppression percentages sum to 100%.
        
        Adjusts target percentages proportionally if they don't sum to 100%.
        
        Args:
            current: Current suppression percentages
            opportunities: List of improvement opportunities (modified in place)
        """
        # Build target distribution
        target_distribution = current.copy()
        
        # Apply all opportunity targets
        for opp in opportunities:
            target_distribution[opp.category] = opp.target_percentage
        
        # Calculate sum
        total = sum(target_distribution.values())
        
        # If not 100%, adjust proportionally
        if abs(total - 100.0) > 0.1:  # Allow 0.1% tolerance
            adjustment_factor = 100.0 / total
            
            # Adjust all target percentages
            for opp in opportunities:
                opp.target_percentage *= adjustment_factor
            
            # Adjust current distribution for categories not in opportunities
            for category in target_distribution:
                if category not in [opp.category for opp in opportunities]:
                    target_distribution[category] *= adjustment_factor
