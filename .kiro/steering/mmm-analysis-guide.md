---
inclusion: auto
---

# Marketing Mix Modeling Analysis - Implementation Guide

This steering document provides guidance for implementing the Marketing Mix Modeling (MMM) analysis system. It covers implementation approach, best practices, common pitfalls, and key technical considerations.

## Project Context

You are building a professional-grade MMM analysis system for the Moniepoint Data Science take-home assessment. The system analyzes 100 weeks of marketing data across 8 channels (TV, Radio, Facebook, Instagram, Google Search, Google Play, YouTube, Display) to quantify channel effectiveness and optimize budget allocation.

**Key Success Criteria:**
- Demonstrate original analytical thinking (minimal LLM dependence)
- Statistical rigor in modeling approach
- Clean, well-documented, reproducible code
- Actionable insights and recommendations

## Implementation Approach

### Phase 1: Foundation (Tasks 1-4)
Build the data pipeline first - this is your foundation.

**Priority Order:**
1. Set up project structure and dependencies
2. Implement DataLoader with validation
3. Implement EDAModule for initial insights
4. Run checkpoint to verify data flows correctly

**Why this order?** You need clean, validated data before any modeling. EDA helps you understand the data characteristics that will inform modeling decisions.

### Phase 2: Core Modeling (Tasks 5-7)
Implement statistical transformations and model fitting.

**Critical Considerations:**
- Start with simple baseline model, then add complexity
- Adstock and saturation transformations are mathematically precise - test thoroughly
- Hyperparameter optimization can be time-consuming - use coarse grid first
- Model diagnostics are essential - don't skip validation

### Phase 3: Attribution & Insights (Tasks 8-10)
Calculate ROI and create visualizations.

**Key Points:**
- Attribution depends on model quality - ensure Phase 2 is solid
- Optimization constraints must be realistic (min/max spend per channel)
- Visualizations should tell a story - not just display data

### Phase 4: Integration & Polish (Tasks 11-13)
Tie everything together and ensure quality.

## Technical Best Practices

### Data Handling

**Column Naming:**
The dataset uses `new customers` (with space). Handle this carefully:
```python
# Good - use exact column name or rename early
df = df.rename(columns={'new customers': 'new_customers'})

# Or access with bracket notation
y = df['new customers']
```

**Date Handling:**
```python
# Parse dates correctly
df['week_start_date'] = pd.to_datetime(df['week_start_date'])

# Set as index for time series operations
df = df.set_index('week_start_date')
```

**Missing Values:**
The dataset appears complete, but always check:
```python
# Check for missing values
assert df.isnull().sum().sum() == 0, "Missing values detected"
```

### Statistical Modeling

**Adstock Transformation:**
Implement geometric decay correctly:
```python
def apply_adstock(spend: np.ndarray, decay: float) -> np.ndarray:
    """Apply adstock transformation with geometric decay.
    
    Formula: adstock[t] = spend[t] + decay * adstock[t-1]
    """
    adstock = np.zeros_like(spend)
    adstock[0] = spend[0]
    for t in range(1, len(spend)):
        adstock[t] = spend[t] + decay * adstock[t-1]
    return adstock
```

**Saturation Transformation:**
Use Hill curve (S-shaped):
```python
def apply_saturation(spend: np.ndarray, alpha: float, gamma: float) -> np.ndarray:
    """Apply Hill saturation curve.
    
    Formula: saturated = spend^gamma / (alpha^gamma + spend^gamma)
    """
    return np.power(spend, gamma) / (np.power(alpha, gamma) + np.power(spend, gamma))
```

**Model Selection:**
Compare models using AIC/BIC:
```python
# Lower is better
models = {
    'baseline': fit_baseline_model(X, y),
    'adstock': fit_adstock_model(X, y),
    'saturation': fit_saturation_model(X, y),
    'full': fit_full_model(X, y)
}

best_model = min(models.items(), key=lambda x: x[1].aic)
```

### Hyperparameter Optimization

**Grid Search Strategy:**
Start coarse, then refine:
```python
# Coarse grid for initial exploration
decay_rates = [0.1, 0.3, 0.5, 0.7, 0.9]
alpha_multipliers = [0.5, 1.0, 1.5, 2.0]  # multiply by mean spend
gamma_values = [0.5, 1.0, 1.5, 2.0]

# Fine grid around best parameters (if needed)
best_decay = 0.5
decay_rates_fine = [0.4, 0.45, 0.5, 0.55, 0.6]
```

**Computational Efficiency:**
- Use vectorized operations (numpy) instead of loops
- Cache transformed features to avoid recomputation
- Consider parallel processing for grid search (joblib)

### Model Diagnostics

**Essential Checks:**
1. **Residual Normality**: Shapiro-Wilk test (p > 0.05 is good)
2. **Heteroscedasticity**: Breusch-Pagan test (p > 0.05 is good)
3. **Multicollinearity**: VIF < 10 for all predictors
4. **Autocorrelation**: Durbin-Watson ≈ 2 (range 1.5-2.5 acceptable)

