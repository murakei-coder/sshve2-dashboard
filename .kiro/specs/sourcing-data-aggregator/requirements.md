# Requirements Document

## Introduction

This feature provides a simple CSV data aggregation tool that reads daily-updated sourcing data and generates a pivot-table-style summary aggregated by MCID. The tool is designed to be extremely simple for Python beginners to use, following the existing project patterns of batch file execution and HTML report generation.

## Glossary

- **MCID**: Merchant/Category ID - the primary grouping dimension for aggregation
- **total_t30d_gms_BAU**: Total 30-day GMS (Gross Merchandise Sales) for Business As Usual
- **SSHVE2_SourcedFlag**: A flag column indicating whether an item is sourced (value "Y") or not
- **Sourced GMS**: The sum of total_t30d_gms_BAU where SSHVE2_SourcedFlag equals "Y"
- **Sourced GMS %**: The percentage of Sourced GMS relative to total GMS
- **Aggregator**: The system component that processes and summarizes the CSV data
- **Report_Generator**: The system component that creates HTML output

## Requirements

### Requirement 1: CSV Data Loading

**User Story:** As a user, I want to load the daily-updated CSV file, so that I can analyze the latest sourcing data.

#### Acceptance Criteria

1. WHEN the user provides a CSV file path, THE Aggregator SHALL read the file using UTF-8 encoding
2. WHEN the CSV file contains the required columns (mcid, total_t30d_gms_BAU, SSHVE2_SourcedFlag), THE Aggregator SHALL load all rows successfully
3. IF the CSV file is missing required columns, THEN THE Aggregator SHALL return a descriptive error message
4. IF the CSV file does not exist at the specified path, THEN THE Aggregator SHALL return a file not found error
5. WHEN loading the CSV file, THE Aggregator SHALL handle common encoding issues gracefully

### Requirement 2: Data Aggregation by MCID

**User Story:** As a user, I want to aggregate data by MCID, so that I can see summarized metrics for each merchant/category.

#### Acceptance Criteria

1. WHEN the data is loaded, THE Aggregator SHALL group all rows by the mcid column
2. FOR each MCID group, THE Aggregator SHALL calculate the sum of total_t30d_gms_BAU
3. FOR each MCID group, THE Aggregator SHALL calculate the sum of total_t30d_gms_BAU where SSHVE2_SourcedFlag equals "Y"
4. FOR each MCID group, THE Aggregator SHALL calculate the percentage as (Sourced GMS / Total GMS) * 100
5. WHEN total_t30d_gms_BAU contains non-numeric values, THE Aggregator SHALL treat them as zero
6. WHEN total GMS is zero for an MCID, THE Aggregator SHALL set Sourced GMS % to zero

### Requirement 3: Output Generation

**User Story:** As a user, I want to see the aggregated results in an HTML report, so that I can easily view and share the analysis.

#### Acceptance Criteria

1. WHEN aggregation is complete, THE Report_Generator SHALL create an HTML file with a table displaying the results
2. THE Report_Generator SHALL include three columns in the output: Total GMS, Sourced GMS, and Sourced GMS %
3. THE Report_Generator SHALL include the MCID as the first column in the output table
4. THE Report_Generator SHALL format numeric values with thousand separators for readability
5. THE Report_Generator SHALL format percentage values with two decimal places
6. THE Report_Generator SHALL include a timestamp showing when the report was generated
7. THE Report_Generator SHALL save the HTML file with a timestamped filename

### Requirement 4: Simple Execution Interface

**User Story:** As a Python beginner, I want to run the tool with a simple batch file, so that I don't need to understand complex command-line arguments.

#### Acceptance Criteria

1. THE System SHALL provide a Windows batch file for execution
2. WHEN the user double-clicks the batch file, THE System SHALL prompt for the CSV file path
3. WHEN the batch file runs, THE System SHALL display progress messages in the console
4. WHEN processing is complete, THE System SHALL display the output file location
5. WHEN an error occurs, THE System SHALL display a user-friendly error message in Japanese
6. THE System SHALL pause at the end to allow the user to read the output

### Requirement 5: Data Validation

**User Story:** As a user, I want the system to validate input data, so that I can identify data quality issues early.

#### Acceptance Criteria

1. WHEN the CSV is loaded, THE Aggregator SHALL check that mcid column exists
2. WHEN the CSV is loaded, THE Aggregator SHALL check that total_t30d_gms_BAU column exists
3. WHEN the CSV is loaded, THE Aggregator SHALL check that SSHVE2_SourcedFlag column exists
4. WHEN validation fails, THE Aggregator SHALL report which columns are missing
5. WHEN the CSV contains no data rows, THE Aggregator SHALL return an error message

### Requirement 6: Excel Export

**User Story:** As a user, I want to export results to Excel, so that I can perform additional analysis in spreadsheet software.

#### Acceptance Criteria

1. WHEN aggregation is complete, THE Report_Generator SHALL create an Excel file with the aggregated data
2. THE Report_Generator SHALL include the same columns as the HTML report
3. THE Report_Generator SHALL apply number formatting to numeric columns in Excel
4. THE Report_Generator SHALL apply percentage formatting to the Sourced GMS % column
5. THE Report_Generator SHALL save the Excel file with a timestamped filename matching the HTML report

### Requirement 7: Integration with Existing Project Structure

**User Story:** As a developer, I want the tool to follow existing project patterns, so that it integrates seamlessly with other analysis tools.

#### Acceptance Criteria

1. THE System SHALL place the main script in the src/ directory
2. THE System SHALL place the batch file in the project root directory
3. THE System SHALL use the existing requirements.txt for dependency management
4. THE System SHALL follow the same logging pattern as other analysis scripts
5. THE System SHALL generate output files in the same directory as the input file by default
6. WHERE an output directory is specified, THE System SHALL create output files in that directory
