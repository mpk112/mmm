# Marketing Mix Modeling Analysis

A comprehensive Python-based Marketing Mix Modeling (MMM) system that evaluates marketing channel effectiveness and ROI to optimize budget allocation.

## Overview

This system analyzes historical marketing spend data across multiple channels (TV, Radio, Facebook, Instagram, Google Search, Google Play, YouTube, Display) to:

- Quantify each channel's contribution to customer acquisition
- Calculate return on investment (ROI) with confidence intervals
- Model advertising carryover effects (adstock) and diminishing returns (saturation)
- Optimize budget allocation to maximize customer acquisition
- Generate comprehensive reports with publication-quality visualizations

## Features

- **Data Validation**: Robust CSV loading with schema and quality checks
- **Exploratory Analysis**: Descriptive statistics, correlations, seasonality detection, outlier identification
- **Statistical Modeling**: Multiple model specifications (baseline, adstock, saturation, full) with automatic selection
- **Marketing Transformations**: Adstock (carryover effects) and Hill saturation curves (diminishing returns)
- **Model Diagnostics**: Comprehensive validation including residual analysis, VIF, cross-validation
- **Attribution Analysis**: Channel contribution calculation with ROI and confidence intervals
- **Budget Optimization**: Constrained optimization to maximize customer acquisition
- **Visualizations**: 7 publication-quality charts (time series, correlations, ROI, response curves, diagnostics)
- **Reporting**: Comprehensive Markdown report with insights and recommendations

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Setup

1. Clone or download this repository

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the complete analysis pipeline with default settings:

```bash
python main.py
```

This will:
- Load data from `MMM dataset - Sheet1.csv`
- Save outputs to `outputs/` directory
- Use $100 as customer lifetime value

### Custom Configuration

Specify custom parameters:

```bash
python main.py --data "path/to/your/data.csv" --output-dir "results" --customer-value 150.0
```

### Command-Line Arguments

- `--data`: Path to CSV file containing MMM data (default: `MMM dataset - Sheet1.csv`)
- `--output-dir`: Directory for saving outputs (default: `outputs`)
- `--customer-value`: Customer lifetime value in dollars for ROI calculation (default: `100.0`)

### Help

View all available options:

```bash
python main.py --help
```

## Input Data Format

The input CSV file must contain the following columns:

| Column | Type | Description |
|--------|------|-------------|
| `week_start_date` | Date | Start date of the week (YYYY-MM-DD format) |
| `tv_spend` | Float | TV advertising spend ($) |
| `radio_spend` | Float | Radio advertising spend ($) |
| `facebook_spend` | Float | Facebook advertising spend ($) |
| `instagram_spend` | Float | Instagram advertising spend ($) |
| `google_search_spend` | Float | Google Search advertising spend ($) |
| `google_play_spend` | Float | Google Play advertising spend ($) |
| `youtube_spend` | Float | YouTube advertising spend ($) |
| `display_spend` | Float | Display advertising spend ($) |
| `holidays` | Integer | Holiday indicator (0 or 1) |
| `competitor_promo` | Integer | Competitor promotion indicator (0 or 1) |
| `new_customers` | Integer | Number of new customers acquired |

**Requirements**:
- Minimum 20 weeks of data
- No missing values
- No duplicate dates
- All spend values must be non-negative

## Output

The pipeline generates the following outputs in the specified output directory:

### Report
- `mmm_analysis_report.md`: Comprehensive Markdown report with:
  - Executive summary
  - Methodology documentation
  - EDA findings
  - Model performance and diagnostics
  - Attribution and ROI analysis
  - Budget optimization recommendations
  - Insights and actionable recommendations

### Visualizations (in `visualizations/` subdirectory)
1. `time_series.png`: Customer acquisition over time with control variable markers
2. `correlation_heatmap.png`: Correlation matrix between channels and customers
3. `spend_comparison.png`: Total spend by channel
4. `roi_comparison.png`: ROI by channel with confidence intervals
5. `channel_scatter_plots.png`: Spend vs customers scatter plots with trend lines
6. `response_curves.png`: Marketing response curves showing saturation effects
7. `residual_diagnostics.png`: Model diagnostic plots (4-panel)

