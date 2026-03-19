# Implementation Plan: Bridge Plan Generator

## Overview

This implementation plan breaks down the Bridge Plan Generator into discrete coding tasks. The system will be built in Python using pandas for data processing, with a modular architecture that separates data loading, processing, plan generation, and reporting. Each task builds incrementally, with testing integrated throughout to catch errors early.

## Tasks

- [x] 1. Set up project structure and core data models
  - Create directory structure (src/, tests/, config/)
  - Define data models using Python dataclasses (ASINData, CIDData, BridgePlan, etc.)
  - Set up configuration management (Config class with JSON serialization)
  - Create requirements.txt with dependencies (pandas, openpyxl, pytest, hypothesis)
  - _Requirements: 14.1, 14.2, 14.3, 14.5_

- [ ]* 1.1 Write property test for configuration round-trip
  - **Property 7: Configuration Round-Trip**
  - **Validates: Requirements 4.4, 14.1, 14.2, 14.3, 14.5**

- [ ]* 1.2 Write unit tests for configuration validation
  - Test missing required parameters
  - Test invalid coefficient values
  - _Requirements: 14.4_

- [x] 2. Implement data loader module
  - [x] 2.1 Create DataLoader class with methods for loading CSV and Excel files
    - Implement load_sourcing_data() with UTF-8 encoding support
    - Implement load_target_data()
    - Implement load_suppression_benchmark()
    - Implement load_cid_mapping() with Excel sheet reading
    - _Requirements: 1.1, 1.2, 1.3, 1.4_
  
  - [x] 2.2 Implement column validation logic
    - Create validate_required_columns() method
    - Return descriptive errors for missing columns
    - _Requirements: 1.5, 1.7_
  
  - [ ]* 2.3 Write property test for column validation completeness
    - **Property 1: Column Validation Completeness**
    - **Validates: Requirements 1.5, 1.7**
  
  - [ ]* 2.4 Write property test for file error descriptiveness
    - **Property 2: File Error Descriptiveness**
    - **Validates: Requirements 1.6**
  
  - [ ]* 2.5 Write unit tests for data loading
    - Test loading valid CSV files
    - Test loading valid Excel files
    - Test error handling for missing files
    - Test Japanese character encoding
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.6, 1.8_

- [x] 3. Implement sourcing data processor
  - [x] 3.1 Create SourcingProcessor class
    - Implement extract_t30_gms_bau() to extract column T values
    - Implement extract_event_flags() for all participation flags
    - Implement calculate_participation_score() with recency weighting
    - Implement aggregate_by_cid() to sum T30 GMS BAU by CID
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [ ]* 3.2 Write property test for event participation score monotonicity
    - **Property 3: Event Participation Score Monotonicity**
    - **Validates: Requirements 2.3, 2.4**
  
  - [ ]* 3.3 Write property test for participation history influence
    - **Property 25: Participation History Influence**
    - **Validates: Requirements 12.1**
  
  - [ ]* 3.4 Write unit tests for sourcing processor
    - Test extraction with specific flag combinations
    - Test participation score calculation with known inputs
    - Test aggregation with sample data
    - _Requirements: 2.1, 2.2, 2.5_

- [x] 4. Implement target and gap calculation
  - [x] 4.1 Create TargetProcessor class
    - Implement extract_targets() to get T30 GMS Target by CID
    - Implement calculate_gaps() to compute target - current
    - Implement identify_missing_targets() for data consistency checks
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  
  - [ ]* 4.2 Write property test for gap calculation correctness
    - **Property 5: Gap Calculation Correctness**
    - **Validates: Requirements 3.3, 8.1, 9.1**
  
  - [ ]* 4.3 Write property test for data inconsistency detection
    - **Property 19: Data Inconsistency Detection**
    - **Validates: Requirements 3.2**
  
  - [ ]* 4.4 Write unit tests for edge cases
    - Test negative gaps (target already achieved)
    - Test zero targets
    - Test missing CIDs in target data
    - _Requirements: 3.2, 3.4_

