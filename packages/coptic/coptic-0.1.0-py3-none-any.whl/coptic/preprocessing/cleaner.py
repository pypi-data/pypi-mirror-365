"""
Data cleaning and preprocessing utilities for time series data.

This module provides the DataCleaner class for handling common data
quality issues in time series datasets.
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
import warnings


class DataCleaner:
    """
    Data cleaning and preprocessing utilities for time series data.
    
    This class provides methods to handle common data quality issues including:
    - Missing values
    - Outliers
    - Duplicate timestamps
    - Data type conversions
    - Frequency standardization
    
    Attributes:
        remove_outliers (bool): Whether to remove outliers
        outlier_method (str): Method for outlier detection
        fill_method (str): Method for filling missing values
        interpolation_method (str): Interpolation method for missing values
    """
    
    def __init__(self, 
                 remove_outliers: bool = False,
                 outlier_method: str = 'iqr',
                 fill_method: str = 'interpolate',
                 interpolation_method: str = 'linear'):
        """
        Initialize the data cleaner.
        
        Parameters:
        -----------
        remove_outliers : bool, default=False
            Whether to remove outlier values
        outlier_method : str, default='iqr'
            Method for outlier detection ('iqr', 'zscore', 'isolation_forest')
        fill_method : str, default='interpolate'
            Method for filling missing values ('interpolate', 'forward_fill', 'backward_fill', 'mean')
        interpolation_method : str, default='linear'
            Interpolation method ('linear', 'polynomial', 'spline')
        """
        self.remove_outliers = remove_outliers
        self.outlier_method = outlier_method
        self.fill_method = fill_method
        self.interpolation_method = interpolation_method
    
    def clean(self, df: pd.DataFrame, 
              date_col: str, 
              target_col: str,
              freq: Optional[str] = None) -> pd.DataFrame:
        """
        Perform comprehensive data cleaning.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Input dataframe
        date_col : str
            Name of the date column
        target_col : str
            Name of the target column
        freq : str, optional
            Target frequency for resampling
            
        Returns:
        --------
        pd.DataFrame
            Cleaned dataframe
        """
        df_clean = df.copy()
        
        # Convert date column to datetime
        df_clean = self._convert_datetime(df_clean, date_col)
        
        # Remove duplicate timestamps
        df_clean = self._remove_duplicates(df_clean, date_col)
        
        # Sort by date
        df_clean = df_clean.sort_values(date_col).reset_index(drop=True)
        
        # Handle missing values in target
        df_clean = self._handle_missing_values(df_clean, target_col)
        
        # Remove outliers if requested
        if self.remove_outliers:
            df_clean = self._remove_outliers_from_data(df_clean, target_col)
        
        # Standardize frequency if requested
        if freq is not None:
            df_clean = self._standardize_frequency(df_clean, date_col, target_col, freq)
        
        return df_clean
    
    def _convert_datetime(self, df: pd.DataFrame, date_col: str) -> pd.DataFrame:
        """Convert date column to datetime type."""
        try:
            df[date_col] = pd.to_datetime(df[date_col])
        except Exception as e:
            raise ValueError(f"Could not convert '{date_col}' to datetime: {e}")
        
        return df
    
    def _remove_duplicates(self, df: pd.DataFrame, date_col: str) -> pd.DataFrame:
        """Remove duplicate timestamps, keeping the first occurrence."""
        initial_count = len(df)
        df_clean = df.drop_duplicates(subset=[date_col], keep='first')
        
        removed_count = initial_count - len(df_clean)
        if removed_count > 0:
            warnings.warn(f"Removed {removed_count} duplicate timestamps")
        
        return df_clean
    
    def _handle_missing_values(self, df: pd.DataFrame, target_col: str) -> pd.DataFrame:
        """Handle missing values in the target column."""
        missing_count = df[target_col].isnull().sum()
        
        if missing_count == 0:
            return df
        
        warnings.warn(f"Found {missing_count} missing values in '{target_col}'")
        
        if self.fill_method == 'interpolate':
            df[target_col] = df[target_col].interpolate(method=self.interpolation_method)
        elif self.fill_method == 'forward_fill':
            df[target_col] = df[target_col].ffill()
        elif self.fill_method == 'backward_fill':
            df[target_col] = df[target_col].bfill()
        elif self.fill_method == 'mean':
            df[target_col] = df[target_col].fillna(df[target_col].mean())
        else:
            raise ValueError(f"Unknown fill method: {self.fill_method}")
        
        # If still missing values, forward fill then backward fill
        df[target_col] = df[target_col].ffill().bfill()
        
        return df
    
    def _remove_outliers_from_data(self, df: pd.DataFrame, target_col: str) -> pd.DataFrame:
        """Remove outliers from the target column."""
        initial_count = len(df)
        
        if self.outlier_method == 'iqr':
            df_clean = self._remove_outliers_iqr(df, target_col)
        elif self.outlier_method == 'zscore':
            df_clean = self._remove_outliers_zscore(df, target_col)
        elif self.outlier_method == 'isolation_forest':
            df_clean = self._remove_outliers_isolation_forest(df, target_col)
        else:
            raise ValueError(f"Unknown outlier method: {self.outlier_method}")
        
        removed_count = initial_count - len(df_clean)
        if removed_count > 0:
            warnings.warn(f"Removed {removed_count} outliers using {self.outlier_method} method")
        
        return df_clean
    
    def _remove_outliers_iqr(self, df: pd.DataFrame, target_col: str) -> pd.DataFrame:
        """Remove outliers using Interquartile Range method."""
        Q1 = df[target_col].quantile(0.25)
        Q3 = df[target_col].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        return df[(df[target_col] >= lower_bound) & (df[target_col] <= upper_bound)]
    
    def _remove_outliers_zscore(self, df: pd.DataFrame, target_col: str, threshold: float = 3.0) -> pd.DataFrame:
        """Remove outliers using Z-score method."""
        z_scores = np.abs((df[target_col] - df[target_col].mean()) / df[target_col].std())
        return df[z_scores < threshold]
    
    def _remove_outliers_isolation_forest(self, df: pd.DataFrame, target_col: str) -> pd.DataFrame:
        """Remove outliers using Isolation Forest."""
        try:
            from sklearn.ensemble import IsolationForest
            
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            outliers = iso_forest.fit_predict(df[[target_col]])
            
            return df[outliers == 1]
        except ImportError:
            warnings.warn("scikit-learn not available, falling back to IQR method")
            return self._remove_outliers_iqr(df, target_col)
    
    def _standardize_frequency(self, df: pd.DataFrame, 
                              date_col: str, 
                              target_col: str, 
                              freq: str) -> pd.DataFrame:
        """Standardize the frequency of the time series."""
        df = df.set_index(date_col)
        
        # Create a complete date range
        full_range = pd.date_range(
            start=df.index.min(),
            end=df.index.max(),
            freq=freq
        )
        
        # Reindex to the full range
        df_reindexed = df.reindex(full_range)
        
        # Interpolate missing values
        df_reindexed[target_col] = df_reindexed[target_col].interpolate(method='linear')
        
        # Reset index
        df_reindexed = df_reindexed.reset_index()
        df_reindexed = df_reindexed.rename(columns={'index': date_col})
        
        return df_reindexed
    
    def detect_outliers(self, df: pd.DataFrame, target_col: str) -> Dict[str, Any]:
        """
        Detect outliers in the target column and return statistics.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Input dataframe
        target_col : str
            Name of the target column
            
        Returns:
        --------
        dict
            Dictionary containing outlier statistics and indices
        """
        results = {}
        
        # IQR method
        Q1 = df[target_col].quantile(0.25)
        Q3 = df[target_col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        iqr_outliers = df[(df[target_col] < lower_bound) | (df[target_col] > upper_bound)].index
        
        # Z-score method
        z_scores = np.abs((df[target_col] - df[target_col].mean()) / df[target_col].std())
        zscore_outliers = df[z_scores > 3].index
        
        results = {
            'iqr_outliers': {
                'count': len(iqr_outliers),
                'indices': iqr_outliers.tolist(),
                'lower_bound': lower_bound,
                'upper_bound': upper_bound
            },
            'zscore_outliers': {
                'count': len(zscore_outliers),
                'indices': zscore_outliers.tolist(),
                'threshold': 3.0
            },
            'statistics': {
                'mean': df[target_col].mean(),
                'std': df[target_col].std(),
                'min': df[target_col].min(),
                'max': df[target_col].max(),
                'Q1': Q1,
                'Q3': Q3,
                'IQR': IQR
            }
        }
        
        return results
    
    def get_data_quality_report(self, df: pd.DataFrame, 
                               date_col: str, 
                               target_col: str) -> Dict[str, Any]:
        """
        Generate a comprehensive data quality report.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Input dataframe
        date_col : str
            Name of the date column
        target_col : str
            Name of the target column
            
        Returns:
        --------
        dict
            Comprehensive data quality report
        """
        report = {
            'dataset_info': {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'date_range': {
                    'start': df[date_col].min() if pd.api.types.is_datetime64_any_dtype(df[date_col]) else None,
                    'end': df[date_col].max() if pd.api.types.is_datetime64_any_dtype(df[date_col]) else None
                }
            },
            'missing_values': {
                'target_missing': df[target_col].isnull().sum(),
                'target_missing_pct': (df[target_col].isnull().sum() / len(df)) * 100,
                'date_missing': df[date_col].isnull().sum()
            },
            'duplicates': {
                'duplicate_rows': df.duplicated().sum(),
                'duplicate_dates': df[date_col].duplicated().sum() if date_col in df.columns else 0
            },
            'outliers': self.detect_outliers(df, target_col),
            'data_types': df.dtypes.to_dict()
        }
        
        return report
