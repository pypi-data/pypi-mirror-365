"""
Plotting utilities for time series forecasting.

This module provides various plotting functions for visualizing
forecasts, model performance, and diagnostic plots.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import Optional, Dict, Any, Tuple, Union
import warnings


def plot_forecast(df_train: pd.DataFrame,
                 df_forecast: pd.DataFrame,
                 date_col: str = 'date',
                 target_col: str = 'sales',
                 forecast_col: str = 'yhat',
                 lower_col: Optional[str] = 'yhat_lower',
                 upper_col: Optional[str] = 'yhat_upper',
                 title: Optional[str] = None,
                 figsize: Tuple[int, int] = (12, 6)) -> plt.Figure:
    """
    Plot time series forecast with confidence intervals.
    
    Parameters:
    -----------
    df_train : pd.DataFrame
        Training data with historical values
    df_forecast : pd.DataFrame
        Forecast data with predictions
    date_col : str, default='date'
        Name of the date column
    target_col : str, default='sales'
        Name of the target column in training data
    forecast_col : str, default='yhat'
        Name of the forecast column
    lower_col : str, optional
        Name of the lower confidence bound column
    upper_col : str, optional
        Name of the upper confidence bound column
    title : str, optional
        Custom title for the plot
    figsize : tuple, default=(12, 6)
        Figure size
        
    Returns:
    --------
    plt.Figure
        The generated figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot historical data
    ax.plot(df_train[date_col], df_train[target_col], 
           label='Historical', color='blue', linewidth=1.5)
    
    # Plot forecast
    ax.plot(df_forecast[date_col], df_forecast[forecast_col], 
           label='Forecast', color='orange', linewidth=2)
    
    # Plot confidence intervals if available
    if (lower_col and upper_col and 
        lower_col in df_forecast.columns and upper_col in df_forecast.columns):
        ax.fill_between(df_forecast[date_col],
                       df_forecast[lower_col],
                       df_forecast[upper_col],
                       color='orange', alpha=0.2, label='Confidence Interval')
    
    # Add vertical line at forecast start
    if len(df_train) > 0:
        forecast_start = df_train[date_col].max()
        ax.axvline(x=forecast_start, color='red', linestyle='--', 
                  alpha=0.7, label='Forecast Start')
    
    # Formatting
    ax.legend()
    ax.set_xlabel('Date')
    ax.set_ylabel(target_col.title())
    
    if title is None:
        title = 'Time Series Forecast'
    ax.set_title(title)
    
    ax.grid(True, alpha=0.3)
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    return fig


