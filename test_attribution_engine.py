"""
Test script for AttributionEngine component.

This script tests the AttributionEngine with the fitted model from previous tasks.
"""

import sys
import pandas as pd
import numpy as np
from src.data_loader import DataLoader
from src.statistical_modeler import StatisticalModeler
from src.attribution_engine import AttributionEngine


def test_attribution_engine():
    """Test AttributionEngine with real data."""
    print("=" * 80)
    print("Testing AttributionEngine Component")
    print("=" * 80)
    
    # Load data
    print("\n1. Loading data...")
    loader = DataLoader()
    df = loader.load_data('MMM dataset - Sheet1.csv')
    print(f"   Loaded {len(df)} weeks of data")
    
    # Fit model
    print("\n2. Fitting statistical model...")
    modeler = StatisticalModeler(random_state=42)
    model_results = modeler.fit(df, test_size=0.2)
    print(f"   Best model: {model_results.model_type}")
    print(f"   Test R²: {model_results.diagnostics.r_squared_test:.4f}")
    
    # Initialize AttributionEngine
    print("\n3. Initializing AttributionEngine...")
    customer_value = 100.0  # Assume $100 customer lifetime value
    engine = AttributionEngine(model_results, customer_value=customer_value)
    print(f"   Customer value: ${customer_value}")
    
    # Calculate attribution
    print("\n4. Calculating attribution...")
    attribution = engine.calculate_attribution(df)
    
    print("\n   Marginal Contributions (Incremental Customers):")
    for channel, contribution in sorted(
        attribution.marginal_contributions.items(),
        key=lambda x: x[1],
        reverse=True
    ):
        print(f"      {channel:25s}: {contribution:10.2f} customers")
    
    print("\n   ROI by Channel:")
    for channel, roi in attribution.channel_rankings:
        roi_val, (ci_lower, ci_upper) = attribution.roi_by_channel[channel]
        print(f"      {channel:25s}: {roi_val*100:8.2f}% (95% CI: [{ci_lower*100:8.2f}%, {ci_upper*100:8.2f}%])")
    
    print("\n   Percentage Contributions:")
    for channel, pct in sorted(
        attribution.percentage_contributions.items(),
        key=lambda x: x[1],
        reverse=True
    ):
        print(f"      {channel:25s}: {pct:6.2f}%")
    
    # Optimize budget
    print("\n5. Optimizing budget allocation...")
    total_budget = sum(df[ch].sum() for ch in engine.spend_channels if ch in df.columns)
    print(f"   Total current budget: ${total_budget:,.2f}")
    
    optimization = engine.optimize_budget(df, total_budget)
    
    print(f"\n   Optimization Status: {optimization.convergence_status}")
    print(f"   Iterations: {optimization.iterations}")
    print(f"   Current customers: {optimization.current_customers:.2f}")
    print(f"   Expected customers (optimized): {optimization.expected_customers:.2f}")
    print(f"   Expected lift: {optimization.expected_lift:.2f}%")
    
    print("\n   Budget Reallocation Recommendations:")
    print(f"      {'Channel':<25s} {'Current':>12s} {'Optimal':>12s} {'Change':>12s} {'Change %':>10s}")
    print("      " + "-" * 75)
    
    for channel in engine.spend_channels:
        if channel in optimization.current_allocation:
            current = optimization.current_allocation[channel]
            optimal = optimization.optimal_allocation[channel]
            change = optimal - current
            change_pct = (change / current * 100) if current > 0 else 0
            
            print(f"      {channel:<25s} ${current:>11,.2f} ${optimal:>11,.2f} ${change:>11,.2f} {change_pct:>9.1f}%")
    
    print("\n" + "=" * 80)
    print("AttributionEngine Test Complete!")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    try:
        success = test_attribution_engine()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
