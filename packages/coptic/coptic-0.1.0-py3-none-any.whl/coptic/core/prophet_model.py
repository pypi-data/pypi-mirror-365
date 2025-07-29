"""
Facebook Prophet implementation for time series forecasting.

This module provides a Prophet-based forecasting model with
seasonality detection and component analysis.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
import matplotlib.pyplot as plt
import warnings

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    warnings.warn("Prophet not available. Install with: pip install prophet")

from .base_model import BaseModel


class ProphetModel(BaseModel):
    """
    Facebook Prophet implementation for time series forecasting.
    
    This model uses Prophet for time series forecasting with automatic
    seasonality detection, holiday effects, and trend analysis.
    
    Attributes:
        seasonality_mode (str): Type of seasonality ('additive' or 'multiplicative')
        yearly_seasonality (bool): Whether to include yearly seasonality
        weekly_seasonality (bool): Whether to include weekly seasonality
        daily_seasonality (bool): Whether to include daily seasonality
        model (Prophet): The trained Prophet model
        forecast_df (pd.DataFrame): Generated forecasts with components
    """
    
    def __init__(self, 
                 seasonality_mode: str = 'additive',
                 yearly_seasonality: bool = 'auto',
                 weekly_seasonality: bool = 'auto',
                 daily_seasonality: bool = 'auto',
                 growth: str = 'linear',
                 changepoint_prior_scale: float = 0.05,
                 seasonality_prior_scale: float = 10.0,
                 holidays_prior_scale: float = 10.0,
                 mcmc_samples: int = 0,
                 **kwargs):
        """
        Initialize the Prophet model.
        
        Parameters:
        -----------
        seasonality_mode : str, default='additive'
            Type of seasonality ('additive' or 'multiplicative')
        yearly_seasonality : bool or 'auto', default='auto'
            Whether to include yearly seasonality
        weekly_seasonality : bool or 'auto', default='auto'
            Whether to include weekly seasonality
        daily_seasonality : bool or 'auto', default='auto'
            Whether to include daily seasonality
        growth : str, default='linear'
            Type of growth ('linear' or 'logistic')
        changepoint_prior_scale : float, default=0.05
            Strength of the sparse prior for changepoints
        seasonality_prior_scale : float, default=10.0
            Strength of the prior for seasonality
        holidays_prior_scale : float, default=10.0
            Strength of the prior for holidays
        mcmc_samples : int, default=0
            Number of MCMC samples (0 for MAP estimation)
        **kwargs : dict
            Additional parameters for the base class
        """
        super().__init__(**kwargs)
        
        if not PROPHET_AVAILABLE:
            raise ImportError("Prophet is required for ProphetModel. Install with: pip install prophet")
        
        self.seasonality_mode = seasonality_mode
        self.yearly_seasonality = yearly_seasonality
        self.weekly_seasonality = weekly_seasonality
        self.daily_seasonality = daily_seasonality
        self.growth = growth
        self.changepoint_prior_scale = changepoint_prior_scale
        self.seasonality_prior_scale = seasonality_prior_scale
        self.holidays_prior_scale = holidays_prior_scale
        self.mcmc_samples = mcmc_samples
        
        self.model = Prophet(
            seasonality_mode=seasonality_mode,
            yearly_seasonality=yearly_seasonality,
            weekly_seasonality=weekly_seasonality,
            daily_seasonality=daily_seasonality,
            growth=growth,
            changepoint_prior_scale=changepoint_prior_scale,
            seasonality_prior_scale=seasonality_prior_scale,
            holidays_prior_scale=holidays_prior_scale,
            mcmc_samples=mcmc_samples
        )
    
    def fit(self, df: pd.DataFrame, 
            date_col: str, 
            target_col: str, 
            validation_data: Optional[pd.DataFrame] = None):
        """
        Fit the Prophet model to the training data.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Training dataframe
        date_col : str
            Name of the date column
        target_col : str
            Name of the target column
        validation_data : pd.DataFrame, optional
            Not used for Prophet (kept for API consistency)
        """
        # Call parent fit method for validation
        super().fit(df, date_col, target_col, validation_data)
        
        # Prepare data in Prophet format
        prophet_df = df[[date_col, target_col]].copy()
        prophet_df.columns = ['ds', 'y']
        prophet_df['ds'] = pd.to_datetime(prophet_df['ds'])
        
        # Remove any missing values
        prophet_df = prophet_df.dropna()
        
        if len(prophet_df) == 0:
            raise ValueError("No valid samples found after removing missing values")
        
        # Fit the model
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.model.fit(prophet_df)
        
        self.is_fitted = True
        self.metadata.update({
            'training_completed': pd.Timestamp.now().isoformat(),
            'training_samples': len(prophet_df),
            'seasonalities': list(self.model.seasonalities.keys()),
            'changepoints': len(self.model.changepoints)
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
            Whether to include forecast components
            
        Returns:
        --------
        pd.DataFrame
            DataFrame with forecasted values and components
        """
        super().predict(periods, freq, return_components)
        
        # Create future dataframe
        future = self.model.make_future_dataframe(periods=periods, freq=freq)
        
        # Make predictions
        forecast = self.model.predict(future)
        
        # Extract forecast for future periods only
        n_train = len(self.train_df)
        future_forecast = forecast.tail(periods).copy()
        
        # Rename columns to match standard format
        self.forecast_df = pd.DataFrame({
            self.date_col: future_forecast['ds'],
            'yhat': future_forecast['yhat'],
            'yhat_lower': future_forecast['yhat_lower'],
            'yhat_upper': future_forecast['yhat_upper']
        })
        
        # Add components if requested
        if return_components:
            component_cols = ['trend', 'seasonal', 'yearly', 'weekly']
            for col in component_cols:
                if col in future_forecast.columns:
                    self.forecast_df[col] = future_forecast[col].values
        
        # Store full forecast for plotting
        self.full_forecast = forecast
        
        return self.forecast_df
    
    def plot(self, plot_components: bool = False, 
             figsize: tuple = (12, 8)) -> plt.Figure:
        """
        Plot the forecast results using Prophet's built-in plotting.
        
        Parameters:
        -----------
        plot_components : bool, default=False
            Whether to plot forecast components
        figsize : tuple, default=(12, 8)
            Figure size for the plot
            
        Returns:
        --------
        plt.Figure
            The generated figure
        """
        if not hasattr(self, 'full_forecast'):
            raise RuntimeError("Make predictions before plotting")
        
        if plot_components:
            # Plot components
            fig = self.model.plot_components(self.full_forecast, figsize=figsize)
        else:
            # Plot main forecast
            fig = self.model.plot(self.full_forecast, figsize=figsize)
            ax = fig.gca()
            ax.set_title(f'{self.metadata["model_type"]} Forecast')
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def plot_components(self, figsize: tuple = (12, 10)) -> plt.Figure:
        """
        Plot forecast components separately.
        
        Parameters:
        -----------
        figsize : tuple, default=(12, 10)
            Figure size for the plot
            
        Returns:
        --------
        plt.Figure
            The generated figure
        """
        if not hasattr(self, 'full_forecast'):
            raise RuntimeError("Make predictions before plotting components")
        
        return self.model.plot_components(self.full_forecast, figsize=figsize)
    
    def plot_changepoints(self, figsize: tuple = (12, 6)) -> plt.Figure:
        """
        Plot detected changepoints.
        
        Parameters:
        -----------
        figsize : tuple, default=(12, 6)
            Figure size for the plot
            
        Returns:
        --------
        plt.Figure
            The generated figure
        """
        if not hasattr(self, 'full_forecast'):
            raise RuntimeError("Make predictions before plotting changepoints")
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot historical data
        ax.plot(self.train_df[self.date_col], 
                self.train_df[self.target_col], 
                'k.', label='Observations')
        
        # Plot trend
        ax.plot(self.full_forecast['ds'], 
                self.full_forecast['trend'], 
                'b-', label='Trend')
        
        # Plot changepoints
        for cp in self.model.changepoints:
            ax.axvline(x=cp, color='red', linestyle='--', alpha=0.7)
        
        ax.set_xlabel('Date')
        ax.set_ylabel(self.target_col.title())
        ax.set_title('Trend with Changepoints')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return fig
    
    def add_seasonality(self, name: str, period: float, fourier_order: int):
        """
        Add custom seasonality to the model.
        
        Parameters:
        -----------
        name : str
            Name of the seasonality
        period : float
            Period of the seasonality in days
        fourier_order : int
            Number of Fourier terms to use
        """
        if self.is_fitted:
            warnings.warn("Adding seasonality after fitting. You may need to refit the model.")
        
        self.model.add_seasonality(
            name=name,
            period=period,
            fourier_order=fourier_order
        )
    
    def add_holidays(self, holidays: pd.DataFrame):
        """
        Add holiday effects to the model.
        
        Parameters:
        -----------
        holidays : pd.DataFrame
            DataFrame with 'holiday' and 'ds' columns
        """
        if self.is_fitted:
            warnings.warn("Adding holidays after fitting. You may need to refit the model.")
        
        # Add holidays to the model
        for holiday in holidays['holiday'].unique():
            holiday_dates = holidays[holidays['holiday'] == holiday]['ds']
            self.model.add_country_holidays(country_name=holiday)
    
    def cross_validate(self, initial: str = '365 days', 
                      period: str = '180 days', 
                      horizon: str = '365 days') -> pd.DataFrame:
        """
        Perform cross-validation using Prophet's built-in method.
        
        Parameters:
        -----------
        initial : str, default='365 days'
            Size of initial training period
        period : str, default='180 days'
            Spacing between cutoff dates
        horizon : str, default='365 days'
            Forecast horizon
            
        Returns:
        --------
        pd.DataFrame
            Cross-validation results
        """
        try:
            from prophet.diagnostics import cross_validation, performance_metrics
            
            # Prepare data
            prophet_df = self.train_df[[self.date_col, self.target_col]].copy()
            prophet_df.columns = ['ds', 'y']
            prophet_df['ds'] = pd.to_datetime(prophet_df['ds'])
            
            # Create a new model for CV
            cv_model = Prophet(
                seasonality_mode=self.seasonality_mode,
                yearly_seasonality=self.yearly_seasonality,
                weekly_seasonality=self.weekly_seasonality,
                daily_seasonality=self.daily_seasonality,
                growth=self.growth,
                changepoint_prior_scale=self.changepoint_prior_scale,
                seasonality_prior_scale=self.seasonality_prior_scale,
                holidays_prior_scale=self.holidays_prior_scale,
                mcmc_samples=self.mcmc_samples
            )
            
            cv_model.fit(prophet_df)
            
            # Perform cross-validation
            df_cv = cross_validation(
                cv_model, 
                initial=initial, 
                period=period, 
                horizon=horizon
            )
            
            # Calculate performance metrics
            df_p = performance_metrics(df_cv)
            
            return df_p
            
        except ImportError:
            warnings.warn("Prophet diagnostics not available")
            return pd.DataFrame()
    
    def _serialize_model(self) -> Dict[str, Any]:
        """Serialize Prophet model to JSON-compatible format."""
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before serialization")
            
        return {
            'model_params': {
                'seasonality_mode': self.seasonality_mode,
                'yearly_seasonality': self.yearly_seasonality,
                'weekly_seasonality': self.weekly_seasonality,
                'daily_seasonality': self.daily_seasonality,
                'growth': self.growth,
                'changepoint_prior_scale': self.changepoint_prior_scale,
                'seasonality_prior_scale': self.seasonality_prior_scale,
                'holidays_prior_scale': self.holidays_prior_scale,
                'mcmc_samples': self.mcmc_samples
            },
            'training_samples': self.metadata.get('training_samples'),
            'seasonalities': self.metadata.get('seasonalities'),
            'changepoints': self.metadata.get('changepoints')
        }
    
    def _deserialize_model(self, model_data: Dict[str, Any]):
        """Deserialize Prophet model from JSON."""
        # Reconstruct model with saved parameters
        params = model_data['model_params']
        self.model = Prophet(**params)
        
        # Note: This is a simplified deserialization
        # For full model restoration, use pickle format
        warnings.warn("JSON deserialization for Prophet is limited. "
                     "Use pickle format for complete model restoration.")
        
        self.is_fitted = True