def plot_residuals(y_true: Union[np.ndarray, pd.Series],
                  y_pred: Union[np.ndarray, pd.Series],
                  dates: Optional[Union[np.ndarray, pd.Series]] = None,
                  figsize: Tuple[int, int] = (15, 8)) -> plt.Figure:
    """
    Plot residual analysis for model diagnostics.
    
    Parameters:
    -----------
    y_true : array-like
        True values
    y_pred : array-like
        Predicted values
    dates : array-like, optional
        Date values for time series plot
    figsize : tuple, default=(15, 8)
        Figure size
        
    Returns:
    --------
    plt.Figure
        The generated figure
    """
    # Calculate residuals
    residuals = np.asarray(y_true) - np.asarray(y_pred)
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    
    # Residuals vs Fitted
    axes[0, 0].scatter(y_pred, residuals, alpha=0.6)
    axes[0, 0].axhline(y=0, color='red', linestyle='--')
    axes[0, 0].set_xlabel('Fitted Values')
    axes[0, 0].set_ylabel('Residuals')
    axes[0, 0].set_title('Residuals vs Fitted')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Residuals histogram
    axes[0, 1].hist(residuals, bins=30, density=True, alpha=0.7, color='skyblue')
    axes[0, 1].set_xlabel('Residuals')
    axes[0, 1].set_ylabel('Density')
    axes[0, 1].set_title('Residuals Distribution')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Add normal curve overlay
    try:
        from scipy.stats import norm
        mu, sigma = np.mean(residuals), np.std(residuals)
        x = np.linspace(residuals.min(), residuals.max(), 100)
        axes[0, 1].plot(x, norm.pdf(x, mu, sigma), 'r-', label='Normal')
        axes[0, 1].legend()
    except ImportError:
        pass
    
    # Time series plot of residuals (if dates provided)
    if dates is not None:
        axes[1, 0].plot(dates, residuals, alpha=0.7)
        axes[1, 0].axhline(y=0, color='red', linestyle='--')
        axes[1, 0].set_xlabel('Date')
        axes[1, 0].set_ylabel('Residuals')
        axes[1, 0].set_title('Residuals Over Time')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Format dates if they are datetime
        if hasattr(dates, 'dtype') and np.issubdtype(dates.dtype, np.datetime64):
            axes[1, 0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            plt.setp(axes[1, 0].xaxis.get_majorticklabels(), rotation=45)
    else:
        axes[1, 0].plot(residuals, alpha=0.7)
        axes[1, 0].axhline(y=0, color='red', linestyle='--')
        axes[1, 0].set_xlabel('Observation')
        axes[1, 0].set_ylabel('Residuals')
        axes[1, 0].set_title('Residuals Over Observations')
        axes[1, 0].grid(True, alpha=0.3)
    
    # Q-Q plot
    try:
        from scipy.stats import probplot
        probplot(residuals, dist="norm", plot=axes[1, 1])
        axes[1, 1].set_title('Q-Q Plot')
        axes[1, 1].grid(True, alpha=0.3)
    except ImportError:
        # Simple Q-Q plot without scipy
        sorted_residuals = np.sort(residuals)
        n = len(sorted_residuals)
        theoretical_quantiles = np.linspace(0.01, 0.99, n)
        
        # Approximate normal quantiles
        normal_quantiles = np.array([
            -2.33 + (4.66 * q) for q in theoretical_quantiles
        ])
        
        axes[1, 1].scatter(normal_quantiles, sorted_residuals, alpha=0.6)
        axes[1, 1].plot(normal_quantiles, normal_quantiles, 'r--', label='Perfect Normal')
        axes[1, 1].set_xlabel('Theoretical Quantiles')
        axes[1, 1].set_ylabel('Sample Quantiles')
        axes[1, 1].set_title('Q-Q Plot (Approximate)')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_actual_vs_predicted(y_true: Union[np.ndarray, pd.Series],
                            y_pred: Union[np.ndarray, pd.Series],
                            title: Optional[str] = None,
                            figsize: Tuple[int, int] = (8, 8)) -> plt.Figure:
    """
    Plot actual vs predicted values.
    
    Parameters:
    -----------
    y_true : array-like
        True values
    y_pred : array-like
        Predicted values
    title : str, optional
        Custom title for the plot
    figsize : tuple, default=(8, 8)
        Figure size
        
    Returns:
    --------
    plt.Figure
        The generated figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Convert to numpy arrays
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    
    # Remove NaN values
    mask = ~(np.isnan(y_true) | np.isnan(y_pred))
    y_true_clean = y_true[mask]
    y_pred_clean = y_pred[mask]
    
    # Scatter plot
    ax.scatter(y_true_clean, y_pred_clean, alpha=0.6, s=50)
    
    # Perfect prediction line
    min_val = min(y_true_clean.min(), y_pred_clean.min())
    max_val = max(y_true_clean.max(), y_pred_clean.max())
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', 
           label='Perfect Prediction', linewidth=2)
    
    # Calculate R²
    try:
        from sklearn.metrics import r2_score
        r2 = r2_score(y_true_clean, y_pred_clean)
        ax.text(0.05, 0.95, f'R² = {r2:.3f}', transform=ax.transAxes, 
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    except ImportError:
        # Manual R² calculation
        ss_res = np.sum((y_true_clean - y_pred_clean) ** 2)
        ss_tot = np.sum((y_true_clean - np.mean(y_true_clean)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        ax.text(0.05, 0.95, f'R² = {r2:.3f}', transform=ax.transAxes, 
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    ax.set_xlabel('Actual Values')
    ax.set_ylabel('Predicted Values')
    
    if title is None:
        title = 'Actual vs Predicted Values'
    ax.set_title(title)
    
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Make axes equal
    ax.set_aspect('equal', adjustable='box')
    
    plt.tight_layout()
    return fig


def plot_feature_importance(importance_df: pd.DataFrame,
                           top_n: int = 15,
                           title: Optional[str] = None,
                           figsize: Tuple[int, int] = (10, 8)) -> plt.Figure:
    """
    Plot feature importance.
    
    Parameters:
    -----------
    importance_df : pd.DataFrame
        DataFrame with 'feature' and 'importance' columns
    top_n : int, default=15
        Number of top features to display
    title : str, optional
        Custom title for the plot
    figsize : tuple, default=(10, 8)
        Figure size
        
    Returns:
    --------
    plt.Figure
        The generated figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Get top N features
    top_features = importance_df.head(top_n).copy()
    top_features = top_features.sort_values('importance')
    
    # Create horizontal bar plot
    bars = ax.barh(range(len(top_features)), top_features['importance'], 
                  color='steelblue', alpha=0.7)
    
    ax.set_yticks(range(len(top_features)))
    ax.set_yticklabels(top_features['feature'])
    ax.set_xlabel('Importance Score')
    
    if title is None:
        title = f'Top {top_n} Feature Importances'
    ax.set_title(title)
    
    # Add value labels on bars
    for i, (bar, importance) in enumerate(zip(bars, top_features['importance'])):
        ax.text(bar.get_width() + 0.001, bar.get_y() + bar.get_height()/2, 
               f'{importance:.3f}', va='center', fontsize=9)
    
    ax.grid(True, alpha=0.3, axis='x')
    plt.tight_layout()
    return fig


def plot_seasonal_decomposition(ts_data: pd.Series,
                               period: int = 12,
                               figsize: Tuple[int, int] = (15, 10)) -> plt.Figure:
    """
    Plot seasonal decomposition of time series.
    
    Parameters:
    -----------
    ts_data : pd.Series
        Time series data with datetime index
    period : int, default=12
        Seasonal period
    figsize : tuple, default=(15, 10)
        Figure size
        
    Returns:
    --------
    plt.Figure
        The generated figure
    """
    try:
        from statsmodels.tsa.seasonal import seasonal_decompose
        
        # Perform decomposition
        decomposition = seasonal_decompose(
            ts_data, 
            model='additive', 
            period=min(period, len(ts_data) // 2)
        )
        
        fig, axes = plt.subplots(4, 1, figsize=figsize)
        
        # Original
        axes[0].plot(decomposition.observed, color='blue')
        axes[0].set_title('Original Time Series')
        axes[0].grid(True, alpha=0.3)
        
        # Trend
        axes[1].plot(decomposition.trend, color='green')
        axes[1].set_title('Trend')
        axes[1].grid(True, alpha=0.3)
        
        # Seasonal
        axes[2].plot(decomposition.seasonal, color='orange')
        axes[2].set_title('Seasonal')
        axes[2].grid(True, alpha=0.3)
        
        # Residual
        axes[3].plot(decomposition.resid, color='red')
        axes[3].set_title('Residual')
        axes[3].grid(True, alpha=0.3)
        
        # Format x-axis
        for ax in axes:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        return fig
        
    except ImportError:
        warnings.warn("statsmodels not available for seasonal decomposition")
        return None


def plot_multiple_forecasts(df_train: pd.DataFrame,
                           forecasts_dict: Dict[str, pd.DataFrame],
                           date_col: str = 'date',
                           target_col: str = 'sales',
                           forecast_col: str = 'yhat',
                           title: Optional[str] = None,
                           figsize: Tuple[int, int] = (15, 8)) -> plt.Figure:
    """
    Plot multiple forecasts for comparison.
    
    Parameters:
    -----------
    df_train : pd.DataFrame
        Training data with historical values
    forecasts_dict : dict
        Dictionary mapping model names to forecast DataFrames
    date_col : str, default='date'
        Name of the date column
    target_col : str, default='sales'
        Name of the target column
    forecast_col : str, default='yhat'
        Name of the forecast column
    title : str, optional
        Custom title for the plot
    figsize : tuple, default=(15, 8)
        Figure size
        
    Returns:
    --------
    plt.Figure
        The generated figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot historical data
    ax.plot(df_train[date_col], df_train[target_col], 
           label='Historical', color='blue', linewidth=1.5)
    
    # Color palette for forecasts
    colors = ['orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive']
    
    # Plot each forecast
    for i, (model_name, forecast_df) in enumerate(forecasts_dict.items()):
        color = colors[i % len(colors)]
        ax.plot(forecast_df[date_col], forecast_df[forecast_col], 
               label=f'{model_name} Forecast', color=color, linewidth=2)
    
    # Add vertical line at forecast start
    if len(df_train) > 0:
        forecast_start = df_train[date_col].max()
        ax.axvline(x=forecast_start, color='black', linestyle='--', 
                  alpha=0.5, label='Forecast Start')
    
    # Formatting
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.set_xlabel('Date')
    ax.set_ylabel(target_col.title())
    
    if title is None:
        title = 'Model Comparison - Multiple Forecasts'
    ax.set_title(title)
    
    ax.grid(True, alpha=0.3)
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    return fig


def save_plot(fig: plt.Figure, filepath: str, dpi: int = 300, **kwargs):
    """
    Save a matplotlib figure to file.
    
    Parameters:
    -----------
    fig : plt.Figure
        Figure to save
    filepath : str
        Path to save the figure
    dpi : int, default=300
        Resolution for saved figure
    **kwargs : dict
        Additional arguments for savefig
    """
    fig.savefig(filepath, dpi=dpi, bbox_inches='tight', **kwargs)
    print(f"Plot saved to: {filepath}")