- [x] 5. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement suppression data processor
  - [x] 6.1 Create SuppressionProcessor class
    - Implement extract_benchmark_percentages() from benchmark data
    - Implement validate_percentage_sum() with 1% tolerance
    - Implement calculate_current_suppression() from ASIN suppression categories
    - Implement aggregate_by_cid_pf() for Product Family breakdowns
    - _Requirements: 4.1, 4.2, 7.1, 7.2, 7.3, 7.4_
  
  - [ ]* 6.2 Write property test for percentage sum invariant
    - **Property 6: Percentage Sum Invariant**
    - **Validates: Requirements 4.2, 7.2, 9.5**
  
  - [ ]* 6.3 Write property test for suppression percentage calculation
    - **Property 10: Suppression Percentage Calculation**
    - **Validates: Requirements 7.2**
  
  - [ ]* 6.4 Write property test for suppression difference correctness
    - **Property 11: Suppression Difference Correctness**
    - **Validates: Requirements 7.4**
  
  - [ ]* 6.5 Write unit tests for suppression processor
    - Test percentage extraction from benchmark
    - Test validation with percentages summing to 100%
    - Test validation with percentages not summing to 100%
    - Test current suppression calculation
    - _Requirements: 4.1, 4.2, 7.1, 7.2_

- [x] 7. Implement hierarchy mapping and aggregation
  - [x] 7.1 Create HierarchyProcessor class
    - Implement build_hierarchy_map() to create CID→Alias→Mgr→Team mappings
    - Implement aggregate_by_alias() to sum metrics by Alias
    - Implement aggregate_by_manager() to sum metrics by Mgr
    - Implement aggregate_by_team() to sum metrics by Team
    - Handle unmapped CIDs by excluding them from aggregations
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ]* 7.2 Write property test for aggregation preservation
    - **Property 4: Aggregation Preservation**
    - **Validates: Requirements 2.5, 5.2, 5.3, 5.4, 6.3**
  
  - [ ]* 7.3 Write property test for unmapped CID exclusion
    - **Property 18: Unmapped CID Exclusion**
    - **Validates: Requirements 5.5**
  
  - [ ]* 7.4 Write unit tests for hierarchy aggregation
    - Test aggregation with known mappings
    - Test multi-level aggregation (CID→Alias→Mgr→Team)
    - Test handling of unmapped CIDs
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 8. Implement Promotion OPS calculation
  - [x] 8.1 Create PromotionOPSCalculator class
    - Implement calculate_promotion_ops_target() using the weighted formula
    - Implement calculate_current_promotion_ops() for current state
    - Support configurable coefficients
    - _Requirements: 6.1, 6.2_
  
  - [ ]* 8.2 Write property test for Promotion OPS formula correctness
    - **Property 8: Promotion OPS Formula Correctness**
    - **Validates: Requirements 6.1**
  
  - [ ]* 8.3 Write property test for coefficient update propagation
    - **Property 9: Coefficient Update Propagation**
    - **Validates: Requirements 6.2**
  
  - [ ]* 8.4 Write unit tests for Promotion OPS calculation
    - Test calculation with known inputs and expected outputs
    - Test with different coefficient sets
    - Test aggregation of Promotion OPS at different levels
    - _Requirements: 6.1, 6.2, 6.3_

- [x] 9. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Implement sourcing plan generator
  - [x] 10.1 Create SourcingPlanGenerator class
    - Implement rank_asins_by_potential() considering T30 GMS BAU and participation score
    - Implement calculate_expected_contribution() to estimate ASIN contributions
    - Implement generate_plan() to create sourcing recommendations
    - Calculate remaining gap after sourcing
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [ ]* 10.2 Write property test for sourcing recommendation ranking
    - **Property 12: Sourcing Recommendation Ranking**
    - **Validates: Requirements 8.2, 8.3**
  
  - [ ]* 10.3 Write property test for sourcing contribution sum
    - **Property 13: Sourcing Contribution Sum**
    - **Validates: Requirements 8.4**
  
  - [ ]* 10.4 Write property test for remaining gap calculation
    - **Property 14: Remaining Gap Calculation**
    - **Validates: Requirements 8.5**
  
  - [ ]* 10.5 Write unit tests for sourcing plan generator
    - Test ranking with specific ASIN combinations
    - Test gap closure scenarios
    - Test insufficient sourcing candidates scenario
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 11. Implement suppression plan generator
  - [x] 11.1 Create SuppressionPlanGenerator class
    - Implement identify_improvement_opportunities() prioritizing Price Error and No suppression
    - Implement calculate_impact_of_reduction() to estimate sales impact
    - Implement generate_plan() to create suppression recommendations
    - Ensure recommended percentages sum to 100%
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [ ]* 11.2 Write property test for suppression impact prioritization
    - **Property 15: Suppression Impact Prioritization**
    - **Validates: Requirements 9.2, 12.2**
  
  - [ ]* 11.3 Write property test for suppression improvement sum
    - **Property 16: Suppression Improvement Sum**
    - **Validates: Requirements 9.4**
  
  - [ ]* 11.4 Write unit tests for suppression plan generator
    - Test opportunity identification
    - Test impact calculation with known coefficients
    - Test percentage sum constraint
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 12. Implement bridge plan orchestrator
  - [x] 12.1 Create BridgePlanOrchestrator class
    - Implement generate_sourcing_focused_pattern() (Pattern 1)
    - Implement generate_suppression_focused_pattern() (Pattern 2)
    - Implement generate_balanced_pattern() (Pattern 3)
    - Implement generate_all_patterns() to create multiple patterns
    - Calculate feasibility scores for each pattern
    - Include confidence levels in recommendations
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 12.5_
  
  - [ ]* 12.2 Write property test for pattern contribution accuracy
    - **Property 17: Pattern Contribution Accuracy**
    - **Validates: Requirements 10.4**
  
  - [ ]* 12.3 Write property test for recommendation confidence inclusion
    - **Property 24: Recommendation Confidence Inclusion**
    - **Validates: Requirements 12.5**
  
  - [ ]* 12.4 Write unit tests for pattern generation
    - Test Pattern 1 (Sourcing-focused) generation
    - Test Pattern 2 (Suppression-focused) generation
    - Test Pattern 3 (Balanced) generation
    - Test infeasible pattern handling
    - _Requirements: 10.1, 10.2, 10.3, 10.5_

