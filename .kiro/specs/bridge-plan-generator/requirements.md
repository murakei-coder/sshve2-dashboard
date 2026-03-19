# Requirements Document

## Introduction

The Bridge Plan Generator is an AI-powered application designed to help Amazon sales representatives create strategic Bridge Plans to achieve their sales targets. The system analyzes sales data, event participation history, and suppression patterns to generate actionable recommendations through two primary optimization approaches: Sourcing (identifying high-potential ASINs for event participation) and Suppression (reducing operational issues that prevent sales).

## Glossary

- **Bridge_Plan**: A strategic plan that identifies specific actions to close the gap between current sales performance and target sales goals
- **CID**: Customer ID, a unique identifier for sellers on Amazon
- **ASIN**: Amazon Standard Identification Number, a unique identifier for products
- **PF**: Product Family or category grouping
- **T30_GMS**: Trailing 30-day Gross Merchandise Sales, the total sales value over the past 30 days
- **BAU**: Business As Usual, baseline sales performance without event participation
- **Promotion_OPS**: Promotional Operations Sales, the sales generated during promotional events
- **Sourcing**: The process of identifying and recruiting ASINs/sellers to participate in promotional events
- **Suppression**: Operational issues that prevent products from being displayed or sold during events
- **Suppression_Category**: Classification of why a product was suppressed (OOS, VRP missing, Price Error, Others, No suppression)
- **Event_Participation_Flag**: Binary indicator (Y/N) showing whether an ASIN participated in a previous event
- **Alias**: A sales representative's identifier or username
- **Mgr**: Manager, the supervisor overseeing one or more sales representatives
- **Team**: A group of sales representatives and their manager(s)
- **Gap**: The difference between current performance and target performance
- **Coefficient**: A multiplier that converts suppression percentages into expected sales impact

## Requirements

### Requirement 1: Data File Loading and Validation

**User Story:** As a sales representative, I want the system to load and validate all required data files, so that I can trust the accuracy of the bridge plan recommendations.

#### Acceptance Criteria

1. WHEN the system starts, THE System SHALL load the Sourcing data CSV file from the configured path
2. WHEN the system starts, THE System SHALL load the Target data CSV file from the configured path
3. WHEN the system starts, THE System SHALL load the Suppression benchmark CSV file from the configured path
4. WHEN the system starts, THE System SHALL load the CID mapping Excel file from the configured path
5. WHEN loading any data file, THE System SHALL validate that all required columns are present
6. IF a required file is missing or inaccessible, THEN THE System SHALL return a descriptive error message indicating which file is missing
7. IF a required column is missing from a file, THEN THE System SHALL return a descriptive error message indicating which column is missing from which file
8. WHEN all files are loaded successfully, THE System SHALL confirm successful data loading to the user

### Requirement 2: Sourcing Data Processing

**User Story:** As a sales representative, I want the system to process sourcing data with event participation history, so that I can identify high-potential ASINs for event recruitment.

#### Acceptance Criteria

1. WHEN processing Sourcing data, THE System SHALL extract T30 GMS BAU values from column T (total_t30d_gms_BAU) for each ASIN×CID combination
2. WHEN processing Sourcing data, THE System SHALL extract all event participation flags (sshve1_flag, fy26_mde2_flag, nys26_flag, bf25_flag, fy25_mde4_flag, t365_flag) for each ASIN
3. WHEN analyzing event participation flags, THE System SHALL treat flags in order of recency (sshve1_flag is most recent, t365_flag is least recent)
4. WHEN calculating participation likelihood, THE System SHALL assign higher probability scores to ASINs with more recent event participation (Y values in earlier flag columns)
5. WHEN aggregating sourcing data by CID, THE System SHALL sum all T30 GMS BAU values for ASINs belonging to that CID

### Requirement 3: Target Data Processing

**User Story:** As a sales representative, I want the system to process target data by seller, so that I can understand the sales goals I need to achieve.

#### Acceptance Criteria

1. WHEN processing Target data, THE System SHALL extract T30 GMS Target values for each CID
2. WHEN a CID exists in Sourcing data but not in Target data, THE System SHALL flag this as a data inconsistency warning
3. WHEN calculating gaps, THE System SHALL compute the difference between T30 GMS Target and current T30 GMS BAU for each CID
4. WHEN the gap is negative (current sales exceed target), THE System SHALL report this as target already achieved

### Requirement 4: Suppression Benchmark Processing

**User Story:** As a sales representative, I want the system to process suppression benchmark data from previous events, so that I can understand typical suppression patterns and set realistic improvement goals.

#### Acceptance Criteria

