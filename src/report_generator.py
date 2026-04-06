"""
ReportGenerator for Marketing Mix Modeling analysis.

This module provides report generation functionality to create comprehensive
markdown reports aggregating all MMM analysis results including EDA findings,
model performance, attribution analysis, budget optimization, and recommendations.
"""

from typing import List, Optional
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

from src.eda_module import EDAResults
from src.statistical_modeler import ModelResults
from src.attribution_engine import AttributionResults, OptimizationResults


class ReportGenerator:
    """Report generator for Marketing Mix Modeling analysis.

    This class creates comprehensive markdown reports that aggregate all analysis
    results including exploratory data analysis, statistical modeling, attribution
    analysis, budget optimization, and actionable recommendations.

    The report includes:
    - Executive summary with key findings
    - Introduction and methodology
    - EDA findings with descriptive statistics
    - Model development and validation results
    - Attribution and ROI analysis
    - Budget optimization recommendations
    - Insights and actionable recommendations
    - Limitations and assumptions
    - Technical appendix

    Attributes:
        output_path: File path for saving the generated report
    """

    def __init__(self, output_path: str = "outputs/mmm_analysis_report.md"):
        """Initialize ReportGenerator with output file path.

        Creates the output directory if it doesn't exist.

        Args:
            output_path: File path for saving the generated markdown report.
                Parent directories will be created if they don't exist.
        """
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def generate_report(
        self,
        eda_results: EDAResults,
        model_results: ModelResults,
        attribution_results: AttributionResults,
        optimization_results: OptimizationResults,
        visualization_paths: List[str],
    ) -> str:
        """Generate comprehensive markdown report.

        This is the main entry point for report generation. It creates a
        comprehensive markdown document with all analysis results, embedded
        visualizations, and actionable recommendations.

        Args:
            eda_results: Results from exploratory data analysis
            model_results: Results from statistical modeling
            attribution_results: Results from attribution analysis
            optimization_results: Results from budget optimization
            visualization_paths: List of file paths to generated visualizations

        Returns:
            Path to generated report file
        """
        # Build report sections
        sections = []

        # Header
        sections.append(self._generate_header())

        # Executive Summary
        sections.append(
            self._generate_executive_summary(
                model_results, attribution_results, optimization_results
            )
        )

        # Introduction
        sections.append(self._generate_introduction(eda_results))

        # Methodology
        sections.append(self._generate_methodology(model_results))

        # EDA Section
        sections.append(self._generate_eda_section(eda_results, visualization_paths))

        # Model Development and Validation
        sections.append(
            self._generate_model_section(model_results, visualization_paths)
        )

        # Attribution and ROI Analysis
        sections.append(
            self._generate_attribution_section(attribution_results, visualization_paths)
        )

        # Budget Optimization
        sections.append(self._generate_optimization_section(optimization_results))

        # Insights and Recommendations
        sections.append(
            self._generate_insights_section(attribution_results, optimization_results)
        )

        # Limitations and Assumptions
        sections.append(self._generate_limitations_section())

        # Appendix
        sections.append(self._generate_appendix(model_results, eda_results))

        # Combine all sections
        report_content = "\n\n".join(sections)

        # Write to file
        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        return str(self.output_path)

    def _generate_header(self) -> str:
        """Generate report header with title and metadata."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return f"""# Marketing Mix Modeling Analysis Report

**Generated:** {timestamp}

**Analysis Type:** Marketing Mix Modeling (MMM)

**Objective:** Evaluate marketing channel effectiveness and ROI to optimize budget allocation

---"""

    def _generate_executive_summary(
        self,
        model_results: ModelResults,
        attribution_results: AttributionResults,
        optimization_results: OptimizationResults,
    ) -> str:
        """Generate executive summary section."""
        # Get top 3 channels by ROI
        top_channels = attribution_results.channel_rankings[:3]

        # Format top channels
        top_channels_text = "\n".join(
            [
                f"   - **{self._format_channel_name(ch)}**: {roi*100:.1f}% ROI"
                for ch, roi in top_channels
            ]
        )

        # Get model performance
        r2_test = model_results.diagnostics.r_squared_test
        rmse_test = model_results.diagnostics.rmse_test

        # Get optimization lift
        expected_lift = optimization_results.expected_lift

        summary = f"""## Executive Summary

