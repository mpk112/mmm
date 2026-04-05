"""Test script for Task 6: StatisticalModeler model fitting."""

import pandas as pd
import numpy as np
from src.data_loader import DataLoader
from src.statistical_modeler import StatisticalModeler


def test_model_fitting():
    """Test model fitting with real data."""
    print("=" * 60)
    print("Testing StatisticalModeler Model Fitting")
    print("=" * 60)
    print()
    
    # Load data
    print("Loading data...")
    loader = DataLoader()
    df = loader.load_data('MMM dataset - Sheet1.csv')
    print(f"  Loaded {len(df)} weeks of data")
    print()
    
    # Initialize modeler
    print("Initializing StatisticalModeler...")
    modeler = StatisticalModeler(random_state=42)
    print()
    
    # Fit model
    print("Fitting models (this may take a minute)...")
    print("-" * 60)
    try:
        results = modeler.fit(df, test_size=0.2)
        print("-" * 60)
        print()
        
        # Display results
        print("Model Fitting Results:")
        print(f"  Model Type: {results.model_type}")
        print()
        
        print("Performance Metrics:")
        print(f"  Train R²: {results.diagnostics.r_squared_train:.4f}")
        print(f"  Test R²: {results.diagnostics.r_squared_test:.4f}")
        print(f"  Train RMSE: {results.diagnostics.rmse_train:.2f}")
        print(f"  Test RMSE: {results.diagnostics.rmse_test:.2f}")
        print(f"  Train MAE: {results.diagnostics.mae_train:.2f}")
        print(f"  Test MAE: {results.diagnostics.mae_test:.2f}")
        print()
        
        print("Model Selection Criteria:")
        print(f"  AIC: {results.diagnostics.aic:.2f}")
        print(f"  BIC: {results.diagnostics.bic:.2f}")
        print()
        
        print("Diagnostic Tests:")
        print(f"  Residual Normality (p-value): {results.diagnostics.residual_normality_pvalue:.4f}")
        print(f"  Heteroscedasticity (p-value): {results.diagnostics.heteroscedasticity_pvalue:.4f}")
        print(f"  Durbin-Watson: {results.diagnostics.durbin_watson:.4f}")
        print()
        
        print("VIF Values (Multicollinearity Check):")
        for var, vif in results.diagnostics.vif_values.items():
            if not np.isnan(vif):
                status = "⚠️ HIGH" if vif > 10 else "✓ OK"
                print(f"  {var}: {vif:.2f} {status}")
        print()
        
        if results.diagnostics.cv_scores:
            print("Cross-Validation Scores:")
            print(f"  Mean CV R²: {np.mean(results.diagnostics.cv_scores):.4f}")
            print(f"  Std CV R²: {np.std(results.diagnostics.cv_scores):.4f}")
            print()
        
        print("Top 5 Coefficients:")
        # Sort by absolute coefficient value
        coef_sorted = results.coefficients.sort_values('coef', key=abs, ascending=False)
        for idx, row in coef_sorted.head(5).iterrows():
            print(f"  {idx}: {row['coef']:.4f} (95% CI: [{row['ci_lower']:.4f}, {row['ci_upper']:.4f}])")
        print()
        
        print("Transformation Parameters:")
        if results.transformation_params:
            for channel, params in list(results.transformation_params.items())[:3]:
                print(f"  {channel}: {params}")
        else:
            print("  No transformations applied (baseline model)")
        print()
        
        print("✓ Model fitting completed successfully!")
        
    except Exception as e:
        print(f"✗ Error during model fitting: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    print("=" * 60)
    print("Test completed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    test_model_fitting()
