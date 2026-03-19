"""
Sourcing Plan Generator for the Bridge Plan Generator.

This module generates sourcing-based bridge plans by identifying high-potential
ASINs for event recruitment based on historical participation and sales performance.
"""

import pandas as pd
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ASINRecommendation:
    """Recommendation for a specific ASIN to include in sourcing plan."""
    asin: str
    cid: str
    expected_contribution: float
    participation_score: float
    t30_gms_bau: float
    rationale: str


@dataclass
class SourcingPlan:
    """Complete sourcing-based bridge plan."""
    total_gap: float
    gap_closable_by_sourcing: float
    recommended_asins: List[ASINRecommendation]
    remaining_gap: float


class SourcingPlanGenerator:
    """
    Generates sourcing-based bridge plans to close sales gaps.
    
    The generator identifies high-potential ASINs for event recruitment by
    considering both sales performance (T30 GMS BAU) and event participation
    history (participation score).
    """
    
    def __init__(self, participation_score_calculator=None):
        """
        Initialize the sourcing plan generator.
        
        Args:
            participation_score_calculator: Optional callable that takes a dict of flags
                                          and returns a participation score (0-1)
        """
        self.participation_score_calculator = participation_score_calculator
    
    def rank_asins_by_potential(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Rank ASINs by their sourcing potential considering both T30 GMS BAU and participation score.
        
        Higher T30 GMS BAU and higher participation scores result in higher rankings.
        The ranking uses a composite score that weights both factors.
        
        Args:
            df: DataFrame with columns: ASIN, CID, t30_gms_bau, participation_score
            
        Returns:
            DataFrame sorted by potential (highest first) with added 'potential_score' column
            
        Raises:
            KeyError: If required columns are missing
        """
        required_cols = ['ASIN', 'CID', 't30_gms_bau', 'participation_score']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise KeyError(f"Missing required columns: {', '.join(missing)}")
        
        result = df.copy()
        
        # Handle missing or invalid values
        result['t30_gms_bau'] = pd.to_numeric(result['t30_gms_bau'], errors='coerce').fillna(0)
        result['participation_score'] = pd.to_numeric(result['participation_score'], errors='coerce').fillna(0)
        
        # Normalize t30_gms_bau to 0-1 range for fair comparison with participation_score
        max_gms = result['t30_gms_bau'].max()
        if max_gms > 0:
            normalized_gms = result['t30_gms_bau'] / max_gms
        else:
            normalized_gms = 0
        
        # Composite score: 60% weight on GMS (sales potential), 40% weight on participation score
        result['potential_score'] = 0.6 * normalized_gms + 0.4 * result['participation_score']
        
        # Sort by potential score (highest first), then by t30_gms_bau as tiebreaker
        result = result.sort_values(
            by=['potential_score', 't30_gms_bau'],
            ascending=[False, False]
        ).reset_index(drop=True)
        
        return result
    
    def calculate_expected_contribution(
        self,
        asins: pd.DataFrame,
        gap: float
    ) -> List[ASINRecommendation]:
        """
        Calculate expected contribution of each ASIN to closing the gap.
        
        The expected contribution is based on the ASIN's T30 GMS BAU weighted by
        its participation score (likelihood of actually participating).
        
        Args:
            asins: DataFrame with ranked ASINs (from rank_asins_by_potential)
            gap: The sales gap to close
            
        Returns:
            List of ASINRecommendation objects with expected contributions
        """
        recommendations = []
        
        for _, row in asins.iterrows():
            # Expected contribution = T30 GMS BAU × participation score
            # This accounts for the likelihood that the ASIN will actually participate
            expected_contribution = row['t30_gms_bau'] * row['participation_score']
            
            # Generate rationale based on the ASIN's characteristics
            rationale = self._generate_rationale(
                row['t30_gms_bau'],
                row['participation_score'],
                row.get('potential_score', 0)
            )
            
            recommendation = ASINRecommendation(
                asin=row['ASIN'],
                cid=row['CID'],
                expected_contribution=expected_contribution,
                participation_score=row['participation_score'],
                t30_gms_bau=row['t30_gms_bau'],
                rationale=rationale
            )
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def generate_plan(
        self,
        gap: float,
        sourcing_data: pd.DataFrame
    ) -> SourcingPlan:
        """
        Generate a complete sourcing-based bridge plan.
        
        Args:
            gap: The sales gap to close (T30 GMS Target - T30 GMS BAU)
            sourcing_data: DataFrame with columns: ASIN, CID, t30_gms_bau, participation_score
            
        Returns:
            SourcingPlan with recommendations and remaining gap calculation
            
        Raises:
            ValueError: If gap is negative or sourcing_data is empty
        """
        if gap < 0:
            raise ValueError(f"Gap cannot be negative: {gap}")
        
        if sourcing_data.empty:
            return SourcingPlan(
                total_gap=gap,
                gap_closable_by_sourcing=0.0,
                recommended_asins=[],
                remaining_gap=gap
            )
        
        # Rank ASINs by potential
        ranked_asins = self.rank_asins_by_potential(sourcing_data)
        
        # Calculate expected contributions
        all_recommendations = self.calculate_expected_contribution(ranked_asins, gap)
        
        # Select ASINs until gap is closed or we run out of candidates
        selected_recommendations = []
        cumulative_contribution = 0.0
        
        for recommendation in all_recommendations:
            if cumulative_contribution >= gap:
                break
            
            selected_recommendations.append(recommendation)
            cumulative_contribution += recommendation.expected_contribution
        
        # Calculate remaining gap
        remaining_gap = max(0.0, gap - cumulative_contribution)
        
        return SourcingPlan(
            total_gap=gap,
            gap_closable_by_sourcing=cumulative_contribution,
            recommended_asins=selected_recommendations,
            remaining_gap=remaining_gap
        )
    
    def _generate_rationale(
        self,
        t30_gms_bau: float,
        participation_score: float,
        potential_score: float
    ) -> str:
        """
        Generate a human-readable rationale for why an ASIN is recommended.
        
        Args:
            t30_gms_bau: The ASIN's T30 GMS BAU value
            participation_score: The ASIN's participation score (0-1)
            potential_score: The ASIN's composite potential score (0-1)
            
        Returns:
            Rationale string
        """
        # Categorize participation likelihood
        if participation_score >= 0.7:
            participation_desc = "very high"
        elif participation_score >= 0.5:
            participation_desc = "high"
        elif participation_score >= 0.3:
            participation_desc = "moderate"
        else:
            participation_desc = "low"
        
        # Categorize sales value
        if t30_gms_bau >= 100000:
            value_desc = "very high"
        elif t30_gms_bau >= 50000:
            value_desc = "high"
        elif t30_gms_bau >= 10000:
            value_desc = "moderate"
        else:
            value_desc = "low"
        
        return f"{participation_desc} participation likelihood, {value_desc} sales value"
