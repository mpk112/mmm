# Design Document: Marketing Mix Modeling Analysis

## Overview

This document specifies the design for a Marketing Mix Modeling (MMM) analysis system that evaluates marketing channel effectiveness and ROI. The system implements a modular Python-based architecture with clear separation between data ingestion, exploratory analysis, statistical modeling, attribution calculation, visualization, and reporting.

The design emphasizes:
- **Modularity**: Independent components with well-defined interfaces
- **Statistical rigor**: Proper implementation of adstock transformations, saturation curves, and model diagnostics
- **Reproducibility**: Deterministic results with proper random seed management
- **Testability**: Pure functions and clear data flows enabling comprehensive testing
- **Professional output**: Publication-quality visualizations and comprehensive reporting

## Architecture

### System Architecture

The MMM system follows a pipeline architecture with six primary components:

```
┌─────────────┐
│ Data_Loader │
└──────┬──────┘
       │ validated_data
       ▼
┌─────────────┐
│ EDA_Module  │
└──────┬──────┘
       │ eda_results
       ▼
┌──────────────────┐
│Statistical_Modeler│
└──────┬───────────┘
       │ model_results
       ▼
┌──────────────────┐
│Attribution_Engine│
└──────┬───────────┘
       │ attribution_results
       ▼
┌────────────────────────┐
│Visualization_Generator │
└──────┬─────────────────┘
       │ visualization_paths
       ▼
┌─────────────────┐
│Report_Generator │
└─────────────────┘
```

### Component Interactions

1. **Data_Loader** reads and validates CSV data, producing a clean DataFrame
2. **EDA_Module** consumes validated data and produces statistical summaries
3. **Statistical_Modeler** builds regression models with transformations
4. **Attribution_Engine** uses model coefficients to calculate ROI and optimize budgets
5. **Visualization_Generator** creates charts from all previous outputs
6. **Report_Generator** aggregates all results into a comprehensive document

### Technology Stack

- **Core**: Python 3.9+
- **Data manipulation**: pandas, numpy
- **Statistical modeling**: statsmodels, scikit-learn, scipy
- **Optimization**: scipy.optimize
- **Visualization**: matplotlib, seaborn
- **Testing**: pytest, hypothesis (for property-based testing)
- **Documentation**: Markdown, potentially reportlab for PDF generation
- **Code quality**: black (formatting), mypy (type checking), pylint (linting)

## Components and Interfaces

### 1. Data_Loader

**Responsibility**: Ingest and validate marketing data from CSV files.

**Interface**:
```python
class DataLoader:
    def load_data(self, file_path: str) -> pd.DataFrame:
        """Load and validate MMM dataset from CSV.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Validated DataFrame with proper types
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If validation fails or insufficient data
        """
        
    def validate_schema(self, df: pd.DataFrame) -> ValidationResult:
        """Validate DataFrame has required columns and types."""
        
    def validate_data_quality(self, df: pd.DataFrame) -> ValidationResult:
        """Check for missing values, duplicates, negative values."""
```

**Key Methods**:
- `_check_required_columns()`: Verify all 12 required columns present
- `_validate_numeric_columns()`: Ensure spend and customer columns are non-negative
- `_validate_date_column()`: Parse and validate date format
- `_check_duplicates()`: Detect duplicate week entries
- `_check_missing_values()`: Report any NaN values
- `_type_conversion()`: Convert columns to appropriate dtypes

**Data Contract**:
- Input: CSV with 12 columns (week_start_date, 8 spend channels, 2 control variables, new_customers)
- Output: DataFrame with datetime index, float64 for numeric columns, int64 for binary indicators
- Minimum 20 weeks of data required

### 2. EDA_Module

**Responsibility**: Perform exploratory data analysis and generate statistical summaries.

**Interface**:
```python
class EDAModule:
    def analyze(self, df: pd.DataFrame) -> EDAResults:
        """Perform comprehensive exploratory analysis.
        
        Args:
            df: Validated DataFrame from DataLoader
            
        Returns:
            EDAResults containing statistics, correlations, patterns
        """
        
    def compute_descriptive_stats(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculate mean, median, std, min, max, quartiles."""
        
    def compute_correlations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate correlation matrix between channels and customers."""
        
    def detect_outliers(self, df: pd.DataFrame) -> Dict[str, List[int]]:
        """Identify outliers using IQR method."""
        
    def analyze_seasonality(self, df: pd.DataFrame) -> SeasonalityResults:
        """Detect seasonal patterns in customer acquisition."""
        
    def analyze_control_variables(self, df: pd.DataFrame) -> ControlAnalysis:
        """Quantify impact of holidays and competitor promos."""
```

