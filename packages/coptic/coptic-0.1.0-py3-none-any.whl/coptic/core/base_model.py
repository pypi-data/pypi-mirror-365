"""
Abstract base class for all forecasting models in coptic library.

This module provides the BaseModel class that defines the interface
and common functionality for all forecasting models.
"""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Union, Optional, Dict, Any, Tuple
from pathlib import Path
import pickle
import json
import warnings


class BaseModel(ABC):
    """
    Abstract base class for all forecasting models in coptic.
    
    This class defines the interface that all forecasting models must implement
    and provides common functionality for data validation, plotting, and model
    persistence.
    
    Attributes:
        params (dict): Model parameters
        is_fitted (bool): Whether the model has been trained
        training_date (str): ISO timestamp of when training completed
        metadata (dict): Model metadata including creation time and version
        date_col (str): Name of the date column
        target_col (str): Name of the target column
        train_df (pd.DataFrame): Training data
        forecast_df (pd.DataFrame): Generated forecasts
    """
    
    def __init__(self, **params):
        """
        Initialize the base model.
        
        Parameters:
        -----------
        **params : dict
            Model-specific parameters
        """
        self.params = params
        self.is_fitted = False
        self.training_date = None
        self.metadata = {
            'created_at': datetime.now().isoformat(),
            'version': '0.1.0',
            'model_type': self.__class__.__name__
        }
    
    @abstractmethod
    def fit(self, df: pd.DataFrame, date_col: str, target_col: str, 
            validation_data: Optional[pd.DataFrame] = None):
        """
        Fit the model to the training data.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Training dataframe
        date_col : str
            Name of datetime column
        target_col : str
            Name of target column
        validation_data : pd.DataFrame, optional
            Optional validation dataframe
        """
        self._validate_data(df, date_col, target_col)
        self.date_col = date_col
        self.target_col = target_col
        self.train_df = df.copy()
        self.training_date = datetime.now().isoformat()
    
    @abstractmethod
    def predict(self, periods: int = 30, freq: str = "D", 
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
            Whether to return forecast components
            
        Returns:
        --------
        pd.DataFrame
            Dataframe with forecasted values
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before prediction")
    
    def _validate_data(self, df: pd.DataFrame, date_col: str, target_col: str):
        """
        Validate input data structure.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Input dataframe to validate
        date_col : str
            Name of date column
        target_col : str
            Name of target column
            
        Raises:
        -------
        ValueError
            If data validation fails
        """
        if date_col not in df.columns:
            raise ValueError(f"Date column '{date_col}' not found in dataframe")
        if target_col not in df.columns:
            raise ValueError(f"Target column '{target_col}' not found in dataframe")
        
        # Convert to datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
            try:
                df[date_col] = pd.to_datetime(df[date_col])
            except Exception as e:
                raise ValueError(f"Could not convert '{date_col}' to datetime: {e}")
        
        # Check for missing values in target
        if df[target_col].isnull().any():
            warnings.warn(f"Target column '{target_col}' contains missing values")
        
        # Check for duplicate dates
        if df[date_col].duplicated().any():
            warnings.warn(f"Date column '{date_col}' contains duplicate values")
    
    def plot(self, plot_components: bool = False, figsize: Tuple[int, int] = (12, 6), 
             title: Optional[str] = None) -> plt.Figure:
        """
        Plot the forecast results with enhanced visualization.
        
        Parameters:
        -----------
        plot_components : bool, default=False
            Whether to plot forecast components (if available)
        figsize : tuple, default=(12, 6)
            Figure size for the plot
        title : str, optional
            Custom title for the plot
            
        Returns:
        --------
        plt.Figure
            The generated figure
        """
        if not hasattr(self, 'forecast_df'):
            raise RuntimeError("Make predictions before plotting")
            
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot historical data
        ax.plot(self.train_df[self.date_col], 
                self.train_df[self.target_col], 
                label='Historical', color='blue', linewidth=1.5)
        
        # Plot forecast
        ax.plot(self.forecast_df[self.date_col], 
                self.forecast_df['yhat'], 
                label='Forecast', color='orange', linewidth=2)
        
        # Plot confidence intervals if available
        if all(col in self.forecast_df.columns for col in ['yhat_lower', 'yhat_upper']):
            ax.fill_between(self.forecast_df[self.date_col],
                          self.forecast_df['yhat_lower'],
                          self.forecast_df['yhat_upper'],
                          color='orange', alpha=0.2, label='Confidence Interval')
        
        # Add vertical line at training cutoff
        last_train_date = self.train_df[self.date_col].max()
        ax.axvline(x=last_train_date, color='red', linestyle='--', 
                  alpha=0.7, label='Training Cutoff')
        
        ax.legend()
        ax.set_xlabel('Date')
        ax.set_ylabel(self.target_col.title())
        
        if title is None:
            title = f'{self.metadata["model_type"]} Forecast'
        ax.set_title(title)
        
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return fig
    
    def evaluate(self, test_df: pd.DataFrame) -> Dict[str, float]:
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
        # Import here to avoid circular imports
        from ..utils.metrics import calculate_metrics
        
        if not hasattr(self, 'forecast_df'):
            raise RuntimeError("Make predictions before evaluation")
            
        # Merge forecast with actuals
        merged = pd.merge(
            test_df[[self.date_col, self.target_col]],
            self.forecast_df,
            on=self.date_col,
            how='inner'
        )
        
        if merged.empty:
            raise ValueError("No overlapping dates found between test data and forecasts")
        
        return calculate_metrics(
            merged[self.target_col], 
            merged['yhat']
        )
    
    def save(self, filepath: Union[str, Path], save_format: str = 'pickle'):
        """
        Save the model to a file with multiple format options.
        
        Parameters:
        -----------
        filepath : str or Path
            Path where to save the model
        save_format : str, default='pickle'
            Format to save the model ('pickle' or 'json')
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        if save_format == 'pickle':
            with open(filepath, 'wb') as f:
                pickle.dump(self, f)
        elif save_format == 'json':
            # For models that can be serialized to JSON
            model_data = {
                'metadata': self.metadata,
                'params': self.params,
                'training_date': self.training_date,
                'date_col': getattr(self, 'date_col', None),
                'target_col': getattr(self, 'target_col', None),
                'model_data': self._serialize_model()
            }
            with open(filepath, 'w') as f:
                json.dump(model_data, f, indent=2)
        else:
            raise ValueError(f"Unsupported save format: {save_format}")
    
    @classmethod
    def load(cls, filepath: Union[str, Path], save_format: str = 'pickle'):
        """
        Load a saved model from a file.
        
        Parameters:
        -----------
        filepath : str or Path
            Path to the saved model file
        save_format : str, default='pickle'
            Format of the saved model ('pickle' or 'json')
            
        Returns:
        --------
        BaseModel
            Loaded model instance
        """
        filepath = Path(filepath)
        
        if save_format == 'pickle':
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        elif save_format == 'json':
            with open(filepath, 'r') as f:
                data = json.load(f)
            model = cls(**data['params'])
            model._deserialize_model(data['model_data'])
            model.metadata = data['metadata']
            model.training_date = data['training_date']
            model.date_col = data['date_col']
            model.target_col = data['target_col']
            return model
        else:
            raise ValueError(f"Unsupported save format: {save_format}")
    
    def _serialize_model(self) -> Dict[str, Any]:
        """
        Convert model-specific data to serializable format.
        
        Returns:
        --------
        dict
            Serializable representation of the model
        """
        raise NotImplementedError("Serialization not implemented for this model")
    
    def _deserialize_model(self, model_data: Dict[str, Any]):
        """
        Reconstruct model from serialized data.
        
        Parameters:
        -----------
        model_data : dict
            Serialized model data
        """
        raise NotImplementedError("Deserialization not implemented for this model")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get comprehensive information about the model.
        
        Returns:
        --------
        dict
            Model information including metadata, parameters, and training status
        """
        info = {
            'model_type': self.metadata.get('model_type'),
            'version': self.metadata.get('version'),
            'created_at': self.metadata.get('created_at'),
            'training_date': self.training_date,
            'is_fitted': self.is_fitted,
            'parameters': self.params
        }
        
        if hasattr(self, 'date_col'):
            info['date_column'] = self.date_col
        if hasattr(self, 'target_col'):
            info['target_column'] = self.target_col
        if hasattr(self, 'train_df'):
            info['training_samples'] = len(self.train_df)
        if hasattr(self, 'forecast_df'):
            info['forecast_periods'] = len(self.forecast_df)
            
        return info