1. WHEN processing Suppression benchmark data, THE System SHALL extract suppression reason percentages for each suppression category (No suppression, OOS, VRP missing, Price Error, Others)
2. WHEN benchmark data is loaded, THE System SHALL validate that suppression percentages sum to approximately 100% (within 1% tolerance)
3. WHEN benchmark data contains multiple events, THE System SHALL allow the user to select which event to use as the benchmark
4. THE System SHALL store suppression coefficients as configurable values (No suppression: 53.43%, OOS: 28.07%, VRP missing: 9.63%, Price Error: 27.5%, Others: 18.01%)

### Requirement 5: CID Mapping and Hierarchy Processing

**User Story:** As a sales representative, I want the system to process organizational hierarchy data, so that I can generate bridge plans at different aggregation levels (CID, Alias, Manager, Team).

#### Acceptance Criteria

1. WHEN processing CID mapping data, THE System SHALL extract the mapping between CID, Alias, Mgr, and Team from the specified Excel sheet
2. WHEN aggregating data by Alias, THE System SHALL sum all metrics for CIDs assigned to that Alias
3. WHEN aggregating data by Mgr, THE System SHALL sum all metrics for Aliases assigned to that Mgr
4. WHEN aggregating data by Team, THE System SHALL sum all metrics for all members of that Team
5. WHEN a CID appears in Sourcing data but not in the mapping file, THE System SHALL flag this as unmapped and exclude it from hierarchy aggregations

### Requirement 6: Promotion OPS Target Calculation

**User Story:** As a sales representative, I want the system to calculate Promotion OPS targets based on suppression benchmarks, so that I can understand the realistic sales potential if suppression issues are addressed.

#### Acceptance Criteria

1. WHEN calculating Promotion OPS Target, THE System SHALL apply the formula: T30_GMS_Target × (benchmark_no_suppression_% × 0.5343 + benchmark_oos_% × 0.2807 + benchmark_vrp_missing_% × 0.0963 + benchmark_price_error_% × 0.2750 + benchmark_others_% × 0.1801)
2. WHEN suppression coefficients are updated, THE System SHALL recalculate all Promotion OPS Targets using the new coefficients
3. WHEN calculating at aggregated levels (Alias, Mgr, Team), THE System SHALL sum the Promotion OPS Targets of all constituent CIDs
4. THE System SHALL display both T30 GMS Target and Promotion OPS Target for comparison

### Requirement 7: Current Suppression Status Analysis

**User Story:** As a sales representative, I want the system to analyze current suppression status by ASIN and CID, so that I can identify which suppression issues are most impactful.

#### Acceptance Criteria

1. WHEN analyzing current suppression, THE System SHALL extract suppression_category_large values (1-5) for each ASIN from Sourcing data
2. WHEN aggregating by CID, THE System SHALL calculate the percentage of ASINs in each suppression category
3. WHEN aggregating by CID×PF, THE System SHALL calculate suppression percentages separately for each Product Family
4. WHEN comparing to benchmark, THE System SHALL calculate the difference between current suppression percentages and benchmark percentages for each category
5. THE System SHALL identify the suppression categories with the largest negative impact (high percentage in OOS, Price Error, Others)

### Requirement 8: Sourcing-Based Bridge Plan Generation

**User Story:** As a sales representative, I want the system to generate sourcing-based bridge plans, so that I can identify which ASINs to recruit for upcoming events to close my sales gap.

#### Acceptance Criteria

1. WHEN generating a Sourcing bridge plan, THE System SHALL calculate the gap between current T30 GMS BAU and T30 GMS Target for the selected aggregation level
2. WHEN identifying candidate ASINs, THE System SHALL prioritize ASINs with recent event participation flags (Y in sshve1_flag, fy26_mde2_flag, etc.)
3. WHEN ranking ASINs for sourcing, THE System SHALL consider both T30 GMS BAU value (higher is better) and event participation recency (more recent is better)
4. WHEN the gap can be closed through sourcing, THE System SHALL generate a list of recommended ASINs with their expected contribution to closing the gap
5. WHEN the gap cannot be fully closed through available sourcing candidates, THE System SHALL indicate the remaining gap and suggest supplementing with suppression optimization

### Requirement 9: Suppression-Based Bridge Plan Generation

**User Story:** As a sales representative, I want the system to generate suppression-based bridge plans, so that I can understand how reducing operational issues can help achieve my sales targets.

#### Acceptance Criteria

1. WHEN generating a Suppression bridge plan, THE System SHALL calculate the gap between current Promotion OPS and Promotion OPS Target
2. WHEN analyzing suppression opportunities, THE System SHALL prioritize reducing Price Error percentage and increasing No suppression percentage
3. WHEN recommending suppression improvements, THE System SHALL calculate the expected sales impact of moving ASINs from problematic categories (Price Error, OOS) to No suppression
4. WHEN the gap can be closed through suppression optimization, THE System SHALL generate specific recommendations for how much to reduce each suppression category percentage
5. WHEN recommending percentage changes, THE System SHALL ensure the total suppression percentages sum to 100%