**Key Analyses**:
- Descriptive statistics for all numeric columns
- Correlation analysis (Pearson correlation coefficients)
- Time period identification (start, end, duration)
- Total spend per channel
- Outlier detection (IQR method: Q1 - 1.5*IQR, Q3 + 1.5*IQR)
- Seasonality analysis (decomposition, trend identification)
- Control variable impact (t-tests comparing means)

**Output Structure**:
```python
@dataclass
class EDAResults:
    descriptive_stats: Dict[str, pd.Series]
    correlations: pd.DataFrame
    time_period: Dict[str, Any]  # start, end, n_weeks
    total_spend_by_channel: pd.Series
    outliers: Dict[str, List[int]]  # channel -> list of week indices
    seasonality: SeasonalityResults
    control_impact: ControlAnalysis
```

### 3. Statistical_Modeler

**Responsibility**: Build and validate statistical models with marketing transformations.

**Interface**:
```python
class StatisticalModeler:
    def __init__(self, random_state: int = 42):
        """Initialize modeler with random seed for reproducibility."""
        
    def fit(self, df: pd.DataFrame, test_size: float = 0.2) -> ModelResults:
        """Fit multiple model specifications and select best.
        
        Args:
            df: Validated DataFrame
            test_size: Proportion of data for testing
            
        Returns:
            ModelResults with fitted model, coefficients, diagnostics
        """
        
    def apply_adstock_transformation(
        self, 
        spend: np.ndarray, 
        decay_rate: float
    ) -> np.ndarray:
        """Apply adstock transformation for carryover effects.
        
        Args:
            spend: Array of weekly spend values
            decay_rate: Decay parameter (0 < decay_rate < 1)
            
        Returns:
            Transformed spend with carryover effects
        """
        
    def apply_saturation_transformation(
        self,
        spend: np.ndarray,
        alpha: float,
        gamma: float
    ) -> np.ndarray:
        """Apply Hill saturation curve for diminishing returns.
        
        Args:
            spend: Array of weekly spend values
            alpha: Half-saturation point
            gamma: Shape parameter
            
        Returns:
            Transformed spend with saturation effects
        """
        
    def validate_model(self, model, X_test, y_test) -> DiagnosticsResults:
        """Perform comprehensive model diagnostics."""
```

**Transformation Specifications**:

1. **Adstock Transformation** (Geometric decay):
   ```
   adstock_t = spend_t + decay * adstock_{t-1}
   
   where decay ∈ (0, 1)
   ```
   - Captures carryover effects of advertising
   - Higher decay = longer memory
   - Implemented as recursive convolution

2. **Saturation Transformation** (Hill curve):
   ```
   saturated_spend = spend^gamma / (alpha^gamma + spend^gamma)
   
   where:
   - alpha: half-saturation point (spend level at 50% max response)
   - gamma: shape parameter (controls curve steepness)
   ```
   - Models diminishing returns
   - S-shaped response curve
   - Asymptotic behavior at high spend

**Model Specifications**:

1. **Baseline Model**:
   ```
   new_customers = β₀ + Σ(βᵢ * spendᵢ) + β_holiday * holidays + β_promo * competitor_promo + ε
   ```

2. **Adstock Model**:
   ```
   new_customers = β₀ + Σ(βᵢ * adstock(spendᵢ)) + controls + ε
   ```

3. **Saturation Model**:
   ```
   new_customers = β₀ + Σ(βᵢ * saturate(spendᵢ)) + controls + ε
   ```

4. **Full Model** (Adstock + Saturation):
   ```
   new_customers = β₀ + Σ(βᵢ * saturate(adstock(spendᵢ))) + controls + ε
   ```

**Hyperparameter Optimization**:
- Grid search over decay rates: [0.1, 0.3, 0.5, 0.7, 0.9]
- Grid search over alpha (saturation): [mean_spend * k for k in [0.5, 1.0, 1.5, 2.0]]
- Grid search over gamma (shape): [0.5, 1.0, 1.5, 2.0]
- Select parameters minimizing AIC/BIC on validation set

