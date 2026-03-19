"""
Unit tests for bridge plan data models.
"""

import pytest
from src.bridge_models import (
    ASINData,
    CIDData,
    ASINRecommendation,
    SuppressionOpportunity,
    SourcingPlan,
    SuppressionPlan,
    BridgePlan,
    HierarchyMap
)


def test_asin_data_creation():
    """Test creating an ASINData instance."""
    asin = ASINData(
        asin="B001",
        cid="C001",
        t30_gms_bau=1000.0,
        event_flags={"sshve1_flag": "Y", "bf25_flag": "N"},
        participation_score=0.8,
        suppression_category=1
    )
    
    assert asin.asin == "B001"
    assert asin.cid == "C001"
    assert asin.t30_gms_bau == 1000.0
    assert asin.event_flags["sshve1_flag"] == "Y"
    assert asin.participation_score == 0.8
    assert asin.suppression_category == 1


def test_cid_data_creation():
    """Test creating a CIDData instance."""
    cid = CIDData(
        cid="C001",
        alias="A001",
        manager="M001",
        team="T001",
        t30_gms_bau=5000.0,
        t30_gms_target=6000.0,
        gap=1000.0,
        current_suppression={"No suppression": 50.0, "OOS": 30.0},
        asins=[]
    )
    
    assert cid.cid == "C001"
    assert cid.alias == "A001"
    assert cid.gap == 1000.0
    assert len(cid.asins) == 0


def test_bridge_plan_creation():
    """Test creating a BridgePlan instance."""
    plan = BridgePlan(
        pattern_name="Sourcing-Focused",
        aggregation_level="CID",
        entity_id="C001",
        current_t30_gms=5000.0,
        target_t30_gms=6000.0,
        total_gap=1000.0,
        sourcing_plan=None,
        suppression_plan=None,
        feasibility_score=0.75,
        recommendations=["Recruit high-potential ASINs"]
    )
    
    assert plan.pattern_name == "Sourcing-Focused"
    assert plan.total_gap == 1000.0
    assert plan.feasibility_score == 0.75
    assert len(plan.recommendations) == 1


def test_hierarchy_map_creation():
    """Test creating a HierarchyMap instance."""
    hierarchy = HierarchyMap(
        cid_to_alias={"C001": "A001", "C002": "A001"},
        alias_to_manager={"A001": "M001"},
        manager_to_team={"M001": "T001"}
    )
    
    assert hierarchy.cid_to_alias["C001"] == "A001"
    assert hierarchy.alias_to_manager["A001"] == "M001"
    assert hierarchy.manager_to_team["M001"] == "T001"


def test_sourcing_plan_with_recommendations():
    """Test creating a SourcingPlan with recommendations."""
    recommendations = [
        ASINRecommendation(
            asin="B001",
            cid="C001",
            expected_contribution=500.0,
            participation_score=0.9,
            rationale="High participation history"
        )
    ]
    
    plan = SourcingPlan(
        total_gap=1000.0,
        gap_closable_by_sourcing=500.0,
        recommended_asins=recommendations,
        remaining_gap=500.0
    )
    
    assert plan.total_gap == 1000.0
    assert plan.gap_closable_by_sourcing == 500.0
    assert len(plan.recommended_asins) == 1
    assert plan.remaining_gap == 500.0


def test_suppression_plan_with_opportunities():
    """Test creating a SuppressionPlan with opportunities."""
    opportunities = [
        SuppressionOpportunity(
            category="Price Error",
            current_percentage=15.0,
            target_percentage=10.0,
            expected_impact=300.0,
            recommended_actions=["Fix pricing for top 20 ASINs"]
        )
    ]
    
    plan = SuppressionPlan(
        total_gap=1000.0,
        gap_closable_by_suppression=300.0,
        opportunities=opportunities,
        remaining_gap=700.0
    )
    
    assert plan.total_gap == 1000.0
    assert plan.gap_closable_by_suppression == 300.0
    assert len(plan.opportunities) == 1
    assert plan.remaining_gap == 700.0
