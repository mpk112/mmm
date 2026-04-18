# Marketing Mix Modeling Analysis Report

**Generated:** 2026-04-06 19:45:59

**Analysis Type:** Marketing Mix Modeling (MMM)

**Objective:** Evaluate marketing channel effectiveness and ROI to optimize budget allocation

---

## Executive Summary

### Key Findings

1. **Model Performance**: The saturation model achieved an R² of 0.875 on the test set, explaining 87.5% of variance in customer acquisition.

2. **Top Performing Channels**:
   - **Google Play**: 2577042.5% ROI
   - **Instagram**: 1113220.2% ROI
   - **Display**: 397437.6% ROI

3. **Budget Optimization**: Reallocating the marketing budget according to the optimized allocation could increase customer acquisition by **39.5%**.

4. **Model Accuracy**: The model predicts customer acquisition with a root mean squared error (RMSE) of 1321.1 customers per week.

### Recommendations

- **Increase investment** in high-ROI channels identified in the attribution analysis
- **Reduce spend** on channels showing negative or low ROI
- **Monitor saturation effects** to avoid diminishing returns on high-spend channels
- **Implement the optimized budget allocation** to maximize customer acquisition efficiency

## 1. Introduction

### Objective

This Marketing Mix Modeling (MMM) analysis evaluates the effectiveness of marketing channels in driving customer acquisition. The analysis quantifies the contribution and return on investment (ROI) of each marketing channel and provides data-driven recommendations for optimal budget allocation.

### Dataset Description

The analysis uses weekly marketing data covering **101 weeks** from **2023-08-07** to **2025-06-30**.

**Marketing Channels Analyzed:**
- TV advertising
- Radio advertising
- Facebook advertising
- Instagram advertising
- Google Search advertising
- Google Play advertising
- YouTube advertising
- Display advertising

**Control Variables:**
- Holidays (binary indicator)
- Competitor promotions (binary indicator)

**Target Variable:**
- New customer acquisitions per week

### Analysis Period

- **Start Date:** 2023-08-07
- **End Date:** 2025-06-30
- **Duration:** 101 weeks
- **Total Observations:** 101 weekly data points

## 2. Methodology

### Model Specifications

This analysis implements multiple Marketing Mix Model specifications and selects the best-performing model based on statistical criteria (AIC/BIC).

**Model Types Evaluated:**
1. **Baseline Model:** Linear regression with raw spend values
2. **Adstock Model:** Incorporates advertising carryover effects using geometric decay
3. **Saturation Model:** Models diminishing returns using Hill saturation curves
4. **Full Model:** Combines both adstock and saturation transformations

**Selected Model:** SATURATION

### Transformations

**Adstock Transformation (Carryover Effects):**
The adstock transformation captures the phenomenon where advertising effects persist beyond the initial exposure period using a geometric decay model:

```
adstock_t = spend_t + decay_rate × adstock_(t-1)
```

- **Adstock transformation:** Not applied

**Saturation Transformation (Diminishing Returns):**
The Hill saturation curve models diminishing returns where incremental spend produces progressively smaller increases in response:

```
saturated_spend = spend^gamma / (alpha^gamma + spend^gamma)
```

- **Saturation shape parameter (gamma):** 2.0

### Model Validation Approach

**Train/Test Split:**
- Training set: 80% of data (chronologically first observations)
- Test set: 20% of data (chronologically last observations)
- Time-series ordering preserved to avoid look-ahead bias

**Validation Metrics:**
- R-squared (coefficient of determination)
- RMSE (Root Mean Squared Error)
- MAE (Mean Absolute Error)
- AIC (Akaike Information Criterion)
- BIC (Bayesian Information Criterion)

**Diagnostic Tests:**
- Shapiro-Wilk test for residual normality
- Breusch-Pagan test for heteroscedasticity
- Variance Inflation Factor (VIF) for multicollinearity
- Durbin-Watson statistic for autocorrelation
- 5-fold cross-validation for model stability

### Model Selection Criteria

Models were compared using AIC (Akaike Information Criterion), which balances model fit with complexity. Lower AIC values indicate better models that avoid overfitting.

## 3. Exploratory Data Analysis

### Descriptive Statistics

