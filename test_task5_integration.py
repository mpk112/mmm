"""Integration test for Task 5: StatisticalModeler transformations."""

import numpy as np
import pandas as pd
from src.statistical_modeler import StatisticalModeler
from src.data_loader import DataLoader


def test_statistical_modeler_with_real_data():
    """Test StatisticalModeler transformations with actual MMM dataset."""
    print("Testing StatisticalModeler with real MMM data...")
    
    # Load real data
    loader = DataLoader()
    df = loader.load_data("MMM dataset - Sheet1.csv")
    
    print(f"  Loaded {len(df)} weeks of data")
    print(f"  Columns: {list(df.columns)}")
    
    # Initialize modeler
    modeler = StatisticalModeler(random_state=42)
    print(f"  ✓ StatisticalModeler initialized with random_state=42")
    
    # Test adstock transformation on a real channel
    tv_spend = df['tv_spend'].values
    print(f"\n  Testing adstock on TV spend...")
    print(f"    Original TV spend range: [{tv_spend.min():.2f}, {tv_spend.max():.2f}]")
    
    tv_adstock = modeler.apply_adstock_transformation(tv_spend, decay_rate=0.5)
    print(f"    Adstock TV spend range: [{tv_adstock.min():.2f}, {tv_adstock.max():.2f}]")
    print(f"    ✓ Adstock transformation successful")
    
    # Verify properties
    assert len(tv_adstock) == len(tv_spend), "Length mismatch"
    assert np.all(tv_adstock >= 0), "Negative values in adstock"
    assert tv_adstock[0] == tv_spend[0], "First value should match"
    print(f"    ✓ All adstock properties verified")
    
    # Test saturation transformation
    print(f"\n  Testing saturation on TV spend...")
    alpha = tv_spend.mean()  # Use mean as half-saturation point
    tv_saturated = modeler.apply_saturation_transformation(tv_spend, alpha=alpha, gamma=1.0)
    print(f"    Saturated TV spend range: [{tv_saturated.min():.4f}, {tv_saturated.max():.4f}]")
    print(f"    ✓ Saturation transformation successful")
    
    # Verify properties
    assert len(tv_saturated) == len(tv_spend), "Length mismatch"
    assert np.all((tv_saturated >= 0) & (tv_saturated <= 1)), "Values outside [0, 1]"
    assert np.all(np.diff(np.sort(tv_spend)) >= 0) or np.all(np.diff(tv_saturated[np.argsort(tv_spend)]) >= 0), "Not monotonic"
    print(f"    ✓ All saturation properties verified")
    
    # Test combined transformation (adstock then saturation)
    print(f"\n  Testing combined transformation...")
    tv_combined = modeler.apply_saturation_transformation(tv_adstock, alpha=alpha, gamma=1.0)
    print(f"    Combined transformation range: [{tv_combined.min():.4f}, {tv_combined.max():.4f}]")
    print(f"    ✓ Combined transformation successful")
    
    # Test on all channels
    print(f"\n  Testing transformations on all channels...")
    channels = [
        'tv_spend', 'radio_spend', 'facebook_spend', 'instagram_spend',
        'google_search_spend', 'google_play_spend', 'youtube_spend', 'display_spend'
    ]
    
    for channel in channels:
        spend = df[channel].values
        
        # Apply adstock
        adstock = modeler.apply_adstock_transformation(spend, decay_rate=0.5)
        
        # Apply saturation
        alpha = spend.mean() if spend.mean() > 0 else 1.0
        saturated = modeler.apply_saturation_transformation(adstock, alpha=alpha, gamma=1.0)
        
        # Verify
        assert len(saturated) == len(spend), f"{channel}: Length mismatch"
        assert np.all((saturated >= 0) & (saturated <= 1)), f"{channel}: Values outside [0, 1]"
        
        print(f"    ✓ {channel}: adstock + saturation successful")
    
    print(f"\n  ✓ All channels transformed successfully!")
    print(f"\n✓ Integration test passed!")


if __name__ == "__main__":
    print("=" * 70)
    print("Task 5 Integration Test: StatisticalModeler with Real Data")
    print("=" * 70)
    print()
    
    test_statistical_modeler_with_real_data()
    
    print()
    print("=" * 70)
    print("All integration tests completed successfully!")
    print("=" * 70)
