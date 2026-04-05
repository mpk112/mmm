"""
EDAModule for Marketing Mix Modeling analysis.

This module provides exploratory data analysis functionality including descriptive
statistics, correlation analysis, outlier detection, seasonality analysis, and
control variable impact assessment.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Tuple
import pandas as pd
import numpy as np
from scipy import stats


@dataclass
class SeasonalityResults:
    """Results from seasonality analysis.
    
    Attributes:
        trend: Trend component of time series
        seasonal: Seasonal component of time series
        residual: Residual component of time series
        period: Detected seasonality period in weeks
    """
    trend: np.ndarray
    seasonal: np.ndarray
    residual: np.ndarray
    period: int


@dataclass
class ControlAnalysis:
    """Results from control variable impact analysis.
    
    Attributes:
        holiday_effect: Tuple of (mean_difference, p_value) for holiday impact
        promo_effect: Tuple of (mean_difference, p_value) for competitor promo impact
    """
    holiday_effect: Tuple[float, float]
    promo_effect: Tuple[float, float]


@dataclass
class EDAResults:
    """Comprehensive results from exploratory data analysis.
    
    Attributes:
        descriptive_stats: Dictionary mapping column names to descriptive statistics
        correlations: Correlation matrix between channels and customers
        time_period: Dictionary with start, end, and n_weeks
        total_spend_by_channel: Total spend per marketing channel
        outliers: Dictionary mapping channel names to lists of outlier indices
        seasonality: Seasonality analysis results
        control_impact: Control variable impact analysis results
    """
    descriptive_stats: Dict[str, pd.Series]
    correlations: pd.DataFrame
    time_period: Dict[str, Any]
    total_spend_by_channel: pd.Series
    outliers: Dict[str, List[int]]
    seasonality: SeasonalityResults
    control_impact: ControlAnalysis


class EDAModule:
    """Exploratory Data Analysis module for Marketing Mix Modeling.
    
    This class performs comprehensive exploratory analysis on marketing data,
    including descriptive statistics, correlation analysis, outlier detection,
    seasonality patterns, and control variable impact assessment.
    
    Attributes:
        SPEND_CHANNELS: List of marketing channel spend column names
        CONTROL_VARIABLES: List of control variable column names
    """
    
    SPEND_CHANNELS = [
        'tv_spend',
        'radio_spend',
        'facebook_spend',
        'instagram_spend',
        'google_search_spend',
        'google_play_spend',
        'youtube_spend',
        'display_spend'
    ]
    
    CONTROL_VARIABLES = ['holidays', 'competitor_promo']
    
    def analyze(self, df: pd.DataFrame) -> EDAResults:
        """Perform comprehensive exploratory data analysis.
        
        This method orchestrates all EDA analyses and returns a structured
        summary of findings including statistics, correlations, outliers,
        seasonality patterns, and control variable impacts.
        
        Args:
            df: Validated DataFrame from DataLoader with datetime index
            
        Returns:
            EDAResults containing all analysis findings
        """
        # Compute descriptive statistics
        descriptive_stats = self.compute_descriptive_stats(df)
        
        # Compute correlations
        correlations = self.compute_correlations(df)
        
        # Identify time period
        time_period = self._identify_time_period(df)
        
        # Calculate total spend by channel
        total_spend_by_channel = self._calculate_total_spend(df)
        
        # Detect outliers
        outliers = self.detect_outliers(df)
        
        # Analyze seasonality
        seasonality = self.analyze_seasonality(df)
        
        # Analyze control variables
        control_impact = self.analyze_control_variables(df)
        
        return EDAResults(
            descriptive_stats=descriptive_stats,
            correlations=correlations,
            time_period=time_period,
            total_spend_by_channel=total_spend_by_channel,
            outliers=outliers,
            seasonality=seasonality,
            control_impact=control_impact
        )
    
    def compute_descriptive_stats(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculate descriptive statistics for all numeric columns.
        
        Computes mean, median, standard deviation, min, max, and quartiles
        (25th, 50th, 75th percentiles) for each numeric column.
        
        Args:
            df: DataFrame with numeric columns
            
        Returns:
            Dictionary mapping column names to Series of descriptive statistics
        """
        stats_dict = {}
        
        # Get all numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            stats_dict[col] = pd.Series({
                'mean': df[col].mean(),
                'median': df[col].median(),
                'std': df[col].std(),
                'min': df[col].min(),
                'max': df[col].max(),
                'q25': df[col].quantile(0.25),
                'q50': df[col].quantile(0.50),
                'q75': df[col].quantile(0.75)
            })
        
        return stats_dict
    
    def compute_correlations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate correlation matrix between channels and customers.
        
        Computes Pearson correlation coefficients between each marketing
        channel spend and new customer acquisitions, as well as inter-channel
        correlations.
        
        Args:
            df: DataFrame with spend channels and new_customers columns
            
        Returns:
            Correlation matrix as DataFrame
        """
        # Select spend channels and new_customers
        cols_to_correlate = self.SPEND_CHANNELS + ['new_customers']
        
        # Filter to only columns that exist in the dataframe
        available_cols = [col for col in cols_to_correlate if col in df.columns]
        
        # Compute correlation matrix
        correlation_matrix = df[available_cols].corr()
        
        return correlation_matrix

    
    def _identify_time_period(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify the time period covered by the dataset.
        
        Args:
            df: DataFrame with datetime index
            
        Returns:
            Dictionary with start_date, end_date, and n_weeks
        """
        return {
            'start_date': df.index.min(),
            'end_date': df.index.max(),
            'n_weeks': len(df)
        }
    
    def _calculate_total_spend(self, df: pd.DataFrame) -> pd.Series:
        """Calculate total spend per marketing channel.
        
        Args:
            df: DataFrame with spend channel columns
            
        Returns:
            Series with total spend per channel
        """
        total_spend = {}
        
        for channel in self.SPEND_CHANNELS:
            if channel in df.columns:
                total_spend[channel] = df[channel].sum()
        
        return pd.Series(total_spend)
    
    def detect_outliers(self, df: pd.DataFrame) -> Dict[str, List[int]]:
        """Identify outliers in spend data using IQR method.
        
        Uses the Interquartile Range (IQR) method to detect outliers.
        Values outside [Q1 - 1.5*IQR, Q3 + 1.5*IQR] are considered outliers.
        
        Args:
            df: DataFrame with spend channel columns
            
        Returns:
            Dictionary mapping channel names to lists of outlier row indices
        """
        outliers = {}
        
        for channel in self.SPEND_CHANNELS:
            if channel not in df.columns:
                continue
            
            # Calculate Q1, Q3, and IQR
            q1 = df[channel].quantile(0.25)
            q3 = df[channel].quantile(0.75)
            iqr = q3 - q1
            
            # Define outlier bounds
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            # Find outliers
            outlier_mask = (df[channel] < lower_bound) | (df[channel] > upper_bound)
            outlier_indices = df[outlier_mask].index.tolist()
            
            if outlier_indices:
                outliers[channel] = outlier_indices
        
        return outliers
    
    def analyze_seasonality(self, df: pd.DataFrame) -> SeasonalityResults:
        """Detect seasonal patterns in customer acquisition data.
        
        Performs simple seasonal decomposition to identify trend, seasonal,
        and residual components in the new_customers time series.
        
        Args:
            df: DataFrame with new_customers column and datetime index
            
        Returns:
            SeasonalityResults with decomposed components
        """
        # Get customer acquisition data
        customers = df['new_customers'].values
        n = len(customers)
        
        # Simple moving average for trend (4-week window)
        window = min(4, n // 2)
        if window < 2:
            window = 2
        
        # Calculate trend using centered moving average
        trend = pd.Series(customers).rolling(window=window, center=True).mean().values
        
        # Fill NaN values at edges with nearest valid values
        trend = pd.Series(trend).bfill().ffill().values
        
        # Detrend the data
        detrended = customers - trend
        
        # Estimate seasonality period (try common periods: 4, 13, 26, 52 weeks)
        # For simplicity, use 4 weeks (monthly) as default period
        period = 4
        
        # Calculate seasonal component by averaging detrended values at same position in cycle
        seasonal = np.zeros(n)
        for i in range(period):
            indices = np.arange(i, n, period)
            if len(indices) > 0:
                seasonal_value = np.mean(detrended[indices])
                seasonal[indices] = seasonal_value
        
        # Calculate residual
        residual = customers - trend - seasonal
        
        return SeasonalityResults(
            trend=trend,
            seasonal=seasonal,
            residual=residual,
            period=period
        )
    
    def analyze_control_variables(self, df: pd.DataFrame) -> ControlAnalysis:
        """Quantify the impact of control variables on customer acquisition.
        
        Uses independent t-tests to compare mean customer acquisition during
        periods with and without holidays/competitor promotions.
        
        Args:
            df: DataFrame with holidays, competitor_promo, and new_customers columns
            
        Returns:
            ControlAnalysis with effect sizes and p-values
        """
        # Analyze holiday effect
        if 'holidays' in df.columns and 'new_customers' in df.columns:
            holiday_customers = df[df['holidays'] == 1]['new_customers']
            non_holiday_customers = df[df['holidays'] == 0]['new_customers']
            
            if len(holiday_customers) > 0 and len(non_holiday_customers) > 0:
                # Calculate mean difference
                holiday_mean_diff = holiday_customers.mean() - non_holiday_customers.mean()
                
                # Perform t-test
                t_stat, holiday_pvalue = stats.ttest_ind(
                    holiday_customers,
                    non_holiday_customers,
                    equal_var=False  # Welch's t-test
                )
            else:
                holiday_mean_diff = 0.0
                holiday_pvalue = 1.0
        else:
            holiday_mean_diff = 0.0
            holiday_pvalue = 1.0
        
        # Analyze competitor promo effect
        if 'competitor_promo' in df.columns and 'new_customers' in df.columns:
            promo_customers = df[df['competitor_promo'] == 1]['new_customers']
            non_promo_customers = df[df['competitor_promo'] == 0]['new_customers']
            
            if len(promo_customers) > 0 and len(non_promo_customers) > 0:
                # Calculate mean difference
                promo_mean_diff = promo_customers.mean() - non_promo_customers.mean()
                
                # Perform t-test
                t_stat, promo_pvalue = stats.ttest_ind(
                    promo_customers,
                    non_promo_customers,
                    equal_var=False  # Welch's t-test
                )
            else:
                promo_mean_diff = 0.0
                promo_pvalue = 1.0
        else:
            promo_mean_diff = 0.0
            promo_pvalue = 1.0
        
        return ControlAnalysis(
            holiday_effect=(holiday_mean_diff, holiday_pvalue),
            promo_effect=(promo_mean_diff, promo_pvalue)
        )
