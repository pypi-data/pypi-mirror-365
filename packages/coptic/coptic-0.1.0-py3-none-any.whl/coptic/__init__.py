"""
Coptic - Advanced Time Series Forecasting Library
================================================

A comprehensive Python library for time series forecasting with multiple 
algorithms including Random Forest, XGBoost, Prophet, and ARIMA.

Main Components:
- CopticForecaster: Main interface for forecasting
- BaseModel: Abstract base class for all models
- Feature engineering and preprocessing utilities
- Visualization and evaluation tools

Example:
    >>> from coptic import CopticForecaster
    >>> forecaster = CopticForecaster(model_type="randomforest")
    >>> forecaster.fit(df, date_col="date", target_col="sales")
    >>> forecast = forecaster.predict(periods=30)
"""

from .core.base_model import BaseModel
from .core.rf_model import RandomForestModel
from .core.xgb_model import XGBoostModel
from .core.prophet_model import ProphetModel
from .core.arima_model import ARIMAModel

from .preprocessing.cleaner import DataCleaner
from .preprocessing.features import FeatureGenerator

from .utils.metrics import calculate_metrics
from .utils.plot import plot_forecast

__version__ = "0.1.0"
__author__ = "Coptic Team"
__all__ = ['CopticForecaster', 'BaseModel', 'RandomForestModel', 'XGBoostModel', 
           'ProphetModel', 'ARIMAModel', 'DataCleaner', 'FeatureGenerator',
           'calculate_metrics', 'plot_forecast']


class CopticForecaster:
    """
    Main forecasting interface for coptic library.
    
    This class provides a unified interface for different forecasting models,
    making it easy to switch between algorithms and compare results.
    
    Attributes:
        model_type (str): Type of forecasting model being used
        model: The underlying forecasting model instance
        date_col (str): Name of the date column
        target_col (str): Name of the target column
    """
    
    def __init__(self, model_type="randomforest", **model_params):
        """
        Initialize the forecaster with specified model type.
        
        Parameters:
        -----------
        model_type : str
            Type of model to use. Options:
            - "randomforest": Random Forest Regressor
            - "xgboost": XGBoost Regressor  
            - "prophet": Facebook Prophet
            - "arima": Auto ARIMA
        model_params : dict
            Additional parameters to pass to the underlying model
            
        Examples:
        ---------
        >>> # Basic usage
        >>> forecaster = CopticForecaster()
        
        >>> # With specific model and parameters
        >>> forecaster = CopticForecaster(
        ...     model_type="xgboost",
        ...     n_estimators=200,
        ...     learning_rate=0.1
        ... )
        """
        self.model_type = model_type.lower()
        self.model_params = model_params
        
        # Initialize the appropriate model
        if self.model_type == "randomforest":
            self.model = RandomForestModel(**model_params)
        elif self.model_type == "xgboost":
            self.model = XGBoostModel(**model_params)
        elif self.model_type == "prophet":
            self.model = ProphetModel(**model_params)
        elif self.model_type == "arima":
            self.model = ARIMAModel(**model_params)
        else:
            raise ValueError(f"Unknown model type: {model_type}. "
                           f"Supported types: randomforest, xgboost, prophet, arima")
    
    def fit(self, df, date_col="date", target_col="sales", validation_data=None):
        """
        Fit the model to the training data.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Input dataframe with time series data
        date_col : str, default="date"
            Name of the column containing dates
        target_col : str, default="sales"
            Name of the column containing target values
        validation_data : pd.DataFrame, optional
            Validation dataset for early stopping (XGBoost only)
            
        Returns:
        --------
        self : CopticForecaster
            Returns self for method chaining
            
        Examples:
        ---------
        >>> forecaster.fit(df, date_col="timestamp", target_col="revenue")
        >>> 
        >>> # With validation data
        >>> forecaster.fit(train_df, validation_data=val_df)
        """
        self.date_col = date_col
        self.target_col = target_col
        self.model.fit(df, date_col=date_col, target_col=target_col, 
                      validation_data=validation_data)
        return self
    
    def predict(self, periods=30, freq="D", return_components=False):
        """
        Generate forecasts for future periods.
        
        Parameters:
        -----------
        periods : int, default=30
            Number of future periods to forecast
        freq : str, default="D"
            Frequency of the time series (e.g., "D" for daily, "M" for monthly)
        return_components : bool, default=False
            Whether to return forecast components (Prophet only)
            
        Returns:
        --------
        pd.DataFrame
            DataFrame with forecasted values and optional confidence intervals
            
        Examples:
        ---------
        >>> # Basic prediction
        >>> forecast = forecaster.predict(periods=60)
        >>> 
        >>> # Weekly forecasts
        >>> forecast = forecaster.predict(periods=12, freq="W")
        """
        return self.model.predict(periods=periods, freq=freq, 
                                return_components=return_components)
    
    def plot(self, **kwargs):
        """
        Plot the forecast results.
        
        Parameters:
        -----------
        **kwargs : dict
            Additional plotting parameters passed to the model's plot method
            
        Returns:
        --------
        matplotlib.figure.Figure
            The generated plot figure
        """
        return self.model.plot(**kwargs)
    
    def evaluate(self, test_df):
        """
        Evaluate model performance on test data.
        
        Parameters:
        -----------
        test_df : pd.DataFrame
            Test dataset with actual values
            
        Returns:
        --------
        dict
            Dictionary containing various evaluation metrics
        """
        return self.model.evaluate(test_df)
    
    def save(self, filepath, save_format='pickle'):
        """
        Save the trained model to a file.
        
        Parameters:
        -----------
        filepath : str or Path
            Path where to save the model
        save_format : str, default='pickle'
            Format to save the model ('pickle' or 'json')
        """
        self.model.save(filepath, save_format=save_format)
    
    @classmethod
    def load(cls, filepath, save_format='pickle'):
        """
        Load a saved model from a file.
        
        Parameters:
        -----------
        filepath : str or Path
            Path to the saved model
        save_format : str, default='pickle'
            Format of the saved model ('pickle' or 'json')
            
        Returns:
        --------
        CopticForecaster
            Loaded forecaster instance
        """
        model = BaseModel.load(filepath, save_format=save_format)
        forecaster = cls.__new__(cls)
        forecaster.model = model
        forecaster.model_type = model.metadata.get('model_type', 'unknown')
        forecaster.date_col = getattr(model, 'date_col', None)
        forecaster.target_col = getattr(model, 'target_col', None)
        return forecaster
    
    def get_feature_importance(self):
        """
        Get feature importance for tree-based models.
        
        Returns:
        --------
        pd.DataFrame or None
            Feature importance dataframe if available
        """
        if hasattr(self.model, 'feature_importances_'):
            return self.model.feature_importances_
        else:
            print(f"Feature importance not available for {self.model_type}")
            return None
    
    def plot_feature_importance(self, **kwargs):
        """
        Plot feature importance for tree-based models.
        
        Returns:
        --------
        matplotlib.figure.Figure or None
            Feature importance plot if available
        """
        if hasattr(self.model, 'plot_feature_importance'):
            return self.model.plot_feature_importance(**kwargs)
        else:
            print(f"Feature importance plotting not available for {self.model_type}")
            return None
