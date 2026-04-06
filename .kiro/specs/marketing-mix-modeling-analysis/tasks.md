# Implementation Plan: Marketing Mix Modeling Analysis

## Overview

This implementation plan breaks down the MMM analysis system into discrete, testable coding tasks. The system follows a pipeline architecture with six main components: DataLoader, EDAModule, StatisticalModeler, AttributionEngine, VisualizationGenerator, and ReportGenerator. Each component is implemented incrementally with testing integrated throughout.

The implementation uses Python with pandas, numpy, statsmodels, scikit-learn, scipy, matplotlib, and seaborn. Property-based tests validate core mathematical transformations, while unit and integration tests ensure overall system correctness.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create directory structure (src/, tests/, outputs/)
  - Create requirements.txt with all dependencies and versions
  - Create README.md with setup instructions and usage examples
  - Set up logging configuration
  - Create __init__.py files for proper package structure
  - _Requirements: 7.1, 7.4, 7.5_

- [x] 2. Implement DataLoader component
  - [x] 2.1 Create DataLoader class with schema validation
    - Implement load_data() method to read CSV files
    - Implement validate_schema() to check required columns
    - Implement _check_required_columns() helper method
    - Implement _validate_date_column() for date parsing
    - Add type hints and docstrings
    - _Requirements: 1.1, 1.2, 1.4_
  
  - [x] 2.2 Add data quality validation methods
    - Implement validate_data_quality() method
    - Implement _validate_numeric_columns() for non-negative checks
    - Implement _check_missing_values() to detect NaN values
    - Implement _check_duplicates() for duplicate date detection
    - Implement _type_conversion() for proper dtype casting
    - _Requirements: 1.3, 1.6, 1.7, 1.8_
  
  - [x] 2.3 Add error handling for edge cases
    - Handle FileNotFoundError with descriptive messages
    - Validate minimum data requirements (20 weeks)
    - Return ValidationResult with errors and warnings
    - _Requirements: 1.5, 10.1, 10.2_
  
  - [ ]* 2.4 Write property tests for DataLoader
    - **Property 1: Schema validation is consistent**
    - **Validates: Requirements 1.2**
    - Test that valid schemas always pass, invalid always fail
    - Test that column order doesn't affect validation
  
  - [ ]* 2.5 Write unit tests for DataLoader
    - Test successful data loading with valid CSV
    - Test error handling for missing files
    - Test error handling for invalid schemas
    - Test error handling for insufficient data
    - Test missing value detection
    - Test duplicate detection
    - _Requirements: 1.1-1.8, 10.1, 10.2_

- [x] 3. Implement EDAModule component
  - [x] 3.1 Create EDAModule class with descriptive statistics
    - Implement analyze() method as main entry point
    - Implement compute_descriptive_stats() for mean, median, std, min, max, quartiles
    - Implement compute_correlations() for correlation matrix
    - Create EDAResults dataclass for structured output
    - _Requirements: 2.1, 2.2_
  
  - [x] 3.2 Add time period and spend analysis methods
    - Implement time period identification (start, end, n_weeks)
    - Implement total spend calculation per channel
    - _Requirements: 2.3, 2.4_
  
  - [x] 3.3 Implement outlier detection
    - Implement detect_outliers() using IQR method
    - Calculate Q1, Q3, and IQR for each channel
    - Identify values outside [Q1 - 1.5*IQR, Q3 + 1.5*IQR]
    - _Requirements: 2.5_
  
  - [x] 3.4 Implement seasonality and control variable analysis
    - Implement analyze_seasonality() for pattern detection
    - Implement analyze_control_variables() for holiday/promo impact
    - Use t-tests to compare means for control variables
    - Create SeasonalityResults and ControlAnalysis dataclasses
    - _Requirements: 2.6, 2.7_
  
  - [ ]* 3.5 Write unit tests for EDAModule
    - Test descriptive statistics calculations
    - Test correlation matrix computation
    - Test outlier detection with known data
    - Test time period identification
    - Test control variable impact analysis
    - _Requirements: 2.1-2.8_