**Model Diagnostics**:
```python
@dataclass
class DiagnosticsResults:
    r_squared_train: float
    r_squared_test: float
    rmse_train: float
    rmse_test: float
    mae_train: float
    mae_test: float
    residual_normality_pvalue: float  # Shapiro-Wilk test
    heteroscedasticity_pvalue: float  # Breusch-Pagan test
    vif_values: Dict[str, float]  # Variance Inflation Factors
    durbin_watson: float  # Autocorrelation test
    aic: float
    bic: float
    cv_scores: List[float]  # 5-fold cross-validation R²
```

### 4. Attribution_Engine

**Responsibility**: Calculate channel contributions, ROI, and optimize budget allocation.

**Interface**:
```python
class AttributionEngine:
    def __init__(self, model_results: ModelResults, customer_value: float = 100.0):
        """Initialize with fitted model and assumed customer lifetime value."""
        
    def calculate_attribution(self, df: pd.DataFrame) -> AttributionResults:
        """Calculate marginal contribution and ROI for each channel.
        
        Returns:
            AttributionResults with contributions, ROI, rankings
        """
        
    def calculate_marginal_contribution(
        self,
        channel: str,
        df: pd.DataFrame
    ) -> float:
        """Calculate incremental customers from a channel."""
        
    def calculate_roi(
        self,
        channel: str,
        contribution: float,
        total_spend: float
    ) -> Tuple[float, Tuple[float, float]]:
        """Calculate ROI with confidence interval.
        
        Returns:
            (roi, (lower_ci, upper_ci))
        """
        
    def optimize_budget(
        self,
        total_budget: float,
        constraints: Optional[Dict[str, Tuple[float, float]]] = None
    ) -> OptimizationResults:
        """Find optimal budget allocation maximizing customer acquisition.
        
        Args:
            total_budget: Total marketing budget constraint
            constraints: Optional dict of (min_spend, max_spend) per channel
            
        Returns:
            OptimizationResults with optimal allocation and expected lift
        """
```

**Attribution Methodology**:

1. **Marginal Contribution**:
   ```
   contribution_i = Σ_t (β_i * transformed_spend_i_t)
   ```
   - Sum of predicted customers from channel i across all time periods
   - Uses model coefficients and transformed spend values

2. **ROI Calculation**:
   ```
   ROI_i = (contribution_i * customer_value - total_spend_i) / total_spend_i
   ROI_i = (contribution_i * customer_value) / total_spend_i - 1
   ```
   - Confidence intervals via bootstrap or delta method
   - Accounts for coefficient uncertainty

3. **Percentage Contribution**:
   ```
   pct_contribution_i = contribution_i / Σ_j(contribution_j)
   ```

**Optimization Algorithm**:

Use Sequential Least Squares Programming (SLSQP) from scipy.optimize:

```python
def objective(allocation: np.ndarray) -> float:
    """Negative expected customers (for minimization)."""
    transformed_spend = apply_transformations(allocation)
    predicted_customers = model.predict(transformed_spend)
    return -predicted_customers.sum()

constraints = [
    {'type': 'eq', 'fun': lambda x: x.sum() - total_budget},  # Budget constraint
    *[{'type': 'ineq', 'fun': lambda x, i=i: x[i] - min_spend[i]} 
      for i in range(n_channels)],  # Minimum spend
    *[{'type': 'ineq', 'fun': lambda x, i=i: max_spend[i] - x[i]} 
      for i in range(n_channels)]  # Maximum spend
]

result = minimize(objective, x0=initial_allocation, method='SLSQP', constraints=constraints)
```

**Output Structure**:
```python
@dataclass
class AttributionResults:
    marginal_contributions: Dict[str, float]  # channel -> customers
    roi_by_channel: Dict[str, Tuple[float, Tuple[float, float]]]  # channel -> (roi, ci)
    percentage_contributions: Dict[str, float]  # channel -> percentage
    channel_rankings: List[Tuple[str, float]]  # sorted by ROI
    optimal_spend_levels: Dict[str, float]  # channel -> optimal spend

@dataclass
class OptimizationResults:
    optimal_allocation: Dict[str, float]  # channel -> spend
    expected_customers: float
    expected_lift: float  # vs current allocation
    current_allocation: Dict[str, float]
    current_customers: float
```

### 5. Visualization_Generator

**Responsibility**: Create publication-quality visualizations of analysis results.