### Key Findings

1. **Model Performance**: The {model_results.model_type} model achieved an R² of {r2_test:.3f} on the test set, explaining {r2_test*100:.1f}% of variance in customer acquisition.

2. **Top Performing Channels**:
{top_channels_text}

3. **Budget Optimization**: Reallocating the marketing budget according to the optimized allocation could increase customer acquisition by **{expected_lift:.1f}%**.

4. **Model Accuracy**: The model predicts customer acquisition with a root mean squared error (RMSE) of {rmse_test:.1f} customers per week.

### Recommendations

- **Increase investment** in high-ROI channels identified in the attribution analysis
- **Reduce spend** on channels showing negative or low ROI
- **Monitor saturation effects** to avoid diminishing returns on high-spend channels
- **Implement the optimized budget allocation** to maximize customer acquisition efficiency"""

        return summary

    def _generate_introduction(self, eda_results: EDAResults) -> str:
        """Generate introduction section."""
        time_period = eda_results.time_period
        start_date = time_period["start_date"]
        end_date = time_period["end_date"]
        n_weeks = time_period["n_weeks"]

        intro = f"""## 1. Introduction

### Objective

This Marketing Mix Modeling (MMM) analysis evaluates the effectiveness of marketing channels in driving customer acquisition. The analysis quantifies the contribution and return on investment (ROI) of each marketing channel and provides data-driven recommendations for optimal budget allocation.

### Dataset Description

The analysis uses weekly marketing data covering **{n_weeks} weeks** from **{start_date.strftime('%Y-%m-%d')}** to **{end_date.strftime('%Y-%m-%d')}**.

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

- **Start Date:** {start_date.strftime('%Y-%m-%d')}
- **End Date:** {end_date.strftime('%Y-%m-%d')}
- **Duration:** {n_weeks} weeks
- **Total Observations:** {n_weeks} weekly data points"""

        return intro

    def _generate_methodology(self, model_results: ModelResults) -> str:
        """Generate methodology section."""
        model_type = model_results.model_type
        transformation_params = model_results.transformation_params

        # Get transformation details
        if model_type == "adstock" and transformation_params:
            sample_channel = list(transformation_params.keys())[0]
            decay_rate = transformation_params[sample_channel].get("decay", "N/A")
            adstock_text = f"- **Adstock decay rate:** {decay_rate}"
        else:
            adstock_text = "- **Adstock transformation:** Not applied"

        if model_type in ["saturation", "full"] and transformation_params:
            sample_channel = list(transformation_params.keys())[0]
            gamma = transformation_params[sample_channel].get("gamma", "N/A")
            saturation_text = f"- **Saturation shape parameter (gamma):** {gamma}"
        else:
            saturation_text = "- **Saturation transformation:** Not applied"

        methodology = f"""## 2. Methodology

### Model Specifications

This analysis implements multiple Marketing Mix Model specifications and selects the best-performing model based on statistical criteria (AIC/BIC).

**Model Types Evaluated:**
1. **Baseline Model:** Linear regression with raw spend values
2. **Adstock Model:** Incorporates advertising carryover effects using geometric decay
3. **Saturation Model:** Models diminishing returns using Hill saturation curves
4. **Full Model:** Combines both adstock and saturation transformations

**Selected Model:** {model_type.upper()}

### Transformations

**Adstock Transformation (Carryover Effects):**
The adstock transformation captures the phenomenon where advertising effects persist beyond the initial exposure period using a geometric decay model:

```
adstock_t = spend_t + decay_rate × adstock_(t-1)
```

{adstock_text}

**Saturation Transformation (Diminishing Returns):**
The Hill saturation curve models diminishing returns where incremental spend produces progressively smaller increases in response:

```
saturated_spend = spend^gamma / (alpha^gamma + spend^gamma)
```

{saturation_text}

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

