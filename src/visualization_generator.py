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
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
        plt.rcParams['font.size'] = 12
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['xtick.labelsize'] = 10
        plt.rcParams['ytick.labelsize'] = 10
        plt.rcParams['legend.fontsize'] = 10
        
        # Grid styling
        plt.rcParams['grid.alpha'] = 0.3
        plt.rcParams['grid.color'] = 'gray'
    
    def generate_all(
        self,
        df: pd.DataFrame,
        eda_results: EDAResults,
        model_results: ModelResults,
        attribution_results: AttributionResults
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
