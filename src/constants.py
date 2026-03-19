"""
Constants for Deal Sourcing Analyzer.
Defines required columns and sort orders for analysis.
"""

# Required columns for input data (Requirements 1.2)
REQUIRED_COLUMNS = [
    'asin',
    'merchant_customer_id',
    'pf',
    'gl',
    'paid-flag',
    'dealflag',
    'pointsdealflag',
    'price&pointsdealflag',
    'retailflag',
    'domesticoocflag',
    'priceband',
    'asintenure',
    'gms',
    'units',
    'our_price',
    'asin_tenure_days'
]

# Price Band sort order (Requirements 3.3)
PRICE_BAND_ORDER = [
    '1~1000',
    '1001~2000',
    '2001~3000',
    '3001~4000',
    '4001~5000',
    '5001~10000',
    '10001~50000',
    '50001~100000',
    '100000~',
    'Unknown'
]

# ASIN Tenure sort order (Requirements 4.3)
TENURE_ORDER = [
    '1.0-30 days',
    '2.31-90 days',
    '3.91-180 days',
    '4.181-365 days',
    '5.1-2 years',
    '6.2-3 years',
    '7.3-4 years',
    '8.4-5 years',
    '9.5-6 years',
    '10.6-7 years',
    '11.7-8 years',
    '12.8-9 years',
    '13.9-10 years',
    '14.10+ years',
    '15.Unknown'
]
