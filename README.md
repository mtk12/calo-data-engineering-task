# Calo Data Engineering Task

A comprehensive data engineering solution for analyzing balance synchronization logs and transaction data. This project processes log files, extracts transaction patterns, identifies errors, and generates detailed analytical reports with visualizations.

## Features

- **Log Parsing**: Intelligent parsing of compressed log files using regex patterns
- **Transaction Analysis**: Comprehensive analysis of credit/debit transactions over time
- **Error Detection**: Identification and analysis of balance synchronization errors
- **User Analytics**: User-specific analysis including error tracking and loss calculations
- **Visualization**: Automated generation of charts and graphs for data insights
- **Excel Reporting**: Professional Excel reports with embedded charts and multiple data sheets
- **Docker Support**: Containerized execution for consistent deployment

## Project Structure

```
├── analysis.py              # Core analysis functions and chart generation
├── user_analysis.py         # User-specific analysis and metrics
├── parser.py               # Log parsing utilities with regex patterns
├── run_reports.py          # Main entry point for report generation
├── reports/
│   ├── __init__.py
│   └── excel_report.py     # Excel report generation and chart embedding
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
└── README.md              # Project documentation
```

## Analytics Generated

### Transaction Analysis
- Transaction count over time periods
- Credit vs Debit transaction trends
- Transaction patterns by action type
- Top users by transaction volume

### Error Analysis
- Error transaction detection with anomaly identification
- Error patterns by action type
- User-specific error analysis
- Balance synchronization loss calculations

### Reporting
- Multi-sheet Excel reports with:
  - Raw transaction data
  - Error data analysis
  - User-wise error analysis
  - Embedded visualization charts

## Requirements

- Python 3.10+
- Dependencies listed in `requirements.txt`:
  - pandas>=1.5.0
  - matplotlib
  - seaborn
  - plotly>=5.0.0
  - openpyxl
  - Jinja2>=3.0.0
  - python-dateutil>=2.8.0

## Usage

### Local Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run analysis:
```bash
python run_reports.py <input_directory> <output_directory>
```

**Parameters:**
- `input_directory`: Directory containing compressed log files (.gz)
- `output_directory`: Directory where reports and charts will be generated

### Docker Usage

#### Build Docker Image
```bash
docker build -t calo-data-engineering .
```

#### Run Analysis with Docker
```bash
docker run -v /path/to/logs:/app/input -v /path/to/output:/app/output calo-data-engineering /app/input /app/output
```

**Volume Mounts:**
- `/path/to/logs`: Local directory containing your log files
- `/path/to/output`: Local directory where reports will be saved

## Output

The analysis generates:

1. **Excel Report** (`balance_sync_analytics_report.xlsx`):
   - Transaction data sheet
   - Error data sheet  
   - User-wise error analysis sheet
   - Embedded charts and visualizations

2. **Chart Images** (PNG format):
   - Transaction count over time
   - Credit/Debit transaction trends
   - Error transaction patterns
   - User analysis visualizations

## Log File Format

The system processes log files with the following structure:
- Timestamp-based entries
- Transaction records with metadata
- Balance synchronization messages
- Error tracking information

## Development

### Adding New Analysis

1. Create analysis functions in `analysis.py`
2. Add chart generation with `matplotlib`/`seaborn`
3. Integrate with Excel reporting in `reports/excel_report.py`
4. Update the main analysis runner in `run_complete_analysis()`

### Extending Parsers

Modify regex patterns in `parser.py` to handle new log formats or additional data fields.
