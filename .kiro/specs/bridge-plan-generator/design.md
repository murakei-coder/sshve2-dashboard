# Design Document: Bridge Plan Generator

## Overview

The Bridge Plan Generator is a data-driven application that helps Amazon sales representatives create strategic plans to achieve sales targets. The system processes multiple data sources (sourcing data, targets, suppression benchmarks, and organizational mappings) to generate actionable recommendations through two complementary approaches:

1. **Sourcing Optimization**: Identifying high-potential ASINs for event recruitment based on historical participation and sales performance
2. **Suppression Optimization**: Reducing operational issues (OOS, Price Error, VRP missing) that prevent products from selling during events

The application supports multi-level analysis (CID, Alias, Manager, Team) and generates multiple bridge plan patterns to give users flexibility in choosing their strategy.

## Architecture

The system follows a modular pipeline architecture with clear separation of concerns:

```
┌─────────────────┐
│  Data Loaders   │ → Load and validate CSV/Excel files
└────────┬────────┘
         │
┌────────▼────────┐
│  Data Processors│ → Transform, aggregate, and enrich data
└────────┬────────┘
         │
┌────────▼────────┐
│ Bridge Plan     │ → Generate sourcing and suppression plans
│ Generator       │
└────────┬────────┘
         │
┌────────▼────────┐
│ Report Generator│ → Create visualizations and export reports
└─────────────────┘
```

### Key Architectural Decisions

1. **Pandas-based processing**: Use pandas DataFrames for efficient data manipulation and aggregation
2. **Configuration-driven**: Externalize file paths and coefficients for easy adaptation to different events
3. **Lazy evaluation**: Load and process data only when needed to minimize memory usage
4. **Modular design**: Each component (loader, processor, generator) is independent and testable

## Components and Interfaces

### 1. Data Loader Module

**Responsibility**: Load and validate all input data files

**Classes**:

```python
class DataLoader:
    def load_sourcing_data(file_path: str) -> pd.DataFrame
    def load_target_data(file_path: str) -> pd.DataFrame
    def load_suppression_benchmark(file_path: str) -> pd.DataFrame
    def load_cid_mapping(file_path: str, sheet_name: str) -> pd.DataFrame
    def validate_required_columns(df: pd.DataFrame, required_columns: List[str], file_name: str) -> ValidationResult
```

**Key Operations**:
- Load CSV files using pandas with appropriate encoding (UTF-8 for Japanese text)
- Load Excel files using openpyxl engine
- Validate presence of required columns
- Return descriptive errors for missing files or columns

### 2. Data Processor Module

**Responsibility**: Transform and aggregate raw data into analysis-ready structures

**Classes**:

```python
class SourcingProcessor:
    def extract_t30_gms_bau(df: pd.DataFrame) -> pd.DataFrame
    def extract_event_flags(df: pd.DataFrame) -> pd.DataFrame
    def calculate_participation_score(flags: pd.Series) -> float
    def aggregate_by_cid(df: pd.DataFrame) -> pd.DataFrame

class TargetProcessor:
    def extract_targets(df: pd.DataFrame) -> pd.DataFrame
    def calculate_gaps(current: pd.DataFrame, targets: pd.DataFrame) -> pd.DataFrame
    def identify_missing_targets(sourcing_cids: Set[str], target_cids: Set[str]) -> List[str]

class SuppressionProcessor:
    def extract_benchmark_percentages(df: pd.DataFrame) -> Dict[str, float]
    def validate_percentage_sum(percentages: Dict[str, float]) -> bool
    def calculate_current_suppression(df: pd.DataFrame) -> pd.DataFrame
    def aggregate_by_cid_pf(df: pd.DataFrame) -> pd.DataFrame

class HierarchyProcessor:
    def build_hierarchy_map(df: pd.DataFrame) -> HierarchyMap
    def aggregate_by_alias(data: pd.DataFrame, hierarchy: HierarchyMap) -> pd.DataFrame
    def aggregate_by_manager(data: pd.DataFrame, hierarchy: HierarchyMap) -> pd.DataFrame
    def aggregate_by_team(data: pd.DataFrame, hierarchy: HierarchyMap) -> pd.DataFrame
```

**Key Operations**:
- Extract relevant columns from raw data
- Calculate derived metrics (participation scores, gaps, suppression percentages)
- Aggregate data at different organizational levels
- Handle missing or inconsistent data gracefully

### 3. Bridge Plan Generator Module

**Responsibility**: Generate sourcing and suppression-based bridge plans

**Classes**:

```python
class PromotionOPSCalculator:
    def __init__(coefficients: Dict[str, float])
    def calculate_promotion_ops_target(t30_gms_target: float, benchmark_percentages: Dict[str, float]) -> float
    def calculate_current_promotion_ops(t30_gms_bau: float, current_percentages: Dict[str, float]) -> float

class SourcingPlanGenerator:
    def generate_plan(gap: float, sourcing_data: pd.DataFrame) -> SourcingPlan
    def rank_asins_by_potential(df: pd.DataFrame) -> pd.DataFrame
    def calculate_expected_contribution(asins: pd.DataFrame, gap: float) -> List[ASINRecommendation]

class SuppressionPlanGenerator:
    def generate_plan(gap: float, current_suppression: pd.DataFrame, benchmark: Dict[str, float]) -> SuppressionPlan
    def identify_improvement_opportunities(current: Dict[str, float], benchmark: Dict[str, float]) -> List[Opportunity]
    def calculate_impact_of_reduction(category: str, reduction_percentage: float, coefficients: Dict[str, float]) -> float

class BridgePlanOrchestrator:
    def generate_all_patterns(data: ProcessedData, config: Config) -> List[BridgePlan]
    def generate_sourcing_focused_pattern(data: ProcessedData) -> BridgePlan
    def generate_suppression_focused_pattern(data: ProcessedData) -> BridgePlan
    def generate_balanced_pattern(data: ProcessedData) -> BridgePlan
```

**Key Operations**:
- Calculate Promotion OPS targets using configurable coefficients
- Rank ASINs by participation likelihood and sales potential
- Identify suppression improvement opportunities
- Generate multiple bridge plan patterns
- Assess feasibility of each pattern

### 4. Report Generator Module

**Responsibility**: Create visualizations and export reports

**Classes**:

```python
class ReportGenerator:
    def generate_summary_report(plan: BridgePlan) -> Report
    def create_visualizations(plan: BridgePlan) -> List[Chart]
    def export_to_csv(plan: BridgePlan, output_path: str) -> None
    def export_to_excel(plan: BridgePlan, output_path: str) -> None

class Visualizer:
    def create_gap_chart(current: float, target: float) -> Chart
    def create_suppression_breakdown(percentages: Dict[str, float]) -> Chart
    def create_pattern_comparison(patterns: List[BridgePlan]) -> Chart
```

**Key Operations**:
- Generate summary statistics and recommendations
- Create charts (progress bars, stacked bars, pie charts)
- Export to CSV and Excel with Japanese language support
- Format reports for readability

### 5. Configuration Module

**Responsibility**: Manage application configuration

```python
class Config:
    sourcing_data_path: str
    target_data_path: str
    suppression_benchmark_path: str
    cid_mapping_path: str
    cid_mapping_sheet: str
    suppression_coefficients: Dict[str, float]
    event_flag_priority: List[str]
    
    def load_from_file(config_path: str) -> Config
    def save_to_file(config_path: str) -> None
    def validate() -> ValidationResult
```

## Data Models

### Core Data Structures

```python
@dataclass
class ASINData:
    asin: str
    cid: str
    t30_gms_bau: float
    event_flags: Dict[str, str]  # flag_name -> 'Y' or 'N'
    participation_score: float
    suppression_category: int  # 1-5

@dataclass
class CIDData:
    cid: str
    alias: str
    manager: str
    team: str
    t30_gms_bau: float
    t30_gms_target: float
    gap: float
    current_suppression: Dict[str, float]  # category -> percentage
    asins: List[ASINData]

@dataclass
class ASINRecommendation:
    asin: str
    cid: str
    expected_contribution: float
    participation_score: float
    rationale: str

@dataclass
class SuppressionOpportunity:
    category: str
    current_percentage: float
    target_percentage: float
    expected_impact: float
    recommended_actions: List[str]

@dataclass
class SourcingPlan:
    total_gap: float
    gap_closable_by_sourcing: float
    recommended_asins: List[ASINRecommendation]
    remaining_gap: float

@dataclass
class SuppressionPlan:
    total_gap: float
    gap_closable_by_suppression: float
    opportunities: List[SuppressionOpportunity]
    remaining_gap: float

@dataclass
class BridgePlan:
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
    cid_to_alias: Dict[str, str]
    alias_to_manager: Dict[str, str]
    manager_to_team: Dict[str, str]
```

### Calculation Formulas