**Interpretation:**
```python
if diagnostics.residual_normality_pvalue < 0.05:
    print("WARNING: Residuals not normally distributed")
    print("Consider: log transformation, robust regression, or additional features")

if any(vif > 10 for vif in diagnostics.vif_values.values()):
    print("WARNING: Multicollinearity detected")
    print("Consider: removing correlated channels or using regularization")
```

### Attribution & ROI

**Customer Lifetime Value:**
Default assumption: $100 per customer. Adjust based on business context:
```python
# Conservative estimate
customer_value = 100.0

# Calculate ROI
roi = (contribution * customer_value - total_spend) / total_spend
```

**Confidence Intervals:**
Use bootstrap or delta method:
```python
from scipy import stats

# Delta method for coefficient uncertainty
se = model.bse[channel]  # standard error
ci_lower = coef - 1.96 * se
ci_upper = coef + 1.96 * se
```

### Budget Optimization

**Constraint Formulation:**
```python
from scipy.optimize import minimize

# Constraints
constraints = [
    # Budget constraint (equality)
    {'type': 'eq', 'fun': lambda x: x.sum() - total_budget},
    
    # Minimum spend per channel (inequality)
    *[{'type': 'ineq', 'fun': lambda x, i=i: x[i] - min_spend[i]} 
      for i in range(n_channels)],
    
    # Maximum spend per channel (inequality)
    *[{'type': 'ineq', 'fun': lambda x, i=i: max_spend[i] - x[i]} 
      for i in range(n_channels)]
]

# Bounds (alternative to inequality constraints)
bounds = [(min_spend[i], max_spend[i]) for i in range(n_channels)]
```