| Variable | Mean | Median | Std Dev | Min | Max |
|----------|------|--------|---------|-----|-----|
| New Customers | 126441.6 | 126500.0 | 4610.0 | 118400.0 | 136800.0 |
| Tv | 467.0 | 470.0 | 58.4 | 370.0 | 570.0 |
| Radio | 205.4 | 205.0 | 16.8 | 175.0 | 240.0 |
| Facebook | 313.6 | 310.0 | 26.6 | 270.0 | 365.0 |
| Instagram | 154.9 | 155.0 | 13.3 | 135.0 | 180.0 |
| Google Search | 422.0 | 420.0 | 23.7 | 380.0 | 465.0 |
| Google Play | 110.1 | 110.0 | 14.5 | 85.0 | 135.0 |
| Youtube | 281.6 | 285.0 | 27.9 | 230.0 | 335.0 |
| Display | 205.5 | 205.0 | 15.4 | 175.0 | 235.0 |


### Correlation Analysis

The correlation analysis reveals the linear relationships between marketing channel spend and customer acquisition.

**Key Finding:** Google Play shows the strongest correlation with customer acquisition (r = 0.843).

![Correlation Heatmap](outputs/visualizations/correlation_heatmap.png)

### Total Spend by Channel

![Total Marketing Spend by Channel](outputs/visualizations/spend_comparison.png)

### Time Series Patterns

![Customer Acquisition Over Time](outputs/visualizations/time_series.png)

**Seasonality:** The analysis detected a 4-week seasonal pattern in customer acquisition data.

### Control Variable Impact

**Holidays Effect:**
- Mean difference in customer acquisition: 6615.3 customers
- Statistical significance: p-value = 0.0004
- Interpretation: Statistically significant impact on customer acquisition

**Competitor Promotions Effect:**
- Mean difference in customer acquisition: -1958.3 customers
- Statistical significance: p-value = 0.0997
- Interpretation: Not statistically significant impact on customer acquisition

### Outlier Detection

No significant outliers detected in marketing spend data.

## 4. Model Development and Validation

### Model Performance Metrics

| Metric | Training Set | Test Set |
|--------|--------------|----------|
| R² | 0.8635 | 0.8750 |
| RMSE | 1763.34 | 1321.09 |
| MAE | 1196.20 | 988.33 |
| AIC | 1445.02 | - |
| BIC | 1471.23 | - |

**Interpretation:**
- The model explains **87.5%** of the variance in customer acquisition on the test set
- Test set RMSE of **1321.1** customers indicates the average prediction error
- ✓ No significant overfitting detected

### Coefficient Estimates

| Variable | Coefficient | Std Error | 95% CI Lower | 95% CI Upper |
|----------|-------------|-----------|--------------|---------------|
| Tv | 3036.4802 | 4159.8233 | -5262.1402 | 11335.1006 |
| Radio | 8647.6982 | 6041.8333 | -3405.4295 | 20700.8258 |
| Facebook | 6046.6126 | 10337.4287 | -14575.9934 | 26669.2187 |
| Instagram | 34615.7030 | 18288.1911 | -1868.2399 | 71099.6459 |
| Google Search | -23621.3891 | 33200.9616 | -89855.4952 | 42612.7170 |
| Google Play | 57254.3443 | 24057.2626 | 9261.4187 | 105247.2700 |
| Youtube | -31941.4950 | 33835.5678 | -99441.6058 | 35558.6158 |
| Display | 16387.3551 | 25747.3068 | -34977.1166 | 67751.8268 |
| Holidays | 5597.9780 | 696.1087 | 4209.2790 | 6986.6769 |
| Competitor Promo | -638.0777 | 599.4820 | -1834.0116 | 557.8562 |


**Note:** Coefficients represent the marginal effect of each transformed marketing channel on customer acquisition. Confidence intervals are at the 95% level.

### Model Diagnostics

#### Residual Normality Test (Shapiro-Wilk)
- **P-value:** 0.0001
- **Interpretation:** ⚠️ Residuals deviate from normality

#### Heteroscedasticity Test (Breusch-Pagan)
- **P-value:** 0.0001
- **Interpretation:** ⚠️ Heteroscedasticity detected

#### Multicollinearity Analysis (VIF)

| Variable | VIF |
|----------|-----|
| Tv | 88.03 ⚠️ |
| Radio | 190.60 ⚠️ |
| Facebook | 575.47 ⚠️ |
| Instagram | 1695.19 ⚠️ |
| Google Search | 4329.77 ⚠️ |
| Google Play | 2468.45 ⚠️ |
| Youtube | 6313.12 ⚠️ |
| Display | 2993.38 ⚠️ |
| Holidays | 1.34 ✓ |
| Competitor Promo | 1.57 ✓ |


