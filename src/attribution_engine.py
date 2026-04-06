"""
AttributionEngine for Marketing Mix Modeling analysis.

This module provides attribution and budget optimization functionality,
calculating channel contributions, ROI, and optimal budget allocation.
"""

from dataclasses import dataclass
from typing import Dict, Tuple, Optional, List
import pandas as pd
import numpy as np
from scipy.optimize import minimize
from src.statistical_modeler import ModelResults


@dataclass
class AttributionResults:
    """Results from marketing attribution analysis.

    Attributes:
        marginal_contributions: Dictionary mapping channel names to incremental customers
        roi_by_channel: Dictionary mapping channel names to (ROI, (lower_ci, upper_ci))
        percentage_contributions: Dictionary mapping channel names to percentage of total
        channel_rankings: List of (channel, ROI) tuples sorted by ROI descending
        optimal_spend_levels: Dictionary mapping channel names to optimal spend levels
    """

    marginal_contributions: Dict[str, float]
    roi_by_channel: Dict[str, Tuple[float, Tuple[float, float]]]
    percentage_contributions: Dict[str, float]
    channel_rankings: List[Tuple[str, float]]
    optimal_spend_levels: Dict[str, float]


@dataclass
class OptimizationResults:
    """Results from budget optimization.

    Attributes:
        optimal_allocation: Dictionary mapping channel names to optimal spend amounts
        expected_customers: Expected customer acquisitions with optimal allocation
        expected_lift: Percentage lift vs current allocation
        current_allocation: Dictionary mapping channel names to current spend amounts
        current_customers: Current customer acquisitions
        convergence_status: Status message from optimizer
        iterations: Number of optimization iterations
    """

    optimal_allocation: Dict[str, float]
    expected_customers: float
    expected_lift: float
    current_allocation: Dict[str, float]
    current_customers: float
    convergence_status: str
    iterations: int