**Participation Score**:
```python
def calculate_participation_score(flags: Dict[str, str]) -> float:
    """
    Calculate participation likelihood based on event flags.
    More recent flags have higher weight.
    """
    weights = {
        'sshve1_flag': 1.0,      # Most recent
        'fy26_mde2_flag': 0.8,
        'nys26_flag': 0.6,
        'bf25_flag': 0.4,
        'fy25_mde4_flag': 0.2,
        't365_flag': 0.1         # Least recent
    }
    
    score = 0.0
    for flag_name, weight in weights.items():
        if flags.get(flag_name) == 'Y':
            score += weight
    
    return score / sum(weights.values())  # Normalize to 0-1
```

**Promotion OPS Target**:
```python
def calculate_promotion_ops_target(
    t30_gms_target: float,
    benchmark_percentages: Dict[str, float],
    coefficients: Dict[str, float]
) -> float:
    """
    Calculate Promotion OPS Target based on benchmark suppression distribution.
    
    Formula:
    Promotion_OPS_Target = T30_GMS_Target × Σ(benchmark_% × coefficient)
    """
    promotion_ops = 0.0
    
    for category, benchmark_pct in benchmark_percentages.items():
        coefficient = coefficients.get(category, 0.0)
        promotion_ops += t30_gms_target * (benchmark_pct / 100.0) * coefficient
    
    return promotion_ops
```