Models were compared using AIC (Akaike Information Criterion), which balances model fit with complexity. Lower AIC values indicate better models that avoid overfitting."""

        return methodology

    def _generate_eda_section(
        self, eda_results: EDAResults, visualization_paths: List[str]
    ) -> str:
        """Generate EDA section."""
        # Build descriptive statistics table
        stats_table = self._build_descriptive_stats_table(eda_results.descriptive_stats)

        # Get correlation insights
        correlations = eda_results.correlations
        if "new_customers" in correlations.columns:
            channel_correlations = correlations["new_customers"].drop(
                "new_customers", errors="ignore"
            )
            top_corr_channel = channel_correlations.idxmax()
            top_corr_value = channel_correlations.max()
        else:
            top_corr_channel = "N/A"
            top_corr_value = 0.0

        # Get seasonality info
        seasonality = eda_results.seasonality
        period = seasonality.period

        # Get control variable effects
        control_impact = eda_results.control_impact
        holiday_effect, holiday_pvalue = control_impact.holiday_effect
        promo_effect, promo_pvalue = control_impact.promo_effect

        # Find visualization paths
        time_series_path = self._find_visualization(visualization_paths, "time_series")
        correlation_path = self._find_visualization(
            visualization_paths, "correlation_heatmap"
        )
        spend_path = self._find_visualization(visualization_paths, "spend_comparison")

        eda_section = f"""## 3. Exploratory Data Analysis

### Descriptive Statistics

{stats_table}

### Correlation Analysis

The correlation analysis reveals the linear relationships between marketing channel spend and customer acquisition.

**Key Finding:** {self._format_channel_name(top_corr_channel)} shows the strongest correlation with customer acquisition (r = {top_corr_value:.3f}).

{self._embed_visualization(correlation_path, "Correlation Heatmap")}

### Total Spend by Channel

{self._embed_visualization(spend_path, "Total Marketing Spend by Channel")}

### Time Series Patterns

{self._embed_visualization(time_series_path, "Customer Acquisition Over Time")}

**Seasonality:** The analysis detected a {period}-week seasonal pattern in customer acquisition data.

### Control Variable Impact

**Holidays Effect:**
- Mean difference in customer acquisition: {holiday_effect:.1f} customers
- Statistical significance: p-value = {holiday_pvalue:.4f}
- Interpretation: {"Statistically significant" if holiday_pvalue < 0.05 else "Not statistically significant"} impact on customer acquisition

**Competitor Promotions Effect:**
- Mean difference in customer acquisition: {promo_effect:.1f} customers
- Statistical significance: p-value = {promo_pvalue:.4f}
- Interpretation: {"Statistically significant" if promo_pvalue < 0.05 else "Not statistically significant"} impact on customer acquisition

### Outlier Detection

{self._format_outliers(eda_results.outliers)}"""

        return eda_section

    def _generate_model_section(
        self, model_results: ModelResults, visualization_paths: List[str]
    ) -> str:
        """Generate model development and validation section."""
        diagnostics = model_results.diagnostics

        # Build model comparison table
        model_comparison = f"""| Metric | Training Set | Test Set |
|--------|--------------|----------|
| R² | {diagnostics.r_squared_train:.4f} | {diagnostics.r_squared_test:.4f} |
| RMSE | {diagnostics.rmse_train:.2f} | {diagnostics.rmse_test:.2f} |
| MAE | {diagnostics.mae_train:.2f} | {diagnostics.mae_test:.2f} |
| AIC | {diagnostics.aic:.2f} | - |
| BIC | {diagnostics.bic:.2f} | - |"""

        # Build coefficient table
        coef_table = self._build_coefficient_table(model_results.coefficients)

        # Cross-validation results
        cv_scores = diagnostics.cv_scores
        if cv_scores:
            cv_mean = np.mean(cv_scores)
            cv_std = np.std(cv_scores)
            cv_text = f"Mean R² = {cv_mean:.4f} (±{cv_std:.4f})"
        else:
            cv_text = "Not available"

        # VIF analysis
        vif_text = self._format_vif_values(diagnostics.vif_values)

        # Find residual diagnostics visualization
        residual_path = self._find_visualization(
            visualization_paths, "residual_diagnostics"
        )

        model_section = f"""## 4. Model Development and Validation