class AttributionEngine:
    """Attribution and optimization engine for Marketing Mix Modeling.

    This class calculates channel contributions, ROI with confidence intervals,
    and performs budget optimization to maximize customer acquisition.

    Attributes:
        model_results: Fitted model results from StatisticalModeler
        customer_value: Assumed customer lifetime value in dollars
        spend_channels: List of marketing channel names
    """

    SPEND_CHANNELS = [
        "tv_spend",
        "radio_spend",
        "facebook_spend",
        "instagram_spend",
        "google_search_spend",
        "google_play_spend",
        "youtube_spend",
        "display_spend",
    ]

    def __init__(self, model_results: ModelResults, customer_value: float = 100.0):
        """Initialize AttributionEngine with fitted model and customer value.

        Args:
            model_results: Fitted model results from StatisticalModeler
            customer_value: Assumed customer lifetime value in dollars (default $100)
        """
        self.model_results = model_results
        self.customer_value = customer_value
        self.spend_channels = self.SPEND_CHANNELS

    def calculate_attribution(self, df: pd.DataFrame) -> AttributionResults:
        """Calculate marginal contribution and ROI for each channel.

        This method computes:
        1. Marginal contribution (incremental customers) per channel
        2. ROI with confidence intervals
        3. Percentage contributions
        4. Channel rankings by ROI

        Args:
            df: Original DataFrame with spend data

        Returns:
            AttributionResults with contributions, ROI, and rankings
        """
        marginal_contributions = {}
        roi_by_channel = {}

        # Calculate total spend per channel
        total_spend_by_channel = {}
        for channel in self.spend_channels:
            if channel in df.columns:
                total_spend_by_channel[channel] = df[channel].sum()

        # Calculate marginal contribution for each channel
        for channel in self.spend_channels:
            if channel in df.columns:
                contribution = self.calculate_marginal_contribution(channel, df)
                marginal_contributions[channel] = contribution

                # Calculate ROI
                total_spend = total_spend_by_channel[channel]
                roi, ci = self.calculate_roi(channel, contribution, total_spend)
                roi_by_channel[channel] = (roi, ci)

        # Calculate percentage contributions
        total_contribution = sum(marginal_contributions.values())
        percentage_contributions = {}
        for channel, contribution in marginal_contributions.items():
            if total_contribution > 0:
                percentage_contributions[channel] = (
                    contribution / total_contribution
                ) * 100
            else:
                percentage_contributions[channel] = 0.0

        # Rank channels by ROI
        channel_rankings = sorted(
            [(ch, roi_by_channel[ch][0]) for ch in roi_by_channel.keys()],
            key=lambda x: x[1],
            reverse=True,
        )

        # Placeholder for optimal spend levels (will be calculated in optimize_budget)
        optimal_spend_levels = {
            ch: 0.0 for ch in self.spend_channels if ch in df.columns
        }

        return AttributionResults(
            marginal_contributions=marginal_contributions,
            roi_by_channel=roi_by_channel,
            percentage_contributions=percentage_contributions,
            channel_rankings=channel_rankings,
            optimal_spend_levels=optimal_spend_levels,
        )

    def calculate_marginal_contribution(self, channel: str, df: pd.DataFrame) -> float:
        """Calculate incremental customers from a channel.

        The marginal contribution is calculated as the sum of predicted customers
        attributed to the channel across all time periods:

        contribution_i = Σ_t (β_i * transformed_spend_i_t)

        Args:
            channel: Name of the marketing channel
            df: Original DataFrame with spend data

        Returns:
            Total incremental customers attributed to the channel
        """
        # Get the coefficient for this channel
        model = self.model_results.model
        coefficients = self.model_results.coefficients
        transformation_params = self.model_results.transformation_params
        model_type = self.model_results.model_type

        # Determine the feature name based on model type
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

        # Get coefficient
        if feature_name not in coefficients.index:
            return 0.0

        coef = coefficients.loc[feature_name, "coef"]

        # Get transformed spend values
        if model_type == "baseline":
            # Use original spend
            transformed_spend = df[channel].values
        else:
            # Apply transformations
            from src.statistical_modeler import StatisticalModeler

            modeler = StatisticalModeler()

            if model_type == "adstock":
                decay = transformation_params[channel]["decay"]
                transformed_spend = modeler.apply_adstock_transformation(
                    df[channel].values, decay_rate=decay
                )
            elif model_type == "saturation":
                alpha = transformation_params[channel]["alpha"]
                gamma = transformation_params[channel]["gamma"]
                transformed_spend = modeler.apply_saturation_transformation(
                    df[channel].values, alpha=alpha, gamma=gamma
                )
            elif model_type == "full":
                # Apply both transformations
                decay = transformation_params[channel]["decay"]
                alpha = transformation_params[channel]["alpha"]
                gamma = transformation_params[channel]["gamma"]

                # First adstock
                adstock = modeler.apply_adstock_transformation(
                    df[channel].values, decay_rate=decay
                )
                # Then saturation
                transformed_spend = modeler.apply_saturation_transformation(
                    adstock, alpha=alpha, gamma=gamma
                )
            else:
                transformed_spend = df[channel].values

        # Calculate marginal contribution
        contribution = np.sum(coef * transformed_spend)

        return contribution

    def calculate_roi(
        self, channel: str, contribution: float, total_spend: float
    ) -> Tuple[float, Tuple[float, float]]:
        """Calculate ROI with confidence interval.

        ROI is calculated as:
        ROI_i = (contribution_i * customer_value) / total_spend_i - 1

        Confidence intervals are calculated using the coefficient confidence intervals.

        Args:
            channel: Name of the marketing channel
            contribution: Marginal contribution (incremental customers)
            total_spend: Total spend on the channel

        Returns:
            Tuple of (roi, (lower_ci, upper_ci))
        """
        if total_spend == 0:
            return (0.0, (0.0, 0.0))

        # Calculate ROI
        revenue = contribution * self.customer_value
        roi = (revenue / total_spend) - 1

        # Calculate confidence interval using coefficient CI
        coefficients = self.model_results.coefficients
        model_type = self.model_results.model_type

        # Determine feature name
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
            return (roi, (roi, roi))

        # Get coefficient confidence interval
        ci_lower = coefficients.loc[feature_name, "ci_lower"]
        ci_upper = coefficients.loc[feature_name, "ci_upper"]
        coef = coefficients.loc[feature_name, "coef"]

        # Scale contribution by CI ratio
        if coef != 0:
            contribution_lower = contribution * (ci_lower / coef)
            contribution_upper = contribution * (ci_upper / coef)
        else:
            contribution_lower = contribution
            contribution_upper = contribution

        # Calculate ROI confidence interval
        roi_lower = (contribution_lower * self.customer_value / total_spend) - 1
        roi_upper = (contribution_upper * self.customer_value / total_spend) - 1

        return (roi, (roi_lower, roi_upper))

    def optimize_budget(
        self,
        df: pd.DataFrame,
        total_budget: float,
        constraints: Optional[Dict[str, Tuple[float, float]]] = None,
    ) -> OptimizationResults:
        """Find optimal budget allocation maximizing customer acquisition.

        This method uses scipy.optimize.minimize with SLSQP method to find
        the budget allocation that maximizes expected customer acquisitions
        while respecting:
        1. Total budget constraint (sum of allocations = total_budget)
        2. Channel-specific min/max spend constraints

        Args:
            df: Original DataFrame with spend data (used for current allocation)
            total_budget: Total marketing budget constraint
            constraints: Optional dict of (min_spend, max_spend) per channel.
                If None, uses 0.5x to 2x current spend as bounds.

        Returns:
            OptimizationResults with optimal allocation and expected lift
        """
        # Calculate current allocation
        current_allocation = {}
        for channel in self.spend_channels:
            if channel in df.columns:
                current_allocation[channel] = df[channel].sum()

        # Set up constraints if not provided
        if constraints is None:
            constraints = {}
            for channel, current_spend in current_allocation.items():
                if current_spend > 0:
                    # Allow 0.5x to 2x current spend
                    constraints[channel] = (current_spend * 0.5, current_spend * 2.0)
                else:
                    # If no current spend, allow 0 to 10% of total budget
                    constraints[channel] = (0.0, total_budget * 0.1)

        # Get active channels (those in the model)
        active_channels = [ch for ch in self.spend_channels if ch in current_allocation]
        n_channels = len(active_channels)

        # Initial allocation (proportional to current spend)
        total_current = sum(current_allocation.values())
        if total_current > 0:
            x0 = np.array(
                [
                    (current_allocation[ch] / total_current) * total_budget
                    for ch in active_channels
                ]
            )
        else:
            # Equal allocation if no current spend
            x0 = np.array([total_budget / n_channels] * n_channels)

        # Define objective function (negative expected customers for minimization)
        def objective(allocation: np.ndarray) -> float:
            """Calculate negative expected customers."""
            expected_customers = self._predict_customers(
                allocation, active_channels, df
            )
            return -expected_customers

        # Set up optimization constraints
        opt_constraints = []

        # Budget equality constraint
        opt_constraints.append(
            {"type": "eq", "fun": lambda x: np.sum(x) - total_budget}
        )

        # Channel-specific min/max constraints
        bounds = []
        for i, channel in enumerate(active_channels):
            min_spend, max_spend = constraints.get(channel, (0.0, total_budget))
            bounds.append((min_spend, max_spend))

        # Run optimization
        result = minimize(
            objective,
            x0=x0,
            method="SLSQP",
            bounds=bounds,
            constraints=opt_constraints,
            options={"maxiter": 1000, "ftol": 1e-6},
        )

        # Extract optimal allocation
        optimal_allocation = {
            channel: result.x[i] for i, channel in enumerate(active_channels)
        }

        # Calculate expected customers with optimal allocation
        expected_customers = self._predict_customers(result.x, active_channels, df)

        # Calculate current customers
        current_customers = self._predict_customers(
            np.array([current_allocation[ch] for ch in active_channels]),
            active_channels,
            df,
        )

        # Calculate lift
        if current_customers > 0:
            expected_lift = (
                (expected_customers - current_customers) / current_customers
            ) * 100
        else:
            expected_lift = 0.0

        # Convergence status
        convergence_status = (
            "Success" if result.success else f"Failed: {result.message}"
        )

        return OptimizationResults(
            optimal_allocation=optimal_allocation,
            expected_customers=expected_customers,
            expected_lift=expected_lift,
            current_allocation=current_allocation,
            current_customers=current_customers,
            convergence_status=convergence_status,
            iterations=result.nit if hasattr(result, "nit") else 0,
        )

    def _predict_customers(
        self, allocation: np.ndarray, channels: List[str], df: pd.DataFrame
    ) -> float:
        """Predict total customers for a given budget allocation.

        Args:
            allocation: Array of spend amounts per channel
            channels: List of channel names corresponding to allocation
            df: Original DataFrame (used for time periods and control variables)

        Returns:
            Predicted total customer acquisitions
        """
        from src.statistical_modeler import StatisticalModeler

        model = self.model_results.model
        model_type = self.model_results.model_type
        transformation_params = self.model_results.transformation_params

        # Number of time periods
        n_periods = len(df)

        # Distribute allocation evenly across time periods
        # (This is a simplification; in practice, you might want to optimize timing too)
        spend_per_period = allocation / n_periods

        # Create feature matrix
        modeler = StatisticalModeler()
        features = []

        for i, channel in enumerate(channels):
            spend = np.full(n_periods, spend_per_period[i])

            # Apply transformations based on model type
            if model_type == "baseline":
                transformed = spend
            elif model_type == "adstock":
                decay = transformation_params[channel]["decay"]
                transformed = modeler.apply_adstock_transformation(
                    spend, decay_rate=decay
                )
            elif model_type == "saturation":
                alpha = transformation_params[channel]["alpha"]
                gamma = transformation_params[channel]["gamma"]
                transformed = modeler.apply_saturation_transformation(
                    spend, alpha=alpha, gamma=gamma
                )
            elif model_type == "full":
                decay = transformation_params[channel]["decay"]
                alpha = transformation_params[channel]["alpha"]
                gamma = transformation_params[channel]["gamma"]

                # Apply adstock then saturation
                adstock = modeler.apply_adstock_transformation(spend, decay_rate=decay)
                transformed = modeler.apply_saturation_transformation(
                    adstock, alpha=alpha, gamma=gamma
                )
            else:
                transformed = spend

            features.append(transformed)

        # Stack features
        X = np.column_stack(features)

        # Add control variables from original data
        if "holidays" in df.columns:
            X = np.column_stack([X, df["holidays"].values])
        if "competitor_promo" in df.columns:
            X = np.column_stack([X, df["competitor_promo"].values])

        # Add constant
        X = np.column_stack([np.ones(n_periods), X])

        # Predict
        predictions = model.predict(X)

        # Sum across all periods
        total_customers = np.sum(predictions)

        return total_customers