**Interpretation:** VIF values above 10 indicate problematic multicollinearity. ⚠️ Some variables show high multicollinearity

#### Autocorrelation Test (Durbin-Watson)
- **Statistic:** 1.7444
- **Interpretation:** Values near 2.0 indicate no autocorrelation. ✓ No significant autocorrelation

#### Cross-Validation Results (5-Fold)
- **Cross-validation R²:** Mean R² = 0.8361 (±0.0868)
- **Interpretation:** ✓ Model shows good stability across folds

### Residual Diagnostic Plots

![Residual Diagnostic Plots](outputs/visualizations/residual_diagnostics.png)

**Diagnostic Plot Interpretation:**
- **Residuals vs Fitted:** Should show random scatter around zero (no patterns)
- **Q-Q Plot:** Points should follow the diagonal line (normality)
- **Scale-Location:** Should show random scatter (homoscedasticity)
- **Residuals vs Leverage:** Identifies influential observations

## 5. Attribution and ROI Analysis

### Channel Contribution and ROI

| Channel | Marginal Contribution | ROI | 95% CI Lower | 95% CI Upper | % of Total |
|---------|----------------------|-----|--------------|--------------|------------|
| Google Play | 2867071.0 | 2577042.5% | 416776.6% | 4737308.4% | 81.2% |
| Instagram | 1741789.5 | 1113220.2% | -60186.9% | 2286627.4% | 49.3% |
| Display | 825288.0 | 397437.6% | -848602.9% | 1643478.0% | 23.4% |
| Radio | 435279.5 | 209673.3% | -82707.9% | 502054.4% | 12.3% |
| Facebook | 304276.9 | 95962.2% | -231667.9% | 423592.2% | 8.6% |
| Tv | 152172.5 | 32160.4% | -56006.5% | 120327.4% | 4.3% |
| Google Search | -1191017.0 | -279517.5% | -1063000.9% | 503966.0% | -33.7% |
| Youtube | -1605294.4 | -564549.5% | -1757368.0% | 628269.0% | -45.5% |


### ROI Rankings

**Top 3 Performing Channels:**
1. 🏆 **Google Play**: 2577042.5% ROI
2. 📈 **Instagram**: 1113220.2% ROI
3. 📈 **Display**: 397437.6% ROI


**Bottom 3 Performing Channels:**
1. 📉 **Tv**: 32160.4% ROI
2. 📉 **Google Search**: -279517.5% ROI
3. 📉 **Youtube**: -564549.5% ROI


![ROI Comparison by Channel](outputs/visualizations/roi_comparison.png)

### Channel Response Analysis

![Channel Spend vs Customer Acquisition](outputs/visualizations/channel_scatter_plots.png)

### Saturation Effects

![Marketing Response Curves](outputs/visualizations/response_curves.png)

**Response Curve Interpretation:**
The response curves show how incremental customers change with spend level for each channel. Flattening curves indicate saturation effects where additional spend produces diminishing returns.

### Key Insights

- **6 channels** show positive ROI and should be prioritized for investment
- **2 channels** show negative ROI and require investigation or budget reduction
- **3 channels** contribute more than 15% each to total customer acquisition


## 6. Budget Optimization

### Optimization Objective

Maximize customer acquisition subject to:
- Total budget constraint: $218,190
- Channel-specific minimum and maximum spend constraints

### Current vs Optimal Allocation

| Channel | Current Spend | Optimal Spend | Change ($) | Change (%) |
|---------|---------------|---------------|------------|------------|
| Tv | $47,170 | $23,585 | $-23,585 ↓ | -50.0% |
| Radio | $20,750 | $34,010 | $13,260 ↑ | 63.9% |
| Facebook | $31,675 | $30,002 | $-1,673 ↓ | -5.3% |
| Instagram | $15,645 | $31,290 | $15,645 ↑ | 100.0% |
| Google Search | $42,625 | $21,312 | $-21,312 ↓ | -50.0% |
| Google Play | $11,125 | $22,250 | $11,125 ↑ | 100.0% |
| Youtube | $28,440 | $14,220 | $-14,220 ↓ | -50.0% |
| Display | $20,760 | $41,520 | $20,760 ↑ | 100.0% |


### Expected Impact

