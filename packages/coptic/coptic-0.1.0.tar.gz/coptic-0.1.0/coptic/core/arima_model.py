"""
ARIMA implementation for time series forecasting.

This module provides an auto-ARIMA based forecasting model with
automatic parameter selection and seasonal decomposition.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, Tuple
import matplotlib.pyplot as plt
import warnings

try:
    import pmdarima as pm
    from pmdarima import auto_arima
    PMDARIMA_AVAILABLE = True
except ImportError:
    PMDARIMA_AVAILABLE = False
    warnings.warn("pmdarima not available. Install with: pip install pmdarima")

try:
    import statsmodels.api as sm
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.seasonal import seasonal_decompose
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    warnings.warn("statsmodels not available. Install with: pip install statsmodels")

from .base_model import BaseModel


class ARIMAModel(BaseModel):
    """
    Auto-ARIMA implementation for time series forecasting.
    
    This model uses auto-ARIMA for automatic parameter selection and
    forecasting. It supports seasonal and non-seasonal ARIMA models.
    
    Attributes:
        seasonal (bool): Whether to use seasonal ARIMA
        m (int): Seasonal period
        max_p (int): Maximum AR order
        max_q (int): Maximum MA order
        max_d (int): Maximum differencing order
        model (ARIMA): The fitted ARIMA model
        model_fit: The fitted ARIMA model results
        order (tuple): The ARIMA order (p, d, q)
        seasonal_order (tuple): The seasonal ARIMA order
    """
    
    def __init__(self, 
                 seasonal: bool = True,
                 m: int = 12,
                 max_p: int = 3,
                 max_q: int = 3,
                 max_d: int = 2,
                 max_P: int = 2,
                 max_Q: int = 2,
                 max_D: int = 1,
                 stepwise: bool = True,
                 suppress_warnings: bool = True,
                 **kwargs):
        """
        Initialize the ARIMA model.
        
        Parameters:
        -----------
        seasonal : bool, default=True
            Whether to use seasonal ARIMA
        m : int, default=12
            Seasonal period (12 for monthly, 4 for quarterly, etc.)
        max_p : int, default=3
            Maximum AR order
        max_q : int, default=3
            Maximum MA order
        max_d : int, default=2
            Maximum differencing order
        max_P : int, default=2
            Maximum seasonal AR order
        max_Q : int, default=2
            Maximum seasonal MA order
        max_D : int, default=1
            Maximum seasonal differencing order
        stepwise : bool, default=True
            Whether to use stepwise algorithm for faster fitting
        suppress_warnings : bool, default=True
            Whether to suppress convergence warnings
        **kwargs : dict
            Additional parameters for the base class
        """
        super().__init__(**kwargs)
        
        if not PMDARIMA_AVAILABLE:
            raise ImportError("pmdarima is required for ARIMAModel. Install with: pip install pmdarima")
        
        self.seasonal = seasonal
        self.m = m
        self.max_p = max_p
        self.max_q = max_q
        self.max_d = max_d
        self.max_P = max_P
        self.max_Q = max_Q
        self.max_D = max_D
        self.stepwise = stepwise
        self.suppress_warnings = suppress_warnings
        
        self.model = None
        self.model_fit = None
        self.order = None
        self.seasonal_order = None
    
    def fit(self, df: pd.DataFrame, 
            date_col: str, 
            target_col: str, 
            validation_data: Optional[pd.DataFrame] = None):
        """
        Fit the auto-ARIMA model to the training data.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Training dataframe
        date_col : str
            Name of the date column
        target_col : str
            Name of the target column
        validation_data : pd.DataFrame, optional
            Not used for ARIMA (kept for API consistency)
        """
        # Call parent fit method for validation
        super().fit(df, date_col, target_col, validation_data)
        
        # Prepare time series data
        ts_data = df.set_index(date_col)[target_col].dropna()
        ts_data.index = pd.to_datetime(ts_data.index)
        ts_data = ts_data.sort_index()
        
        if len(ts_data) == 0:
            raise ValueError("No valid samples found after removing missing values")
        
        # Fit auto-ARIMA model
        try:
            self.model = auto_arima(
                ts_data,
                seasonal=self.seasonal,
                m=self.m,
                max_p=self.max_p,
                max_q=self.max_q,
                max_d=self.max_d,
                max_P=self.max_P if self.seasonal else 0,
                max_Q=self.max_Q if self.seasonal else 0,
                max_D=self.max_D if self.seasonal else 0,
                stepwise=self.stepwise,
                suppress_warnings=self.suppress_warnings,
                error_action='ignore',
                trace=False
            )
            
            # Store model parameters
            self.order = self.model.order
            self.seasonal_order = self.model.seasonal_order if self.seasonal else None
            
            # Store time series data
            self.ts_data = ts_data
            
        except Exception as e:
            raise RuntimeError(f"Failed to fit ARIMA model: {e}")
        
        self.is_fitted = True
        self.metadata.update({
            'training_completed': pd.Timestamp.now().isoformat(),
            'training_samples': len(ts_data),
            'order': self.order,
            'seasonal_order': self.seasonal_order,
            'aic': self.model.aic(),
            'bic': self.model.bic()
        })
    
    def predict(self, periods: int = 30, 
                freq: str = "D", 
                return_components: bool = False) -> pd.DataFrame:
        """
        Generate forecasts for future periods.
        
        Parameters:
        -----------
        periods : int, default=30
            Number of future periods to forecast
        freq : str, default="D"
            Frequency of the time series
        return_components : bool, default=False
            Whether to return forecast components (not implemented for ARIMA)
            
        Returns:
        --------
        pd.DataFrame
            DataFrame with forecasted values and confidence intervals
        """
        super().predict(periods, freq, return_components)
        
        # Generate forecast
        forecast, conf_int = self.model.predict(
            n_periods=periods, 
            return_conf_int=True,
            alpha=0.05  # 95% confidence intervals
        )
        
        # Create future dates
        last_date = self.ts_data.index[-1]
        future_dates = pd.date_range(
            start=last_date, 
            periods=periods + 1,
            freq=freq
        )[1:]
        
        # Create forecast dataframe
        self.forecast_df = pd.DataFrame({
            self.date_col: future_dates,
            'yhat': forecast,
            'yhat_lower': conf_int[:, 0],
            'yhat_upper': conf_int[:, 1]
        })
        
        return self.forecast_df
    
    def plot_diagnostics(self, figsize: tuple = (15, 10)) -> plt.Figure:
        """
        Plot model diagnostics.
        
        Parameters:
        -----------
        figsize : tuple, default=(15, 10)
            Figure size for the plot
            
        Returns:
        --------
        plt.Figure
            The generated figure
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before plotting diagnostics")
        
        # Get residuals
        residuals = self.model.resid()
        
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        
        # Residuals plot
        axes[0, 0].plot(residuals)
        axes[0, 0].set_title('Residuals')
        axes[0, 0].set_xlabel('Time')
        axes[0, 0].set_ylabel('Residuals')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Residuals histogram
        axes[0, 1].hist(residuals, bins=30, density=True, alpha=0.7)
        axes[0, 1].set_title('Residuals Distribution')
        axes[0, 1].set_xlabel('Residuals')
        axes[0, 1].set_ylabel('Density')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Q-Q plot
        if STATSMODELS_AVAILABLE:
            sm.qqplot(residuals, line='s', ax=axes[1, 0])
            axes[1, 0].set_title('Q-Q Plot')
            axes[1, 0].grid(True, alpha=0.3)
        else:
            axes[1, 0].text(0.5, 0.5, 'Q-Q plot requires statsmodels', 
                           ha='center', va='center', transform=axes[1, 0].transAxes)
            axes[1, 0].set_title('Q-Q Plot (statsmodels required)')
        
        # ACF of residuals
        try:
            from statsmodels.tsa.stattools import acf
            from statsmodels.graphics.tsaplots import plot_acf
            
            plot_acf(residuals, ax=axes[1, 1], lags=20)
            axes[1, 1].set_title('ACF of Residuals')
        except ImportError:
            axes[1, 1].text(0.5, 0.5, 'ACF plot requires statsmodels', 
                           ha='center', va='center', transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('ACF of Residuals (statsmodels required)')
        
        plt.tight_layout()
        return fig
    
    def plot_decomposition(self, figsize: tuple = (15, 10)) -> plt.Figure:
        """
        Plot seasonal decomposition of the time series.
        
        Parameters:
        -----------
        figsize : tuple, default=(15, 10)
            Figure size for the plot
            
        Returns:
        --------
        plt.Figure
            The generated figure
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before plotting decomposition")
        
        if not STATSMODELS_AVAILABLE:
            raise ImportError("statsmodels is required for decomposition plots")
        
        # Perform seasonal decomposition
        try:
            decomposition = seasonal_decompose(
                self.ts_data, 
                model='additive', 
                period=min(self.m, len(self.ts_data) // 2)
            )
            
            fig, axes = plt.subplots(4, 1, figsize=figsize)
            
            # Original
            axes[0].plot(decomposition.observed)
            axes[0].set_title('Original Time Series')
            axes[0].grid(True, alpha=0.3)
            
            # Trend
            axes[1].plot(decomposition.trend)
            axes[1].set_title('Trend')
            axes[1].grid(True, alpha=0.3)
            
            # Seasonal
            axes[2].plot(decomposition.seasonal)
            axes[2].set_title('Seasonal')
            axes[2].grid(True, alpha=0.3)
            
            # Residual
            axes[3].plot(decomposition.resid)
            axes[3].set_title('Residual')
            axes[3].grid(True, alpha=0.3)
            
            plt.tight_layout()
            return fig
            
        except Exception as e:
            warnings.warn(f"Decomposition plot failed: {e}")
            return None
    
    def summary(self) -> str:
        """
        Get model summary.
        
        Returns:
        --------
        str
            Model summary string
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before getting summary")
        
        return str(self.model.summary())
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get detailed model information.
        
        Returns:
        --------
        dict
            Dictionary with model information
        """
        base_info = super().get_model_info()
        
        if self.is_fitted:
            arima_info = {
                'order': self.order,
                'seasonal_order': self.seasonal_order,
                'aic': self.model.aic(),
                'bic': self.model.bic(),
                'hqic': self.model.hqic(),
                'seasonal': self.seasonal,
                'seasonal_period': self.m
            }
            base_info.update(arima_info)
        
        return base_info
    
    def _serialize_model(self) -> Dict[str, Any]:
        """Serialize ARIMA model to JSON-compatible format."""
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before serialization")
            
        return {
            'model_params': {
                'seasonal': self.seasonal,
                'm': self.m,
                'max_p': self.max_p,
                'max_q': self.max_q,
                'max_d': self.max_d,
                'max_P': self.max_P,
                'max_Q': self.max_Q,
                'max_D': self.max_D,
                'stepwise': self.stepwise,
                'suppress_warnings': self.suppress_warnings
            },
            'fitted_params': {
                'order': self.order,
                'seasonal_order': self.seasonal_order,
                'aic': self.model.aic(),
                'bic': self.model.bic()
            },
            'training_samples': self.metadata.get('training_samples')
        }
    
    def _deserialize_model(self, model_data: Dict[str, Any]):
        """Deserialize ARIMA model from JSON."""
        # Restore parameters
        params = model_data['model_params']
        self.seasonal = params['seasonal']
        self.m = params['m']
        self.max_p = params['max_p']
        self.max_q = params['max_q']
        self.max_d = params['max_d']
        self.max_P = params['max_P']
        self.max_Q = params['max_Q']
        self.max_D = params['max_D']
        self.stepwise = params['stepwise']
        self.suppress_warnings = params['suppress_warnings']
        
        # Restore fitted parameters
        fitted_params = model_data['fitted_params']
        self.order = tuple(fitted_params['order'])
        self.seasonal_order = tuple(fitted_params['seasonal_order']) if fitted_params['seasonal_order'] else None
        
        # Note: This is a simplified deserialization
        # For full model restoration, use pickle format
        warnings.warn("JSON deserialization for ARIMA is limited. "
                     "Use pickle format for complete model restoration.")
        
        self.is_fitted = True
