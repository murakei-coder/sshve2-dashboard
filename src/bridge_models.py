"""
Core data models for the Bridge Plan Generator.

This module defines the data structures used throughout the application
for representing ASINs, CIDs, bridge plans, and related entities.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ASINData:
    """Represents data for a single ASIN (product)."""
    asin: str
    cid: str
    t30_gms_bau: float
    event_flags: Dict[str, str]  # flag_name -> 'Y' or 'N'
    participation_score: float
    suppression_category: int  # 1-5


@dataclass
class CIDData:
    """Represents aggregated data for a single CID (seller)."""
    cid: str
    alias: str
    manager: str
    team: str
    t30_gms_bau: float
    t30_gms_target: float
    gap: float
    current_suppression: Dict[str, float]  # category -> percentage
    asins: List[ASINData] = field(default_factory=list)


@dataclass
class ASINRecommendation:
    """Represents a sourcing recommendation for a specific ASIN."""
    asin: str
    cid: str
    expected_contribution: float
    participation_score: float
    rationale: str


@dataclass
class SuppressionOpportunity:
    """Represents an opportunity to improve sales by reducing suppression."""
    category: str
    current_percentage: float
    target_percentage: float
    expected_impact: float
    recommended_actions: List[str]


@dataclass
class SourcingPlan:
    """Represents a sourcing-based bridge plan."""
    total_gap: float
    gap_closable_by_sourcing: float
    recommended_asins: List[ASINRecommendation]
    remaining_gap: float


@dataclass
class SuppressionPlan:
    """Represents a suppression-based bridge plan."""
    total_gap: float
    gap_closable_by_suppression: float
    opportunities: List[SuppressionOpportunity]
    remaining_gap: float


@dataclass
class BridgePlan:
    """Represents a complete bridge plan with sourcing and/or suppression strategies."""
    pattern_name: str  # "Sourcing-Focused", "Suppression-Focused", "Balanced"
    aggregation_level: str  # "CID", "Alias", "Mgr", "Team"
    entity_id: str  # The specific CID, Alias, Mgr, or Team
    current_t30_gms: float
    target_t30_gms: float
    total_gap: float
    sourcing_plan: Optional[SourcingPlan]
    suppression_plan: Optional[SuppressionPlan]
    feasibility_score: float
    recommendations: List[str]


@dataclass
class HierarchyMap:
    """Represents the organizational hierarchy mapping."""
    cid_to_alias: Dict[str, str]
    alias_to_manager: Dict[str, str]
    manager_to_team: Dict[str, str]
