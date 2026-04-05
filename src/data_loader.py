"""
DataLoader module for Marketing Mix Modeling analysis.

This module provides functionality to load and validate marketing data from CSV files,
ensuring data quality and proper schema before analysis.
"""

from dataclasses import dataclass
from typing import List
import pandas as pd
import numpy as np
from pathlib import Path


@dataclass
class ValidationResult:
    """Result of data validation operations.
    
    Attributes:
        is_valid: Whether the validation passed
        errors: List of error messages for critical issues
        warnings: List of warning messages for non-critical issues
    """
    is_valid: bool
    errors: List[str]
    warnings: List[str]


class DataLoader:
    """Load and validate Marketing Mix Modeling dataset from CSV files.
    
    This class handles data ingestion, schema validation, and data quality checks
    for MMM analysis. It ensures that the input data meets all requirements before
    being passed to downstream analysis components.
    
    Attributes:
        REQUIRED_COLUMNS: List of column names that must be present in the dataset
        SPEND_CHANNELS: List of marketing channel spend column names
        CONTROL_VARIABLES: List of control variable column names
        MIN_WEEKS: Minimum number of weeks required for analysis
    """
    
    REQUIRED_COLUMNS = [
        'week_start_date',
        'tv_spend',
        'radio_spend',
        'facebook_spend',
        'instagram_spend',
        'google_search_spend',
        'google_play_spend',
        'youtube_spend',
        'display_spend',
        'holidays',
        'competitor_promo',
        'new_customers'
    ]
    
    # Alternative column names that should be normalized
    COLUMN_ALIASES = {
        'new customers': 'new_customers'
    }
    
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
    MIN_WEEKS = 20
    
    def load_data(self, file_path: str) -> pd.DataFrame:
        """Load and validate MMM dataset from CSV.
        
        This method reads a CSV file, validates its schema and data quality,
        and returns a properly typed DataFrame ready for analysis.
        
        Args:
            file_path: Path to CSV file containing MMM data
            
        Returns:
            Validated DataFrame with proper types:
                - week_start_date as datetime index
                - spend channels as float64
                - control variables as int64
                - new_customers as int64
                
        Raises:
            FileNotFoundError: If the specified file doesn't exist
            ValueError: If validation fails or data is insufficient
        """
        # Check file exists
        if not Path(file_path).exists():
            raise FileNotFoundError(
                f"CSV file not found: {file_path}. "
                f"Please ensure the file path is correct."
            )
        
        # Read CSV
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            raise ValueError(f"Failed to read CSV file: {str(e)}")
        
        # Normalize column names
        df = self._normalize_column_names(df)
        
        # Validate schema
        schema_result = self.validate_schema(df)
        if not schema_result.is_valid:
            error_msg = "Schema validation failed:\n" + "\n".join(schema_result.errors)
            raise ValueError(error_msg)
        
        # Validate data quality
        quality_result = self.validate_data_quality(df)
        if not quality_result.is_valid:
            error_msg = "Data quality validation failed:\n" + "\n".join(quality_result.errors)
            raise ValueError(error_msg)
        
        # Check minimum data requirement
        if len(df) < self.MIN_WEEKS:
            raise ValueError(
                f"Insufficient data: dataset contains {len(df)} weeks, "
                f"but minimum {self.MIN_WEEKS} weeks required for reliable analysis."
            )
        
        # Type conversion
        df = self._type_conversion(df)
        
        return df
    
    def validate_schema(self, df: pd.DataFrame) -> ValidationResult:
        """Validate DataFrame has required columns and structure.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            ValidationResult with validation status and any error messages
        """
        errors = []
        warnings = []
        
        # Check required columns
        missing_cols = self._check_required_columns(df)
        if missing_cols:
            errors.append(
                f"Missing required columns: {', '.join(missing_cols)}. "
                f"Expected columns: {', '.join(self.REQUIRED_COLUMNS)}"
            )
        
        # Validate date column if present
        if 'week_start_date' in df.columns:
            date_errors = self._validate_date_column(df)
            errors.extend(date_errors)
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)
    
    def validate_data_quality(self, df: pd.DataFrame) -> ValidationResult:
        """Check for missing values, duplicates, and invalid numeric values.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            ValidationResult with validation status and any error/warning messages
        """
        errors = []
        warnings = []
        
        # Check for missing values
        missing_info = self._check_missing_values(df)
        if missing_info:
            errors.append(
                f"Missing values detected in columns: {', '.join(missing_info.keys())}. "
                f"Details: {missing_info}"
            )
        
        # Check for duplicates
        duplicate_info = self._check_duplicates(df)
        if duplicate_info:
            errors.append(
                f"Duplicate date entries detected: {duplicate_info['count']} duplicates found. "
                f"Duplicate dates: {duplicate_info['dates']}"
            )
        
        # Validate numeric columns
        numeric_errors = self._validate_numeric_columns(df)
        errors.extend(numeric_errors)
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)
    
    def _check_required_columns(self, df: pd.DataFrame) -> List[str]:
        """Check if all required columns are present.
        
        Args:
            df: DataFrame to check
            
        Returns:
            List of missing column names (empty if all present)
        """
        missing = []
        for col in self.REQUIRED_COLUMNS:
            if col not in df.columns:
                missing.append(col)
        return missing
    
    def _normalize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column names to handle variations.
        
        Args:
            df: DataFrame with potentially non-standard column names
            
        Returns:
            DataFrame with normalized column names
        """
        df = df.copy()
        
        # Apply column aliases
        for old_name, new_name in self.COLUMN_ALIASES.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        return df
    
    def _validate_date_column(self, df: pd.DataFrame) -> List[str]:
        """Validate date column format and parseability.
        
        Args:
            df: DataFrame containing week_start_date column
            
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        try:
            # Attempt to parse dates
            pd.to_datetime(df['week_start_date'])
        except Exception as e:
            errors.append(
                f"Invalid date format in 'week_start_date' column: {str(e)}. "
                f"Expected format: YYYY-MM-DD or similar standard date format."
            )
        
        return errors
    
    def _check_missing_values(self, df: pd.DataFrame) -> dict:
        """Detect missing values in any column.
        
        Args:
            df: DataFrame to check
            
        Returns:
            Dictionary mapping column names to count of missing values
            (empty dict if no missing values)
        """
        missing = {}
        for col in df.columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                missing[col] = null_count
        return missing
    
    def _check_duplicates(self, df: pd.DataFrame) -> dict:
        """Detect duplicate date entries.
        
        Args:
            df: DataFrame to check
            
        Returns:
            Dictionary with duplicate information or empty dict if no duplicates
        """
        if 'week_start_date' not in df.columns:
            return {}
        
        duplicates = df[df.duplicated(subset=['week_start_date'], keep=False)]
        
        if len(duplicates) > 0:
            return {
                'count': len(duplicates),
                'dates': duplicates['week_start_date'].unique().tolist()
            }
        
        return {}
    
    def _validate_numeric_columns(self, df: pd.DataFrame) -> List[str]:
        """Ensure spend and customer columns are non-negative numeric values.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        # Check spend channels
        for col in self.SPEND_CHANNELS:
            if col not in df.columns:
                continue
            
            # Check if numeric
            try:
                numeric_col = pd.to_numeric(df[col], errors='coerce')
                if numeric_col.isnull().any():
                    errors.append(
                        f"Column '{col}' contains non-numeric values. "
                        f"All spend values must be numeric."
                    )
                    continue
                
                # Check for negative values
                if (numeric_col < 0).any():
                    negative_count = (numeric_col < 0).sum()
                    errors.append(
                        f"Column '{col}' contains {negative_count} negative values. "
                        f"Spend values must be non-negative."
                    )
            except Exception as e:
                errors.append(f"Error validating column '{col}': {str(e)}")
        
        # Check new_customers column
        if 'new_customers' in df.columns:
            try:
                numeric_col = pd.to_numeric(df['new_customers'], errors='coerce')
                if numeric_col.isnull().any():
                    errors.append(
                        "Column 'new_customers' contains non-numeric values. "
                        "Customer counts must be numeric."
                    )
                elif (numeric_col < 0).any():
                    errors.append(
                        "Column 'new_customers' contains negative values. "
                        "Customer counts must be non-negative."
                    )
            except Exception as e:
                errors.append(f"Error validating 'new_customers' column: {str(e)}")
        
        return errors
    
    def _type_conversion(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert columns to appropriate data types.
        
        Args:
            df: DataFrame to convert
            
        Returns:
            DataFrame with properly typed columns
        """
        df = df.copy()
        
        # Convert date column to datetime
        df['week_start_date'] = pd.to_datetime(df['week_start_date'])
        
        # Convert spend channels to float64
        for col in self.SPEND_CHANNELS:
            if col in df.columns:
                df[col] = df[col].astype('float64')
        
        # Convert control variables to int64
        for col in self.CONTROL_VARIABLES:
            if col in df.columns:
                df[col] = df[col].astype('int64')
        
        # Convert new_customers to int64
        if 'new_customers' in df.columns:
            df['new_customers'] = df['new_customers'].astype('int64')
        
        # Set date as index
        df = df.set_index('week_start_date')
        
        return df
