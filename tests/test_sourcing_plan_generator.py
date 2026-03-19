"""
Tests for the SourcingPlanGenerator module.

This module contains unit tests for the sourcing plan generation functionality,
including ASIN ranking, contribution calculation, and plan generation.
"""

import pytest
import pandas as pd
from src.bridge_plan_generator.sourcing_plan_generator import (
    SourcingPlanGenerator,
    ASINRecommendation,
    SourcingPlan
)


class TestSourcingPlanGenerator:
    """Test suite for SourcingPlanGenerator class."""
    
    @pytest.fixture
    def generator(self):
        """Create a SourcingPlanGenerator instance for testing."""
        return SourcingPlanGenerator()
    
    @pytest.fixture
    def sample_sourcing_data(self):
        """Create sample sourcing data for testing."""
        return pd.DataFrame({
            'ASIN': ['A001', 'A002', 'A003', 'A004', 'A005'],
            'CID': ['C001', 'C001', 'C002', 'C002', 'C003'],
            't30_gms_bau': [50000, 30000, 80000, 20000, 10000],
            'participation_score': [0.8, 0.5, 0.9, 0.3, 0.1]
        })
    
    def test_rank_asins_by_potential_basic(self, generator, sample_sourcing_data):
        """Test basic ASIN ranking functionality."""
        ranked = generator.rank_asins_by_potential(sample_sourcing_data)
        
        # Check that result has potential_score column
        assert 'potential_score' in ranked.columns
        
        # Check that result is sorted (highest potential first)
        assert ranked['potential_score'].is_monotonic_decreasing or \
               (ranked['potential_score'].diff().dropna() <= 0).all()
        
        # Check that all original rows are present
        assert len(ranked) == len(sample_sourcing_data)
    
    def test_rank_asins_by_potential_high_gms_high_score(self, generator):
        """Test that ASINs with both high GMS and high participation score rank highest."""
        data = pd.DataFrame({
            'ASIN': ['A001', 'A002'],
            'CID': ['C001', 'C001'],
            't30_gms_bau': [100000, 50000],
            'participation_score': [0.9, 0.5]
        })
        
        ranked = generator.rank_asins_by_potential(data)
        
        # A001 should rank higher (higher GMS and higher score)
        assert ranked.iloc[0]['ASIN'] == 'A001'
        assert ranked.iloc[1]['ASIN'] == 'A002'
    
    def test_rank_asins_by_potential_missing_columns(self, generator):
        """Test that ranking raises error when required columns are missing."""
        data = pd.DataFrame({
            'ASIN': ['A001'],
            'CID': ['C001']
            # Missing t30_gms_bau and participation_score
        })
        
        with pytest.raises(KeyError) as exc_info:
            generator.rank_asins_by_potential(data)
        
        assert "Missing required columns" in str(exc_info.value)
    
    def test_rank_asins_by_potential_handles_nan(self, generator):
        """Test that ranking handles NaN values gracefully."""
        data = pd.DataFrame({
            'ASIN': ['A001', 'A002', 'A003'],
            'CID': ['C001', 'C001', 'C001'],
            't30_gms_bau': [50000, None, 30000],
            'participation_score': [0.8, 0.5, None]
        })
        
        ranked = generator.rank_asins_by_potential(data)
        
        # Should not raise error and should handle NaN as 0
        assert len(ranked) == 3
        assert 'potential_score' in ranked.columns
    
    def test_rank_asins_by_potential_zero_max_gms(self, generator):
        """Test ranking when all GMS values are zero."""
        data = pd.DataFrame({
            'ASIN': ['A001', 'A002'],
            'CID': ['C001', 'C001'],
            't30_gms_bau': [0, 0],
            'participation_score': [0.8, 0.5]
        })
        
        ranked = generator.rank_asins_by_potential(data)
        
        # Should rank by participation score only
        assert ranked.iloc[0]['ASIN'] == 'A001'  # Higher participation score
    
    def test_calculate_expected_contribution_basic(self, generator, sample_sourcing_data):
        """Test basic expected contribution calculation."""
        ranked = generator.rank_asins_by_potential(sample_sourcing_data)
        recommendations = generator.calculate_expected_contribution(ranked, gap=100000)
        
        # Check that we get recommendations for all ASINs
        assert len(recommendations) == len(sample_sourcing_data)
        
        # Check that each recommendation has required fields
        for rec in recommendations:
            assert isinstance(rec, ASINRecommendation)
            assert rec.asin is not None
            assert rec.cid is not None
            assert rec.expected_contribution >= 0
            assert 0 <= rec.participation_score <= 1
            assert rec.t30_gms_bau >= 0
            assert rec.rationale is not None
    
    def test_calculate_expected_contribution_formula(self, generator):
        """Test that expected contribution is calculated correctly."""
        data = pd.DataFrame({
            'ASIN': ['A001'],
            'CID': ['C001'],
            't30_gms_bau': [50000],
            'participation_score': [0.8]
        })
        
        ranked = generator.rank_asins_by_potential(data)
        recommendations = generator.calculate_expected_contribution(ranked, gap=100000)
        
        # Expected contribution = t30_gms_bau × participation_score
        expected = 50000 * 0.8
        assert recommendations[0].expected_contribution == expected
    
    def test_generate_plan_basic(self, generator, sample_sourcing_data):
        """Test basic plan generation."""
        gap = 100000
        plan = generator.generate_plan(gap, sample_sourcing_data)
        
        # Check plan structure
        assert isinstance(plan, SourcingPlan)
        assert plan.total_gap == gap
        assert plan.gap_closable_by_sourcing >= 0
        assert isinstance(plan.recommended_asins, list)
        assert plan.remaining_gap >= 0
    
    def test_generate_plan_gap_closure(self, generator):
        """Test that plan selects ASINs until gap is closed."""
        data = pd.DataFrame({
            'ASIN': ['A001', 'A002', 'A003'],
            'CID': ['C001', 'C001', 'C001'],
            't30_gms_bau': [50000, 30000, 20000],
            'participation_score': [1.0, 1.0, 1.0]  # 100% participation for simplicity
        })
        
        gap = 60000  # Should need A001 (50000) + A002 (30000) = 80000
        plan = generator.generate_plan(gap, data)
        
        # Should select at least enough ASINs to close the gap
        total_contribution = sum(rec.expected_contribution for rec in plan.recommended_asins)
        assert total_contribution >= gap or len(plan.recommended_asins) == len(data)
    
    def test_generate_plan_remaining_gap_calculation(self, generator):
        """Test that remaining gap is calculated correctly."""
        data = pd.DataFrame({
            'ASIN': ['A001', 'A002'],
            'CID': ['C001', 'C001'],
            't30_gms_bau': [30000, 20000],
            'participation_score': [1.0, 1.0]
        })
        
        gap = 100000  # More than available sourcing can provide
        plan = generator.generate_plan(gap, data)
        
        # Remaining gap = total gap - sum of contributions
        expected_remaining = gap - sum(rec.expected_contribution for rec in plan.recommended_asins)
        assert abs(plan.remaining_gap - expected_remaining) < 0.01
    
    def test_generate_plan_negative_gap(self, generator, sample_sourcing_data):
        """Test that plan generation raises error for negative gap."""
        with pytest.raises(ValueError) as exc_info:
            generator.generate_plan(-10000, sample_sourcing_data)
        
        assert "Gap cannot be negative" in str(exc_info.value)
    
    def test_generate_plan_empty_data(self, generator):
        """Test plan generation with empty sourcing data."""
        empty_data = pd.DataFrame({
            'ASIN': [],
            'CID': [],
            't30_gms_bau': [],
            'participation_score': []
        })
        
        gap = 50000
        plan = generator.generate_plan(gap, empty_data)
        
        # Should return plan with no recommendations and full remaining gap
        assert plan.total_gap == gap
        assert plan.gap_closable_by_sourcing == 0.0
        assert len(plan.recommended_asins) == 0
        assert plan.remaining_gap == gap
    
    def test_generate_plan_zero_gap(self, generator, sample_sourcing_data):
        """Test plan generation with zero gap."""
        plan = generator.generate_plan(0, sample_sourcing_data)
        
        # Should return plan with no recommendations
        assert plan.total_gap == 0
        assert len(plan.recommended_asins) == 0
        assert plan.remaining_gap == 0
    
    def test_generate_plan_insufficient_sourcing(self, generator):
        """Test plan generation when sourcing cannot close the gap."""
        data = pd.DataFrame({
            'ASIN': ['A001'],
            'CID': ['C001'],
            't30_gms_bau': [10000],
            'participation_score': [0.5]
        })
        
        gap = 100000  # Much larger than available sourcing
        plan = generator.generate_plan(gap, data)
        
        # Should use all available ASINs but still have remaining gap
        assert len(plan.recommended_asins) == 1
        assert plan.remaining_gap > 0
        assert plan.gap_closable_by_sourcing < gap
    
    def test_rationale_generation_high_participation(self, generator):
        """Test rationale generation for high participation ASINs."""
        rationale = generator._generate_rationale(
            t30_gms_bau=100000,
            participation_score=0.8,
            potential_score=0.9
        )
        
        assert "high" in rationale.lower()
        assert "participation" in rationale.lower()
    
    def test_rationale_generation_low_participation(self, generator):
        """Test rationale generation for low participation ASINs."""
        rationale = generator._generate_rationale(
            t30_gms_bau=50000,
            participation_score=0.2,
            potential_score=0.4
        )
        
        assert "low" in rationale.lower()
        assert "participation" in rationale.lower()
    
    def test_ranking_with_equal_potential_scores(self, generator):
        """Test that ASINs with equal potential scores are ranked by GMS as tiebreaker."""
        data = pd.DataFrame({
            'ASIN': ['A001', 'A002'],
            'CID': ['C001', 'C001'],
            't30_gms_bau': [60000, 40000],
            'participation_score': [0.5, 0.5]  # Same participation score
        })
        
        ranked = generator.rank_asins_by_potential(data)
        
        # A001 should rank higher due to higher GMS (tiebreaker)
        assert ranked.iloc[0]['ASIN'] == 'A001'
    
    def test_plan_selects_highest_potential_first(self, generator):
        """Test that plan selects ASINs in order of potential."""
        data = pd.DataFrame({
            'ASIN': ['A001', 'A002', 'A003'],
            'CID': ['C001', 'C001', 'C001'],
            't30_gms_bau': [100000, 50000, 30000],
            'participation_score': [0.9, 0.7, 0.5]
        })
        
        gap = 50000  # Small gap, should only need top ASIN
        plan = generator.generate_plan(gap, data)
        
        # First recommendation should be the highest potential ASIN
        if len(plan.recommended_asins) > 0:
            # The first ASIN should have the highest potential
            first_asin = plan.recommended_asins[0].asin
            # A001 has highest GMS and participation, so should be first
            assert first_asin == 'A001'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