- [x] 4. Checkpoint - Ensure data pipeline works end-to-end
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement StatisticalModeler component - Core transformations
  - [x] 5.1 Create StatisticalModeler class and transformation methods
    - Implement __init__() with random_state for reproducibility
    - Implement apply_adstock_transformation() with geometric decay
    - Implement apply_saturation_transformation() with Hill curve
    - Add docstrings explaining transformation mathematics
    - _Requirements: 3.2, 3.3_
  
  - [ ]* 5.2 Write property tests for adstock transformation
    - **Property 2: Adstock preserves non-negativity**
    - **Validates: Requirements 3.2**
    - Test that non-negative spend produces non-negative adstock
    - **Property 3: Adstock with zero decay equals identity**
    - **Validates: Requirements 3.2**
    - Test that decay=0 returns original spend
  
  - [ ]* 5.3 Write property tests for saturation transformation
    - **Property 4: Saturation is monotonically increasing**
    - **Validates: Requirements 3.3**
    - Test that higher spend produces higher saturated value
    - **Property 5: Saturation is bounded**
    - **Validates: Requirements 3.3**
    - Test that saturated values are in [0, 1] range
  
  - [ ]* 5.4 Write unit tests for transformations
    - Test adstock with known decay rates
    - Test saturation with known parameters
    - Test edge cases (zero spend, very high spend)
    - _Requirements: 3.2, 3.3_

- [x] 6. Implement StatisticalModeler component - Model fitting
  - [x] 6.1 Implement model fitting and hyperparameter optimization
    - Implement fit() method with train/test split
    - Implement baseline linear regression model
    - Implement grid search for adstock decay rates
    - Implement grid search for saturation parameters (alpha, gamma)
    - Compare model specifications (baseline, adstock, saturation, full)
    - Select best model using AIC/BIC
    - Create ModelResults dataclass
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_
  
  - [x] 6.2 Implement model diagnostics and validation
    - Implement validate_model() method
    - Calculate R-squared, RMSE, MAE for train and test sets
    - Implement residual normality test (Shapiro-Wilk)
    - Implement heteroscedasticity test (Breusch-Pagan)
    - Calculate VIF for multicollinearity detection
    - Calculate Durbin-Watson statistic for autocorrelation
    - Implement k-fold cross-validation (k=5)
    - Create DiagnosticsResults dataclass
    - _Requirements: 3.7, 3.8, 3.9, 3.10, 8.1-8.9_
  
  - [x] 6.3 Add error handling for model fitting
    - Handle convergence failures with retry logic
    - Detect and exclude zero-variance channels
    - Issue overfitting warnings when test performance degrades
    - _Requirements: 10.3, 10.4, 10.5_
  
  - [ ]* 6.4 Write unit tests for StatisticalModeler
    - Test model fitting with synthetic data
    - Test hyperparameter optimization
    - Test diagnostic calculations
    - Test error handling for edge cases
    - _Requirements: 3.1-3.10, 8.1-8.9_

- [x] 7. Checkpoint - Ensure statistical modeling works correctly
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Implement AttributionEngine component
  - [x] 8.1 Create AttributionEngine class with attribution calculations
    - Implement __init__() accepting ModelResults and customer_value
    - Implement calculate_marginal_contribution() for each channel
    - Implement calculate_roi() with confidence intervals
    - Calculate percentage contributions
    - Rank channels by ROI
    - Create AttributionResults dataclass
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.6, 4.7_
  
  - [x] 8.2 Implement budget optimization
    - Implement optimize_budget() method
    - Define objective function (negative expected customers)
    - Set up constraints (budget equality, min/max spend)
    - Use scipy.optimize.minimize with SLSQP method
    - Calculate expected lift vs current allocation
    - Create OptimizationResults dataclass
    - _Requirements: 4.5, 9.1-9.8_
  
  - [ ]* 8.3 Write property tests for optimization
    - **Property 6: Optimization respects budget constraint**
    - **Validates: Requirements 9.1, 9.2**
    - Test that optimal allocation sums to total budget
    - **Property 7: Optimization respects channel constraints**
    - **Validates: Requirements 9.4**
    - Test that allocations are within min/max bounds
  
  - [ ]* 8.4 Write unit tests for AttributionEngine
    - Test marginal contribution calculations
    - Test ROI calculations with known coefficients
    - Test channel ranking logic
    - Test optimization with simple scenarios
    - Test constraint handling
    - _Requirements: 4.1-4.7, 9.1-9.8_

