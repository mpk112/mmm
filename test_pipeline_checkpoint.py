"""
Checkpoint test for Task 4: End-to-end data pipeline validation.

This script tests that the data pipeline works correctly from data loading
through EDA analysis, ensuring all components integrate properly.
"""

from src.data_loader import DataLoader
from src.eda_module import EDAModule


def test_data_pipeline_end_to_end():
    """Test complete data pipeline from loading to EDA results."""
    
    print("=" * 70)
    print("CHECKPOINT TEST: End-to-End Data Pipeline Validation")
    print("=" * 70)
    
    # Step 1: Load data using DataLoader
    print("\n[Step 1] Loading data with DataLoader...")
    loader = DataLoader()
    
    try:
        df = loader.load_data('MMM dataset - Sheet1.csv')
        print(f"✓ Data loaded successfully")
        print(f"  - Shape: {df.shape}")
        print(f"  - Date range: {df.index.min()} to {df.index.max()}")
        print(f"  - Columns: {len(df.columns)} columns")
    except Exception as e:
        print(f"✗ FAILED: Data loading failed with error: {e}")
        return False
    
    # Step 2: Pass data to EDAModule
    print("\n[Step 2] Running EDA analysis...")
    eda = EDAModule()
    
    try:
        eda_results = eda.analyze(df)
        print(f"✓ EDA analysis completed successfully")
    except Exception as e:
        print(f"✗ FAILED: EDA analysis failed with error: {e}")
        return False
    
    # Step 3: Verify EDAResults structure
    print("\n[Step 3] Verifying EDAResults structure...")
    
    # Check that all expected fields exist
    expected_fields = [
        'descriptive_stats',
        'correlations',
        'time_period',
        'total_spend_by_channel',
        'outliers',
        'seasonality',
        'control_impact'
    ]
    
    all_fields_present = True
    for field in expected_fields:
        if hasattr(eda_results, field):
            print(f"✓ Field '{field}' present")
        else:
            print(f"✗ FAILED: Field '{field}' missing")
            all_fields_present = False
    
    if not all_fields_present:
        return False
    
    # Step 4: Verify field contents are populated
    print("\n[Step 4] Verifying field contents are populated...")
    
    # Check descriptive_stats
    if eda_results.descriptive_stats and len(eda_results.descriptive_stats) > 0:
        print(f"✓ descriptive_stats: {len(eda_results.descriptive_stats)} columns analyzed")
        # Show sample stats for one column
        sample_col = list(eda_results.descriptive_stats.keys())[0]
        print(f"  - Sample ({sample_col}): mean={eda_results.descriptive_stats[sample_col]['mean']:.2f}")
    else:
        print(f"✗ FAILED: descriptive_stats is empty")
        return False
    
    # Check correlations
    if eda_results.correlations is not None and not eda_results.correlations.empty:
        print(f"✓ correlations: {eda_results.correlations.shape} matrix")
        # Check that new_customers is in the correlation matrix
        if 'new_customers' in eda_results.correlations.columns:
            print(f"  - 'new_customers' column present in correlation matrix")
        else:
            print(f"✗ WARNING: 'new_customers' not in correlation matrix")
    else:
        print(f"✗ FAILED: correlations is empty")
        return False
    
    # Check time_period
    if eda_results.time_period and 'start_date' in eda_results.time_period:
        print(f"✓ time_period: {eda_results.time_period['n_weeks']} weeks")
        print(f"  - Start: {eda_results.time_period['start_date']}")
        print(f"  - End: {eda_results.time_period['end_date']}")
    else:
        print(f"✗ FAILED: time_period is incomplete")
        return False
    
    # Check total_spend_by_channel
    if eda_results.total_spend_by_channel is not None and len(eda_results.total_spend_by_channel) > 0:
        print(f"✓ total_spend_by_channel: {len(eda_results.total_spend_by_channel)} channels")
        print(f"  - Total marketing spend: ${eda_results.total_spend_by_channel.sum():,.0f}")
    else:
        print(f"✗ FAILED: total_spend_by_channel is empty")
        return False
    
    # Check outliers
    if eda_results.outliers is not None:
        outlier_count = sum(len(v) for v in eda_results.outliers.values())
        print(f"✓ outliers: {outlier_count} outliers detected across {len(eda_results.outliers)} channels")
    else:
        print(f"✗ FAILED: outliers is None")
        return False
    
    # Check seasonality
    if eda_results.seasonality is not None:
        print(f"✓ seasonality: period={eda_results.seasonality.period} weeks")
        print(f"  - Trend component: {len(eda_results.seasonality.trend)} values")
        print(f"  - Seasonal component: {len(eda_results.seasonality.seasonal)} values")
        print(f"  - Residual component: {len(eda_results.seasonality.residual)} values")
    else:
        print(f"✗ FAILED: seasonality is None")
        return False
    
    # Check control_impact
    if eda_results.control_impact is not None:
        holiday_effect, holiday_pval = eda_results.control_impact.holiday_effect
        promo_effect, promo_pval = eda_results.control_impact.promo_effect
        print(f"✓ control_impact:")
        print(f"  - Holiday effect: {holiday_effect:+.0f} customers (p={holiday_pval:.4f})")
        print(f"  - Competitor promo effect: {promo_effect:+.0f} customers (p={promo_pval:.4f})")
    else:
        print(f"✗ FAILED: control_impact is None")
        return False
    
    # Step 5: Summary
    print("\n" + "=" * 70)
    print("CHECKPOINT TEST RESULT: ✓ ALL CHECKS PASSED")
    print("=" * 70)
    print("\nThe data pipeline works end-to-end:")
    print("  1. DataLoader successfully loads and validates CSV data")
    print("  2. EDAModule successfully analyzes the data")
    print("  3. EDAResults contains all expected fields")
    print("  4. All fields are properly populated with meaningful data")
    print("\nThe system is ready for the next phase (Statistical Modeling).")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    success = test_data_pipeline_end_to_end()
    exit(0 if success else 1)