### Model Performance Metrics

{model_comparison}

**Interpretation:**
- The model explains **{diagnostics.r_squared_test*100:.1f}%** of the variance in customer acquisition on the test set
- Test set RMSE of **{diagnostics.rmse_test:.1f}** customers indicates the average prediction error
- {"⚠️ Potential overfitting detected" if (diagnostics.r_squared_train - diagnostics.r_squared_test) > 0.2 else "✓ No significant overfitting detected"}

### Coefficient Estimates

{coef_table}

**Note:** Coefficients represent the marginal effect of each transformed marketing channel on customer acquisition. Confidence intervals are at the 95% level.

### Model Diagnostics

#### Residual Normality Test (Shapiro-Wilk)
- **P-value:** {diagnostics.residual_normality_pvalue:.4f}
- **Interpretation:** {"✓ Residuals are approximately normally distributed" if diagnostics.residual_normality_pvalue > 0.05 else "⚠️ Residuals deviate from normality"}

#### Heteroscedasticity Test (Breusch-Pagan)
- **P-value:** {diagnostics.heteroscedasticity_pvalue:.4f}
- **Interpretation:** {"✓ Homoscedasticity assumption satisfied" if diagnostics.heteroscedasticity_pvalue > 0.05 else "⚠️ Heteroscedasticity detected"}

#### Multicollinearity Analysis (VIF)

{vif_text}

**Interpretation:** VIF values above 10 indicate problematic multicollinearity. {"✓ No severe multicollinearity detected" if all(v < 10 for v in diagnostics.vif_values.values() if not np.isnan(v)) else "⚠️ Some variables show high multicollinearity"}

#### Autocorrelation Test (Durbin-Watson)
- **Statistic:** {diagnostics.durbin_watson:.4f}
- **Interpretation:** Values near 2.0 indicate no autocorrelation. {"✓ No significant autocorrelation" if 1.5 < diagnostics.durbin_watson < 2.5 else "⚠️ Autocorrelation may be present"}

#### Cross-Validation Results (5-Fold)
- **Cross-validation R²:** {cv_text}
- **Interpretation:** {"✓ Model shows good stability across folds" if cv_scores and np.mean(cv_scores) > 0.5 else "Model stability could be improved"}

### Residual Diagnostic Plots

{self._embed_visualization(residual_path, "Residual Diagnostic Plots")}

**Diagnostic Plot Interpretation:**
- **Residuals vs Fitted:** Should show random scatter around zero (no patterns)
- **Q-Q Plot:** Points should follow the diagonal line (normality)
- **Scale-Location:** Should show random scatter (homoscedasticity)
- **Residuals vs Leverage:** Identifies influential observations"""

        return model_section

    def _generate_attribution_section(
        self, attribution_results: AttributionResults, visualization_paths: List[str]
    ) -> str:
        """Generate attribution and ROI analysis section."""
        # Build attribution table
        attribution_table = self._build_attribution_table(attribution_results)

        # Find visualizations
        roi_path = self._find_visualization(visualization_paths, "roi_comparison")
        response_path = self._find_visualization(visualization_paths, "response_curves")
        scatter_path = self._find_visualization(visualization_paths, "channel_scatter")

        # Get top and bottom performers
        rankings = attribution_results.channel_rankings
        top_3 = rankings[:3]
        bottom_3 = rankings[-3:]

        attribution_section = f"""## 5. Attribution and ROI Analysis

### Channel Contribution and ROI

{attribution_table}

### ROI Rankings

**Top 3 Performing Channels:**
{self._format_rankings(top_3, top=True)}

**Bottom 3 Performing Channels:**
{self._format_rankings(bottom_3, top=False)}

{self._embed_visualization(roi_path, "ROI Comparison by Channel")}

### Channel Response Analysis

{self._embed_visualization(scatter_path, "Channel Spend vs Customer Acquisition")}