**Suppression Impact**:
```python
def calculate_suppression_impact(
    t30_gms_target: float,
    current_percentages: Dict[str, float],
    target_percentages: Dict[str, float],
    coefficients: Dict[str, float]
) -> float:
    """
    Calculate the sales impact of changing suppression percentages.
    """
    current_ops = calculate_promotion_ops_target(t30_gms_target, current_percentages, coefficients)
    target_ops = calculate_promotion_ops_target(t30_gms_target, target_percentages, coefficients)
    
    return target_ops - current_ops
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Column Validation Completeness

*For any* DataFrame and set of required columns, when validating the DataFrame, the system should return an error if and only if at least one required column is missing, and the error message should identify all missing columns.

**Validates: Requirements 1.5, 1.7**

### Property 2: File Error Descriptiveness

*For any* missing or inaccessible file path, when attempting to load the file, the system should return an error message that contains the file path or file name.

**Validates: Requirements 1.6**

### Property 3: Event Participation Score Monotonicity

*For any* two ASINs with the same number of event participations (Y flags), the ASIN with Y flags in more recent events should have a higher or equal participation score than the ASIN with Y flags in less recent events.

**Validates: Requirements 2.3, 2.4**

### Property 4: Aggregation Preservation

*For any* dataset and aggregation level (CID to Alias, Alias to Mgr, Mgr to Team), the sum of a metric at the lower level should equal the aggregated value at the higher level for all entities.

**Validates: Requirements 2.5, 5.2, 5.3, 5.4, 6.3**

### Property 5: Gap Calculation Correctness

*For any* CID with current T30 GMS BAU and T30 GMS Target values, the calculated gap should equal the target minus the current value.

**Validates: Requirements 3.3, 8.1, 9.1**

### Property 6: Percentage Sum Invariant

*For any* suppression category distribution (benchmark or current), the sum of all category percentages should equal 100% within a 1% tolerance.

**Validates: Requirements 4.2, 7.2, 9.5**

### Property 7: Configuration Round-Trip

*For any* valid configuration object containing suppression coefficients, file paths, and event flag priorities, saving the configuration to a file and then loading it should produce an equivalent configuration object.

**Validates: Requirements 4.4, 14.1, 14.2, 14.3, 14.5**

### Property 8: Promotion OPS Formula Correctness

*For any* T30 GMS Target value, benchmark suppression percentages, and suppression coefficients, the calculated Promotion OPS Target should equal the sum of (T30_GMS_Target × benchmark_percentage × coefficient) for all suppression categories.

**Validates: Requirements 6.1**

### Property 9: Coefficient Update Propagation

*For any* set of CIDs with T30 GMS Targets and benchmark percentages, when suppression coefficients are updated, all recalculated Promotion OPS Targets should reflect the new coefficients in the formula.

**Validates: Requirements 6.2**

### Property 10: Suppression Percentage Calculation

*For any* CID with a set of ASINs having suppression categories, the calculated percentage for each category should equal (count of ASINs in that category / total ASINs) × 100.

**Validates: Requirements 7.2**

### Property 11: Suppression Difference Correctness

*For any* CID with current suppression percentages and benchmark percentages, the calculated difference for each category should equal current percentage minus benchmark percentage.

**Validates: Requirements 7.4**

### Property 12: Sourcing Recommendation Ranking

*For any* two ASINs being considered for sourcing, if ASIN A has both higher T30 GMS BAU and higher participation score than ASIN B, then ASIN A should rank higher than or equal to ASIN B in the recommendation list.

**Validates: Requirements 8.2, 8.3**

### Property 13: Sourcing Contribution Sum

*For any* sourcing plan where the gap can be closed, the sum of expected contributions from all recommended ASINs should be greater than or equal to the total gap.

**Validates: Requirements 8.4**

### Property 14: Remaining Gap Calculation

*For any* sourcing plan, the remaining gap should equal the total gap minus the sum of expected contributions from recommended ASINs.

**Validates: Requirements 8.5**

### Property 15: Suppression Impact Prioritization

*For any* two suppression improvement opportunities, if opportunity A has higher expected sales impact than opportunity B, then opportunity A should rank higher than or equal to opportunity B in the recommendations.

**Validates: Requirements 9.2, 12.2**

### Property 16: Suppression Improvement Sum

*For any* suppression plan where the gap can be closed, the sum of expected impacts from all improvement opportunities should be greater than or equal to the total gap.

**Validates: Requirements 9.4**

### Property 17: Pattern Contribution Accuracy

*For any* bridge plan pattern, the sum of sourcing contribution and suppression contribution should equal the total gap minus the remaining gap.

**Validates: Requirements 10.4**

### Property 18: Unmapped CID Exclusion

*For any* CID that exists in sourcing data but not in the mapping file, that CID should not appear in any aggregated results at Alias, Mgr, or Team levels.

**Validates: Requirements 5.5**

### Property 19: Data Inconsistency Detection

*For any* CID that exists in sourcing data but not in target data, the system should generate a warning that includes the CID identifier.

**Validates: Requirements 3.2**

### Property 20: Report Export Round-Trip

*For any* bridge plan, exporting to CSV format and then importing should preserve all numeric metrics (T30 GMS BAU, T30 GMS Target, gap values) within floating-point precision tolerance.

**Validates: Requirements 13.2**

### Property 21: Excel Export Round-Trip

*For any* bridge plan, exporting to Excel format and then importing should preserve all numeric metrics and text fields including Japanese characters.

**Validates: Requirements 13.3, 13.5**

### Property 22: Report Completeness

*For any* generated bridge plan report, the report should contain all required fields: current T30 GMS, target T30 GMS, gap, sourcing recommendations (if applicable), suppression opportunities (if applicable), and overall recommendations.

**Validates: Requirements 13.1, 13.4**

### Property 23: Configuration Validation

*For any* configuration object, if any required parameter (sourcing_data_path, target_data_path, suppression_benchmark_path, cid_mapping_path, suppression_coefficients) is missing or invalid, validation should return an error identifying the problematic parameter.

**Validates: Requirements 14.4**

### Property 24: Recommendation Confidence Inclusion

*For any* generated recommendation (sourcing or suppression), the recommendation should include a confidence level or feasibility score value.

**Validates: Requirements 12.5**

### Property 25: Participation History Influence

*For any* ASIN with no event participation history (all flags are N), the participation score should be lower than any ASIN with at least one event participation (at least one flag is Y).

**Validates: Requirements 12.1**

## Error Handling

### File Loading Errors

**Missing Files**:
- Catch `FileNotFoundError` exceptions
- Return error message: "File not found: {file_path}. Please check the configuration."
- Log the error with timestamp and attempted path

**Invalid File Format**:
- Catch `pd.errors.ParserError` for CSV files
- Catch `openpyxl` exceptions for Excel files
- Return error message: "Unable to parse {file_name}. Please ensure the file format is correct."

**Encoding Issues**:
- Try UTF-8 encoding first
- Fall back to UTF-8-sig for files with BOM
- If both fail, return error: "Encoding error in {file_name}. Please ensure the file is UTF-8 encoded."

### Data Validation Errors

**Missing Columns**:
- Identify all missing columns in a single pass
- Return error: "Missing required columns in {file_name}: {column_list}"
- Do not proceed with processing if columns are missing

**Data Type Mismatches**:
- Attempt to coerce numeric columns to float
- If coercion fails, return error: "Invalid data type in column {column_name} of {file_name}. Expected numeric values."

**Invalid Values**:
- Check for negative values in T30 GMS columns
- Check for suppression categories outside 1-5 range
- Check for event flags that are not 'Y' or 'N'
- Return descriptive error for each validation failure

### Calculation Errors

**Division by Zero**:
- Check for zero denominators before percentage calculations
- Return 0% if denominator is zero (e.g., no ASINs in a category)
- Log warning: "Zero denominator in percentage calculation for {entity_id}"

**Insufficient Data**:
- If no ASINs available for sourcing, return error: "No sourcing candidates available for {entity_id}"
- If no suppression data available, return error: "No suppression data available for {entity_id}"
- Suggest alternative approaches in error message

**Infeasible Plans**:
- If gap cannot be closed by any pattern, return warning: "Target gap of {gap} cannot be fully closed with available strategies. Maximum achievable: {max_achievable}"
- Provide partial plan with best-effort recommendations

### Configuration Errors

**Invalid Coefficients**:
- Validate that all coefficients are between 0 and 1
- Return error: "Invalid suppression coefficient for {category}: {value}. Must be between 0 and 1."

**Missing Configuration**:
- Check for all required configuration parameters on startup
- Return error: "Missing required configuration: {parameter_name}"
- Provide example configuration in error message

## Testing Strategy

The Bridge Plan Generator requires comprehensive testing to ensure correctness of complex calculations and data transformations. We will use a dual testing approach:

### Unit Testing

Unit tests will focus on specific examples, edge cases, and integration points:

**Data Loading Tests**:
- Test loading valid CSV and Excel files
- Test error handling for missing files
- Test error handling for files with missing columns
- Test Japanese character encoding in file names and content

**Calculation Tests**:
- Test participation score calculation with specific flag combinations
- Test Promotion OPS calculation with known inputs and expected outputs
- Test gap calculation with various current/target combinations
- Test percentage calculations with edge cases (zero ASINs, all in one category)

**Aggregation Tests**:
- Test aggregation from CID to Alias with known mappings
- Test aggregation across multiple hierarchy levels
- Test handling of unmapped CIDs

**Edge Case Tests**:
- Test with empty DataFrames
- Test with single-row DataFrames
- Test with negative gaps (target already achieved)
- Test with zero targets
- Test with all ASINs in "No suppression" category

### Property-Based Testing

Property-based tests will verify universal properties across randomized inputs using a property-based testing library (e.g., Hypothesis for Python):

**Configuration**:
- Minimum 100 iterations per property test
- Each test tagged with: **Feature: bridge-plan-generator, Property {number}: {property_text}**

**Test Data Generation**:
- Generate random DataFrames with valid schemas
- Generate random suppression percentages that sum to 100%
- Generate random event participation flag combinations
- Generate random hierarchy mappings
- Generate random numeric values within realistic ranges

**Property Test Coverage**:
- Each correctness property (Property 1-25) should be implemented as a property-based test
- Properties testing mathematical invariants (sums, differences, percentages) are especially important
- Properties testing round-trip operations (configuration, export/import) ensure data integrity

**Example Property Test Structure**:
```python
# Feature: bridge-plan-generator, Property 4: Aggregation Preservation
@given(
    cid_data=st.lists(st.tuples(st.text(), st.floats(min_value=0)), min_size=1),
    hierarchy=st.dictionaries(st.text(), st.text())
)
def test_aggregation_preservation(cid_data, hierarchy):
    # Create DataFrame from generated data
    df = create_dataframe(cid_data)
    
    # Perform aggregation
    aggregated = aggregate_by_alias(df, hierarchy)
    
    # Verify sum is preserved
    assert sum(df['metric']) == sum(aggregated['metric'])
