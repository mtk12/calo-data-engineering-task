# Implementation Guide

This document provides a detailed explanation of each file in the Calo Data Engineering Task project and their specific functionalities.

## Core Files

### 1. `run_reports.py` - Main Entry Point

**Purpose**: Primary orchestrator that coordinates the entire data processing pipeline.

**Key Functions**:
- `generate_transaction_data(df)`: Processes raw log data to extract transaction records
  - Iterates through log entries and applies transaction parsing
  - Adds request_id and timestamp to each parsed transaction
  - Returns a pandas DataFrame with structured transaction data

- `generate_error_data(df)`: Extracts error-specific data from log entries
  - Filters log entries with ERROR level
  - Parses balance synchronization error messages
  - Returns DataFrame containing error records with balance discrepancies

- `main(input_dir, output_dir)`: Main execution function
  - Walks through input directory to find compressed log files (.gz)
  - Reads and decompresses log files
  - Parses logs using regex patterns
  - Generates transaction and error datasets
  - Orchestrates user analysis and report generation
  - Creates Excel reports and visualizations

**Command Line Interface**: 
- Accepts input directory (containing .gz log files) and output directory parameters
- Provides help documentation for usage

### 2. `parser.py` - Log Parsing Engine

**Purpose**: Core parsing utilities that extract structured data from raw log entries using regex patterns.

**Key Components**:
- `LOG_PATTERN`: Master regex pattern for parsing log entry headers
  - Extracts timestamp, type, request_id, version, and log_level
  - Handles duplicate fields and various log formats

- `TRANSACTION_PATTERN`: Dictionary of regex patterns for transaction data extraction
  - Parses transaction fields: id, type, source, action, userId
  - Extracts financial data: paymentBalance, amount, vat, oldBalance, newBalance
  - Handles metadata and currency information

**Key Functions**:
- `parse_logs(log_text)`: Master log parsing function
  - Splits log text into individual entries
  - Applies LOG_PATTERN to extract header information
  - Processes inline and multiline log content
  - Returns structured DataFrame with parsed log entries

- `parse_transaction(message)`: Transaction-specific parser
  - Applies TRANSACTION_PATTERN to extract transaction details
  - Converts numeric fields to appropriate data types
  - Handles boolean conversion for updatePaymentBalance
  - Returns dictionary with transaction data

- `parse_balance_sync_message(message)`: Error message parser
  - Extracts userId, subscriptionBalance, and paymentBalance from error logs
  - Handles balance synchronization discrepancies
  - Returns dictionary with balance sync error data

### 3. `analysis.py` - Data Analysis and Visualization Engine

**Purpose**: Comprehensive analytics module that generates insights and visualizations from transaction and error data.

**Visualization Functions**:

- `transaction_count_over_period(parsed_df, output_dir, output_file_name)`:
  - Creates bar chart showing daily transaction volumes
  - Groups transactions by date and counts occurrences
  - Saves chart as PNG and embeds in Excel report

- `credit_transactions_over_period(parsed_df, output_dir, output_file_name)`:
  - Analyzes credit transaction patterns over time
  - Filters for CREDIT type transactions
  - Generates time-series visualization

- `debit_transactions_over_period(parsed_df, output_dir, output_file_name)`:
  - Analyzes debit transaction patterns over time
  - Filters for DEBIT type transactions
  - Creates complementary visualization to credit analysis

- `transactions_by_action_over_period(parsed_df, output_dir, output_file_name)`:
  - Groups transactions by action type (e.g., payment, refund)
  - Creates stacked bar chart showing action distribution over time

- `top_users_transacting(parsed_df, output_dir, output_file_name)`:
  - Identifies users with highest transaction volumes
  - Creates horizontal bar chart of top transacting users

**Error Analysis Functions**:

- `error_transactions_over_period(error_df, output_dir, output_file_name)`:
  - Analyzes error transaction patterns over time
  - Includes anomaly detection for unusual error spikes
  - Highlights periods with abnormal error rates

- `error_transactions_by_action(error_df, parsed_df, output_dir, output_file_name, top_n=10)`:
  - Identifies which transaction actions generate most errors
  - Cross-references error data with transaction data
  - Shows top N error-prone actions

- `top_users_error_transactions(error_df, output_dir, output_file_name)`:
  - Identifies users with highest error rates
  - Helps pinpoint problematic user accounts

**Financial Impact Analysis**:

- `total_debit_credit_loss(user_analysis_df, output_dir, output_file_name)`:
  - Calculates total financial losses from balance sync errors
  - Separates debit and credit losses
  - Provides overall financial impact assessment

