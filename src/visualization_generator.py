"""
VisualizationGenerator for Marketing Mix Modeling analysis.

This module provides visualization functionality to create publication-quality
charts and plots for MMM analysis results, including time series, correlations,
ROI comparisons, response curves, and diagnostic plots.
"""

from typing import List, Optional
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

from src.eda_module import EDAResults
from src.statistical_modeler import ModelResults
from src.attribution_engine import AttributionResults


class VisualizationGenerator:
    """Visualization generator for Marketing Mix Modeling analysis.

    This class creates publication-quality visualizations of MMM analysis results,
    including time series plots, correlation heatmaps, ROI comparisons, response
    curves, and model diagnostic plots.

    All plots are saved as PNG files with 300 DPI for publication quality.
    Uses colorblind-friendly palettes for accessibility.

    Attributes:
        output_dir: Directory path for saving visualization files
        dpi: Resolution for saved plots (default 300)
        figsize_standard: Standard figure size for single plots
        figsize_large: Large figure size for multi-panel plots
    """

    def __init__(self, output_dir: str = "outputs/visualizations"):
        """Initialize VisualizationGenerator with output directory.

        Creates the output directory if it doesn't exist and sets up
        matplotlib/seaborn styling for consistent, publication-quality plots.

        Args:
            output_dir: Directory path for saving visualization files.
                Will be created if it doesn't exist.
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Plot settings
        self.dpi = 300
        self.figsize_standard = (12, 8)
        self.figsize_large = (16, 12)

        # Set up styling
        self._setup_style()

    def _setup_style(self):
        """Configure matplotlib and seaborn styling for publication quality."""
        # Use seaborn style
        sns.set_style("whitegrid")

        # Use colorblind-friendly palette
        sns.set_palette("colorblind")

        # Set font properties
        plt.rcParams["font.family"] = "sans-serif"
        plt.rcParams["font.sans-serif"] = ["Arial", "Helvetica", "DejaVu Sans"]
        plt.rcParams["font.size"] = 12
        plt.rcParams["axes.titlesize"] = 14
        plt.rcParams["axes.labelsize"] = 12
        plt.rcParams["xtick.labelsize"] = 10
        plt.rcParams["ytick.labelsize"] = 10
        plt.rcParams["legend.fontsize"] = 10

        # Grid styling
        plt.rcParams["grid.alpha"] = 0.3
        plt.rcParams["grid.color"] = "gray"

    def generate_all(
        self,
        df: pd.DataFrame,
        eda_results: EDAResults,
        model_results: ModelResults,
        attribution_results: AttributionResults,
    ) -> List[str]:
        """Generate all visualizations and return file paths.

        This is the main entry point for visualization generation. It creates
        all seven types of visualizations and returns a list of file paths.
        Each visualization is wrapped in error handling to ensure failures
        don't stop the entire process.

        Args:
            df: Original validated DataFrame with datetime index
            eda_results: Results from EDA analysis
            model_results: Results from statistical modeling
            attribution_results: Results from attribution analysis

        Returns:
            List of file paths to successfully generated visualizations
        """
        file_paths = []

        # 1. Time series plot
        try:
            path = self.plot_time_series(df)
            file_paths.append(path)
        except Exception as e:
            warnings.warn(f"Failed to generate time series plot: {str(e)}")

        # 2. Correlation heatmap
        try:
            path = self.plot_correlation_heatmap(eda_results.correlations)
            file_paths.append(path)
        except Exception as e:
            warnings.warn(f"Failed to generate correlation heatmap: {str(e)}")

        # 3. Spend comparison
        try:
            path = self.plot_spend_comparison(eda_results.total_spend_by_channel)
            file_paths.append(path)
        except Exception as e:
            warnings.warn(f"Failed to generate spend comparison chart: {str(e)}")

        # 4. ROI comparison
        try:
            path = self.plot_roi_comparison(attribution_results)
            file_paths.append(path)
        except Exception as e:
            warnings.warn(f"Failed to generate ROI comparison chart: {str(e)}")

        # 5. Channel scatter plots
        try:
            path = self.plot_channel_scatter(df)
            file_paths.append(path)
        except Exception as e:
            warnings.warn(f"Failed to generate channel scatter plots: {str(e)}")

        # 6. Response curves
        try:
            path = self.plot_response_curves(model_results, df)
            file_paths.append(path)
        except Exception as e:
            warnings.warn(f"Failed to generate response curves: {str(e)}")

        # 7. Residual diagnostics
        try:
            path = self.plot_residual_diagnostics(model_results)
            file_paths.append(path)
        except Exception as e:
            warnings.warn(f"Failed to generate residual diagnostic plots: {str(e)}")

        return file_paths

    def plot_time_series(self, df: pd.DataFrame) -> str:
        """Create time series plot of customer acquisition with control markers.

        Plots new customers over time with vertical lines indicating holidays
        (red) and competitor promotions (orange).

        Args:
            df: DataFrame with datetime index, new_customers, holidays, competitor_promo

        Returns:
            File path to saved plot
        """
        fig, ax = plt.subplots(figsize=self.figsize_standard, dpi=self.dpi)

        # Plot customer acquisition time series
        ax.plot(
            df.index,
            df["new_customers"],
            marker="o",
            linewidth=2,
            markersize=4,
            label="New Customers",
        )

        # Add vertical lines for holidays
        if "holidays" in df.columns:
            holiday_dates = df[df["holidays"] == 1].index
            for date in holiday_dates:
                ax.axvline(x=date, color="red", linestyle="--", alpha=0.5, linewidth=1)

        # Add vertical lines for competitor promos
        if "competitor_promo" in df.columns:
            promo_dates = df[df["competitor_promo"] == 1].index
            for date in promo_dates:
                ax.axvline(
                    x=date, color="orange", linestyle="--", alpha=0.5, linewidth=1
                )

        # Create custom legend
        from matplotlib.lines import Line2D

        legend_elements = [
            Line2D(
                [0], [0], color="C0", marker="o", linewidth=2, label="New Customers"
            ),
            Line2D(
                [0], [0], color="red", linestyle="--", linewidth=1, label="Holidays"
            ),
            Line2D(
                [0],
                [0],
                color="orange",
                linestyle="--",
                linewidth=1,
                label="Competitor Promo",
            ),
        ]
        ax.legend(handles=legend_elements, loc="best")

        ax.set_xlabel("Week Start Date")
        ax.set_ylabel("New Customers")
        ax.set_title("Customer Acquisition Over Time")
        ax.grid(True, alpha=0.3)

        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha="right")

        plt.tight_layout()

        # Save plot
        output_path = self.output_dir / "time_series.png"
        plt.savefig(output_path, dpi=self.dpi, bbox_inches="tight")
        plt.close()

        return str(output_path)

    def plot_correlation_heatmap(self, correlations: pd.DataFrame) -> str:
        """Create correlation heatmap showing channel-customer relationships.

        Displays a heatmap with correlation coefficients between all marketing
        channels and new customer acquisitions.

        Args:
            correlations: Correlation matrix DataFrame

        Returns:
            File path to saved plot
        """
        fig, ax = plt.subplots(figsize=self.figsize_standard, dpi=self.dpi)

        # Create heatmap with annotations
        sns.heatmap(
            correlations,
            annot=True,
            fmt=".3f",
            cmap="RdBu_r",
            center=0,
            vmin=-1,
            vmax=1,
            square=True,
            linewidths=0.5,
            cbar_kws={"label": "Correlation Coefficient"},
            ax=ax,
        )

        ax.set_title("Correlation Matrix: Marketing Channels and Customer Acquisition")

        plt.tight_layout()

        # Save plot
        output_path = self.output_dir / "correlation_heatmap.png"
        plt.savefig(output_path, dpi=self.dpi, bbox_inches="tight")
        plt.close()

        return str(output_path)

    def plot_spend_comparison(self, total_spend: pd.Series) -> str:
        """Create bar chart comparing total spend across channels.

        Displays a horizontal bar chart of total spend by marketing channel,
        sorted by spend amount.

        Args:
            total_spend: Series with channel names as index and total spend as values

        Returns:
            File path to saved plot
        """
        fig, ax = plt.subplots(figsize=self.figsize_standard, dpi=self.dpi)

        # Sort by spend
        spend_sorted = total_spend.sort_values(ascending=True)

        # Create horizontal bar chart
        bars = ax.barh(range(len(spend_sorted)), spend_sorted.values)

        # Color bars with colorblind-friendly palette
        colors = sns.color_palette("colorblind", len(spend_sorted))
        for bar, color in zip(bars, colors):
            bar.set_color(color)

        # Format channel names (remove '_spend' suffix)
        channel_names = [
            name.replace("_spend", "").replace("_", " ").title()
            for name in spend_sorted.index
        ]
        ax.set_yticks(range(len(spend_sorted)))
        ax.set_yticklabels(channel_names)

        ax.set_xlabel("Total Spend ($)")
        ax.set_title("Total Marketing Spend by Channel")
        ax.grid(True, alpha=0.3, axis="x")

        # Add value labels on bars
        for i, (idx, value) in enumerate(spend_sorted.items()):
            ax.text(value, i, f" ${value:,.0f}", va="center", fontsize=9)

        plt.tight_layout()

        # Save plot
        output_path = self.output_dir / "spend_comparison.png"
        plt.savefig(output_path, dpi=self.dpi, bbox_inches="tight")
        plt.close()

        return str(output_path)

    def plot_roi_comparison(self, attribution: AttributionResults) -> str:
        """Create bar chart showing ROI by channel with confidence intervals.

        Displays a horizontal bar chart of ROI by marketing channel with
        error bars representing 95% confidence intervals, sorted by ROI.

        Args:
            attribution: AttributionResults with ROI data

        Returns:
            File path to saved plot
        """
        fig, ax = plt.subplots(figsize=self.figsize_standard, dpi=self.dpi)

        # Extract ROI data
        channels = []
        roi_values = []
        ci_lower = []
        ci_upper = []

        for channel, (roi, (lower, upper)) in attribution.roi_by_channel.items():
            channels.append(channel)
            roi_values.append(roi * 100)  # Convert to percentage
            ci_lower.append(lower * 100)
            ci_upper.append(upper * 100)

        # Create DataFrame for sorting
        roi_df = pd.DataFrame(
            {
                "channel": channels,
                "roi": roi_values,
                "ci_lower": ci_lower,
                "ci_upper": ci_upper,
            }
        )
        roi_df = roi_df.sort_values("roi", ascending=True)

        # Calculate error bar sizes
        yerr_lower = roi_df["roi"].values - roi_df["ci_lower"].values
        yerr_upper = roi_df["ci_upper"].values - roi_df["roi"].values
        yerr = np.array([yerr_lower, yerr_upper])

        # Create horizontal bar chart
        bars = ax.barh(
            range(len(roi_df)),
            roi_df["roi"].values,
            xerr=yerr,
            capsize=5,
            error_kw={"linewidth": 1.5},
        )

        # Color bars based on positive/negative ROI
        colors = ["green" if roi > 0 else "red" for roi in roi_df["roi"].values]
        for bar, color in zip(bars, colors):
            bar.set_color(color)
            bar.set_alpha(0.7)

        # Format channel names
        channel_names = [
            name.replace("_spend", "").replace("_", " ").title()
            for name in roi_df["channel"]
        ]
        ax.set_yticks(range(len(roi_df)))
        ax.set_yticklabels(channel_names)

        ax.set_xlabel("ROI (%)")
        ax.set_title("Return on Investment by Marketing Channel")
        ax.axvline(x=0, color="black", linestyle="-", linewidth=0.8)
        ax.grid(True, alpha=0.3, axis="x")

        # Add value labels
        for i, (idx, row) in enumerate(roi_df.iterrows()):
            ax.text(row["roi"], i, f' {row["roi"]:.1f}%', va="center", fontsize=9)

        plt.tight_layout()

        # Save plot
        output_path = self.output_dir / "roi_comparison.png"
        plt.savefig(output_path, dpi=self.dpi, bbox_inches="tight")
        plt.close()

        return str(output_path)

    def plot_channel_scatter(self, df: pd.DataFrame) -> str:
        """Create scatter plots with trend lines for each channel.

        Displays a grid of scatter plots showing the relationship between
        each marketing channel's spend and new customer acquisitions, with
        linear regression trend lines.

        Args:
            df: DataFrame with spend channels and new_customers

        Returns:
            File path to saved plot
        """
        # Define spend channels
        spend_channels = [
            "tv_spend",
            "radio_spend",
            "facebook_spend",
            "instagram_spend",
            "google_search_spend",
            "google_play_spend",
            "youtube_spend",
            "display_spend",
        ]

        # Filter to available channels
        available_channels = [ch for ch in spend_channels if ch in df.columns]

        # Calculate grid dimensions
        n_channels = len(available_channels)
        n_cols = 3
        n_rows = (n_channels + n_cols - 1) // n_cols

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4 * n_rows), dpi=self.dpi)
        axes = axes.flatten() if n_channels > 1 else [axes]

        for idx, channel in enumerate(available_channels):
            ax = axes[idx]

            # Scatter plot
            ax.scatter(df[channel], df["new_customers"], alpha=0.6, s=50)

            # Add trend line
            x = df[channel].values
            y = df["new_customers"].values

            # Calculate linear regression
            if len(x) > 1 and np.std(x) > 0:
                z = np.polyfit(x, y, 1)
                p = np.poly1d(z)
                x_line = np.linspace(x.min(), x.max(), 100)
                ax.plot(x_line, p(x_line), "r--", linewidth=2, alpha=0.8, label="Trend")

                # Calculate R-squared
                y_pred = p(x)
                ss_res = np.sum((y - y_pred) ** 2)
                ss_tot = np.sum((y - np.mean(y)) ** 2)
                r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

                # Add R-squared to plot
                ax.text(
                    0.05,
                    0.95,
                    f"R² = {r_squared:.3f}",
                    transform=ax.transAxes,
                    va="top",
                    fontsize=9,
                    bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
                )

            # Format labels
            channel_name = channel.replace("_spend", "").replace("_", " ").title()
            ax.set_xlabel(f"{channel_name} Spend ($)")
            ax.set_ylabel("New Customers")
            ax.set_title(f"{channel_name}")
            ax.grid(True, alpha=0.3)

        # Hide unused subplots
        for idx in range(n_channels, len(axes)):
            axes[idx].set_visible(False)

        plt.suptitle(
            "Marketing Channel Spend vs Customer Acquisition", fontsize=16, y=1.00
        )
        plt.tight_layout()

        # Save plot
        output_path = self.output_dir / "channel_scatter_plots.png"
        plt.savefig(output_path, dpi=self.dpi, bbox_inches="tight")
        plt.close()

        return str(output_path)

    def plot_response_curves(
        self, model_results: ModelResults, df: pd.DataFrame
    ) -> str:
        """Create response curves showing saturation effects for each channel.

        Displays curves showing the predicted incremental customers as a function
        of spend level for each marketing channel, illustrating saturation effects.

        Args:
            model_results: ModelResults with transformation parameters
            df: Original DataFrame for spend ranges

        Returns:
            File path to saved plot
        """
        from src.statistical_modeler import StatisticalModeler

        fig, ax = plt.subplots(figsize=self.figsize_standard, dpi=self.dpi)

        # Define spend channels
        spend_channels = [
            "tv_spend",
            "radio_spend",
            "facebook_spend",
            "instagram_spend",
            "google_search_spend",
            "google_play_spend",
            "youtube_spend",
            "display_spend",
        ]

        # Filter to available channels
        available_channels = [ch for ch in spend_channels if ch in df.columns]

        # Get model type and transformation params
        model_type = model_results.model_type
        transformation_params = model_results.transformation_params
        coefficients = model_results.coefficients

        # Create modeler for transformations
        modeler = StatisticalModeler()

        # Plot response curve for each channel
        colors = sns.color_palette("colorblind", len(available_channels))

        for idx, channel in enumerate(available_channels):
            # Get spend range (0 to 2x max observed)
            max_spend = df[channel].max()
            spend_range = np.linspace(0, max_spend * 2, 100)

            # Get coefficient
            if model_type == "baseline":
                feature_name = channel
            elif model_type == "adstock":
                feature_name = f"{channel}_adstock"
            elif model_type == "saturation":
                feature_name = f"{channel}_sat"
            elif model_type == "full":
                feature_name = f"{channel}_full"
            else:
                feature_name = channel

            if feature_name not in coefficients.index:
                continue

            coef = coefficients.loc[feature_name, "coef"]

            # Apply transformations
            if model_type == "baseline":
                transformed_spend = spend_range
            elif model_type == "adstock":
                # For visualization, show cumulative effect
                decay = transformation_params[channel]["decay"]
                transformed_spend = spend_range * (1 / (1 - decay))
            elif model_type == "saturation":
                alpha = transformation_params[channel]["alpha"]
                gamma = transformation_params[channel]["gamma"]
                transformed_spend = modeler.apply_saturation_transformation(
                    spend_range, alpha=alpha, gamma=gamma
                )
            elif model_type == "full":
                # Apply both transformations
                decay = transformation_params[channel]["decay"]
                alpha = transformation_params[channel]["alpha"]
                gamma = transformation_params[channel]["gamma"]

                # For visualization, approximate adstock effect
                adstock_factor = 1 / (1 - decay)
                adstock_spend = spend_range * adstock_factor

                transformed_spend = modeler.apply_saturation_transformation(
                    adstock_spend, alpha=alpha, gamma=gamma
                )
            else:
                transformed_spend = spend_range

            # Calculate incremental customers
            incremental_customers = coef * transformed_spend

            # Plot curve
            channel_name = channel.replace("_spend", "").replace("_", " ").title()
            ax.plot(
                spend_range,
                incremental_customers,
                linewidth=2,
                label=channel_name,
                color=colors[idx],
            )

        ax.set_xlabel("Spend Level ($)")
        ax.set_ylabel("Incremental Customers")
        ax.set_title("Marketing Response Curves (Saturation Effects)")
        ax.legend(loc="best", ncol=2)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        # Save plot
        output_path = self.output_dir / "response_curves.png"
        plt.savefig(output_path, dpi=self.dpi, bbox_inches="tight")
        plt.close()

        return str(output_path)

    def plot_residual_diagnostics(self, model_results: ModelResults) -> str:
        """Create residual diagnostic plots for model validation.

        Displays a 2x2 grid of diagnostic plots:
        1. Residuals vs Fitted values
        2. Q-Q plot for normality
        3. Scale-Location plot (sqrt standardized residuals)
        4. Residuals vs Leverage

        Args:
            model_results: ModelResults with model and predictions

        Returns:
            File path to saved plot
        """
        fig, axes = plt.subplots(2, 2, figsize=self.figsize_large, dpi=self.dpi)

        # Get residuals and fitted values
        model = model_results.model
        residuals = model.resid
        fitted_values = model.fittedvalues

        # Standardized residuals
        residuals_std = (residuals - residuals.mean()) / residuals.std()

        # 1. Residuals vs Fitted
        ax = axes[0, 0]
        ax.scatter(fitted_values, residuals, alpha=0.6, s=50)
        ax.axhline(y=0, color="r", linestyle="--", linewidth=2)
        ax.set_xlabel("Fitted Values")
        ax.set_ylabel("Residuals")
        ax.set_title("Residuals vs Fitted")
        ax.grid(True, alpha=0.3)

        # Add lowess smooth line
        try:
            from statsmodels.nonparametric.smoothers_lowess import lowess

            smoothed = lowess(residuals, fitted_values, frac=0.3)
            ax.plot(smoothed[:, 0], smoothed[:, 1], "b-", linewidth=2, label="Lowess")
        except Exception:
            pass

        # 2. Q-Q Plot
        ax = axes[0, 1]
        from scipy import stats

        stats.probplot(residuals, dist="norm", plot=ax)
        ax.set_title("Normal Q-Q Plot")
        ax.grid(True, alpha=0.3)

        # 3. Scale-Location Plot
        ax = axes[1, 0]
        sqrt_abs_resid_std = np.sqrt(np.abs(residuals_std))
        ax.scatter(fitted_values, sqrt_abs_resid_std, alpha=0.6, s=50)
        ax.set_xlabel("Fitted Values")
        ax.set_ylabel("√|Standardized Residuals|")
        ax.set_title("Scale-Location Plot")
        ax.grid(True, alpha=0.3)

        # Add lowess smooth line
        try:
            from statsmodels.nonparametric.smoothers_lowess import lowess

            smoothed = lowess(sqrt_abs_resid_std, fitted_values, frac=0.3)
            ax.plot(smoothed[:, 0], smoothed[:, 1], "r-", linewidth=2)
        except Exception:
            pass

        # 4. Residuals vs Leverage
        ax = axes[1, 1]
        try:
            # Calculate leverage
            from statsmodels.stats.outliers_influence import OLSInfluence

            influence = OLSInfluence(model)
            leverage = influence.hat_matrix_diag

            ax.scatter(leverage, residuals_std, alpha=0.6, s=50)
            ax.axhline(y=0, color="r", linestyle="--", linewidth=2)
            ax.set_xlabel("Leverage")
            ax.set_ylabel("Standardized Residuals")
            ax.set_title("Residuals vs Leverage")
            ax.grid(True, alpha=0.3)

            # Add Cook's distance contours
            n = len(residuals)
            p = model.df_model + 1
            x = np.linspace(0.001, max(leverage), 50)

            for cooks_d in [0.5, 1.0]:
                y_pos = np.sqrt(cooks_d * p * (1 - x) / x)
                y_neg = -y_pos
                ax.plot(x, y_pos, "r--", linewidth=1, alpha=0.5)
                ax.plot(x, y_neg, "r--", linewidth=1, alpha=0.5)

        except Exception as e:
            # If leverage calculation fails, show residuals vs index
            ax.scatter(range(len(residuals_std)), residuals_std, alpha=0.6, s=50)
            ax.axhline(y=0, color="r", linestyle="--", linewidth=2)
            ax.set_xlabel("Observation Index")
            ax.set_ylabel("Standardized Residuals")
            ax.set_title("Residuals vs Index")
            ax.grid(True, alpha=0.3)

        plt.suptitle("Residual Diagnostic Plots", fontsize=16, y=1.00)
        plt.tight_layout()

        # Save plot
        output_path = self.output_dir / "residual_diagnostics.png"
        plt.savefig(output_path, dpi=self.dpi, bbox_inches="tight")
        plt.close()

        return str(output_path)
