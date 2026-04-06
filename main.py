#!/usr/bin/env python3
"""
Main pipeline orchestration for Marketing Mix Modeling analysis.

This script runs the complete MMM analysis pipeline from data loading through
report generation, coordinating all components in the correct sequence.

Usage:
    python main.py --data "MMM dataset - Sheet1.csv" --output-dir outputs --customer-value 100.0
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from src.data_loader import DataLoader
from src.eda_module import EDAModule
from src.statistical_modeler import StatisticalModeler
from src.attribution_engine import AttributionEngine
from src.visualization_generator import VisualizationGenerator
from src.report_generator import ReportGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("mmm_pipeline.log"),
    ],
)
logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Marketing Mix Modeling Analysis Pipeline",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--data",
        type=str,
        default="MMM dataset - Sheet1.csv",
        help="Path to CSV file containing MMM data",
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="outputs",
        help="Directory for saving outputs (visualizations and report)",
    )

    parser.add_argument(
        "--customer-value",
        type=float,
        default=100.0,
        help="Customer lifetime value in dollars for ROI calculation",
    )

    return parser.parse_args()


def run_pipeline(data_path: str, output_dir: str, customer_value: float) -> int:
    """Run the complete MMM analysis pipeline.

    Args:
        data_path: Path to CSV data file
        output_dir: Directory for saving outputs
        customer_value: Customer lifetime value for ROI calculation

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {output_path.absolute()}")

        # ========================================
        # Stage 1: Data Loading and Validation
        # ========================================
        logger.info("=" * 60)
        logger.info("STAGE 1: Data Loading and Validation")
        logger.info("=" * 60)

        data_loader = DataLoader()
        logger.info(f"Loading data from: {data_path}")

        try:
            df = data_loader.load_data(data_path)
            logger.info(f"✓ Data loaded successfully: {len(df)} weeks of data")
            logger.info(f"  Date range: {df.index.min()} to {df.index.max()}")
        except FileNotFoundError as e:
            logger.error(f"✗ Data file not found: {e}")
            return 1
        except ValueError as e:
            logger.error(f"✗ Data validation failed: {e}")
            return 1

        # ========================================
        # Stage 2: Exploratory Data Analysis
        # ========================================
        logger.info("\n" + "=" * 60)
        logger.info("STAGE 2: Exploratory Data Analysis")
        logger.info("=" * 60)

        eda_module = EDAModule()
        logger.info("Performing exploratory data analysis...")

        try:
            eda_results = eda_module.analyze(df)
            logger.info("✓ EDA completed successfully")
            logger.info(f"  Time period: {eda_results.time_period['n_weeks']} weeks")
            logger.info(
                f"  Channels analyzed: {len(eda_results.total_spend_by_channel)}"
            )
            logger.info(
                f"  Outliers detected: {sum(len(v) for v in eda_results.outliers.values())} data points"
            )
        except Exception as e:
            logger.error(f"✗ EDA failed: {e}")
            return 1

        # ========================================
        # Stage 3: Statistical Modeling
        # ========================================
        logger.info("\n" + "=" * 60)
        logger.info("STAGE 3: Statistical Modeling")
        logger.info("=" * 60)

        modeler = StatisticalModeler(random_state=42)
        logger.info("Fitting statistical models with transformations...")
        logger.info("  - Baseline model")
        logger.info("  - Adstock model (carryover effects)")
        logger.info("  - Saturation model (diminishing returns)")
        logger.info("  - Full model (adstock + saturation)")

        try:
            model_results = modeler.fit(df, test_size=0.2)
            logger.info(
                f"✓ Model fitting completed: {model_results.model_type} model selected"
            )
            logger.info(f"  Train R²: {model_results.diagnostics.r_squared_train:.4f}")
            logger.info(f"  Test R²: {model_results.diagnostics.r_squared_test:.4f}")
            logger.info(
                f"  Test RMSE: {model_results.diagnostics.rmse_test:.2f} customers"
            )
            logger.info(f"  AIC: {model_results.diagnostics.aic:.2f}")
        except Exception as e:
            logger.error(f"✗ Model fitting failed: {e}")
            return 1

        # ========================================
        # Stage 4: Attribution Analysis
        # ========================================
        logger.info("\n" + "=" * 60)
        logger.info("STAGE 4: Attribution Analysis and ROI Calculation")
        logger.info("=" * 60)

        attribution_engine = AttributionEngine(
            model_results=model_results, customer_value=customer_value
        )
        logger.info(
            f"Calculating channel attribution (customer value: ${customer_value:.2f})..."
        )

        try:
            attribution_results = attribution_engine.calculate_attribution(df)
            logger.info("✓ Attribution analysis completed")

            # Log top 3 channels by ROI
            top_3 = attribution_results.channel_rankings[:3]
            logger.info("  Top 3 channels by ROI:")
            for channel, roi in top_3:
                channel_name = channel.replace("_spend", "").replace("_", " ").title()
                logger.info(f"    - {channel_name}: {roi*100:.1f}% ROI")
        except Exception as e:
            logger.error(f"✗ Attribution analysis failed: {e}")
            return 1

        # ========================================
        # Stage 5: Budget Optimization
        # ========================================
        logger.info("\n" + "=" * 60)
        logger.info("STAGE 5: Budget Optimization")
        logger.info("=" * 60)

        # Calculate total current budget
        total_budget = sum(
            df[ch].sum() for ch in attribution_engine.spend_channels if ch in df.columns
        )
        logger.info(
            f"Optimizing budget allocation (total budget: ${total_budget:,.0f})..."
        )

        try:
            optimization_results = attribution_engine.optimize_budget(
                df=df,
                total_budget=total_budget,
                constraints=None,  # Use default constraints (0.5x to 2x current spend)
            )
            logger.info("✓ Budget optimization completed")
            logger.info(
                f"  Current customers: {optimization_results.current_customers:.0f}"
            )
            logger.info(
                f"  Expected customers: {optimization_results.expected_customers:.0f}"
            )
            logger.info(f"  Expected lift: {optimization_results.expected_lift:.1f}%")
            logger.info(f"  Convergence: {optimization_results.convergence_status}")
        except Exception as e:
            logger.error(f"✗ Budget optimization failed: {e}")
            return 1

        # ========================================
        # Stage 6: Visualization Generation
        # ========================================
        logger.info("\n" + "=" * 60)
        logger.info("STAGE 6: Visualization Generation")
        logger.info("=" * 60)

        viz_generator = VisualizationGenerator(
            output_dir=str(output_path / "visualizations")
        )
        logger.info("Generating visualizations...")

        try:
            visualization_paths = viz_generator.generate_all(
                df=df,
                eda_results=eda_results,
                model_results=model_results,
                attribution_results=attribution_results,
            )
            logger.info(
                f"✓ Visualizations generated: {len(visualization_paths)} charts created"
            )
            for path in visualization_paths:
                logger.info(f"  - {Path(path).name}")
        except Exception as e:
            logger.error(f"✗ Visualization generation failed: {e}")
            logger.warning("Continuing with report generation...")
            visualization_paths = []

        # ========================================
        # Stage 7: Report Generation
        # ========================================
        logger.info("\n" + "=" * 60)
        logger.info("STAGE 7: Report Generation")
        logger.info("=" * 60)

        report_generator = ReportGenerator(
            output_path=str(output_path / "mmm_analysis_report.md")
        )
        logger.info("Generating comprehensive analysis report...")

        try:
            report_path = report_generator.generate_report(
                eda_results=eda_results,
                model_results=model_results,
                attribution_results=attribution_results,
                optimization_results=optimization_results,
                visualization_paths=visualization_paths,
            )
            logger.info(f"✓ Report generated: {report_path}")
        except Exception as e:
            logger.error(f"✗ Report generation failed: {e}")
            return 1

        # ========================================
        # Pipeline Summary
        # ========================================
        logger.info("\n" + "=" * 60)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info("\nOutput Summary:")
        logger.info(f"  Report: {report_path}")
        logger.info(
            f"  Visualizations: {len(visualization_paths)} charts in {output_path / 'visualizations'}"
        )
        logger.info(f"  Log file: mmm_pipeline.log")

        logger.info("\nKey Findings:")
        logger.info(
            f"  Model: {model_results.model_type} (R² = {model_results.diagnostics.r_squared_test:.4f})"
        )
        logger.info(
            f"  Best channel: {attribution_results.channel_rankings[0][0].replace('_spend', '').title()} "
            f"({attribution_results.channel_rankings[0][1]*100:.1f}% ROI)"
        )
        logger.info(f"  Optimization lift: {optimization_results.expected_lift:.1f}%")

        return 0

    except Exception as e:
        logger.error(f"✗ Pipeline failed with unexpected error: {e}", exc_info=True)
        return 1


def main() -> int:
    """Main entry point for the pipeline.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Parse arguments
    args = parse_arguments()

    # Log pipeline start
    logger.info("=" * 60)
    logger.info("Marketing Mix Modeling Analysis Pipeline")
    logger.info("=" * 60)
    logger.info(f"Data file: {args.data}")
    logger.info(f"Output directory: {args.output_dir}")
    logger.info(f"Customer value: ${args.customer_value:.2f}")
    logger.info("")

    # Run pipeline
    exit_code = run_pipeline(
        data_path=args.data,
        output_dir=args.output_dir,
        customer_value=args.customer_value,
    )

    # Log completion
    if exit_code == 0:
        logger.info("\n✓ Pipeline completed successfully!")
    else:
        logger.error("\n✗ Pipeline failed. Check logs for details.")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
