"""
StatisticalModeler for Marketing Mix Modeling analysis.

This module provides statistical modeling functionality including adstock and
saturation transformations, model fitting, hyperparameter optimization, and
comprehensive model diagnostics.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple, List
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.stattools import durbin_watson
from statsmodels.stats.outliers_influence import variance_inflation_factor
from scipy import stats
import warnings


@dataclass
class DiagnosticsResults:
    """Results from comprehensive model diagnostics.

    Attributes:
        r_squared_train: R-squared on training set
        r_squared_test: R-squared on test set
        rmse_train: Root Mean Squared Error on training set
        rmse_test: Root Mean Squared Error on test set
        mae_train: Mean Absolute Error on training set
        mae_test: Mean Absolute Error on test set
        residual_normality_pvalue: P-value from Shapiro-Wilk normality test
        heteroscedasticity_pvalue: P-value from Breusch-Pagan test
        vif_values: Variance Inflation Factors for each predictor
        durbin_watson: Durbin-Watson statistic for autocorrelation
        aic: Akaike Information Criterion
        bic: Bayesian Information Criterion
        cv_scores: Cross-validation R-squared scores
    """

    r_squared_train: float
    r_squared_test: float
    rmse_train: float
    rmse_test: float
    mae_train: float
    mae_test: float
    residual_normality_pvalue: float
    heteroscedasticity_pvalue: float
    vif_values: Dict[str, float]
    durbin_watson: float
    aic: float
    bic: float
    cv_scores: List[float]


@dataclass
class ModelResults:
    """Results from model fitting and validation.

    Attributes:
        model: Fitted statsmodels OLS model
        coefficients: DataFrame with coef, std_err, ci_lower, ci_upper
        diagnostics: Comprehensive diagnostics results
        train_predictions: Predictions on training set
        test_predictions: Predictions on test set
        X_train: Training features
        X_test: Test features
        y_train: Training target
        y_test: Test target
        transformation_params: Parameters used for transformations
        model_type: Type of model ('baseline', 'adstock', 'saturation', 'full')
    """

    model: Any
    coefficients: pd.DataFrame
    diagnostics: DiagnosticsResults
    train_predictions: np.ndarray
    test_predictions: np.ndarray
    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: np.ndarray
    y_test: np.ndarray
    transformation_params: Dict[str, Dict[str, float]]
    model_type: str


class StatisticalModeler:
    """Statistical modeling component for Marketing Mix Modeling.

    This class implements marketing mix transformations (adstock and saturation),
    builds regression models, performs hyperparameter optimization, and validates
    model assumptions through comprehensive diagnostics.

    Attributes:
        random_state: Random seed for reproducibility
    """

    def __init__(self, random_state: int = 42):
        """Initialize StatisticalModeler with random seed.

        Args:
            random_state: Random seed for reproducibility in train/test splits
                and any stochastic operations. Default is 42.
        """
        self.random_state = random_state
        np.random.seed(random_state)

    def apply_adstock_transformation(
        self, spend: np.ndarray, decay_rate: float
    ) -> np.ndarray:
        """Apply adstock transformation to capture advertising carryover effects.

        The adstock transformation models the phenomenon where advertising effects
        persist beyond the initial exposure period. This is implemented using a
        geometric decay model where each period's effect includes a decayed
        contribution from previous periods.

        Mathematical Formula:
            adstock_t = spend_t + decay_rate * adstock_{t-1}

        where:
            - adstock_t: transformed spend at time t
            - spend_t: original spend at time t
            - decay_rate: decay parameter controlling memory length (0 < decay_rate < 1)
            - adstock_{t-1}: transformed spend from previous period

        The transformation is computed recursively starting from t=0 where
        adstock_0 = spend_0.

        Properties:
            - Higher decay_rate means longer advertising memory
            - decay_rate = 0 returns original spend (no carryover)
            - decay_rate → 1 means effects persist almost indefinitely
            - Output is always non-negative if input is non-negative

        Args:
            spend: Array of weekly spend values (length n_weeks)
            decay_rate: Decay parameter in range (0, 1). Typical values are
                0.3-0.7 for most advertising channels.

        Returns:
            Transformed spend array with carryover effects (same length as input)

        Raises:
            ValueError: If decay_rate is not in range (0, 1)
            ValueError: If spend contains negative values

        Examples:
            >>> modeler = StatisticalModeler()
            >>> spend = np.array([100, 0, 0, 0])
            >>> adstock = modeler.apply_adstock_transformation(spend, decay_rate=0.5)
            >>> print(adstock)
            [100.0, 50.0, 25.0, 12.5]
        """
        # Validate decay_rate
        if not (0 < decay_rate < 1):
            raise ValueError(f"decay_rate must be in range (0, 1), got {decay_rate}")

        # Validate spend is non-negative
        if np.any(spend < 0):
            raise ValueError(
                "spend array contains negative values. "
                "All spend values must be non-negative."
            )

        # Initialize adstock array
        adstock = np.zeros_like(spend, dtype=float)

        # Compute adstock recursively
        for t in range(len(spend)):
            if t == 0:
                adstock[t] = spend[t]
            else:
                adstock[t] = spend[t] + decay_rate * adstock[t - 1]

        return adstock

    def apply_saturation_transformation(
        self, spend: np.ndarray, alpha: float, gamma: float
    ) -> np.ndarray:
        """Apply Hill saturation curve to model diminishing returns.

        The saturation transformation models the diminishing returns phenomenon
        where incremental advertising spend produces progressively smaller
        increases in response. This is implemented using the Hill equation,
        which produces an S-shaped curve.

        Mathematical Formula:
            saturated_spend = spend^gamma / (alpha^gamma + spend^gamma)

        where:
            - saturated_spend: transformed spend (bounded between 0 and 1)
            - spend: original spend value
            - alpha: half-saturation point (spend level producing 50% of max response)
            - gamma: shape parameter controlling curve steepness

        Interpretation:
            - alpha represents the spend level at which you achieve half of the
              maximum possible response
            - gamma controls how quickly saturation is reached:
                * gamma < 1: gradual saturation
                * gamma = 1: linear-like response in middle range
                * gamma > 1: sharp saturation threshold
            - Output is always in range [0, 1]
            - The curve is monotonically increasing

        Properties:
            - saturated_spend(0) = 0
            - saturated_spend(alpha) = 0.5
            - saturated_spend(∞) → 1
            - Derivative is always positive (monotonically increasing)

        Args:
            spend: Array of weekly spend values (length n_weeks)
            alpha: Half-saturation point (must be positive). Typically set to
                mean or median spend level.
            gamma: Shape parameter (must be positive). Typical values are
                0.5-2.0 for most advertising channels.

        Returns:
            Transformed spend array with saturation effects (same length as input)
            Values are in range [0, 1]

        Raises:
            ValueError: If alpha is not positive
            ValueError: If gamma is not positive
            ValueError: If spend contains negative values

        Examples:
            >>> modeler = StatisticalModeler()
            >>> spend = np.array([0, 50, 100, 200])
            >>> saturated = modeler.apply_saturation_transformation(
            ...     spend, alpha=100, gamma=1.0
            ... )
            >>> print(saturated)
            [0.0, 0.333, 0.5, 0.667]
        """
        # Validate alpha
        if alpha <= 0:
            raise ValueError(f"alpha must be positive, got {alpha}")

        # Validate gamma
        if gamma <= 0:
            raise ValueError(f"gamma must be positive, got {gamma}")

        # Validate spend is non-negative
        if np.any(spend < 0):
            raise ValueError(
                "spend array contains negative values. "
                "All spend values must be non-negative."
            )

        # Apply Hill saturation curve
        # Handle zero spend to avoid division issues
        saturated = np.zeros_like(spend, dtype=float)

        # Compute saturation for non-zero spend
        spend_gamma = np.power(spend, gamma)
        alpha_gamma = np.power(alpha, gamma)

        saturated = spend_gamma / (alpha_gamma + spend_gamma)

        return saturated

    def fit(self, df: pd.DataFrame, test_size: float = 0.2) -> ModelResults:
        """Fit multiple model specifications and select best.

        This method implements a comprehensive model fitting pipeline:
        1. Splits data into train/test sets
        2. Fits baseline linear regression model
        3. Performs grid search for adstock decay rates
        4. Performs grid search for saturation parameters
        5. Compares model specifications (baseline, adstock, saturation, full)
        6. Selects best model using AIC/BIC
        7. Validates model with comprehensive diagnostics

        Args:
            df: Validated DataFrame with spend channels and new_customers
            test_size: Proportion of data for testing (default 0.2)

        Returns:
            ModelResults with fitted model, coefficients, and diagnostics

        Raises:
            ValueError: If df doesn't contain required columns
            RuntimeError: If model fitting fails to converge
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

        # Validate required columns
        required_cols = spend_channels + [
            "new_customers",
            "holidays",
            "competitor_promo",
        ]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Remove zero-variance channels
        active_channels = []
        for channel in spend_channels:
            if df[channel].std() > 0:
                active_channels.append(channel)
            else:
                warnings.warn(
                    f"Channel '{channel}' has zero variance and will be excluded from the model."
                )

        if len(active_channels) == 0:
            raise ValueError("No channels with non-zero variance found.")

        # Prepare features and target
        y = df["new_customers"].values

        # Split data
        train_idx, test_idx = train_test_split(
            np.arange(len(df)),
            test_size=test_size,
            random_state=self.random_state,
            shuffle=False,  # Preserve time order
        )

        # Fit baseline model
        print("Fitting baseline model...")
        baseline_result = self._fit_baseline_model(
            df, active_channels, train_idx, test_idx
        )

        # Fit adstock model with grid search
        print("Fitting adstock model with grid search...")
        adstock_result = self._fit_adstock_model(
            df, active_channels, train_idx, test_idx
        )

        # Fit saturation model with grid search
        print("Fitting saturation model with grid search...")
        saturation_result = self._fit_saturation_model(
            df, active_channels, train_idx, test_idx
        )

        # Fit full model (adstock + saturation)
        print("Fitting full model (adstock + saturation)...")
        full_result = self._fit_full_model(df, active_channels, train_idx, test_idx)

        # Select best model using AIC
        models = {
            "baseline": baseline_result,
            "adstock": adstock_result,
            "saturation": saturation_result,
            "full": full_result,
        }

        best_model_type = min(models.keys(), key=lambda k: models[k].diagnostics.aic)
        best_result = models[best_model_type]

        print(f"\nBest model selected: {best_model_type}")
        print(f"  AIC: {best_result.diagnostics.aic:.2f}")
        print(f"  BIC: {best_result.diagnostics.bic:.2f}")
        print(f"  Test R²: {best_result.diagnostics.r_squared_test:.4f}")

        # Check for overfitting
        r2_diff = (
            best_result.diagnostics.r_squared_train
            - best_result.diagnostics.r_squared_test
        )
        if r2_diff > 0.2:
            warnings.warn(
                f"Potential overfitting detected: Train R² ({best_result.diagnostics.r_squared_train:.4f}) "
                f"is significantly higher than Test R² ({best_result.diagnostics.r_squared_test:.4f}). "
                f"Consider using regularization or collecting more data."
            )

        return best_result

    def _fit_baseline_model(
        self,
        df: pd.DataFrame,
        channels: List[str],
        train_idx: np.ndarray,
        test_idx: np.ndarray,
    ) -> ModelResults:
        """Fit baseline linear regression model without transformations."""
        # Prepare features
        X = df[channels + ["holidays", "competitor_promo"]].values
        y = df["new_customers"].values

        X_train, y_train = X[train_idx], y[train_idx]
        X_test, y_test = X[test_idx], y[test_idx]

        # Add constant
        X_train_sm = sm.add_constant(X_train)
        X_test_sm = sm.add_constant(X_test)

        # Fit model
        try:
            model = sm.OLS(y_train, X_train_sm).fit()
        except Exception as e:
            raise RuntimeError(f"Model fitting failed: {str(e)}")

        # Predictions
        train_pred = model.predict(X_train_sm)
        test_pred = model.predict(X_test_sm)

        # Create feature names
        feature_names = ["const"] + channels + ["holidays", "competitor_promo"]

        # Prepare DataFrames
        X_train_df = pd.DataFrame(X_train_sm, columns=feature_names)
        X_test_df = pd.DataFrame(X_test_sm, columns=feature_names)

        # Validate model
        diagnostics = self.validate_model(
            model, X_train_df, X_test_df, y_train, y_test, train_pred, test_pred
        )

        # Extract coefficients
        conf_int = model.conf_int()
        coefficients = pd.DataFrame(
            {
                "coef": model.params,
                "std_err": model.bse,
                "ci_lower": conf_int[:, 0],
                "ci_upper": conf_int[:, 1],
            },
            index=feature_names,
        )

        return ModelResults(
            model=model,
            coefficients=coefficients,
            diagnostics=diagnostics,
            train_predictions=train_pred,
            test_predictions=test_pred,
            X_train=X_train_df,
            X_test=X_test_df,
            y_train=y_train,
            y_test=y_test,
            transformation_params={},
            model_type="baseline",
        )

    def _fit_adstock_model(
        self,
        df: pd.DataFrame,
        channels: List[str],
        train_idx: np.ndarray,
        test_idx: np.ndarray,
    ) -> ModelResults:
        """Fit model with adstock transformations using grid search."""
        decay_rates = [0.1, 0.3, 0.5, 0.7, 0.9]
        best_aic = np.inf
        best_result = None

        for decay in decay_rates:
            # Apply adstock transformation
            df_transformed = df.copy()
            transformation_params = {}

            for channel in channels:
                adstock = self.apply_adstock_transformation(
                    df[channel].values, decay_rate=decay
                )
                df_transformed[f"{channel}_adstock"] = adstock
                transformation_params[channel] = {"decay": decay}

            # Prepare features
            adstock_cols = [f"{ch}_adstock" for ch in channels]
            X = df_transformed[adstock_cols + ["holidays", "competitor_promo"]].values
            y = df["new_customers"].values

            X_train, y_train = X[train_idx], y[train_idx]
            X_test, y_test = X[test_idx], y[test_idx]

            # Add constant
            X_train_sm = sm.add_constant(X_train)
            X_test_sm = sm.add_constant(X_test)

            # Fit model
            try:
                model = sm.OLS(y_train, X_train_sm).fit()
            except Exception:
                continue

            # Check AIC
            if model.aic < best_aic:
                best_aic = model.aic

                # Predictions
                train_pred = model.predict(X_train_sm)
                test_pred = model.predict(X_test_sm)

                # Feature names
                feature_names = (
                    ["const"] + adstock_cols + ["holidays", "competitor_promo"]
                )
                X_train_df = pd.DataFrame(X_train_sm, columns=feature_names)
                X_test_df = pd.DataFrame(X_test_sm, columns=feature_names)

                # Validate
                diagnostics = self.validate_model(
                    model, X_train_df, X_test_df, y_train, y_test, train_pred, test_pred
                )

                # Coefficients
                conf_int = model.conf_int()
                coefficients = pd.DataFrame(
                    {
                        "coef": model.params,
                        "std_err": model.bse,
                        "ci_lower": conf_int[:, 0],
                        "ci_upper": conf_int[:, 1],
                    },
                    index=feature_names,
                )

                best_result = ModelResults(
                    model=model,
                    coefficients=coefficients,
                    diagnostics=diagnostics,
                    train_predictions=train_pred,
                    test_predictions=test_pred,
                    X_train=X_train_df,
                    X_test=X_test_df,
                    y_train=y_train,
                    y_test=y_test,
                    transformation_params=transformation_params,
                    model_type="adstock",
                )

        if best_result is None:
            raise RuntimeError("Adstock model fitting failed for all decay rates.")

        return best_result

    def _fit_saturation_model(
        self,
        df: pd.DataFrame,
        channels: List[str],
        train_idx: np.ndarray,
        test_idx: np.ndarray,
    ) -> ModelResults:
        """Fit model with saturation transformations using grid search."""
        best_aic = np.inf
        best_result = None

        # Grid search parameters
        gamma_values = [0.5, 1.0, 1.5, 2.0]

        for gamma in gamma_values:
            # Apply saturation transformation
            df_transformed = df.copy()
            transformation_params = {}

            for channel in channels:
                # Use mean spend as alpha
                alpha = df[channel].mean()
                if alpha == 0:
                    alpha = 1.0  # Avoid division by zero

                saturated = self.apply_saturation_transformation(
                    df[channel].values, alpha=alpha, gamma=gamma
                )
                df_transformed[f"{channel}_sat"] = saturated
                transformation_params[channel] = {"alpha": alpha, "gamma": gamma}

            # Prepare features
            sat_cols = [f"{ch}_sat" for ch in channels]
            X = df_transformed[sat_cols + ["holidays", "competitor_promo"]].values
            y = df["new_customers"].values

            X_train, y_train = X[train_idx], y[train_idx]
            X_test, y_test = X[test_idx], y[test_idx]

            # Add constant
            X_train_sm = sm.add_constant(X_train)
            X_test_sm = sm.add_constant(X_test)

            # Fit model
            try:
                model = sm.OLS(y_train, X_train_sm).fit()
            except Exception:
                continue

            # Check AIC
            if model.aic < best_aic:
                best_aic = model.aic

                # Predictions
                train_pred = model.predict(X_train_sm)
                test_pred = model.predict(X_test_sm)

                # Feature names
                feature_names = ["const"] + sat_cols + ["holidays", "competitor_promo"]
                X_train_df = pd.DataFrame(X_train_sm, columns=feature_names)
                X_test_df = pd.DataFrame(X_test_sm, columns=feature_names)

                # Validate
                diagnostics = self.validate_model(
                    model, X_train_df, X_test_df, y_train, y_test, train_pred, test_pred
                )

                # Coefficients
                conf_int = model.conf_int()
                coefficients = pd.DataFrame(
                    {
                        "coef": model.params,
                        "std_err": model.bse,
                        "ci_lower": conf_int[:, 0],
                        "ci_upper": conf_int[:, 1],
                    },
                    index=feature_names,
                )

                best_result = ModelResults(
                    model=model,
                    coefficients=coefficients,
                    diagnostics=diagnostics,
                    train_predictions=train_pred,
                    test_predictions=test_pred,
                    X_train=X_train_df,
                    X_test=X_test_df,
                    y_train=y_train,
                    y_test=y_test,
                    transformation_params=transformation_params,
                    model_type="saturation",
                )

        if best_result is None:
            raise RuntimeError(
                "Saturation model fitting failed for all parameter combinations."
            )

        return best_result

    def _fit_full_model(
        self,
        df: pd.DataFrame,
        channels: List[str],
        train_idx: np.ndarray,
        test_idx: np.ndarray,
    ) -> ModelResults:
        """Fit model with both adstock and saturation transformations."""
        decay_rates = [0.3, 0.5, 0.7]
        gamma_values = [0.5, 1.0, 1.5]

        best_aic = np.inf
        best_result = None

        for decay in decay_rates:
            for gamma in gamma_values:
                # Apply transformations
                df_transformed = df.copy()
                transformation_params = {}

                for channel in channels:
                    # First apply adstock
                    adstock = self.apply_adstock_transformation(
                        df[channel].values, decay_rate=decay
                    )

                    # Then apply saturation
                    alpha = df[channel].mean()
                    if alpha == 0:
                        alpha = 1.0

                    saturated = self.apply_saturation_transformation(
                        adstock, alpha=alpha, gamma=gamma
                    )

                    df_transformed[f"{channel}_full"] = saturated
                    transformation_params[channel] = {
                        "decay": decay,
                        "alpha": alpha,
                        "gamma": gamma,
                    }

                # Prepare features
                full_cols = [f"{ch}_full" for ch in channels]
                X = df_transformed[full_cols + ["holidays", "competitor_promo"]].values
                y = df["new_customers"].values

                X_train, y_train = X[train_idx], y[train_idx]
                X_test, y_test = X[test_idx], y[test_idx]

                # Add constant
                X_train_sm = sm.add_constant(X_train)
                X_test_sm = sm.add_constant(X_test)

                # Fit model
                try:
                    model = sm.OLS(y_train, X_train_sm).fit()
                except Exception:
                    continue

                # Check AIC
                if model.aic < best_aic:
                    best_aic = model.aic

                    # Predictions
                    train_pred = model.predict(X_train_sm)
                    test_pred = model.predict(X_test_sm)

                    # Feature names
                    feature_names = (
                        ["const"] + full_cols + ["holidays", "competitor_promo"]
                    )
                    X_train_df = pd.DataFrame(X_train_sm, columns=feature_names)
                    X_test_df = pd.DataFrame(X_test_sm, columns=feature_names)

                    # Validate
                    diagnostics = self.validate_model(
                        model,
                        X_train_df,
                        X_test_df,
                        y_train,
                        y_test,
                        train_pred,
                        test_pred,
                    )

                    # Coefficients
                    conf_int = model.conf_int()
                    coefficients = pd.DataFrame(
                        {
                            "coef": model.params,
                            "std_err": model.bse,
                            "ci_lower": conf_int[:, 0],
                            "ci_upper": conf_int[:, 1],
                        },
                        index=feature_names,
                    )

                    best_result = ModelResults(
                        model=model,
                        coefficients=coefficients,
                        diagnostics=diagnostics,
                        train_predictions=train_pred,
                        test_predictions=test_pred,
                        X_train=X_train_df,
                        X_test=X_test_df,
                        y_train=y_train,
                        y_test=y_test,
                        transformation_params=transformation_params,
                        model_type="full",
                    )

        if best_result is None:
            raise RuntimeError(
                "Full model fitting failed for all parameter combinations."
            )

        return best_result

    def validate_model(
        self,
        model: Any,
        X_train: pd.DataFrame,
        X_test: pd.DataFrame,
        y_train: np.ndarray,
        y_test: np.ndarray,
        train_pred: np.ndarray,
        test_pred: np.ndarray,
    ) -> DiagnosticsResults:
        """Perform comprehensive model diagnostics.

        This method validates model assumptions and calculates performance metrics:
        - R-squared, RMSE, MAE for train and test sets
        - Residual normality test (Shapiro-Wilk)
        - Heteroscedasticity test (Breusch-Pagan)
        - VIF for multicollinearity
        - Durbin-Watson for autocorrelation
        - k-fold cross-validation (k=5)

        Args:
            model: Fitted statsmodels OLS model
            X_train: Training features
            X_test: Test features
            y_train: Training target
            y_test: Test target
            train_pred: Training predictions
            test_pred: Test predictions

        Returns:
            DiagnosticsResults with all diagnostic metrics
        """
        # Performance metrics
        r2_train = r2_score(y_train, train_pred)
        r2_test = r2_score(y_test, test_pred)
        rmse_train = np.sqrt(mean_squared_error(y_train, train_pred))
        rmse_test = np.sqrt(mean_squared_error(y_test, test_pred))
        mae_train = mean_absolute_error(y_train, train_pred)
        mae_test = mean_absolute_error(y_test, test_pred)

        # Residual normality test (Shapiro-Wilk)
        residuals = model.resid
        if len(residuals) >= 3:
            _, normality_pvalue = stats.shapiro(residuals)
        else:
            normality_pvalue = 1.0

        # Heteroscedasticity test (Breusch-Pagan)
        try:
            _, het_pvalue, _, _ = het_breuschpagan(residuals, model.model.exog)
        except Exception:
            het_pvalue = 1.0

        # VIF for multicollinearity
        vif_values = {}
        try:
            # Exclude constant from VIF calculation
            X_no_const = X_train.iloc[:, 1:]  # Skip first column (constant)
            for i, col in enumerate(X_no_const.columns):
                try:
                    vif = variance_inflation_factor(X_no_const.values, i)
                    vif_values[col] = vif
                except Exception:
                    vif_values[col] = np.nan
        except Exception:
            pass

        # Durbin-Watson statistic
        dw_stat = durbin_watson(residuals)

        # AIC and BIC
        aic = model.aic
        bic = model.bic

        # Cross-validation
        cv_scores = []
        try:
            # Use sklearn LinearRegression for cross-validation
            lr = LinearRegression()
            X_combined = np.vstack([X_train.values, X_test.values])
            y_combined = np.concatenate([y_train, y_test])

            # 5-fold CV
            scores = cross_val_score(lr, X_combined, y_combined, cv=5, scoring="r2")
            cv_scores = scores.tolist()
        except Exception:
            cv_scores = []

        return DiagnosticsResults(
            r_squared_train=r2_train,
            r_squared_test=r2_test,
            rmse_train=rmse_train,
            rmse_test=rmse_test,
            mae_train=mae_train,
            mae_test=mae_test,
            residual_normality_pvalue=normality_pvalue,
            heteroscedasticity_pvalue=het_pvalue,
            vif_values=vif_values,
            durbin_watson=dw_stat,
            aic=aic,
            bic=bic,
            cv_scores=cv_scores,
        )