**Interface**:
```python
class VisualizationGenerator:
    def __init__(self, output_dir: str = "outputs/visualizations"):
        """Initialize with output directory for saving plots."""
        
    def generate_all(
        self,
        df: pd.DataFrame,
        eda_results: EDAResults,
        model_results: ModelResults,
        attribution_results: AttributionResults
    ) -> List[str]:
        """Generate all visualizations and return file paths."""
        
    def plot_time_series(self, df: pd.DataFrame) -> str:
        """Customer acquisition over time with control variable markers."""
        
    def plot_correlation_heatmap(self, correlations: pd.DataFrame) -> str:
        """Heatmap of channel-customer correlations."""
        
    def plot_spend_comparison(self, total_spend: pd.Series) -> str:
        """Bar chart of total spend by channel."""
        
    def plot_roi_comparison(self, attribution: AttributionResults) -> str:
        """Bar chart of ROI by channel with confidence intervals."""
        
    def plot_channel_scatter(self, df: pd.DataFrame, channel: str) -> str:
        """Scatter plot with trend line for channel spend vs customers."""
        
    def plot_response_curves(self, model_results: ModelResults) -> str:
        """Saturation curves for each channel."""
        
    def plot_residual_diagnostics(self, model_results: ModelResults) -> str:
        """Residual plots for model validation."""
```

**Visualization Specifications**:

1. **Time Series Plot**:
   - X-axis: Week start date
   - Y-axis: New customers
   - Markers: Vertical lines for holidays (red) and competitor promos (orange)
   - Style: Line plot with markers

2. **Correlation Heatmap**:
   - Rows/Columns: All channels + new_customers
   - Color scale: Diverging (red-white-blue) from -1 to 1
   - Annotations: Correlation coefficients in cells

3. **Spend Comparison**:
   - X-axis: Marketing channels
   - Y-axis: Total spend ($)
   - Style: Horizontal bar chart, sorted by spend

4. **ROI Comparison**:
   - X-axis: ROI (%)
   - Y-axis: Marketing channels
   - Error bars: 95% confidence intervals
   - Style: Horizontal bar chart, sorted by ROI

5. **Channel Scatter Plots**:
   - X-axis: Channel spend
   - Y-axis: New customers
   - Overlay: Linear regression line with 95% CI band
   - Style: Scatter plot with trend line

6. **Response Curves**:
   - X-axis: Spend level (0 to max observed)
   - Y-axis: Predicted incremental customers
   - Multiple lines: One per channel
   - Style: Line plot showing saturation effects

7. **Residual Diagnostics** (2x2 grid):
   - Top-left: Residuals vs Fitted values
   - Top-right: Q-Q plot for normality
   - Bottom-left: Scale-Location plot (sqrt standardized residuals)
   - Bottom-right: Residuals vs Leverage

**Styling**:
- Figure size: (12, 8) for main plots, (16, 12) for multi-panel
- DPI: 300 for publication quality
- Color palette: Seaborn "colorblind" palette for accessibility
- Font: Arial or Helvetica, size 12 for labels, 14 for titles
- Grid: Light gray, alpha=0.3

### 6. Report_Generator

**Responsibility**: Aggregate all results into a comprehensive analysis report.

**Interface**:
```python
class ReportGenerator:
    def __init__(self, output_path: str = "outputs/mmm_analysis_report.md"):
        """Initialize with output file path."""
        
    def generate_report(
        self,
        eda_results: EDAResults,
        model_results: ModelResults,
        attribution_results: AttributionResults,
        optimization_results: OptimizationResults,
        visualization_paths: List[str]
    ) -> str:
        """Generate comprehensive Markdown report.
        
        Returns:
            Path to generated report file
        """
```

**Report Structure**:

```markdown
# Marketing Mix Modeling Analysis Report

## Executive Summary
- Key findings (top 3-5 insights)
- Overall model performance
- Top performing channels
- Budget optimization recommendations

## 1. Introduction
- Project objective
- Dataset description
- Analysis period

## 2. Methodology
- Data preprocessing steps
- Model specifications (baseline, adstock, saturation, full)
- Transformation details (adstock decay, saturation parameters)
- Train/test split approach
- Model selection criteria

## 3. Exploratory Data Analysis
- Descriptive statistics table
- Correlation analysis findings
- Seasonality patterns
- Control variable impact
- Outlier identification
- [Embedded visualizations]

## 4. Model Development and Validation
- Model comparison table (R², RMSE, AIC, BIC)
- Selected model specification
- Coefficient estimates with confidence intervals
- Model diagnostics results
  - Residual normality test
  - Heteroscedasticity test
  - Multicollinearity (VIF values)
  - Autocorrelation (Durbin-Watson)
- Cross-validation results
- [Embedded residual plots]

## 5. Marketing Attribution and ROI Analysis
- Channel contribution table
- ROI rankings
- Percentage contribution breakdown
- [Embedded ROI comparison chart]
- [Embedded response curves]

## 6. Budget Optimization
- Current vs optimal allocation table
- Expected lift in customer acquisition
- Channel-specific recommendations
- Implementation considerations

## 7. Insights and Recommendations
- High-performing channels (increase budget)
- Underperforming channels (decrease budget or investigate)
- Channels near saturation
- Seasonal considerations
- Control variable insights

## 8. Limitations and Assumptions
- Model assumptions
- Data limitations
- External validity considerations
- Recommended next steps

## Appendix
- Technical details
- Full coefficient table
- Diagnostic test results
- Hyperparameter selection process
```