**Realistic Constraints:**
- Minimum spend: 50% of current spend (can't eliminate channels completely)
- Maximum spend: 200% of current spend (can't scale infinitely)

## Common Pitfalls & Solutions

### Pitfall 1: Overfitting
**Symptom:** High R² on training, low R² on test set

**Solutions:**
- Use simpler model (fewer transformations)
- Add regularization (Ridge/Lasso)
- Increase train/test split (use more training data)
- Cross-validation to assess stability

### Pitfall 2: Multicollinearity
**Symptom:** High VIF values, unstable coefficients

**Solutions:**
- Remove highly correlated channels
- Use PCA for dimensionality reduction
- Use Ridge regression (L2 regularization)
- Combine correlated channels (e.g., Facebook + Instagram = "Social")

### Pitfall 3: Non-convergence in Optimization
**Symptom:** Optimizer fails to find solution

**Solutions:**
- Scale features (standardize spend values)
- Use better initial guess (current allocation)
- Relax constraints slightly
- Try different optimization algorithm (L-BFGS-B, SLSQP, trust-constr)

### Pitfall 4: Unrealistic Saturation Curves
**Symptom:** Saturation at very low or very high spend levels

**Solutions:**
- Constrain alpha to reasonable range (0.5x to 2x mean spend)
- Constrain gamma to (0.3, 3.0) range
- Visualize curves before accepting parameters
- Use domain knowledge to validate

### Pitfall 5: Negative Coefficients
**Symptom:** Model predicts negative impact for marketing spend

**Solutions:**
- Check for data errors (negative spend values)
- Check for multicollinearity (suppression effects)
- Consider non-negativity constraints in regression
- Investigate channel interactions

## Code Quality Standards

### Docstrings
Use Google style:
```python
def calculate_roi(contribution: float, spend: float, customer_value: float) -> float:
    """Calculate return on investment for a marketing channel.
    
    Args:
        contribution: Number of customers attributed to channel
        spend: Total spend on channel
        customer_value: Lifetime value per customer ($)
        
    Returns:
        ROI as a decimal (e.g., 0.5 = 50% return)
        
    Example:
        >>> calculate_roi(1000, 50000, 100)
        1.0  # 100% ROI
    """
    return (contribution * customer_value - spend) / spend
```

### Type Hints
Be explicit:
```python
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np

def fit_model(
    X: pd.DataFrame, 
    y: np.ndarray,
    test_size: float = 0.2
) -> Tuple[object, Dict[str, float]]:
    """Fit regression model and return model + metrics."""
    pass
```

### Error Handling
Be informative:
```python
def load_data(file_path: str) -> pd.DataFrame:
    """Load and validate MMM dataset."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Dataset not found at {file_path}. "
            f"Please ensure the CSV file exists."
        )
    
    df = pd.read_csv(file_path)
    
    if len(df) < 20:
        raise ValueError(
            f"Insufficient data: {len(df)} weeks found, minimum 20 required. "
            f"MMM requires at least 20 weeks for reliable estimation."
        )
    
    return df
```

### Logging
Use appropriate levels:
```python
import logging

logger = logging.getLogger(__name__)

# INFO: Progress updates
logger.info("Loading data from %s", file_path)
logger.info("Fitting model with %d features", X.shape[1])

# WARNING: Potential issues
logger.warning("High VIF detected for channel %s: %.2f", channel, vif)
logger.warning("Test R² (%.3f) much lower than train R² (%.3f)", r2_test, r2_train)

# ERROR: Failures
logger.error("Model fitting failed: %s", str(e))
```

## Testing Strategy

### Unit Tests
Test individual functions with known inputs/outputs:
```python
def test_adstock_zero_decay():
    """Adstock with zero decay should return original spend."""
    spend = np.array([100, 200, 150])
    result = apply_adstock(spend, decay=0.0)
    np.testing.assert_array_equal(result, spend)

def test_saturation_monotonic():
    """Saturation should be monotonically increasing."""
    spend = np.array([0, 100, 200, 300])
    result = apply_saturation(spend, alpha=150, gamma=1.0)
    assert np.all(np.diff(result) >= 0)
```

### Property-Based Tests
Test universal properties:
```python
from hypothesis import given, strategies as st

@given(
    spend=st.lists(st.floats(min_value=0, max_value=1000), min_size=10, max_size=100),
    decay=st.floats(min_value=0.0, max_value=1.0)
)
def test_adstock_preserves_nonnegativity(spend, decay):
    """Adstock of non-negative spend should be non-negative."""
    spend_array = np.array(spend)
    result = apply_adstock(spend_array, decay)
    assert np.all(result >= 0)
```

### Integration Tests
Test full pipeline:
```python
def test_full_pipeline():
    """Test end-to-end execution with sample data."""
    # Load data
    df = load_data("test_data.csv")
    
    # Run EDA
    eda_results = run_eda(df)
    assert eda_results is not None
    
    # Fit model
    model_results = fit_model(df)
    assert model_results.r_squared_test > 0.5
    
    # Calculate attribution
    attribution = calculate_attribution(model_results, df)
    assert len(attribution.roi_by_channel) == 8
    
    # Generate report
    report_path = generate_report(eda_results, model_results, attribution)
    assert os.path.exists(report_path)
```

## Deliverables Checklist

Before submitting, ensure you have:

**Code:**
- [ ] All 6 components implemented (DataLoader, EDA, Modeler, Attribution, Visualization, Report)
- [ ] Main pipeline script (`main.py`) that runs end-to-end
- [ ] Proper error handling throughout
- [ ] Logging at appropriate levels

**Documentation:**
- [ ] README.md with setup and usage instructions
- [ ] Docstrings for all public functions/classes
- [ ] Type hints throughout
- [ ] Comments explaining complex logic

**Testing:**
- [ ] Unit tests for core functions
- [ ] Integration test for full pipeline
- [ ] All tests passing

**Outputs:**
- [ ] Analysis report (Markdown or PDF)
- [ ] All visualizations (9+ charts)
- [ ] Model diagnostics summary
- [ ] Budget optimization recommendations

**Quality:**
- [ ] Code formatted with black
- [ ] PEP 8 compliant
- [ ] No hardcoded paths (use command-line arguments)
- [ ] Reproducible (random seeds set)

## Key Insights to Highlight

When writing your report, emphasize:

1. **Model Performance**: R², RMSE, and how well the model explains customer acquisition
2. **Channel Effectiveness**: Which channels have highest ROI? Which are saturated?
3. **Adstock Effects**: Which channels have long carryover effects?
4. **Saturation Points**: At what spend level do channels hit diminishing returns?
5. **Control Variables**: How do holidays and competitor promos impact acquisition?
6. **Optimization Opportunity**: How much lift can be achieved by reallocating budget?
7. **Actionable Recommendations**: Specific budget changes with expected outcomes

## Dataset-Specific Notes

**Your MMM Dataset:**
- 100 weeks of data (Aug 2023 - Jun 2025)
- 8 marketing channels
- Customer acquisition ranges: ~118K to ~137K per week
- Total spend per week: ~$2,500-$3,000
- Holidays: 9 occurrences
- Competitor promos: 17 occurrences

**Initial Observations:**
- Sufficient data for reliable MMM (100 weeks >> 20 minimum)
- Good variation in spend across channels
- Control variables present for external factors
- No obvious missing values or data quality issues

## References & Resources

**Statistical Methods:**
- Adstock modeling: Broadbent (1979), "One Way TV Advertisements Work"
- Saturation curves: Hill equation from pharmacology
- MMM overview: Google's "Meridian" open-source MMM package

**Python Libraries:**
- statsmodels: OLS regression, diagnostics
- scikit-learn: preprocessing, cross-validation
- scipy: optimization, statistical tests
- matplotlib/seaborn: visualization

**Best Practices:**
- Keep models interpretable (avoid black boxes)
- Validate assumptions rigorously
- Use domain knowledge to sanity-check results
- Document limitations honestly

---

**Remember:** This is a take-home assessment. Show your analytical thinking, statistical rigor, and coding craftsmanship. Quality over quantity - a well-executed analysis with clear insights beats a complex model with unclear results.