- `first_error_reason_count(user_analysis_df, output_dir, output_file_name)`:
  - Analyzes first error reasons for each user
  - Helps identify common initial failure points
  - Filters out null/nan values

**Master Function**:
- `run_complete_analysis(parsed_df, error_df, user_analysis_df, output_dir, output_file_name)`:
  - Orchestrates execution of all analysis functions
  - Ensures consistent output formatting and file naming
  - Coordinates chart generation and Excel integration

### 4. `user_analysis.py` - User-Specific Analytics

**Purpose**: Performs detailed analysis at the individual user level, tracking error patterns and financial impacts.

**Key Functions**:

- `analyze_user_data(user_id, error_data, parsed_transactions)`:
  - Comprehensive analysis for a single user
  - Filters data for specific user ID
  - Calculates user-specific metrics:
    - First and last error transaction timestamps
    - Total transaction count vs error count
    - Debit and credit loss calculations
    - Balance discrepancy analysis
  - Matches error records with transaction records using request_id
  - Implements fallback timestamp matching for unmatched records
  - Returns detailed user analysis dictionary

- `analyze_all_users(error_df, parsed_df)`:
  - Iterates through all unique users in error data
  - Applies individual user analysis to each user
  - Aggregates results into comprehensive DataFrame
  - Provides summary statistics across all users
  - Returns structured dataset for reporting

**Analysis Metrics**:
- User transaction volume and error rates
- Financial loss calculations (debit vs credit)
- Error timing patterns (first/last error analysis)
- Balance synchronization discrepancies

### 5. `reports/excel_report.py` - Report Generation

**Purpose**: Handles Excel report creation and chart embedding functionality.

**Key Functions**:

- `write_to_sheet(df, sheet_name, file_path)`:
  - Writes DataFrame to specific Excel sheet
  - Handles timezone conversion for datetime columns
  - Manages file creation and sheet replacement
  - Uses openpyxl engine for Excel operations

- `generate_excel(parsed_df, error_df, analysis_df, output_excel_file_name, output_excel_file_path)`:
  - Creates multi-sheet Excel workbook
  - Organizes data into logical sheets:
    - "user_wise_error_analysis_data": User analysis results
    - "transaction_data": Raw transaction data
    - "error_data": Error records
  - Ensures consistent file naming and path handling

- `insert_chart_to_excel(output_excel_file_path, output_excel_file_name, sheet_name, image_path, cell)`:
  - Embeds PNG charts into Excel worksheets
  - Creates new sheets if they don't exist
  - Positions charts at specified cell locations
  - Handles workbook loading and saving operations

## Configuration Files

### 6. `requirements.txt` - Dependencies

**Purpose**: Defines Python package dependencies and versions.

**Key Dependencies**:
- `pandas>=1.5.0`: Data manipulation and analysis
- `matplotlib`: Chart and visualization generation
- `seaborn`: Statistical data visualization
- `plotly>=5.0.0`: Interactive plotting capabilities
- `openpyxl`: Excel file operations
- `Jinja2>=3.0.0`: Template engine for reports
- `python-dateutil>=2.8.0`: Date parsing utilities

### 7. `Dockerfile` - Container Configuration

**Purpose**: Defines containerized execution environment.

**Configuration**:
- Base image: `python:3.10-slim`
- Working directory: `/app`
- Installs dependencies from requirements.txt
- Copies application code
- Sets entry point to `run_reports.py`
- Optimized for log processing workloads

## Data Flow Architecture

1. **Input Processing**: `run_reports.py` reads compressed log files
2. **Log Parsing**: `parser.py` extracts structured data using regex patterns
3. **Data Generation**: Transaction and error datasets are created
4. **User Analysis**: `user_analysis.py` performs user-specific calculations
5. **Analytics**: `analysis.py` generates insights and visualizations
6. **Report Generation**: `reports/excel_report.py` creates Excel outputs
7. **Output**: Multi-sheet Excel report with embedded charts

## Error Handling and Data Quality

- Robust regex patterns handle various log formats
- Type conversion with error handling for numeric fields
- Fallback mechanisms for unmatched records
- Data validation and cleaning throughout pipeline
- Comprehensive logging for debugging and monitoring

## Performance Considerations

- Efficient pandas operations for large datasets
- Memory-conscious processing of compressed files
- Optimized chart generation with appropriate DPI settings
- Batch processing capabilities for multiple log files