- [x] 13. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 14. Implement report generator and visualizations
  - [x] 14.1 Create ReportGenerator class
    - Implement generate_summary_report() with all required fields
    - Implement export_to_csv() with UTF-8 encoding for Japanese
    - Implement export_to_excel() with openpyxl for formatted output
    - Ensure all metrics are included in exports
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_
  
  - [ ]* 14.2 Create Visualizer class
    - Implement create_gap_chart() for current vs target visualization
    - Implement create_suppression_breakdown() for category distribution
    - Implement create_pattern_comparison() for side-by-side pattern comparison
    - _Requirements: 15.1, 15.2, 15.3_
  
  - [ ]* 14.3 Write property test for report export round-trip (CSV)
    - **Property 20: Report Export Round-Trip**
    - **Validates: Requirements 13.2**
  
  - [ ]* 14.4 Write property test for Excel export round-trip
    - **Property 21: Excel Export Round-Trip**
    - **Validates: Requirements 13.3, 13.5**
  
  - [ ]* 14.5 Write property test for report completeness
    - **Property 22: Report Completeness**
    - **Validates: Requirements 13.1, 13.4**
  
  - [ ]* 14.6 Write unit tests for report generation
    - Test CSV export with Japanese characters
    - Test Excel export with formatted tables
    - Test report contains all required fields
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

- [x] 15. Implement main application interface
  - [x] 15.1 Create main application entry point
    - Implement command-line interface for selecting aggregation level
    - Implement workflow: load data → process → generate plans → export reports
    - Add progress indicators for long-running operations
    - Support Japanese language in CLI prompts and messages
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 15.4_
  
  - [ ]* 15.2 Add error handling throughout the application
    - Implement file loading error handlers
    - Implement data validation error handlers
    - Implement calculation error handlers (division by zero, insufficient data)
    - Implement configuration error handlers
    - Ensure all error messages are descriptive and actionable
    - _Requirements: 1.6, 1.7, 3.2_
  
  - [ ]* 15.3 Write integration tests for complete workflows
    - Test end-to-end: load → process → generate → export
    - Test at all aggregation levels (CID, Alias, Mgr, Team)
    - Test with realistic sample data
    - Test error scenarios (missing files, invalid data)
    - _Requirements: 11.1, 11.2, 11.3, 11.4_

- [x] 16. Create sample data and documentation
  - [x] 16.1 Create sample data files
    - Create small sample dataset (10 CIDs, 50 ASINs) for testing
    - Create sample configuration file with file paths and coefficients
    - Include Japanese characters in sample data
    - _Requirements: 14.1, 14.2, 14.3_
  
  - [x] 16.2 Write user documentation
    - Create README with installation instructions
    - Document configuration file format
    - Document command-line usage
    - Provide examples of running the application
    - Document output file formats
    - Include Japanese language documentation or translation notes

- [x] 17. Final checkpoint - Ensure all tests pass
  - Run all unit tests and property tests
  - Run integration tests with sample data
  - Verify Japanese character support throughout
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties with randomized inputs
- Unit tests validate specific examples, edge cases, and error conditions
- Integration tests validate end-to-end workflows
- Japanese language support is critical throughout (UTF-8 encoding, UI messages, reports)
- Configuration is externalized for easy adaptation to different events
- Progress indicators improve user experience for long-running operations
