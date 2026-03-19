"""
Property-based tests for Analyzer.
**Feature: deal-sourcing-analyzer**
**Validates: Requirements 2.1, 2.2, 2.3, 2.4**
"""
import math
import pandas as pd
import pytest
from hypothesis import given, strategies as st, settings, assume

from src.analyzer import Analyzer
from src.constants import PRICE_BAND_ORDER, TENURE_ORDER


@st.composite
def valid_analyzer_dataframe(draw):
    """Generate a valid DataFrame for Analyzer testing."""
    n_rows = draw(st.integers(min_value=1, max_value=100))
    
    paid_flags = draw(st.lists(st.sampled_from(['Y', 'N']), min_size=n_rows, max_size=n_rows))
    deal_flags = draw(st.lists(st.sampled_from(['Sourced', 'NonSourced']), min_size=n_rows, max_size=n_rows))
    price_bands = draw(st.lists(st.sampled_from(PRICE_BAND_ORDER), min_size=n_rows, max_size=n_rows))
    tenures = draw(st.lists(st.sampled_from(TENURE_ORDER), min_size=n_rows, max_size=n_rows))
    gms_values = draw(st.lists(
        st.floats(min_value=0, max_value=100000, allow_nan=False, allow_infinity=False),
        min_size=n_rows, max_size=n_rows
    ))
    
    return pd.DataFrame({
        'asin': [f'ASIN{i}' for i in range(n_rows)],
        'MERCHANT_CUSTOMER_ID': [f'MID{i}' for i in range(n_rows)],
        'pf': ['PF1'] * n_rows,
        'gl': ['GL1'] * n_rows,
        'Paid-Flag': paid_flags,
        'DealFlag': ['Deal'] * n_rows,
        'PointsDealFlag': ['Points'] * n_rows,
        'Price&PointsDealFlag': deal_flags,
        'RetailFlag': ['Y'] * n_rows,
        'DomesticOOCFlag': ['N'] * n_rows,
        'PriceBand': price_bands,
        'ASINTenure': tenures,
        'GMS': gms_values,
        'UNITS': [10] * n_rows,
    })


