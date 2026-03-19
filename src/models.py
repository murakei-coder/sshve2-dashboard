"""
Data models for Deal Sourcing Analyzer.
Defines dataclasses for analysis results.
"""
from dataclasses import dataclass


@dataclass
class SegmentAnalysis:
    """
    Analysis result for a single segment (Price Band, ASIN Tenure, or Paid-Flag).
    
    Attributes:
        segment_name: Name of the segment being analyzed
        total_gms: Total GMS for the segment
        sourced_gms: GMS from Sourced entries
        nonsourced_gms: GMS from NonSourced entries
        total_asin_count: Total unique ASIN count
        sourced_asin_count: ASIN count for Sourced entries
        nonsourced_asin_count: ASIN count for NonSourced entries
        sourced_rate: Ratio of sourced ASINs (0.0 - 1.0)
        gms_per_asin: Average GMS per ASIN
        opportunity_gms: Potential GMS from NonSourced (equals nonsourced_gms)
        opportunity_ratio: NonSourced GMS / Total GMS
        opportunity_level: Classification ("高", "中", "低")
    """
    segment_name: str
    total_gms: float
    sourced_gms: float
    nonsourced_gms: float
    total_asin_count: int
    sourced_asin_count: int
    nonsourced_asin_count: int
    sourced_rate: float
    gms_per_asin: float
    opportunity_gms: float
    opportunity_ratio: float
    opportunity_level: str
