"""
XGBoost implementation for time series forecasting.

This module provides an XGBoost-based forecasting model with
early stopping, feature importance analysis, and prediction intervals.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
import matplotlib.pyplot as plt
import warnings

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    warnings.warn("XGBoost not available. Install with: pip install xgboost")

from .base_model import BaseModel
from ..preprocessing.features import FeatureGenerator


class XGBoostModel(BaseModel):
    """
    XGBoost implementation for time series forecasting.
    
    This model uses XGBoost regressor with automatically generated
    time-based features. It supports early stopping, feature importance
    analysis, and prediction intervals.
    
    Attributes:
        n_estimators (int): Number of boosting rounds
        max_depth (int): Maximum depth of trees
        learning_rate (float): Learning rate
        early_stopping_rounds (int): Early stopping patience
        model (xgb.XGBRegressor): The trained model
        feature_generator (FeatureGenerator): Feature engineering pipeline
        feature_importances_ (pd.DataFrame): Feature importance scores
    """
    
    def __init__(self, 
                 n_estimators: int = 100,
                 max_depth: int = 6,
                 learning_rate: float = 0.1,
                 subsample: float = 1.0,
                 colsample_bytree: float = 1.0,
                 early_stopping_rounds: Optional[int] = 10,
                 random_state: Optional[int] = 42,
                 **kwargs):
        """
        Initialize the XGBoost model.
        
        Parameters:
        -----------
        n_estimators : int, default=100
            Number of boosting rounds
        max_depth : int, default=6
            Maximum depth of trees
        learning_rate : float, default=0.1
            Learning rate (eta)
        subsample : float, default=1.0
            Subsample ratio of training instances
        colsample_bytree : float, default=1.0
            Subsample ratio of columns when constructing each tree
        early_stopping_rounds : int, optional
            Number of rounds for early stopping
        random_state : int, optional
            Random state for reproducibility
        **kwargs : dict
            Additional parameters for the base class
        """
        super().__init__(**kwargs)
        
        if not XGBOOST_AVAILABLE:
            raise ImportError("XGBoost is required for XGBoostModel. Install with: pip install xgboost")
        
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.subsample = subsample
        self.colsample_bytree = colsample_bytree
        self.early_stopping_rounds = early_stopping_rounds
        self.random_state = random_state
        
        self.model_params = {
            'n_estimators': n_estimators,
            'max_depth': max_depth,
            'learning_rate': learning_rate,
            'subsample': subsample,
            'colsample_bytree': colsample_bytree,
            'objective': 'reg:squarederror',
            'random_state': random_state,
            'n_jobs': -1
        }
        
        self.model = xgb.XGBRegressor(**self.model_params)
        self.feature_generator = FeatureGenerator()
        self.feature_importances_ = None
    
    def fit(self, df: pd.DataFrame, 
            date_col: str, 
            target_col: str, 
            validation_data: Optional[pd.DataFrame] = None):
        """
        Fit the XGBoost model with optional early stopping.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Training dataframe
        date_col : str
            Name of the date column
        target_col : str
            Name of the target column
        validation_data : pd.DataFrame, optional
            Validation dataset for early stopping
        """
        # Call parent fit method for validation
        super().fit(df, date_col, target_col, validation_data)
        
        # Generate features for training data
        X_train, y_train = self.feature_generator.generate_features(df, date_col, target_col)
        
        # Remove rows with NaN values
        if y_train is not None:
            valid_mask = X_train.notna().all(axis=1) & y_train.notna()
            X_train_clean = X_train[valid_mask]
            y_train_clean = y_train[valid_mask]
        else:
            raise ValueError("Target column is required for training")
        
        if len(X_train_clean) == 0:
            raise ValueError("No valid samples found after feature generation")
        
        # Prepare evaluation set for early stopping
        eval_set = None
        if validation_data is not None and self.early_stopping_rounds is not None:
            X_val, y_val = self.feature_generator.generate_features(
                validation_data, date_col, target_col
            )
            if y_val is not None:
                val_valid_mask = X_val.notna().all(axis=1) & y_val.notna()
                X_val_clean = X_val[val_valid_mask]
                y_val_clean = y_val[val_valid_mask]
                
                if len(X_val_clean) > 0:
                    eval_set = [(X_val_clean, y_val_clean)]
        
        # Train model
        fit_params = {}
        if eval_set is not None:
            fit_params['eval_set'] = eval_set
            fit_params['early_stopping_rounds'] = self.early_stopping_rounds
            fit_params['verbose'] = False
        
        self.model.fit(X_train_clean, y_train_clean, **fit_params)
        
        # Store feature importances
        self.feature_importances_ = pd.DataFrame({
            'feature': X_train_clean.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Store training data for reference
        self.X_train = X_train_clean
        self.y_train = y_train_clean
        
        self.is_fitted = True
        self.metadata.update({
            'training_completed': pd.Timestamp.now().isoformat(),
            'training_samples': len(X_train_clean),
            'n_features': len(X_train_clean.columns),
            'best_iteration': getattr(self.model, 'best_iteration', self.n_estimators)
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
            Not used for XGBoost (kept for API consistency)
            
        Returns:
        --------
        pd.DataFrame
            DataFrame with forecasted values and prediction intervals
        """
        super().predict(periods, freq, return_components)
        
        # Create future dataframe
        last_date = self.train_df[self.date_col].max()
        future_dates = pd.date_range(
            start=last_date, 
            periods=periods + 1,
            freq=freq
        )[1:]
        
        future_df = pd.DataFrame({self.date_col: future_dates})
        
        # For prediction, create combined dataframe for lag features
        combined_df = pd.concat([
            self.train_df[[self.date_col, self.target_col]], 
            future_df.assign(**{self.target_col: np.nan})
        ], ignore_index=True)
        
        # Generate features for the combined dataframe
        X_combined, _ = self.feature_generator.generate_features(
            combined_df, 
            self.date_col, 
            self.target_col
        )
        
        # Extract features for future dates
        X_future = X_combined.tail(periods)
        
        # Make predictions
        y_pred = self.model.predict(X_future)
        
        # Create prediction intervals using bootstrap-like approach
        # Train multiple models with different random states for uncertainty estimation
        if hasattr(self.model, 'predict'):
            # Simple approach: use prediction variance from trees (if available)
            try:
                # For XGBoost, we can get prediction intervals by training multiple models
                # This is a simplified approach
                predictions_bootstrap = []
                for i in range(10):  # Bootstrap-like sampling
                    # Add some noise to training data
                    noise = np.random.normal(0, self.y_train.std() * 0.01, len(self.y_train))
                    y_train_noisy = self.y_train + noise
                    
                    # Train a model with noise
                    temp_model = xgb.XGBRegressor(**self.model_params)
                    temp_model.fit(self.X_train, y_train_noisy)
                    pred_bootstrap = temp_model.predict(X_future)
                    predictions_bootstrap.append(pred_bootstrap)
                
                # Calculate prediction intervals
                predictions_array = np.array(predictions_bootstrap)
                yhat_lower = np.percentile(predictions_array, 5, axis=0)
                yhat_upper = np.percentile(predictions_array, 95, axis=0)
                
            except Exception:
                # Fallback: simple percentage-based intervals
                std_est = self.y_train.std()
                yhat_lower = y_pred - 1.96 * std_est
                yhat_upper = y_pred + 1.96 * std_est
        else:
            # Fallback approach
            std_est = self.y_train.std()
            yhat_lower = y_pred - 1.96 * std_est
            yhat_upper = y_pred + 1.96 * std_est
        
        # Create forecast dataframe
        self.forecast_df = future_df.copy()
        self.forecast_df['yhat'] = y_pred
        self.forecast_df['yhat_lower'] = yhat_lower
        self.forecast_df['yhat_upper'] = yhat_upper
        
        return self.forecast_df
    
    def plot_feature_importance(self, top_n: int = 15, 
                               figsize: tuple = (10, 8)) -> plt.Figure:
        """
        Plot feature importance.
        
        Parameters:
        -----------
        top_n : int, default=15
            Number of top features to display
        figsize : tuple, default=(10, 8)
            Figure size for the plot
            
        Returns:
        --------
        plt.Figure
            The generated figure
        """
        if not self.is_fitted or self.feature_importances_ is None:
            raise RuntimeError("Model must be fitted before plotting feature importance")
            
        fig, ax = plt.subplots(figsize=figsize)
        
        # Get top N features
        top_features = self.feature_importances_.head(top_n)
        
        # Create horizontal bar plot
        bars = ax.barh(range(len(top_features)), top_features['importance'])
        ax.set_yticks(range(len(top_features)))
        ax.set_yticklabels(top_features['feature'])
        ax.set_xlabel('Importance Score')
        ax.set_title(f'Top {top_n} Feature Importances - XGBoost')
        
        # Add value labels on bars
        for i, (bar, importance) in enumerate(zip(bars, top_features['importance'])):
            ax.text(bar.get_width() + 0.001, bar.get_y() + bar.get_height()/2, 
                   f'{importance:.3f}', va='center', fontsize=9)
        
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return fig
    
    def plot_training_progress(self, figsize: tuple = (10, 6)) -> plt.Figure:
        """
        Plot training progress if early stopping was used.
        
        Parameters:
        -----------
        figsize : tuple, default=(10, 6)
            Figure size for the plot
            
        Returns:
        --------
        plt.Figure
            The generated figure
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before plotting training progress")
        
        # Check if we have validation results
        evals_result = getattr(self.model, 'evals_result_', None)
        
        if evals_result is None:
            warnings.warn("No validation results available for plotting")
            return None
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot training and validation loss
        if 'validation_0' in evals_result:
            val_loss = evals_result['validation_0']['rmse']
            ax.plot(val_loss, label='Validation Loss', color='orange')
        
        if 'validation_1' in evals_result:
            train_loss = evals_result['validation_1']['rmse'] 
            ax.plot(train_loss, label='Training Loss', color='blue')
        
        # Mark best iteration
        if hasattr(self.model, 'best_iteration'):
            ax.axvline(x=self.model.best_iteration, color='red', 
                      linestyle='--', label=f'Best Iteration ({self.model.best_iteration})')
        
        ax.set_xlabel('Iteration')
        ax.set_ylabel('RMSE')
        ax.set_title('XGBoost Training Progress')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return fig
    
    def _serialize_model(self) -> Dict[str, Any]:
        """Serialize XGBoost model to JSON-compatible format."""
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before serialization")
            
        return {
            'model_params': self.model_params,
            'feature_importances': self.feature_importances_.to_dict('records') if self.feature_importances_ is not None else None,
            'training_samples': self.metadata.get('training_samples'),
            'n_features': self.metadata.get('n_features'),
            'best_iteration': self.metadata.get('best_iteration')
        }
    
    def _deserialize_model(self, model_data: Dict[str, Any]):
        """Deserialize XGBoost model from JSON."""
        # Reconstruct model with saved parameters
        self.model_params = model_data['model_params']
        self.model = xgb.XGBRegressor(**self.model_params)
        
        # Restore feature importances
        if model_data['feature_importances']:
            self.feature_importances_ = pd.DataFrame(model_data['feature_importances'])
        
        # Note: This is a simplified deserialization
        # For full model restoration, use pickle format
        warnings.warn("JSON deserialization for XGBoost is limited. "
                     "Use pickle format for complete model restoration.")
        
        self.is_fitted = True