```

### Integration Testing

Integration tests will verify end-to-end workflows:

**Complete Pipeline Tests**:
- Load all data files → Process → Generate plans → Export reports
- Test with realistic sample data
- Verify all outputs are generated correctly

**Multi-Level Aggregation Tests**:
- Generate plans at all levels (CID, Alias, Mgr, Team)
- Verify consistency across levels
- Verify drill-down relationships

**Pattern Generation Tests**:
- Generate all three patterns (Sourcing, Suppression, Balanced)
- Verify pattern feasibility logic
- Verify pattern recommendations are actionable

### Test Data

**Sample Data Sets**:
- Small dataset (10 CIDs, 50 ASINs) for quick tests
- Medium dataset (100 CIDs, 1000 ASINs) for realistic tests
- Large dataset (1000 CIDs, 10000 ASINs) for performance tests
- Edge case dataset (missing values, extreme values, boundary conditions)

**Japanese Language Testing**:
- Include Japanese characters in CID names, Alias names, Team names
- Test CSV export/import with Japanese text
- Test Excel export/import with Japanese text
- Verify UTF-8 encoding throughout

### Performance Testing

While not part of automated unit/property tests, performance should be validated:

**Benchmarks**:
- Load 100K row CSV in < 30 seconds
- Generate Team-level plan (1000 CIDs) in < 60 seconds
- Export Excel report in < 10 seconds

**Memory Profiling**:
- Monitor memory usage during large file processing
- Verify chunked processing activates for large datasets
- Ensure no memory leaks in repeated operations
