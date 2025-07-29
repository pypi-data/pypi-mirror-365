"""
Advanced feature engineering for time series forecasting.

This module provides the FeatureGenerator class for creating time-based
features from datetime columns and target variables.
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple, List
from sklearn.preprocessing import StandardScaler
import warnings

try:
    from statsmodels.tsa.seasonal import seasonal_decompose
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False


class FeatureGenerator:
    """
    Advanced feature engineering for time series forecasting.
    
    This class generates various time-based features including:
    - Basic datetime features (year, month, day, etc.)
    - Cyclical encoding for periodic features
    - Lag features
    - Rolling statistics
    - Seasonal decomposition features (if statsmodels is available)
    
    Attributes:
        scale_features (bool): Whether to scale features
        add_lags (bool): Whether to add lag features
        add_seasonality (bool): Whether to add seasonality features
        add_statistics (bool): Whether to add rolling statistics
        scaler (StandardScaler): Scaler for feature normalization
        fitted (bool): Whether the feature generator has been fitted
    """
    
    def __init__(self, 
                 scale_features: bool = True,
                 add_lags: bool = True,
                 add_seasonality: bool = True,
                 add_statistics: bool = True,
                 lag_periods: Optional[List[int]] = None,
                 rolling_windows: Optional[List[int]] = None):
        """
        Initialize the feature generator.
        
        Parameters:
        -----------
        scale_features : bool, default=True
            Whether to standardize features
        add_lags : bool, default=True
            Whether to add lag features
        add_seasonality : bool, default=True
            Whether to add seasonal features
        add_statistics : bool, default=True
            Whether to add rolling statistics
        lag_periods : list of int, optional
            Custom lag periods to use
        rolling_windows : list of int, optional
            Custom rolling window sizes
        """
        self.scale_features = scale_features
        self.add_lags = add_lags
        self.add_seasonality = add_seasonality
        self.add_statistics = add_statistics
        self.scaler = StandardScaler() if scale_features else None
        self.fitted = False
        
        # Default lag periods and rolling windows
        self.lag_periods = lag_periods or [1, 2, 3, 7, 14, 30]
        self.rolling_windows = rolling_windows or [7, 30, 90]
    
    def generate_features(self, 
                         df: pd.DataFrame, 
                         date_col: str, 
                         target_col: Optional[str] = None) -> Tuple[pd.DataFrame, Optional[pd.Series]]:
        """
        Generate advanced time series features.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Input dataframe
        date_col : str
            Name of the datetime column
        target_col : str, optional
            Name of the target column (if None, only features are returned)
            
        Returns:
        --------
        X : pd.DataFrame
            Feature matrix
        y : pd.Series or None
            Target values (if target_col is provided)
        """
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.sort_values(date_col).reset_index(drop=True)
        
        # Initialize features dictionary
        features = {}
        
        # Basic datetime features
        features.update(self._generate_datetime_features(df, date_col))
        
        # Cyclical encoding
        features.update(self._generate_cyclical_features(df, date_col))
        
        # Time since reference
        features.update(self._generate_time_features(df, date_col))
        
        # Target-based features
        y = None
        if target_col is not None:
            y = df[target_col].copy()
            
            if self.add_lags:
                features.update(self._generate_lag_features(df, target_col))
            
            if self.add_statistics:
                features.update(self._generate_statistical_features(df, target_col))
            
            if self.add_seasonality and STATSMODELS_AVAILABLE:
                features.update(self._generate_seasonal_features(df, target_col))
        
        # Create feature dataframe
        X = pd.DataFrame(features, index=df.index)
        
        # Handle missing values
        X = self._handle_missing_values(X, target_col is not None)
        
        # Scale features if requested
        if self.scale_features and X.shape[0] > 0:
            if not self.fitted:
                # Only fit on non-null rows
                valid_mask = X.notna().all(axis=1)
                if valid_mask.sum() > 0:
                    self.scaler.fit(X[valid_mask])
                    self.fitted = True
            
            if self.fitted:
                X_scaled = pd.DataFrame(
                    self.scaler.transform(X), 
                    columns=X.columns, 
                    index=X.index
                )
                X = X_scaled
        
        return X, y
    
    def _generate_datetime_features(self, df: pd.DataFrame, date_col: str) -> dict:
        """Generate basic datetime features."""
        features = {
            'year': df[date_col].dt.year,
            'month': df[date_col].dt.month,
            'day': df[date_col].dt.day,
            'dayofweek': df[date_col].dt.dayofweek,
            'dayofyear': df[date_col].dt.dayofyear,
            'weekofyear': df[date_col].dt.isocalendar().week,
            'quarter': df[date_col].dt.quarter,
            'is_weekend': df[date_col].dt.dayofweek.isin([5, 6]).astype(int),
            'is_month_start': df[date_col].dt.is_month_start.astype(int),
            'is_month_end': df[date_col].dt.is_month_end.astype(int),
            'is_quarter_start': df[date_col].dt.is_quarter_start.astype(int),
            'is_quarter_end': df[date_col].dt.is_quarter_end.astype(int),
            'is_year_start': df[date_col].dt.is_year_start.astype(int),
            'is_year_end': df[date_col].dt.is_year_end.astype(int)
        }
        return features
    
    def _generate_cyclical_features(self, df: pd.DataFrame, date_col: str) -> dict:
        """Generate cyclical encoding for periodic features."""
        features = {}
        
        # Define cyclical periods
        cyclical_mappings = [
            ('month', 12),
            ('dayofweek', 7),
            ('dayofyear', 366),
            ('hour', 24) if df[date_col].dt.hour.nunique() > 1 else None
        ]
        
        for mapping in cyclical_mappings:
            if mapping is None:
                continue
                
            period_name, max_val = mapping
            if period_name == 'hour':
                period_vals = df[date_col].dt.hour
            elif period_name == 'month':
                period_vals = df[date_col].dt.month
            elif period_name == 'dayofweek':
                period_vals = df[date_col].dt.dayofweek
            elif period_name == 'dayofyear':
                period_vals = df[date_col].dt.dayofyear
            else:
                continue
                
            features[f'{period_name}_sin'] = np.sin(2 * np.pi * period_vals / max_val)
            features[f'{period_name}_cos'] = np.cos(2 * np.pi * period_vals / max_val)
        
        return features
    
    def _generate_time_features(self, df: pd.DataFrame, date_col: str) -> dict:
        """Generate time-based features."""
        ref_date = df[date_col].min()
        features = {
            'days_since_start': (df[date_col] - ref_date).dt.days,
            'weeks_since_start': (df[date_col] - ref_date).dt.days // 7,
            'months_since_start': ((df[date_col].dt.year - ref_date.year) * 12 + 
                                 df[date_col].dt.month - ref_date.month)
        }
        return features
    
    def _generate_lag_features(self, df: pd.DataFrame, target_col: str) -> dict:
        """Generate lag features."""
        features = {}
        target_series = df[target_col]
        
        for lag in self.lag_periods:
            features[f'lag_{lag}'] = target_series.shift(lag)
            
            # Lag differences
            if lag == 1:
                features['diff_1'] = target_series.diff(1)
            elif lag == 7:
                features['diff_7'] = target_series.diff(7)
        
        return features
    
    def _generate_statistical_features(self, df: pd.DataFrame, target_col: str) -> dict:
        """Generate rolling statistical features."""
        features = {}
        target_series = df[target_col]
        
        for window in self.rolling_windows:
            rolling = target_series.rolling(window, min_periods=1)
            
            features[f'rolling_mean_{window}'] = rolling.mean()
            features[f'rolling_std_{window}'] = rolling.std()
            features[f'rolling_min_{window}'] = rolling.min()
            features[f'rolling_max_{window}'] = rolling.max()
            features[f'rolling_median_{window}'] = rolling.median()
            
            # Rolling ratios
            features[f'ratio_to_mean_{window}'] = (
                target_series / rolling.mean()
            )
            
            # Expanding features for long windows
            if window >= 30:
                expanding = target_series.expanding(min_periods=1)
                features[f'expanding_mean_{window}'] = expanding.mean()
                features[f'expanding_std_{window}'] = expanding.std()
        
        return features
    
    def _generate_seasonal_features(self, df: pd.DataFrame, target_col: str) -> dict:
        """Generate seasonal decomposition features."""
        if not STATSMODELS_AVAILABLE:
            warnings.warn("statsmodels not available, skipping seasonal features")
            return {}
        
        features = {}
        target_series = df[target_col]
        
        try:
            # Only decompose if we have enough data
            if len(target_series) >= 24:  # Minimum for seasonal decomposition
                decomposition = seasonal_decompose(
                    target_series.dropna(), 
                    model='additive', 
                    period=min(12, len(target_series) // 2),
                    extrapolate_trend='freq'
                )
                
                # Align decomposition with original index
                trend_aligned = pd.Series(index=df.index, dtype=float)
                seasonal_aligned = pd.Series(index=df.index, dtype=float)
                
                valid_idx = target_series.dropna().index
                trend_aligned.loc[valid_idx] = decomposition.trend
                seasonal_aligned.loc[valid_idx] = decomposition.seasonal
                
                features['trend'] = trend_aligned
                features['seasonal'] = seasonal_aligned
                
        except Exception as e:
            warnings.warn(f"Seasonal decomposition failed: {e}")
        
        return features
    
    def _handle_missing_values(self, X: pd.DataFrame, has_target: bool) -> pd.DataFrame:
        """Handle missing values in features."""
        # For lag features, forward fill
        lag_cols = [col for col in X.columns if col.startswith('lag_') or col.startswith('diff_')]
        for col in lag_cols:
            X[col] = X[col].fillna(method='ffill')
        
        # For rolling features, use forward fill then backward fill
        rolling_cols = [col for col in X.columns if 'rolling_' in col or 'expanding_' in col]
        for col in rolling_cols:
            X[col] = X[col].fillna(method='ffill').fillna(method='bfill')
        
        # For other features, fill with appropriate values
        for col in X.columns:
            if col not in lag_cols + rolling_cols:
                if X[col].dtype in ['float64', 'int64']:
                    X[col] = X[col].fillna(X[col].median())
                else:
                    X[col] = X[col].fillna(X[col].mode().iloc[0] if not X[col].mode().empty else 0)
        
        # If we still have NaN values, fill with 0
        X = X.fillna(0)
        
        return X
    
    def fit_transform(self, df: pd.DataFrame, date_col: str, target_col: str) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Fit the feature generator and transform the data.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Input dataframe
        date_col : str
            Name of the datetime column
        target_col : str
            Name of the target column
            
        Returns:
        --------
        X : pd.DataFrame
            Feature matrix
        y : pd.Series
            Target values
        """
        return self.generate_features(df, date_col, target_col)
    
    def transform(self, df: pd.DataFrame, date_col: str) -> pd.DataFrame:
        """
        Transform new data using fitted feature generator.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Input dataframe
        date_col : str
            Name of the datetime column
            
        Returns:
        --------
        X : pd.DataFrame
            Feature matrix
        """
        X, _ = self.generate_features(df, date_col, None)
        return X
