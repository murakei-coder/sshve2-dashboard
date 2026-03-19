"""
Bridge plan orchestrator module for the Bridge Plan Generator.

This module orchestrates the generation of multiple bridge plan patterns
(Sourcing-Focused, Suppression-Focused, Balanced) and calculates feasibility scores.
"""

import pandas as pd
from typing import List, Dict, Optional
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_path = Path(__file__).parent.parent
if str(parent_path) not in sys.path:
    sys.path.insert(0, str(parent_path))

import bridge_models
from bridge_plan_generator import sourcing_plan_generator
from bridge_plan_generator import suppression_plan_generator


class BridgePlanOrchestrator:
    """Orchestrates generation of multiple bridge plan patterns."""
    
    def __init__(
        self, 
        sourcing_generator: 'sourcing_plan_generator.SourcingPlanGenerator',
        suppression_generator: 'suppression_plan_generator.SuppressionPlanGenerator'
    ):
        """
        Initialize the bridge plan orchestrator.
        
        Args:
            sourcing_generator: SourcingPlanGenerator instance
            suppression_generator: SuppressionPlanGenerator instance
        """
        self.sourcing_generator = sourcing_generator
        self.suppression_generator = suppression_generator
    
    def generate_all_patterns(
        self,
        entity_id: str,
        aggregation_level: str,
        current_t30_gms: float,
        target_t30_gms: float,
        gap: float,
        sourcing_data: pd.DataFrame,
        current_suppression: Dict[str, float],
        benchmark_suppression: Dict[str, float]
    ) -> List['bridge_models.BridgePlan']:
        """
        Generate all feasible bridge plan patterns for the given entity.
        
        Args:
            entity_id: The specific CID, Alias, Mgr, or Team identifier
            aggregation_level: "CID", "Alias", "Mgr", or "Team"
            current_t30_gms: Current T30 GMS BAU value
            target_t30_gms: T30 GMS Target value
            gap: Sales gap to close (target - current)
            sourcing_data: DataFrame with ASIN sourcing candidates
            current_suppression: Current suppression percentages by category
            benchmark_suppression: Benchmark suppression percentages by category
            
        Returns:
            List of BridgePlan objects (1-3 patterns depending on feasibility)
        """
        patterns = []
        
        # Generate Pattern 1: Sourcing-Focused
        sourcing_focused = self.generate_sourcing_focused_pattern(
            entity_id, aggregation_level, current_t30_gms, target_t30_gms, gap, sourcing_data
        )
        if sourcing_focused:
            patterns.append(sourcing_focused)
        
        # Generate Pattern 2: Suppression-Focused
        suppression_focused = self.generate_suppression_focused_pattern(
            entity_id, aggregation_level, current_t30_gms, target_t30_gms, gap,
            current_suppression, benchmark_suppression, target_t30_gms
        )
        if suppression_focused:
            patterns.append(suppression_focused)
        
        # Generate Pattern 3: Balanced (if both sourcing and suppression are feasible)
        if len(patterns) >= 2:
            balanced = self.generate_balanced_pattern(
                entity_id, aggregation_level, current_t30_gms, target_t30_gms, gap,
                sourcing_data, current_suppression, benchmark_suppression, target_t30_gms
            )
            if balanced:
                patterns.append(balanced)
        
        return patterns
    
    def generate_sourcing_focused_pattern(
        self,
        entity_id: str,
        aggregation_level: str,
        current_t30_gms: float,
        target_t30_gms: float,
        gap: float,
        sourcing_data: pd.DataFrame
    ) -> Optional['bridge_models.BridgePlan']:
        """
        Generate a sourcing-focused bridge plan (Pattern 1).
        
        Achieves target primarily through recruiting high-potential ASINs.
        
        Args:
            entity_id: Entity identifier
            aggregation_level: Aggregation level
            current_t30_gms: Current T30 GMS BAU
            target_t30_gms: T30 GMS Target
            gap: Sales gap
            sourcing_data: ASIN sourcing candidates
            
        Returns:
            BridgePlan or None if not feasible
        """
        # Generate sourcing plan
        sourcing_plan = self.sourcing_generator.generate_plan(gap, sourcing_data)
        
        # Check if sourcing can close at least 50% of gap
        if sourcing_plan.gap_closable_by_sourcing < gap * 0.5:
            return None  # Not feasible as sourcing-focused
        
        # Calculate feasibility score (0-1)
        feasibility = min(1.0, sourcing_plan.gap_closable_by_sourcing / gap)
        
        # Generate recommendations
        recommendations = [
            f"Focus on sourcing high-potential ASINs to close {sourcing_plan.gap_closable_by_sourcing:.0f} of {gap:.0f} gap",
            f"Recruit {len(sourcing_plan.recommended_asins)} ASINs with strong participation history",
            f"Confidence level: {feasibility * 100:.0f}%"
        ]
        
        if sourcing_plan.remaining_gap > 0:
            recommendations.append(f"Remaining gap: {sourcing_plan.remaining_gap:.0f} - consider supplementing with suppression optimization")
        
        return bridge_models.BridgePlan(
            pattern_name="Sourcing-Focused",
            aggregation_level=aggregation_level,
            entity_id=entity_id,
            current_t30_gms=current_t30_gms,
            target_t30_gms=target_t30_gms,
            total_gap=gap,
            sourcing_plan=sourcing_plan,
            suppression_plan=None,
            feasibility_score=feasibility,
            recommendations=recommendations
        )
    
    def generate_suppression_focused_pattern(
        self,
        entity_id: str,
        aggregation_level: str,
        current_t30_gms: float,
        target_t30_gms: float,
        gap: float,
        current_suppression: Dict[str, float],
        benchmark_suppression: Dict[str, float],
        t30_gms_target: float
    ) -> Optional['bridge_models.BridgePlan']:
        """
        Generate a suppression-focused bridge plan (Pattern 2).
        
        Achieves target primarily through reducing suppression issues.
        
        Args:
            entity_id: Entity identifier
            aggregation_level: Aggregation level
            current_t30_gms: Current T30 GMS BAU
            target_t30_gms: T30 GMS Target
            gap: Sales gap
            current_suppression: Current suppression percentages
            benchmark_suppression: Benchmark suppression percentages
            t30_gms_target: T30 GMS Target for impact calculation
            
        Returns:
            BridgePlan or None if not feasible
        """
        # Generate suppression plan
        suppression_plan = self.suppression_generator.generate_plan(
            gap, current_suppression, benchmark_suppression, t30_gms_target
        )
        
        # Check if suppression can close at least 50% of gap
        if suppression_plan.gap_closable_by_suppression < gap * 0.5:
            return None  # Not feasible as suppression-focused
        
        # Calculate feasibility score (0-1)
        feasibility = min(1.0, suppression_plan.gap_closable_by_suppression / gap)
        
        # Generate recommendations
        recommendations = [
            f"Focus on reducing suppression issues to close {suppression_plan.gap_closable_by_suppression:.0f} of {gap:.0f} gap",
            f"Address {len(suppression_plan.opportunities)} suppression categories",
            f"Confidence level: {feasibility * 100:.0f}%"
        ]
        
        # Add top opportunities
        for opp in suppression_plan.opportunities[:2]:  # Top 2
            recommendations.append(f"Priority: {opp.recommended_actions[0]}")
        
        if suppression_plan.remaining_gap > 0:
            recommendations.append(f"Remaining gap: {suppression_plan.remaining_gap:.0f} - consider supplementing with sourcing")
        
        return bridge_models.BridgePlan(
            pattern_name="Suppression-Focused",
            aggregation_level=aggregation_level,
            entity_id=entity_id,
            current_t30_gms=current_t30_gms,
            target_t30_gms=target_t30_gms,
            total_gap=gap,
            sourcing_plan=None,
            suppression_plan=suppression_plan,
            feasibility_score=feasibility,
            recommendations=recommendations
        )
    
    def generate_balanced_pattern(
        self,
        entity_id: str,
        aggregation_level: str,
        current_t30_gms: float,
        target_t30_gms: float,
        gap: float,
        sourcing_data: pd.DataFrame,
        current_suppression: Dict[str, float],
        benchmark_suppression: Dict[str, float],
        t30_gms_target: float
    ) -> Optional['bridge_models.BridgePlan']:
        """
        Generate a balanced bridge plan (Pattern 3).
        
        Achieves target through a combination of sourcing and suppression optimization.
        
        Args:
            entity_id: Entity identifier
            aggregation_level: Aggregation level
            current_t30_gms: Current T30 GMS BAU
            target_t30_gms: T30 GMS Target
            gap: Sales gap
            sourcing_data: ASIN sourcing candidates
            current_suppression: Current suppression percentages
            benchmark_suppression: Benchmark suppression percentages
            t30_gms_target: T30 GMS Target for impact calculation
            
        Returns:
            BridgePlan or None if not feasible
        """
        # Split gap 50/50 between sourcing and suppression
        sourcing_gap = gap * 0.5
        suppression_gap = gap * 0.5
        
        # Generate sourcing plan for half the gap
        sourcing_plan = self.sourcing_generator.generate_plan(sourcing_gap, sourcing_data)
        
        # Generate suppression plan for half the gap
        suppression_plan = self.suppression_generator.generate_plan(
            suppression_gap, current_suppression, benchmark_suppression, t30_gms_target
        )
        
        # Calculate total gap closure
        total_closable = sourcing_plan.gap_closable_by_sourcing + suppression_plan.gap_closable_by_suppression
        remaining_gap = gap - total_closable
        
        # Check if balanced approach can close at least 70% of gap
        if total_closable < gap * 0.7:
            return None  # Not feasible as balanced
        
        # Calculate feasibility score
        feasibility = min(1.0, total_closable / gap)
        
        # Generate recommendations
        sourcing_pct = (sourcing_plan.gap_closable_by_sourcing / gap) * 100
        suppression_pct = (suppression_plan.gap_closable_by_suppression / gap) * 100
        
        recommendations = [
            f"Balanced approach: {sourcing_pct:.0f}% sourcing + {suppression_pct:.0f}% suppression",
            f"Recruit {len(sourcing_plan.recommended_asins)} ASINs (contributes {sourcing_plan.gap_closable_by_sourcing:.0f})",
            f"Address {len(suppression_plan.opportunities)} suppression issues (contributes {suppression_plan.gap_closable_by_suppression:.0f})",
            f"Confidence level: {feasibility * 100:.0f}%"
        ]
        
        if remaining_gap > 0:
            recommendations.append(f"Remaining gap: {remaining_gap:.0f}")
        
        return bridge_models.BridgePlan(
            pattern_name="Balanced",
            aggregation_level=aggregation_level,
            entity_id=entity_id,
            current_t30_gms=current_t30_gms,
            target_t30_gms=target_t30_gms,
            total_gap=gap,
            sourcing_plan=sourcing_plan,
            suppression_plan=suppression_plan,
            feasibility_score=feasibility,
            recommendations=recommendations
        )