### Saturation Effects

{self._embed_visualization(response_path, "Marketing Response Curves")}

**Response Curve Interpretation:**
The response curves show how incremental customers change with spend level for each channel. Flattening curves indicate saturation effects where additional spend produces diminishing returns.

### Key Insights

{self._generate_attribution_insights(attribution_results)}"""

        return attribution_section

    def _generate_optimization_section(
        self, optimization_results: OptimizationResults
    ) -> str:
        """Generate budget optimization section."""
        # Build allocation comparison table
        allocation_table = self._build_allocation_table(optimization_results)

        # Calculate total budgets
        current_total = sum(optimization_results.current_allocation.values())
        optimal_total = sum(optimization_results.optimal_allocation.values())

        optimization_section = f"""## 6. Budget Optimization

### Optimization Objective

Maximize customer acquisition subject to:
- Total budget constraint: ${optimal_total:,.0f}
- Channel-specific minimum and maximum spend constraints

### Current vs Optimal Allocation

{allocation_table}

### Expected Impact

**Current Performance:**
- Total budget: ${current_total:,.0f}
- Expected customers: {optimization_results.current_customers:.0f}

**Optimized Performance:**
- Total budget: ${optimal_total:,.0f}
- Expected customers: {optimization_results.expected_customers:.0f}
- **Expected lift: {optimization_results.expected_lift:.1f}%**

### Optimization Status

- **Convergence:** {optimization_results.convergence_status}
- **Iterations:** {optimization_results.iterations}

### Implementation Recommendations

{self._generate_optimization_recommendations(optimization_results)}"""

        return optimization_section

    def _generate_insights_section(
        self,
        attribution_results: AttributionResults,
        optimization_results: OptimizationResults,
    ) -> str:
        """Generate insights and recommendations section."""
        # Identify high and low performers
        rankings = attribution_results.channel_rankings
        high_performers = [ch for ch, roi in rankings if roi > 0.5][:3]
        low_performers = [ch for ch, roi in rankings if roi < 0]

        # Identify channels with significant allocation changes
        significant_changes = []
        for channel in optimization_results.optimal_allocation.keys():
            current = optimization_results.current_allocation.get(channel, 0)
            optimal = optimization_results.optimal_allocation[channel]
            if current > 0:
                pct_change = ((optimal - current) / current) * 100
                if abs(pct_change) > 20:  # More than 20% change
                    significant_changes.append((channel, pct_change))

        insights_section = f"""## 7. Insights and Recommendations

### High-Performing Channels

{self._format_channel_recommendations(high_performers, "increase")}

### Underperforming Channels

{self._format_channel_recommendations(low_performers, "decrease")}

### Budget Reallocation Priorities

{self._format_reallocation_priorities(significant_changes)}

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
- Account for the {attribution_results.channel_rankings[0][0] if attribution_results.channel_rankings else "identified"} seasonal patterns when implementing budget changes
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
- Monitor for unexpected market shifts that may invalidate model assumptions"""

        return insights_section

    def _generate_limitations_section(self) -> str:
        """Generate limitations and assumptions section."""
        limitations = """## 8. Limitations and Assumptions

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

5. **Additional Data:** Collect more granular data (daily instead of weekly) and additional variables (creative quality, audience targeting) to improve model accuracy"""

        return limitations

    def _generate_appendix(
        self, model_results: ModelResults, eda_results: EDAResults
    ) -> str:
        """Generate technical appendix section."""
        # Get transformation parameters
        transformation_details = self._format_transformation_params(
            model_results.transformation_params
        )

        appendix = f"""## Appendix

### A. Technical Details

#### Model Specification

**Model Type:** {model_results.model_type}

**Dependent Variable:** new_customers (weekly customer acquisitions)

**Independent Variables:**
- 8 marketing channel spend variables (transformed)
- 2 control variables (holidays, competitor_promo)

**Estimation Method:** Ordinary Least Squares (OLS) regression

#### Transformation Parameters

{transformation_details}

### B. Full Coefficient Table