**Current Performance:**
- Total budget: $218,190
- Expected customers: 12801427

**Optimized Performance:**
- Total budget: $218,190
- Expected customers: 17856410
- **Expected lift: 39.5%**

### Optimization Status

- **Convergence:** Success
- **Iterations:** 43

### Implementation Recommendations

- **Decrease Tv spend by 50%** (from $47,170 to $23,585)
- **Increase Radio spend by 64%** (from $20,750 to $34,010)
- **Increase Instagram spend by 100%** (from $15,645 to $31,290)
- **Decrease Google Search spend by 50%** (from $42,625 to $21,312)
- **Increase Google Play spend by 100%** (from $11,125 to $22,250)
- **Decrease Youtube spend by 50%** (from $28,440 to $14,220)
- **Increase Display spend by 100%** (from $20,760 to $41,520)

## 7. Insights and Recommendations

### High-Performing Channels

- **Google Play**: Strong performance indicates opportunity for increased investment
- **Instagram**: Strong performance indicates opportunity for increased investment
- **Display**: Strong performance indicates opportunity for increased investment


### Underperforming Channels

- **Google Search**: Underperformance suggests need for optimization or budget reallocation
- **Youtube**: Underperformance suggests need for optimization or budget reallocation


### Budget Reallocation Priorities

- **Instagram**: Increase by 100%
- **Google Play**: Increase by 100%
- **Display**: Increase by 100%
- **Radio**: Increase by 64%
- **Tv**: Decrease by 50%


### Actionable Steps

1. **Immediate Actions (0-30 days):**
   - Implement the optimized budget allocation for the next planning period
   - Increase spend on high-ROI channels identified in the analysis
   - Reduce or pause spend on channels with negative ROI

2. **Short-term Actions (1-3 months):**
   - Monitor performance metrics weekly to validate model predictions
   - Conduct A/B tests on channels near saturation to confirm diminishing returns
   - Investigate root causes of underperformance in low-ROI channels

3. **Long-term Actions (3-6 months):**
   - Refine the MMM model with additional data as it becomes available
   - Explore creative optimization or audience targeting for underperforming channels
   - Consider testing new marketing channels not included in current mix

### Strategic Considerations

**Seasonality:**
- Account for the google_play_spend seasonal patterns when implementing budget changes
- Plan higher spend during peak acquisition periods

**Market Dynamics:**
- Monitor competitor activity and adjust spend accordingly
- Be prepared to reallocate budget quickly in response to market changes

**Testing and Learning:**
- Maintain a portion of budget (10-15%) for testing new channels and strategies
- Use controlled experiments to validate model recommendations

**Risk Management:**
- Implement changes gradually to minimize risk
- Maintain minimum spend levels on all channels to preserve brand presence
- Monitor for unexpected market shifts that may invalidate model assumptions

## 8. Limitations and Assumptions

### Model Assumptions

1. **Linear Relationships:** The model assumes linear relationships between transformed spend and customer acquisition (after applying adstock and saturation transformations)

2. **Stationarity:** The model assumes that the relationship between marketing spend and customer acquisition remains stable over the analysis period

3. **No Interaction Effects:** The model does not explicitly capture interaction effects between channels (e.g., synergies between TV and digital advertising)

4. **Customer Value:** ROI calculations assume a constant customer lifetime value across all acquisition channels

5. **Attribution Window:** The adstock transformation assumes a specific decay pattern that may not perfectly capture the true carryover effects

### Data Limitations

1. **Historical Data Only:** The model is based on historical data and may not account for future market changes or competitive dynamics

2. **Aggregated Weekly Data:** Weekly aggregation may mask important intra-week patterns or day-of-week effects

3. **Limited Time Period:** The analysis covers a specific time period and may not generalize to different market conditions

4. **Missing Variables:** Potential confounding factors (e.g., product changes, pricing, seasonality beyond holidays) may not be fully captured

5. **External Validity:** Results are specific to the analyzed time period and market conditions

### Methodological Limitations

1. **Causality:** While the model identifies associations, establishing true causality requires controlled experiments

2. **Optimization Constraints:** The budget optimization assumes constraints that may not reflect all real-world business constraints

3. **Model Selection:** The selected model is the best among evaluated specifications but may not be the globally optimal model

4. **Uncertainty:** Confidence intervals provide a measure of uncertainty but do not capture all sources of variability

### Recommended Next Steps

1. **Validation:** Implement recommendations in a controlled manner and monitor actual vs predicted performance