### Log File
- `mmm_pipeline.log`: Detailed execution log with timestamps

## Project Structure

```
.
├── main.py                          # Main pipeline orchestration script
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── src/                            # Source code modules
│   ├── __init__.py
│   ├── data_loader.py              # Data ingestion and validation
│   ├── eda_module.py               # Exploratory data analysis
│   ├── statistical_modeler.py      # Statistical modeling with transformations
│   ├── attribution_engine.py       # Attribution and budget optimization
│   ├── visualization_generator.py  # Visualization creation
│   └── report_generator.py         # Report generation
├── tests/                          # Test files
│   └── __init__.py
└── outputs/                        # Generated outputs (created at runtime)
    ├── visualizations/
    └── mmm_analysis_report.md
```

## Methodology

### Statistical Models

The system evaluates four model specifications and selects the best based on AIC:

1. **Baseline Model**: Linear regression with raw spend values
2. **Adstock Model**: Incorporates advertising carryover effects using geometric decay
3. **Saturation Model**: Models diminishing returns using Hill saturation curves
4. **Full Model**: Combines both adstock and saturation transformations

### Transformations

**Adstock Transformation** (Carryover Effects):
```
adstock_t = spend_t + decay_rate × adstock_(t-1)
```

**Saturation Transformation** (Diminishing Returns):
```
saturated_spend = spend^gamma / (alpha^gamma + spend^gamma)
```

### Model Selection

- Hyperparameter optimization via grid search
- Model comparison using AIC/BIC
- Comprehensive diagnostics (normality, heteroscedasticity, multicollinearity, autocorrelation)
- 5-fold cross-validation for stability assessment

### Budget Optimization

- Sequential Least Squares Programming (SLSQP)
- Constraints: total budget, channel-specific min/max spend
- Objective: maximize customer acquisition
- Accounts for saturation effects

## Example Output

```
PIPELINE COMPLETED SUCCESSFULLY
================================================================

Output Summary:
  Report: outputs/mmm_analysis_report.md
  Visualizations: 7 charts in outputs/visualizations
  Log file: mmm_pipeline.log

Key Findings:
  Model: full (R² = 0.8234)
  Best channel: Facebook (45.2% ROI)
  Optimization lift: 12.3%
```

## Troubleshooting

### Common Issues

**Issue**: `FileNotFoundError: CSV file not found`
- **Solution**: Verify the file path is correct and the file exists

**Issue**: `ValueError: Missing required columns`
- **Solution**: Ensure your CSV has all 12 required columns with exact names

**Issue**: `ValueError: Insufficient data: dataset contains X weeks, but minimum 20 weeks required`
- **Solution**: Provide at least 20 weeks of data for reliable analysis

**Issue**: Import errors for dependencies
- **Solution**: Ensure all dependencies are installed: `pip install -r requirements.txt`

### Logging

Check `mmm_pipeline.log` for detailed execution logs including:
- Data loading and validation steps
- Model fitting progress
- Optimization convergence status
- Error messages and stack traces

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/ tests/ main.py
```

### Type Checking

```bash
mypy src/ main.py
```

### Linting

```bash
pylint src/ main.py
```

## Technical Details

### Dependencies

- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computations
- **statsmodels**: Statistical modeling and diagnostics
- **scikit-learn**: Machine learning utilities (train/test split, metrics)
- **scipy**: Optimization and statistical tests
- **matplotlib**: Plotting and visualization
- **seaborn**: Statistical data visualization

### Performance

- Typical runtime: 30-60 seconds for 50-100 weeks of data
- Memory usage: < 500 MB for typical datasets
- Scales linearly with number of weeks

### Reproducibility

- Random seed set to 42 for all stochastic operations
- Deterministic train/test splits
- Consistent optimization initialization

## License

This project is provided as-is for the Moniepoint Data Science take-home assessment.

## Contact

For questions or issues, please refer to the project documentation or contact the development team.

---

**Version**: 1.0.0  
**Last Updated**: 2024
