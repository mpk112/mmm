"""
Integration test for ReportGenerator component.

This test verifies that the ReportGenerator can successfully create a
comprehensive markdown report from MMM analysis results.
"""

import pandas as pd
import numpy as np
from pathlib import Path

from src.data_loader import DataLoader
from src.eda_module import EDAModule
from src.statistical_modeler import StatisticalModeler
from src.attribution_engine import AttributionEngine
from src.visualization_generator import VisualizationGenerator
from src.report_generator import ReportGenerator


def test_report_generator_integration():
    """Test ReportGenerator with real MMM pipeline results."""
    print("Testing ReportGenerator integration...")
    
    # Load data
    print("\n1. Loading data...")
    loader = DataLoader()
    df = loader.load_data("MMM dataset - Sheet1.csv")
    print(f"   ✓ Loaded {len(df)} weeks of data")
    
    # Run EDA
    print("\n2. Running EDA...")
    eda_module = EDAModule()
    eda_results = eda_module.analyze(df)
    print(f"   ✓ EDA complete")
    
    # Fit model
    print("\n3. Fitting statistical model...")
    modeler = StatisticalModeler(random_state=42)
    model_results = modeler.fit(df, test_size=0.2)
    print(f"   ✓ Model fitted: {model_results.model_type}")
    print(f"   ✓ Test R²: {model_results.diagnostics.r_squared_test:.4f}")
    
    # Calculate attribution
    print("\n4. Calculating attribution...")
    attribution_engine = AttributionEngine(model_results, customer_value=100.0)
    attribution_results = attribution_engine.calculate_attribution(df)
    print(f"   ✓ Attribution calculated for {len(attribution_results.marginal_contributions)} channels")
    
    # Optimize budget
    print("\n5. Optimizing budget...")
    total_budget = sum(df[ch].sum() for ch in attribution_engine.spend_channels if ch in df.columns)
    optimization_results = attribution_engine.optimize_budget(df, total_budget)
    print(f"   ✓ Optimization complete: {optimization_results.expected_lift:.1f}% expected lift")
    
    # Generate visualizations
    print("\n6. Generating visualizations...")
    viz_generator = VisualizationGenerator(output_dir="outputs/visualizations")
    visualization_paths = viz_generator.generate_all(
        df, eda_results, model_results, attribution_results
    )
    print(f"   ✓ Generated {len(visualization_paths)} visualizations")
    
    # Generate report
    print("\n7. Generating report...")
    report_generator = ReportGenerator(output_path="outputs/mmm_analysis_report.md")
    report_path = report_generator.generate_report(
        eda_results=eda_results,
        model_results=model_results,
        attribution_results=attribution_results,
        optimization_results=optimization_results,
        visualization_paths=visualization_paths
    )
    print(f"   ✓ Report generated: {report_path}")
    
    # Verify report exists and has content
    report_file = Path(report_path)
    assert report_file.exists(), "Report file was not created"
    
    report_content = report_file.read_text(encoding='utf-8')
    assert len(report_content) > 1000, "Report content is too short"
    
    # Check for key sections
    required_sections = [
        "# Marketing Mix Modeling Analysis Report",
        "## Executive Summary",
        "## 1. Introduction",
        "## 2. Methodology",
        "## 3. Exploratory Data Analysis",
        "## 4. Model Development and Validation",
        "## 5. Attribution and ROI Analysis",
        "## 6. Budget Optimization",
        "## 7. Insights and Recommendations",
        "## 8. Limitations and Assumptions",
        "## Appendix"
    ]
    
    for section in required_sections:
        assert section in report_content, f"Missing section: {section}"
    
    print(f"\n✓ All sections present in report")
    print(f"✓ Report size: {len(report_content):,} characters")
    
    # Print sample of report
    print("\n" + "="*80)
    print("REPORT PREVIEW (first 1000 characters):")
    print("="*80)
    print(report_content[:1000])
    print("="*80)
    
    print("\n✅ ReportGenerator integration test PASSED")
    print(f"\nFull report available at: {report_path}")
    
    return True


if __name__ == "__main__":
    try:
        test_report_generator_integration()
    except Exception as e:
        print(f"\n❌ Test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