## Data Models

### Core Data Structures

```python
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]

@dataclass
class EDAResults:
    descriptive_stats: Dict[str, pd.Series]
    correlations: pd.DataFrame
    time_period: Dict[str, Any]
    total_spend_by_channel: pd.Series
    outliers: Dict[str, List[int]]
    seasonality: 'SeasonalityResults'
    control_impact: 'ControlAnalysis'

@dataclass
class SeasonalityResults:
    trend: np.ndarray
    seasonal: np.ndarray
    residual: np.ndarray
    period: int  # detected seasonality period in weeks

@dataclass
class ControlAnalysis:
    holiday_effect: Tuple[float, float]  # (mean_diff, pvalue)
    promo_effect: Tuple[float, float]  # (mean_diff, pvalue)

@dataclass
class ModelResults:
    model: Any  # fitted statsmodels or sklearn model
    coefficients: pd.DataFrame  # coef, std_err, ci_lower, ci_upper
    diagnostics: DiagnosticsResults
    train_predictions: np.ndarray
    test_predictions: np.ndarray
    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: np.ndarray
    y_test: np.ndarray
    transformation_params: Dict[str, Dict[str, float]]  # channel -> {decay, alpha, gamma}
    model_type: str  # 'baseline', 'adstock', 'saturation', 'full'

@dataclass
class DiagnosticsResults:
    r_squared_train: float
    r_squared_test: float
    rmse_train: float
    rmse_test: float
    mae_train: float
    mae_test: float
    residual_normality_pvalue: float
    heteroscedasticity_pvalue: float
    vif_values: Dict[str, float]
    durbin_watson: float
    aic: float
    bic: float
    cv_scores: List[float]

@dataclass
class AttributionResults:
    marginal_contributions: Dict[str, float]
    roi_by_channel: Dict[str, Tuple[float, Tuple[float, float]]]
    percentage_contributions: Dict[str, float]
    channel_rankings: List[Tuple[str, float]]
    optimal_spend_levels: Dict[str, float]

@dataclass
class OptimizationResults:
    optimal_allocation: Dict[str, float]
    expected_customers: float
    expected_lift: float
    current_allocation: Dict[str, float]
    current_customers: float
    convergence_status: str
    iterations: int
```

### Data Flow

```
CSV File
   ↓
[DataLoader.load_data()]
   ↓
pd.DataFrame (validated)
   ├→ [EDAModule.analyze()] → EDAResults
   ├→ [StatisticalModeler.fit()] → ModelResults
   │     ↓
   └→ [AttributionEngine.calculate_attribution()] → AttributionResults
         ↓
      [AttributionEngine.optimize_budget()] → OptimizationResults
         ↓
      [VisualizationGenerator.generate_all()] → List[str] (file paths)
         ↓
      [ReportGenerator.generate_report()] → str (report path)
```


## Correctness Properties

Before proceeding with correctness properties, I need to assess whether property-based testing is appropriate for this feature.

**PBT Applicability Assessment**:

This MMM analysis system contains several components with different testing needs:

1. **Data transformations (adstock, saturation)**: Pure mathematical functions with clear input/output - **PBT APPROPRIATE**
2. **Data validation**: Schema and constraint checking - **PBT APPROPRIATE**
3. **Statistical modeling**: Involves randomness, external libraries, convergence - **PBT PARTIALLY APPROPRIATE** (for data preparation, not model fitting)
4. **Optimization**: Constraint satisfaction, objective function properties - **PBT APPROPRIATE**
5. **Visualization generation**: Side-effect operations creating files - **NOT APPROPRIATE** (use example-based tests)
6. **Report generation**: Document creation - **NOT APPROPRIATE** (use example-based tests)

**Conclusion**: Property-based testing IS appropriate for the core mathematical and data processing components of this system. I will use the prework tool to analyze which acceptance criteria are suitable for property-based testing.

