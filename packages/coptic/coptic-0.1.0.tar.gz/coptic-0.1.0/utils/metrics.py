"""
Evaluation metrics for time series forecasting.

This module provides various metrics to evaluate forecasting performance
including accuracy, error, and statistical measures.
"""

import numpy as np
import pandas as pd
from typing import Dict, Union, Optional
import warnings


def calculate_metrics(y_true: Union[np.ndarray, pd.Series], 
                     y_pred: Union[np.ndarray, pd.Series]) -> Dict[str, float]:
    """
    Calculate comprehensive forecasting metrics.
    
    Parameters:
    -----------
    y_true : array-like
        True values
    y_pred : array-like
        Predicted values
        
    Returns:
    --------
    dict
        Dictionary containing various metrics
    """
    # Convert to numpy arrays
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    
    # Remove any NaN values
    mask = ~(np.isnan(y_true) | np.isnan(y_pred))
    y_true_clean = y_true[mask]
    y_pred_clean = y_pred[mask]
    
    if len(y_true_clean) == 0:
        warnings.warn("No valid observations found after removing NaN values")
        return {}
    
    # Calculate errors
    errors = y_true_clean - y_pred_clean
    abs_errors = np.abs(errors)
    squared_errors = errors ** 2
    
    # Basic metrics
    n = len(y_true_clean)
    mae = np.mean(abs_errors)
    mse = np.mean(squared_errors)
    rmse = np.sqrt(mse)
    
    # Mean Absolute Percentage Error
    mask_nonzero = y_true_clean != 0
    if np.any(mask_nonzero):
        mape = np.mean(np.abs(errors[mask_nonzero] / y_true_clean[mask_nonzero]) * 100)
    else:
        mape = np.inf
    
    # Symmetric Mean Absolute Percentage Error
    denominator = (np.abs(y_true_clean) + np.abs(y_pred_clean)) / 2
    mask_smape = denominator != 0
    if np.any(mask_smape):
        smape = np.mean(np.abs(errors[mask_smape] / denominator[mask_smape]) * 100)
    else:
        smape = np.inf
    
    # Mean Absolute Scaled Error (MASE)
    # Requires seasonal naive forecast for scaling
    if len(y_true_clean) > 1:
        seasonal_errors = np.abs(np.diff(y_true_clean))
        scale = np.mean(seasonal_errors)
        mase = mae / scale if scale != 0 else np.inf
    else:
        mase = np.inf
    
    # R-squared
    ss_res = np.sum(squared_errors)
    ss_tot = np.sum((y_true_clean - np.mean(y_true_clean)) ** 2)
    r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
    
    # Adjusted R-squared (assuming 1 predictor for simplicity)
    adj_r2 = 1 - ((1 - r2) * (n - 1) / (n - 2)) if n > 2 else r2
    
    # Mean Error (bias)
    me = np.mean(errors)
    
    # Mean Percentage Error
    if np.any(mask_nonzero):
        mpe = np.mean(errors[mask_nonzero] / y_true_clean[mask_nonzero] * 100)
    else:
        mpe = 0
    
    # Theil's U statistic
    if len(y_true_clean) > 1:
        u1_num = np.sqrt(np.mean(squared_errors))
        u1_den = np.sqrt(np.mean(y_true_clean ** 2)) + np.sqrt(np.mean(y_pred_clean ** 2))
        theil_u1 = u1_num / u1_den if u1_den != 0 else np.inf
        
        # Theil's U2 (requires lagged values)
        naive_forecast = np.roll(y_true_clean, 1)[1:]  # Simple lag-1 naive forecast
        naive_errors = (y_true_clean[1:] - naive_forecast) ** 2
        u2_num = np.mean(squared_errors[1:])
        u2_den = np.mean(naive_errors)
        theil_u2 = u2_num / u2_den if u2_den != 0 else np.inf
    else:
        theil_u1 = np.inf
        theil_u2 = np.inf
    
    # Directional accuracy
    if len(y_true_clean) > 1:
        true_direction = np.diff(y_true_clean) > 0
        pred_direction = np.diff(y_pred_clean) > 0
        directional_accuracy = np.mean(true_direction == pred_direction) * 100
    else:
        directional_accuracy = np.nan
    
    metrics = {
        'mae': mae,
        'mse': mse,
        'rmse': rmse,
        'mape': mape,
        'smape': smape,
        'mase': mase,
        'r2': r2,
        'adj_r2': adj_r2,
        'me': me,
        'mpe': mpe,
        'theil_u1': theil_u1,
        'theil_u2': theil_u2,
        'directional_accuracy': directional_accuracy,
        'n_observations': n
    }
    
    return metrics


def calculate_residual_stats(y_true: Union[np.ndarray, pd.Series], 
                           y_pred: Union[np.ndarray, pd.Series]) -> Dict[str, float]:
    """
    Calculate residual statistics for model diagnostics.
    
    Parameters:
    -----------
    y_true : array-like
        True values
    y_pred : array-like
        Predicted values
        
    Returns:
    --------
    dict
        Dictionary containing residual statistics
    """
    # Convert to numpy arrays
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    
    # Calculate residuals
    residuals = y_true - y_pred
    residuals = residuals[~np.isnan(residuals)]
    
    if len(residuals) == 0:
        return {}
    
    stats = {
        'residual_mean': np.mean(residuals),
        'residual_std': np.std(residuals),
        'residual_min': np.min(residuals),
        'residual_max': np.max(residuals),
        'residual_skewness': _calculate_skewness(residuals),
        'residual_kurtosis': _calculate_kurtosis(residuals),
        'ljung_box_p': _ljung_box_test(residuals),
        'jarque_bera_p': _jarque_bera_test(residuals)
    }
    
    return stats


