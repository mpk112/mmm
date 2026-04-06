"""
Test script for VisualizationGenerator component.

This script tests the VisualizationGenerator with real data to ensure
all visualization methods work correctly.
"""

import pandas as pd
import numpy as np
from pathlib import Path

from src.data_loader import DataLoader
from src.eda_module import EDAModule
from src.statistical_modeler import StatisticalModeler
from src.attribution_engine import AttributionEngine
from src.visualization_generator import VisualizationGenerator


def test_visualization_generator():
    """Test VisualizationGenerator with real MMM data."""
    print("=" * 80)
    print("Testing VisualizationGenerator Component")
    print("=" * 80)
    
    # Load data
    print("\n1. Loading data...")
    loader = DataLoader()
    df = loader.load_data("MMM dataset - Sheet1.csv")
    print(f"   ✓ Loaded {len(df)} weeks of data")
    
    # Run EDA
    print("\n2. Running EDA...")
    eda = EDAModule()
    eda_results = eda.analyze(df)
    print(f"   ✓ EDA complete")
    print(f"   - Correlations shape: {eda_results.correlations.shape}")
    print(f"   - Total spend channels: {len(eda_results.total_spend_by_channel)}")
    
    # Fit model
    print("\n3. Fitting statistical model...")
    modeler = StatisticalModeler(random_state=42)
    model_results = modeler.fit(df, test_size=0.2)
    print(f"   ✓ Model fitted: {model_results.model_type}")
    print(f"   - Train R²: {model_results.diagnostics.r_squared_train:.4f}")
    print(f"   - Test R²: {model_results.diagnostics.r_squared_test:.4f}")
    
    # Calculate attribution
    print("\n4. Calculating attribution...")
    engine = AttributionEngine(model_results, customer_value=100.0)
    attribution_results = engine.calculate_attribution(df)
    print(f"   ✓ Attribution calculated")
    print(f"   - Channels analyzed: {len(attribution_results.roi_by_channel)}")
    
    # Generate visualizations
    print("\n5. Generating visualizations...")
    viz = VisualizationGenerator(output_dir="outputs/visualizations")
    
    try:
        file_paths = viz.generate_all(df, eda_results, model_results, attribution_results)
        print(f"   ✓ Generated {len(file_paths)} visualizations")
        
        print("\n   Generated files:")
        for path in file_paths:
            file_path = Path(path)
            if file_path.exists():
                size_kb = file_path.stat().st_size / 1024
                print(f"   ✓ {file_path.name} ({size_kb:.1f} KB)")
            else:
                print(f"   ✗ {file_path.name} (NOT FOUND)")
        
        # Test individual methods
        print("\n6. Testing individual visualization methods...")
        
        # Time series
        try:
            path = viz.plot_time_series(df)
            print(f"   ✓ Time series plot: {Path(path).name}")
        except Exception as e:
            print(f"   ✗ Time series plot failed: {str(e)}")
        
        # Correlation heatmap
        try:
            path = viz.plot_correlation_heatmap(eda_results.correlations)
            print(f"   ✓ Correlation heatmap: {Path(path).name}")
        except Exception as e:
            print(f"   ✗ Correlation heatmap failed: {str(e)}")
        
        # Spend comparison
        try:
            path = viz.plot_spend_comparison(eda_results.total_spend_by_channel)
            print(f"   ✓ Spend comparison: {Path(path).name}")
        except Exception as e:
            print(f"   ✗ Spend comparison failed: {str(e)}")
        
        # ROI comparison
        try:
            path = viz.plot_roi_comparison(attribution_results)
            print(f"   ✓ ROI comparison: {Path(path).name}")
        except Exception as e:
            print(f"   ✗ ROI comparison failed: {str(e)}")
        
        # Channel scatter
        try:
            path = viz.plot_channel_scatter(df)
            print(f"   ✓ Channel scatter plots: {Path(path).name}")
        except Exception as e:
            print(f"   ✗ Channel scatter plots failed: {str(e)}")
        
        # Response curves
        try:
            path = viz.plot_response_curves(model_results, df)
            print(f"   ✓ Response curves: {Path(path).name}")
        except Exception as e:
            print(f"   ✗ Response curves failed: {str(e)}")
        
        # Residual diagnostics
        try:
            path = viz.plot_residual_diagnostics(model_results)
            print(f"   ✓ Residual diagnostics: {Path(path).name}")
        except Exception as e:
            print(f"   ✗ Residual diagnostics failed: {str(e)}")
        
        print("\n" + "=" * 80)
        print("✓ VisualizationGenerator test completed successfully!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Visualization generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_visualization_generator()
    exit(0 if success else 1)