- [-] 9. Implement VisualizationGenerator component
  - [ ] 9.1 Create VisualizationGenerator class and setup
    - Implement __init__() with output directory creation
    - Set up matplotlib/seaborn styling (colorblind palette, fonts, DPI)
    - Implement generate_all() as main entry point
    - _Requirements: 5.8, 5.9_
  
  - [ ] 9.2 Implement time series and correlation visualizations
    - Implement plot_time_series() with control variable markers
    - Implement plot_correlation_heatmap() with annotations
    - Save plots as PNG files with proper titles and labels
    - _Requirements: 5.1, 5.2_
  
  - [ ] 9.3 Implement spend and ROI comparison charts
    - Implement plot_spend_comparison() as horizontal bar chart
    - Implement plot_roi_comparison() with confidence intervals
    - Sort bars appropriately (by spend, by ROI)
    - _Requirements: 5.3, 5.4_
  
  - [ ] 9.4 Implement scatter plots and response curves
    - Implement plot_channel_scatter() with trend lines
    - Implement plot_response_curves() showing saturation effects
    - Add 95% confidence bands where appropriate
    - _Requirements: 5.5, 5.6_
  
  - [ ] 9.5 Implement residual diagnostic plots
    - Implement plot_residual_diagnostics() as 2x2 grid
    - Create residuals vs fitted, Q-Q plot, scale-location, leverage plots
    - _Requirements: 5.7_
  
  - [ ] 9.6 Add error handling for visualization failures
    - Wrap each plot generation in try-except
    - Log errors and continue with remaining visualizations
    - _Requirements: 10.7_
  
  - [ ]* 9.7 Write unit tests for VisualizationGenerator
    - Test that all plot methods create files
    - Test that files are saved to correct directory
    - Test error handling when plot generation fails
    - _Requirements: 5.1-5.9, 10.7_

- [ ] 10. Implement ReportGenerator component
  - [ ] 10.1 Create ReportGenerator class and report structure
    - Implement __init__() with output path
    - Implement generate_report() method
    - Create executive summary section with key findings
    - Create introduction section
    - _Requirements: 6.1, 6.2_
  
  - [ ] 10.2 Add methodology and EDA sections
    - Document methodology (model types, transformations, validation)
    - Present EDA findings with tables
    - Embed visualization references
    - _Requirements: 6.3, 6.9_
  
  - [ ] 10.3 Add model validation and attribution sections
    - Present model performance metrics with interpretation
    - Include diagnostics results table
    - Present attribution results and ROI rankings
    - _Requirements: 6.4, 6.5_
  
  - [ ] 10.4 Add optimization and recommendations sections
    - Present current vs optimal allocation comparison
    - Provide specific budget reallocation recommendations
    - Identify high/low performing channels
    - _Requirements: 6.6, 6.7_
  
  - [ ] 10.5 Add limitations and appendix sections
    - Discuss model assumptions and limitations
    - Include technical appendix with full details
    - _Requirements: 6.8_
  
  - [ ]* 10.6 Write unit tests for ReportGenerator
    - Test that report file is created
    - Test that all sections are present
    - Test that visualizations are referenced
    - _Requirements: 6.1-6.10_

- [ ] 11. Create main pipeline orchestration
  - [ ] 11.1 Create main.py script to run full pipeline
    - Accept command-line arguments (CSV path, output directory)
    - Instantiate all components in correct order
    - Pass data through pipeline: DataLoader → EDA → Modeler → Attribution → Visualization → Report
    - Add logging at each pipeline stage
    - Handle errors gracefully with informative messages
    - _Requirements: 7.1, 7.10, 10.6_
  
  - [ ]* 11.2 Write integration tests for full pipeline
    - Test end-to-end execution with sample data
    - Verify all output files are created
    - Verify report contains expected sections
    - Test error propagation through pipeline
    - _Requirements: 7.8_

- [ ] 12. Add code quality and documentation
  - [ ] 12.1 Add comprehensive docstrings
    - Add Google-style docstrings to all public functions and classes
    - Include parameter descriptions, return types, and examples
    - _Requirements: 7.2_
  
  - [ ] 12.2 Add type hints throughout codebase
    - Add type hints to all function parameters and return values
    - Use typing module for complex types (Dict, List, Tuple, Optional)
    - _Requirements: 7.3_
  
  - [ ] 12.3 Format code and check compliance
    - Run black formatter on all Python files
    - Verify PEP 8 compliance
    - _Requirements: 7.6_
  
  - [ ] 12.4 Update README with complete documentation
    - Add installation instructions
    - Add usage examples with command-line arguments
    - Add description of output files
    - Add example interpretation of results
    - _Requirements: 7.5_

- [ ] 13. Final checkpoint - Complete system validation
  - Run full test suite and ensure all tests pass
  - Run pipeline on provided MMM dataset
  - Review generated report for completeness
  - Ensure all requirements are satisfied
  - Ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Property-based tests validate universal mathematical properties
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end pipeline execution
- Checkpoints ensure incremental validation at logical breaks
- All code should follow PEP 8 style guidelines
- Random seeds should be set for reproducibility (random_state=42)
