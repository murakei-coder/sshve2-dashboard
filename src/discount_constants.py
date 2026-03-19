"""
Constants for Discount Effectiveness Analyzer.
Defines required columns, price bands, and analysis parameters.
"""

# Required columns for discount analysis (Requirements 1.2)
REQUIRED_COLUMNS = [
    'asin',
    'pf',
    'our_price',
    'current_discount_percent',
    'past_month_gms',
    'promotion_ops'
]

# Required columns for GL analysis
REQUIRED_COLUMNS_GL = [
    'asin',
    'pf',
    'gl',
    'our_price',
    'current_discount_percent',
    'past_month_gms',
    'promotion_ops'
]

# Numeric columns that must contain valid numbers (Requirements 1.3)
NUMERIC_COLUMNS = [
    'our_price',
    'current_discount_percent',
    'past_month_gms',
    'promotion_ops'
]

# Discount rate tiers for grouping
DISCOUNT_TIERS = [
    (0, 5, '0~5%'),
    (5, 10, '5~10%'),
    (10, 15, '10~15%'),
    (15, 20, '15~20%'),
    (20, 25, '20~25%'),
    (25, 30, '25~30%'),
    (30, 40, '30~40%'),
    (40, 50, '40~50%'),
    (50, 100, '50%以上'),
]

# Discount tier order for display
DISCOUNT_TIER_ORDER = [
    '0~5%',
    '5~10%',
    '10~15%',
    '15~20%',
    '20~25%',
    '25~30%',
    '30~40%',
    '40~50%',
    '50%以上',
    'Unknown'
]

# Price band definitions (Requirements 3.1)
PRICE_BANDS = [
    (1, 1000, '1~1000'),
    (1001, 2000, '1001~2000'),
    (2001, 3000, '2001~3000'),
    (3001, 5000, '3001~5000'),
    (5001, 10000, '5001~10000'),
    (10001, 50000, '10001~50000'),
    (50001, float('inf'), '50001以上'),
]

# Price band sort order for display
PRICE_BAND_ORDER = [
    '1~1000',
    '1001~2000',
    '2001~3000',
    '3001~5000',
    '5001~10000',
    '10001~50000',
    '50001以上',
    'Unknown'
]

# Analysis parameters
OUTLIER_THRESHOLD = 10000  # Growth rate >= 10000% is considered outlier
MIN_SAMPLE_SIZE = 10  # Minimum samples for statistical analysis
SIGNIFICANCE_LEVEL = 0.05  # p-value threshold for significance
DISCOUNT_MIN = 0  # Minimum discount rate
DISCOUNT_MAX = 50  # Maximum discount rate