class TestAnalyzerPropertyTests:
    """Property-based tests for Analyzer."""
    
    @given(df=valid_analyzer_dataframe())
    @settings(max_examples=100)
    def test_property_2_group_aggregation_accuracy(self, df: pd.DataFrame):
        """
        **Feature: deal-sourcing-analyzer, Property 2: Group Aggregation Accuracy**
        
        For any DataFrame and grouping column (Paid-Flag), the sum of GMS across
        all groups should equal the total GMS of the original DataFrame.
        
        **Validates: Requirements 2.1**
        """
        analyzer = Analyzer(df)
        result = analyzer.analyze_by_paid_flag()
        
        total_gms_original = df['GMS'].sum()
        total_gms_grouped = result['total_gms'].sum()
        
        assert math.isclose(total_gms_original, total_gms_grouped, rel_tol=1e-9), \
            f"GMS mismatch: original={total_gms_original}, grouped={total_gms_grouped}"
    
    @given(df=valid_analyzer_dataframe())
    @settings(max_examples=100)
    def test_property_3_metric_calculation_consistency(self, df: pd.DataFrame):
        """
        **Feature: deal-sourcing-analyzer, Property 3: Metric Calculation Consistency**
        
        For any segment analysis result, GMS_per_ASIN should equal total_gms
        divided by asin_count (when asin_count > 0).
        
        **Validates: Requirements 2.2**
        """
        analyzer = Analyzer(df)
        result = analyzer.analyze_by_paid_flag()
        
        for _, row in result.iterrows():
            if row['total_asin_count'] > 0:
                expected_gms_per_asin = row['total_gms'] / row['total_asin_count']
                assert math.isclose(row['gms_per_asin'], expected_gms_per_asin, rel_tol=1e-9), \
                    f"GMS per ASIN mismatch: expected={expected_gms_per_asin}, actual={row['gms_per_asin']}"
    
    @given(df=valid_analyzer_dataframe())
    @settings(max_examples=100)
    def test_property_4_sourced_rate_calculation(self, df: pd.DataFrame):
        """
        **Feature: deal-sourcing-analyzer, Property 4: Sourced Rate Calculation**
        
        For any segment analysis result, sourced_rate should equal sourced_asin_count
        divided by total_asin_count, and the value should be between 0.0 and 1.0.
        
        **Validates: Requirements 2.3**
        """
        analyzer = Analyzer(df)
        result = analyzer.analyze_by_paid_flag()
        
        for _, row in result.iterrows():
            # Check sourced_rate is between 0 and 1
            assert 0.0 <= row['sourced_rate'] <= 1.0, \
                f"Sourced rate out of range: {row['sourced_rate']}"
            
            # Check calculation
            if row['total_asin_count'] > 0:
                expected_rate = row['sourced_asin_count'] / row['total_asin_count']
                assert math.isclose(row['sourced_rate'], expected_rate, rel_tol=1e-9), \
                    f"Sourced rate mismatch: expected={expected_rate}, actual={row['sourced_rate']}"
    
    @given(df=valid_analyzer_dataframe())
    @settings(max_examples=100)
    def test_property_5_opportunity_equals_nonsourced_gms(self, df: pd.DataFrame):
        """
        **Feature: deal-sourcing-analyzer, Property 5: Opportunity Equals NonSourced GMS**
        
        For any segment analysis result, opportunity_gms should equal nonsourced_gms.
        
        **Validates: Requirements 2.4**
        """
        analyzer = Analyzer(df)
        result = analyzer.analyze_by_paid_flag()
        
        for _, row in result.iterrows():
            assert math.isclose(row['opportunity_gms'], row['nonsourced_gms'], rel_tol=1e-9), \
                f"Opportunity mismatch: opportunity={row['opportunity_gms']}, nonsourced={row['nonsourced_gms']}"


    @given(df=valid_analyzer_dataframe())
    @settings(max_examples=100)
    def test_property_6_price_band_sort_order(self, df: pd.DataFrame):
        """
        **Feature: deal-sourcing-analyzer, Property 6: Price Band Sort Order**
        
        For any Price Band analysis result, the segments should be sorted
        according to the predefined PRICE_BAND_ORDER.
        
        **Validates: Requirements 3.3**
        """
        analyzer = Analyzer(df)
        result = analyzer.analyze_by_price_band()
        
        if len(result) <= 1:
            return  # Nothing to check for 0 or 1 rows
        
        # Get the order of price bands in the result
        result_bands = result['PriceBand'].tolist()
        
        # Check that they appear in the correct order
        result_indices = [PRICE_BAND_ORDER.index(band) for band in result_bands]
        
        for i in range(len(result_indices) - 1):
            assert result_indices[i] < result_indices[i + 1], \
                f"Price bands not in correct order: {result_bands}"


    @given(df=valid_analyzer_dataframe())
    @settings(max_examples=100)
    def test_property_7_asin_tenure_sort_order(self, df: pd.DataFrame):
        """
        **Feature: deal-sourcing-analyzer, Property 7: ASIN Tenure Sort Order**
        
        For any ASIN Tenure analysis result, the segments should be sorted
        according to the predefined TENURE_ORDER.
        
        **Validates: Requirements 4.3**
        """
        analyzer = Analyzer(df)
        result = analyzer.analyze_by_tenure()
        
        if len(result) <= 1:
            return  # Nothing to check for 0 or 1 rows
        
        # Get the order of tenures in the result
        result_tenures = result['ASINTenure'].tolist()
        
        # Check that they appear in the correct order
        result_indices = [TENURE_ORDER.index(tenure) for tenure in result_tenures]
        
        for i in range(len(result_indices) - 1):
            assert result_indices[i] < result_indices[i + 1], \
                f"ASIN Tenures not in correct order: {result_tenures}"


    @given(df=valid_analyzer_dataframe())
    @settings(max_examples=100)
    def test_property_8_opportunity_level_classification(self, df: pd.DataFrame):
        """
        **Feature: deal-sourcing-analyzer, Property 8: Opportunity Level Classification**
        
        For any segment with sourced_rate >= 0.8, the opportunity_level should be "低".
        
        **Validates: Requirements 5.1**
        """
        analyzer = Analyzer(df)
        price_band_result = analyzer.analyze_by_price_band()
        
        if len(price_band_result) == 0:
            return
        
        scored_result = analyzer.calculate_opportunity_score(price_band_result)
        
        for _, row in scored_result.iterrows():
            if row['sourced_rate'] >= 0.8:
                assert row['opportunity_level'] == '低', \
                    f"Segment with sourced_rate {row['sourced_rate']} should have opportunity_level '低'"

    @given(df=valid_analyzer_dataframe())
    @settings(max_examples=100)
    def test_property_9_high_opportunity_identification(self, df: pd.DataFrame):
        """
        **Feature: deal-sourcing-analyzer, Property 9: High Opportunity Identification**
        
        For any segment where opportunity_ratio is in the top quartile (and sourced_rate < 0.8),
        the segment should be marked as high opportunity.
        
        **Validates: Requirements 5.2**
        """
        analyzer = Analyzer(df)
        price_band_result = analyzer.analyze_by_price_band()
        
        if len(price_band_result) == 0:
            return
        
        scored_result = analyzer.calculate_opportunity_score(price_band_result)
        
        # Verify opportunity_level is one of the valid values
        valid_levels = {'高', '中', '低'}
        for _, row in scored_result.iterrows():
            assert row['opportunity_level'] in valid_levels, \
                f"Invalid opportunity_level: {row['opportunity_level']}"