2. **Model Refinement:** Update the model regularly with new data to improve accuracy and capture changing dynamics

3. **Experimentation:** Conduct randomized controlled trials to validate causal relationships

4. **Extended Analysis:** Consider more sophisticated models (e.g., Bayesian MMM, hierarchical models) for deeper insights

5. **Additional Data:** Collect more granular data (daily instead of weekly) and additional variables (creative quality, audience targeting) to improve model accuracy

## Appendix

### A. Technical Details

#### Model Specification

**Model Type:** saturation

**Dependent Variable:** new_customers (weekly customer acquisitions)

**Independent Variables:**
- 8 marketing channel spend variables (transformed)
- 2 control variables (holidays, competitor_promo)

**Estimation Method:** Ordinary Least Squares (OLS) regression

#### Transformation Parameters

| Channel | Adstock Decay | Saturation Alpha | Saturation Gamma |
|---------|---------------|------------------|------------------|
| Tv | - | 467.0 | 2.000 |
| Radio | - | 205.4 | 2.000 |
| Facebook | - | 313.6 | 2.000 |
| Instagram | - | 154.9 | 2.000 |
| Google Search | - | 422.0 | 2.000 |
| Google Play | - | 110.1 | 2.000 |
| Youtube | - | 281.6 | 2.000 |
| Display | - | 205.5 | 2.000 |


### B. Full Coefficient Table

| Variable | Coefficient | Std Error | 95% CI Lower | 95% CI Upper |
|----------|-------------|-----------|--------------|---------------|
| const | 91057.139854 | 9191.048402 | 72721.499985 | 109392.779724 |
| tv_spend_sat | 3036.480230 | 4159.823281 | -5262.140152 | 11335.100613 |
| radio_spend_sat | 8647.698151 | 6041.833281 | -3405.429453 | 20700.825754 |
| facebook_spend_sat | 6046.612648 | 10337.428737 | -14575.993414 | 26669.218710 |
| instagram_spend_sat | 34615.703028 | 18288.191053 | -1868.239864 | 71099.645920 |
| google_search_spend_sat | -23621.389073 | 33200.961600 | -89855.495194 | 42612.717047 |
| google_play_spend_sat | 57254.344323 | 24057.262552 | 9261.418696 | 105247.269950 |
| youtube_spend_sat | -31941.494978 | 33835.567779 | -99441.605787 | 35558.615830 |
| display_spend_sat | 16387.355115 | 25747.306827 | -34977.116590 | 67751.826820 |
| holidays | 5597.977953 | 696.108743 | 4209.279007 | 6986.676899 |
| competitor_promo | -638.077729 | 599.482015 | -1834.011626 | 557.856167 |


### C. Diagnostic Test Results

**Shapiro-Wilk Test (Residual Normality):**
- Null hypothesis: Residuals are normally distributed
- Test statistic: 0.000072
- Conclusion: Reject null hypothesis (residuals deviate from normality)

**Breusch-Pagan Test (Heteroscedasticity):**
- Null hypothesis: Homoscedasticity (constant variance)
- Test statistic: 0.000095
- Conclusion: Reject null hypothesis (heteroscedasticity present)

**Durbin-Watson Test (Autocorrelation):**
- Test statistic: 1.7444
- Expected value (no autocorrelation): 2.0
- Conclusion: No significant autocorrelation

### D. Hyperparameter Selection Process

The model hyperparameters (adstock decay rates, saturation parameters) were selected through grid search optimization:

1. **Grid Search Space:**
   - Adstock decay rates: [0.1, 0.3, 0.5, 0.7, 0.9]
   - Saturation gamma: [0.5, 1.0, 1.5, 2.0]
   - Saturation alpha: Based on mean spend per channel

2. **Selection Criterion:** Akaike Information Criterion (AIC)

3. **Validation:** 5-fold cross-validation to assess model stability

### E. Software and Dependencies

**Programming Language:** Python 3.9+

**Key Libraries:**
- pandas: Data manipulation
- numpy: Numerical computations
- statsmodels: Statistical modeling
- scikit-learn: Machine learning utilities
- scipy: Optimization and statistical tests
- matplotlib/seaborn: Visualization

### F. Reproducibility

All analyses were conducted with fixed random seeds (random_state=42) to ensure reproducibility. The train/test split preserves chronological ordering to avoid look-ahead bias.

---

**End of Report**