### Requirement 10: Multi-Pattern Bridge Plan Generation

**User Story:** As a sales representative, I want the system to generate multiple bridge plan patterns, so that I can compare different strategies and choose the most feasible approach.

#### Acceptance Criteria

1. THE System SHALL generate Pattern 1 (Sourcing-focused): Achieve target primarily through recruiting high-potential ASINs
2. THE System SHALL generate Pattern 2 (Suppression-focused): Achieve target primarily through reducing suppression issues
3. WHERE feasible, THE System SHALL generate Pattern 3 (Balanced): Achieve target through a combination of sourcing and suppression optimization
4. WHEN displaying patterns, THE System SHALL show the expected contribution from each approach (sourcing vs suppression) as both absolute values and percentages
5. WHEN a pattern is not feasible (e.g., insufficient sourcing candidates), THE System SHALL indicate why and suggest alternative patterns

### Requirement 11: Multi-Level Aggregation Support

**User Story:** As a sales representative or manager, I want to generate bridge plans at different organizational levels, so that I can plan at the appropriate scope for my role.

#### Acceptance Criteria

1. THE System SHALL support bridge plan generation at CID level (individual seller)
2. THE System SHALL support bridge plan generation at Alias level (individual sales representative)
3. THE System SHALL support bridge plan generation at Mgr level (manager overseeing multiple representatives)
4. THE System SHALL support bridge plan generation at Team level (entire team)
5. WHEN generating plans at aggregated levels, THE System SHALL provide drill-down capability to see constituent lower-level plans

### Requirement 12: AI-Powered Recommendations

**User Story:** As a sales representative, I want the system to provide AI-powered recommendations based on historical data, so that I receive realistic and actionable guidance.

#### Acceptance Criteria

1. WHEN generating sourcing recommendations, THE System SHALL use event participation history to assess likelihood of ASIN participation
2. WHEN generating suppression recommendations, THE System SHALL prioritize actions with the highest expected sales impact based on coefficients
3. WHEN recommending suppression improvements, THE System SHALL suggest specific, actionable steps (e.g., "Reduce Price Error from 15% to 10% by fixing pricing for top 20 ASINs")
4. WHEN historical data shows low participation rates for certain ASIN categories, THE System SHALL adjust sourcing recommendations accordingly
5. THE System SHALL provide confidence levels or feasibility scores for each recommendation

### Requirement 13: Report Generation and Export

**User Story:** As a sales representative, I want to export bridge plans in a clear format, so that I can share them with my team and track progress.

#### Acceptance Criteria

1. WHEN a bridge plan is generated, THE System SHALL create a report showing current status, target, gap, and recommended actions
2. WHEN exporting a report, THE System SHALL support CSV format for data analysis
3. WHEN exporting a report, THE System SHALL support Excel format with formatted tables and charts
4. WHEN exporting a report, THE System SHALL include all relevant metrics (T30 GMS BAU, T30 GMS Target, Promotion OPS Target, suppression percentages, recommended ASINs)
5. THE System SHALL support Japanese language in all exported reports

### Requirement 14: Configuration Management

**User Story:** As a system administrator, I want to configure event-specific parameters, so that the system can be adapted for different promotional events.

#### Acceptance Criteria

1. THE System SHALL allow configuration of suppression coefficients for each event
2. THE System SHALL allow configuration of data file paths
3. THE System SHALL allow configuration of which event participation flags to prioritize
4. WHEN configuration is updated, THE System SHALL validate that all required parameters are present
5. THE System SHALL persist configuration settings between sessions

### Requirement 15: User Interface and Visualization

**User Story:** As a sales representative, I want an intuitive interface with clear visualizations, so that I can quickly understand my performance and recommended actions.

#### Acceptance Criteria

1. WHEN viewing bridge plans, THE System SHALL display current vs target metrics with visual indicators (progress bars, charts)
2. WHEN comparing patterns, THE System SHALL display them side-by-side for easy comparison
3. WHEN viewing suppression analysis, THE System SHALL display suppression category breakdowns as stacked bar charts or pie charts
4. THE System SHALL support Japanese language in all user interface elements
5. WHEN displaying large datasets, THE System SHALL provide filtering and sorting capabilities

### Requirement 16: Performance and Scalability

**User Story:** As a sales representative, I want the system to process large datasets efficiently, so that I can generate bridge plans quickly without long wait times.

#### Acceptance Criteria

1. WHEN loading CSV files with over 100,000 rows, THE System SHALL complete loading within 30 seconds
2. WHEN generating bridge plans at Team level (aggregating hundreds of CIDs), THE System SHALL complete calculation within 60 seconds
3. WHEN processing Excel files, THE System SHALL handle files up to 50MB in size
4. THE System SHALL display progress indicators for operations taking longer than 5 seconds
5. WHEN memory usage exceeds safe thresholds, THE System SHALL process data in chunks to avoid crashes
