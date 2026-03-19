"""
Data models for Discount Effectiveness Analyzer.
Defines dataclasses for analysis results and recommendations.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from datetime import datetime


@dataclass
class SegmentAnalysisResult:
    """
    Analysis result for a single PF/GL × Price Band segment.
    
    Attributes:
        pf: Platform category
        price_band: Price band classification
        sample_count: Number of samples in segment
        correlation: Correlation coefficient between discount and growth rate
        regression_coef: Regression coefficient (slope)
        regression_intercept: Regression intercept
        r_squared: R-squared value
        p_value: P-value for statistical significance
        is_significant: Whether relationship is statistically significant
        is_insufficient_sample: Whether sample size is below threshold
        mean_discount: Mean discount rate in segment
        mean_growth_rate: Mean growth rate in segment
        std_discount: Standard deviation of discount rate
        std_growth_rate: Standard deviation of growth rate
        gl: GL category (optional)
    """
    pf: str
    price_band: str
    sample_count: int
    correlation: Optional[float] = None
    regression_coef: Optional[float] = None
    regression_intercept: Optional[float] = None
    r_squared: Optional[float] = None
    p_value: Optional[float] = None
    is_significant: bool = False
    is_insufficient_sample: bool = False
    mean_discount: float = 0.0
    mean_growth_rate: float = 0.0
    std_discount: float = 0.0
    std_growth_rate: float = 0.0
    gl: str = ''
    
    def to_dict(self) -> dict:
        """Convert to dictionary with JSON-serializable types."""
        d = asdict(self)
        # Convert numpy types to Python native types
        for key, value in d.items():
            if hasattr(value, 'item'):  # numpy scalar
                d[key] = value.item()
            elif isinstance(value, bool):
                d[key] = bool(value)
        return d
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SegmentAnalysisResult':
        """Create from dictionary."""
        # Handle missing gl field for backward compatibility
        if 'gl' not in data:
            data['gl'] = ''
        return cls(**data)



@dataclass
class OptimalDiscountRecommendation:
    """
    Optimal discount rate recommendation for a PF × Price Band segment.
    
    Attributes:
        pf: Platform category
        price_band: Price band classification
        optimal_discount_rate: Recommended discount rate (0-50%)
        expected_growth_rate: Expected growth rate at optimal discount
        confidence_level: Confidence level of recommendation
        note: Additional notes or warnings
    """
    pf: str
    price_band: str
    optimal_discount_rate: float
    expected_growth_rate: float
    confidence_level: str
    note: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'OptimalDiscountRecommendation':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class AnalysisResults:
    """
    Complete analysis results container.
    
    Attributes:
        raw_data_path: Path to the input data file
        analysis_timestamp: Timestamp of analysis execution
        total_records: Total number of records in input
        valid_records: Number of valid records after cleaning
        excluded_records: Number of excluded records
        segment_analyses: List of segment analysis results
        recommendations: List of optimal discount recommendations
    """
    raw_data_path: str
    analysis_timestamp: str
    total_records: int
    valid_records: int
    excluded_records: int
    segment_analyses: List[SegmentAnalysisResult] = field(default_factory=list)
    recommendations: List[OptimalDiscountRecommendation] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'raw_data_path': self.raw_data_path,
            'analysis_timestamp': self.analysis_timestamp,
            'total_records': self.total_records,
            'valid_records': self.valid_records,
            'excluded_records': self.excluded_records,
            'segment_analyses': [s.to_dict() for s in self.segment_analyses],
            'recommendations': [r.to_dict() for r in self.recommendations]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AnalysisResults':
        """Create from dictionary."""
        return cls(
            raw_data_path=data['raw_data_path'],
            analysis_timestamp=data['analysis_timestamp'],
            total_records=data['total_records'],
            valid_records=data['valid_records'],
            excluded_records=data['excluded_records'],
            segment_analyses=[
                SegmentAnalysisResult.from_dict(s) 
                for s in data.get('segment_analyses', [])
            ],
            recommendations=[
                OptimalDiscountRecommendation.from_dict(r) 
                for r in data.get('recommendations', [])
            ]
        )
    
    @classmethod
    def create(cls, raw_data_path: str, total_records: int, valid_records: int) -> 'AnalysisResults':
        """Factory method to create new AnalysisResults."""
        return cls(
            raw_data_path=raw_data_path,
            analysis_timestamp=datetime.now().isoformat(),
            total_records=total_records,
            valid_records=valid_records,
            excluded_records=total_records - valid_records
        )