def _calculate_skewness(data: np.ndarray) -> float:
    """Calculate skewness of data."""
    try:
        from scipy.stats import skew
        return skew(data)
    except ImportError:
        # Manual calculation
        n = len(data)
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        if std == 0:
            return 0
        skewness = (n / ((n - 1) * (n - 2))) * np.sum(((data - mean) / std) ** 3)
        return skewness


def _calculate_kurtosis(data: np.ndarray) -> float:
    """Calculate kurtosis of data."""
    try:
        from scipy.stats import kurtosis
        return kurtosis(data)
    except ImportError:
        # Manual calculation
        n = len(data)
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        if std == 0:
            return 0
        kurt = (n * (n + 1) / ((n - 1) * (n - 2) * (n - 3))) * \
               np.sum(((data - mean) / std) ** 4) - \
               (3 * (n - 1) ** 2) / ((n - 2) * (n - 3))
        return kurt


def _ljung_box_test(residuals: np.ndarray, lags: int = 10) -> float:
    """Ljung-Box test for autocorrelation in residuals."""
    try:
        from statsmodels.stats.diagnostic import acorr_ljungbox
        result = acorr_ljungbox(residuals, lags=lags, return_df=False)
        return result[1][-1]  # p-value for the last lag
    except ImportError:
        warnings.warn("statsmodels not available, skipping Ljung-Box test")
        return np.nan


def _jarque_bera_test(residuals: np.ndarray) -> float:
    """Jarque-Bera test for normality of residuals."""
    try:
        from scipy.stats import jarque_bera
        _, p_value = jarque_bera(residuals)
        return p_value
    except ImportError:
        warnings.warn("scipy not available, skipping Jarque-Bera test")
        return np.nan


def calculate_prediction_intervals(y_pred: Union[np.ndarray, pd.Series],
                                 residuals: Union[np.ndarray, pd.Series],
                                 confidence_level: float = 0.95) -> Dict[str, np.ndarray]:
    """
    Calculate prediction intervals using residual distribution.
    
    Parameters:
    -----------
    y_pred : array-like
        Predicted values
    residuals : array-like
        Model residuals from training
    confidence_level : float, default=0.95
        Confidence level for intervals
        
    Returns:
    --------
    dict
        Dictionary with lower and upper bounds
    """
    alpha = 1 - confidence_level
    
    # Convert to numpy arrays
    y_pred = np.asarray(y_pred)
    residuals = np.asarray(residuals)
    residuals = residuals[~np.isnan(residuals)]
    
    if len(residuals) == 0:
        warnings.warn("No valid residuals found")
        return {
            'lower': np.full_like(y_pred, np.nan),
            'upper': np.full_like(y_pred, np.nan)
        }
    
    # Calculate standard error
    std_residual = np.std(residuals)
    
    try:
        from scipy.stats import norm
        z_score = norm.ppf(1 - alpha/2)
    except ImportError:
        # Approximate z-score for 95% confidence
        z_score = 1.96 if confidence_level == 0.95 else 2.576
    
    margin_of_error = z_score * std_residual
    
    return {
        'lower': y_pred - margin_of_error,
        'upper': y_pred + margin_of_error
    }


def forecast_accuracy_summary(metrics: Dict[str, float]) -> str:
    """
    Generate a human-readable summary of forecast accuracy.
    
    Parameters:
    -----------
    metrics : dict
        Dictionary of calculated metrics
        
    Returns:
    --------
    str
        Formatted summary string
    """
    if not metrics:
        return "No metrics available"
    
    summary_lines = ["Forecast Accuracy Summary", "=" * 30]
    
    # Primary metrics
    if 'mae' in metrics:
        summary_lines.append(f"Mean Absolute Error (MAE): {metrics['mae']:.4f}")
    if 'rmse' in metrics:
        summary_lines.append(f"Root Mean Square Error (RMSE): {metrics['rmse']:.4f}")
    if 'mape' in metrics and not np.isinf(metrics['mape']):
        summary_lines.append(f"Mean Absolute Percentage Error (MAPE): {metrics['mape']:.2f}%")
    if 'r2' in metrics:
        summary_lines.append(f"R-squared: {metrics['r2']:.4f}")
    
    # Additional metrics
    summary_lines.append("")
    summary_lines.append("Additional Metrics:")
    
    if 'smape' in metrics and not np.isinf(metrics['smape']):
        summary_lines.append(f"  SMAPE: {metrics['smape']:.2f}%")
    if 'mase' in metrics and not np.isinf(metrics['mase']):
        summary_lines.append(f"  MASE: {metrics['mase']:.4f}")
    if 'directional_accuracy' in metrics and not np.isnan(metrics['directional_accuracy']):
        summary_lines.append(f"  Directional Accuracy: {metrics['directional_accuracy']:.1f}%")
    if 'n_observations' in metrics:
        summary_lines.append(f"  Number of Observations: {int(metrics['n_observations'])}")
    
    # Interpretation
    summary_lines.append("")
    summary_lines.append("Interpretation:")
    
    if 'r2' in metrics:
        r2 = metrics['r2']
        if r2 > 0.9:
            summary_lines.append("  Excellent fit (R² > 0.9)")
        elif r2 > 0.7:
            summary_lines.append("  Good fit (R² > 0.7)")
        elif r2 > 0.5:
            summary_lines.append("  Moderate fit (R² > 0.5)")
        else:
            summary_lines.append("  Poor fit (R² ≤ 0.5)")
    
    if 'mase' in metrics and not np.isinf(metrics['mase']):
        mase = metrics['mase']
        if mase < 1:
            summary_lines.append("  Better than naive forecast (MASE < 1)")
        else:
            summary_lines.append("  Worse than naive forecast (MASE ≥ 1)")
    
    return "\n".join(summary_lines)