{self._build_detailed_coefficient_table(model_results.coefficients)}

### C. Diagnostic Test Results

**Shapiro-Wilk Test (Residual Normality):**
- Null hypothesis: Residuals are normally distributed
- Test statistic: {model_results.diagnostics.residual_normality_pvalue:.6f}
- Conclusion: {"Fail to reject null hypothesis (residuals are approximately normal)" if model_results.diagnostics.residual_normality_pvalue > 0.05 else "Reject null hypothesis (residuals deviate from normality)"}

**Breusch-Pagan Test (Heteroscedasticity):**
- Null hypothesis: Homoscedasticity (constant variance)
- Test statistic: {model_results.diagnostics.heteroscedasticity_pvalue:.6f}
- Conclusion: {"Fail to reject null hypothesis (homoscedasticity)" if model_results.diagnostics.heteroscedasticity_pvalue > 0.05 else "Reject null hypothesis (heteroscedasticity present)"}

**Durbin-Watson Test (Autocorrelation):**
- Test statistic: {model_results.diagnostics.durbin_watson:.4f}
- Expected value (no autocorrelation): 2.0
- Conclusion: {"No significant autocorrelation" if 1.5 < model_results.diagnostics.durbin_watson < 2.5 else "Autocorrelation may be present"}

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

**End of Report**"""

        return appendix

    # Helper methods for formatting

    def _format_channel_name(self, channel: str) -> str:
        """Format channel name for display."""
        return channel.replace("_spend", "").replace("_", " ").title()

    def _find_visualization(self, paths: List[str], keyword: str) -> Optional[str]:
        """Find visualization path containing keyword."""
        for path in paths:
            if keyword in path:
                return path
        return None

    def _embed_visualization(self, path: Optional[str], alt_text: str) -> str:
        """Embed visualization in markdown."""
        if path:
            return f"![{alt_text}]({path})"
        else:
            return f"*[{alt_text} - Visualization not available]*"

    def _build_descriptive_stats_table(self, descriptive_stats: dict) -> str:
        """Build markdown table of descriptive statistics."""
        # Select key variables for the table
        key_vars = ["new_customers"] + [
            col for col in descriptive_stats.keys() if "_spend" in col
        ]

        # Filter to available variables
        available_vars = [var for var in key_vars if var in descriptive_stats]

        if not available_vars:
            return "*No descriptive statistics available*"

        # Build table header
        table = "| Variable | Mean | Median | Std Dev | Min | Max |\n"
        table += "|----------|------|--------|---------|-----|-----|\n"

        # Add rows
        for var in available_vars:
            stats = descriptive_stats[var]
            var_name = (
                self._format_channel_name(var) if "_spend" in var else "New Customers"
            )
            table += f"| {var_name} | {stats['mean']:.1f} | {stats['median']:.1f} | {stats['std']:.1f} | {stats['min']:.1f} | {stats['max']:.1f} |\n"

        return table

    def _format_outliers(self, outliers: dict) -> str:
        """Format outlier detection results."""
        if not outliers:
            return "No significant outliers detected in marketing spend data."

        outlier_text = "The following channels have outlier observations:\n\n"
        for channel, indices in outliers.items():
            channel_name = self._format_channel_name(channel)
            outlier_text += (
                f"- **{channel_name}:** {len(indices)} outlier(s) detected\n"
            )

        return outlier_text

    def _build_coefficient_table(self, coefficients: pd.DataFrame) -> str:
        """Build markdown table of model coefficients."""
        # Filter out constant term for main table
        coef_df = coefficients[coefficients.index != "const"].copy()

        if len(coef_df) == 0:
            return "*No coefficients available*"

        # Build table
        table = "| Variable | Coefficient | Std Error | 95% CI Lower | 95% CI Upper |\n"
        table += (
            "|----------|-------------|-----------|--------------|---------------|\n"
        )

        for idx, row in coef_df.iterrows():
            # Format variable name
            var_name = idx
            for suffix in ["_adstock", "_sat", "_full", "_spend"]:
                var_name = var_name.replace(suffix, "")
            var_name = self._format_channel_name(var_name)

            table += f"| {var_name} | {row['coef']:.4f} | {row['std_err']:.4f} | {row['ci_lower']:.4f} | {row['ci_upper']:.4f} |\n"

        return table

    def _build_detailed_coefficient_table(self, coefficients: pd.DataFrame) -> str:
        """Build detailed coefficient table including constant."""
        table = "| Variable | Coefficient | Std Error | 95% CI Lower | 95% CI Upper |\n"
        table += (
            "|----------|-------------|-----------|--------------|---------------|\n"
        )

        for idx, row in coefficients.iterrows():
            table += f"| {idx} | {row['coef']:.6f} | {row['std_err']:.6f} | {row['ci_lower']:.6f} | {row['ci_upper']:.6f} |\n"

        return table

    def _format_vif_values(self, vif_values: dict) -> str:
        """Format VIF values as markdown table."""
        if not vif_values:
            return "*VIF analysis not available*"

        table = "| Variable | VIF |\n"
        table += "|----------|-----|\n"

        for var, vif in vif_values.items():
            if not np.isnan(vif):
                # Format variable name
                var_name = var
                for suffix in ["_adstock", "_sat", "_full", "_spend"]:
                    var_name = var_name.replace(suffix, "")
                var_name = self._format_channel_name(var_name)

                status = "⚠️" if vif > 10 else "✓"
                table += f"| {var_name} | {vif:.2f} {status} |\n"

        return table

    def _build_attribution_table(self, attribution_results: AttributionResults) -> str:
        """Build attribution and ROI table."""
        table = "| Channel | Marginal Contribution | ROI | 95% CI Lower | 95% CI Upper | % of Total |\n"
        table += "|---------|----------------------|-----|--------------|--------------|------------|\n"

        # Sort by ROI
        sorted_channels = sorted(
            attribution_results.roi_by_channel.keys(),
            key=lambda ch: attribution_results.roi_by_channel[ch][0],
            reverse=True,
        )

        for channel in sorted_channels:
            channel_name = self._format_channel_name(channel)
            contribution = attribution_results.marginal_contributions[channel]
            roi, (ci_lower, ci_upper) = attribution_results.roi_by_channel[channel]
            pct = attribution_results.percentage_contributions[channel]

            table += f"| {channel_name} | {contribution:.1f} | {roi*100:.1f}% | {ci_lower*100:.1f}% | {ci_upper*100:.1f}% | {pct:.1f}% |\n"

        return table

    def _format_rankings(self, rankings: list, top: bool = True) -> str:
        """Format channel rankings."""
        if not rankings:
            return "*No rankings available*"

        text = ""
        for i, (channel, roi) in enumerate(rankings, 1):
            channel_name = self._format_channel_name(channel)
            emoji = "🏆" if top and i == 1 else "📈" if top else "📉"
            text += f"{i}. {emoji} **{channel_name}**: {roi*100:.1f}% ROI\n"

        return text

    def _generate_attribution_insights(
        self, attribution_results: AttributionResults
    ) -> str:
        """Generate key insights from attribution analysis."""
        rankings = attribution_results.channel_rankings

        # Identify positive and negative ROI channels
        positive_roi = [ch for ch, roi in rankings if roi > 0]
        negative_roi = [ch for ch, roi in rankings if roi < 0]

        insights = ""

        if positive_roi:
            insights += f"- **{len(positive_roi)} channels** show positive ROI and should be prioritized for investment\n"

        if negative_roi:
            insights += f"- **{len(negative_roi)} channels** show negative ROI and require investigation or budget reduction\n"

        # Identify high-contribution channels
        contributions = attribution_results.percentage_contributions
        high_contrib = [ch for ch, pct in contributions.items() if pct > 15]

        if high_contrib:
            insights += f"- **{len(high_contrib)} channels** contribute more than 15% each to total customer acquisition\n"

        return (
            insights
            if insights
            else "- Detailed insights available in the optimization section"
        )

    def _build_allocation_table(self, optimization_results: OptimizationResults) -> str:
        """Build current vs optimal allocation table."""
        table = (
            "| Channel | Current Spend | Optimal Spend | Change ($) | Change (%) |\n"
        )
        table += (
            "|---------|---------------|---------------|------------|------------|\n"
        )

        for channel in optimization_results.optimal_allocation.keys():
            channel_name = self._format_channel_name(channel)
            current = optimization_results.current_allocation.get(channel, 0)
            optimal = optimization_results.optimal_allocation[channel]
            change_abs = optimal - current
            change_pct = ((optimal - current) / current * 100) if current > 0 else 0

            arrow = "↑" if change_abs > 0 else "↓" if change_abs < 0 else "→"
            table += f"| {channel_name} | ${current:,.0f} | ${optimal:,.0f} | ${change_abs:,.0f} {arrow} | {change_pct:.1f}% |\n"

        return table

    def _generate_optimization_recommendations(
        self, optimization_results: OptimizationResults
    ) -> str:
        """Generate specific optimization recommendations."""
        recommendations = []

        for channel in optimization_results.optimal_allocation.keys():
            current = optimization_results.current_allocation.get(channel, 0)
            optimal = optimization_results.optimal_allocation[channel]

            if current > 0:
                change_pct = ((optimal - current) / current) * 100

                if change_pct > 20:
                    channel_name = self._format_channel_name(channel)
                    recommendations.append(
                        f"- **Increase {channel_name} spend by {change_pct:.0f}%** "
                        f"(from ${current:,.0f} to ${optimal:,.0f})"
                    )
                elif change_pct < -20:
                    channel_name = self._format_channel_name(channel)
                    recommendations.append(
                        f"- **Decrease {channel_name} spend by {abs(change_pct):.0f}%** "
                        f"(from ${current:,.0f} to ${optimal:,.0f})"
                    )

        if not recommendations:
            return "- Current allocation is near-optimal; minor adjustments recommended"

        return "\n".join(recommendations)

    def _format_channel_recommendations(self, channels: list, action: str) -> str:
        """Format channel-specific recommendations."""
        if not channels:
            return f"*No channels identified for {action}*"

        text = ""
        for channel in channels:
            channel_name = self._format_channel_name(channel)
            if action == "increase":
                text += f"- **{channel_name}**: Strong performance indicates opportunity for increased investment\n"
            else:
                text += f"- **{channel_name}**: Underperformance suggests need for optimization or budget reallocation\n"

        return text

    def _format_reallocation_priorities(self, changes: list) -> str:
        """Format budget reallocation priorities."""
        if not changes:
            return "*Current allocation is near-optimal*"

        # Sort by absolute change
        changes_sorted = sorted(changes, key=lambda x: abs(x[1]), reverse=True)

        text = ""
        for channel, pct_change in changes_sorted[:5]:  # Top 5 changes
            channel_name = self._format_channel_name(channel)
            direction = "increase" if pct_change > 0 else "decrease"
            text += f"- **{channel_name}**: {direction.capitalize()} by {abs(pct_change):.0f}%\n"

        return text

    def _format_transformation_params(self, transformation_params: dict) -> str:
        """Format transformation parameters."""
        if not transformation_params:
            return "*No transformations applied*"

        text = "| Channel | Adstock Decay | Saturation Alpha | Saturation Gamma |\n"
        text += "|---------|---------------|------------------|------------------|\n"

        for channel, params in transformation_params.items():
            channel_name = self._format_channel_name(channel)
            decay = params.get("decay", "-")
            alpha = params.get("alpha", "-")
            gamma = params.get("gamma", "-")

            # Format values
            decay_str = (
                f"{decay:.3f}" if isinstance(decay, (int, float)) else str(decay)
            )
            alpha_str = (
                f"{alpha:.1f}" if isinstance(alpha, (int, float)) else str(alpha)
            )
            gamma_str = (
                f"{gamma:.3f}" if isinstance(gamma, (int, float)) else str(gamma)
            )

            text += f"| {channel_name} | {decay_str} | {alpha_str} | {gamma_str} |\n"

        return text
