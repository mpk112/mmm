"""Manual test script for StatisticalModeler transformations."""

import numpy as np
from src.statistical_modeler import StatisticalModeler


def test_adstock_basic():
    """Test basic adstock transformation."""
    print("Testing adstock transformation...")
    modeler = StatisticalModeler()
    
    # Test case 1: Simple decay
    spend = np.array([100.0, 0.0, 0.0, 0.0])
    adstock = modeler.apply_adstock_transformation(spend, decay_rate=0.5)
    print(f"  Input: {spend}")
    print(f"  Output (decay=0.5): {adstock}")
    print(f"  Expected: [100.0, 50.0, 25.0, 12.5]")
    
    # Test case 2: Zero decay (should return original)
    spend = np.array([100.0, 50.0, 75.0])
    try:
        adstock = modeler.apply_adstock_transformation(spend, decay_rate=0.0)
        print(f"  ERROR: Should have raised ValueError for decay_rate=0")
    except ValueError as e:
        print(f"  ✓ Correctly rejected decay_rate=0: {e}")
    
    # Test case 3: Negative spend (should raise error)
    spend = np.array([100.0, -50.0, 75.0])
    try:
        adstock = modeler.apply_adstock_transformation(spend, decay_rate=0.5)
        print(f"  ERROR: Should have raised ValueError for negative spend")
    except ValueError as e:
        print(f"  ✓ Correctly rejected negative spend: {e}")
    
    print()


def test_saturation_basic():
    """Test basic saturation transformation."""
    print("Testing saturation transformation...")
    modeler = StatisticalModeler()
    
    # Test case 1: Basic saturation
    spend = np.array([0.0, 50.0, 100.0, 200.0])
    saturated = modeler.apply_saturation_transformation(spend, alpha=100.0, gamma=1.0)
    print(f"  Input: {spend}")
    print(f"  Output (alpha=100, gamma=1): {saturated}")
    print(f"  Expected: [0.0, ~0.333, 0.5, ~0.667]")
    
    # Test case 2: Check bounds [0, 1]
    spend = np.array([0.0, 1000.0, 10000.0])
    saturated = modeler.apply_saturation_transformation(spend, alpha=100.0, gamma=1.0)
    print(f"  High spend saturation: {saturated}")
    print(f"  All values in [0, 1]: {np.all((saturated >= 0) & (saturated <= 1))}")
    
    # Test case 3: Negative alpha (should raise error)
    spend = np.array([100.0, 50.0, 75.0])
    try:
        saturated = modeler.apply_saturation_transformation(spend, alpha=-100.0, gamma=1.0)
        print(f"  ERROR: Should have raised ValueError for negative alpha")
    except ValueError as e:
        print(f"  ✓ Correctly rejected negative alpha: {e}")
    
    # Test case 4: Monotonicity check
    spend = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
    saturated = modeler.apply_saturation_transformation(spend, alpha=30.0, gamma=1.5)
    is_monotonic = np.all(np.diff(saturated) >= 0)
    print(f"  Monotonicity test: {is_monotonic} (should be True)")
    
    print()


def test_combined_transformations():
    """Test combining adstock and saturation."""
    print("Testing combined transformations...")
    modeler = StatisticalModeler()
    
    spend = np.array([100.0, 50.0, 75.0, 0.0, 100.0])
    
    # Apply adstock first
    adstock = modeler.apply_adstock_transformation(spend, decay_rate=0.5)
    print(f"  Original spend: {spend}")
    print(f"  After adstock: {adstock}")
    
    # Then apply saturation
    saturated = modeler.apply_saturation_transformation(adstock, alpha=100.0, gamma=1.0)
    print(f"  After saturation: {saturated}")
    print(f"  All values in [0, 1]: {np.all((saturated >= 0) & (saturated <= 1))}")
    
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("StatisticalModeler Transformation Tests")
    print("=" * 60)
    print()
    
    test_adstock_basic()
    test_saturation_basic()
    test_combined_transformations()
    
    print("=" * 60)
    print("All manual tests completed!")
    print("=" * 60)
