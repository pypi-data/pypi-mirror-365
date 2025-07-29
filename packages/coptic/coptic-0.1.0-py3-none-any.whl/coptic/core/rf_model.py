"""
Random Forest implementation for time series forecasting.

This module provides a Random Forest-based forecasting model with
feature engineering and prediction intervals.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import warnings

from .base_model import BaseModel
from ..preprocessing.features import FeatureGenerator


class RandomForestModel(BaseModel):
    """
    Random Forest implementation for time series forecasting.
    
    This model uses a Random Forest regressor with automatically generated
    time-based features for forecasting. It supports feature importance
    analysis and prediction intervals through quantile regression.
    
    Attributes:
        n_estimators (int): Number of trees in the forest
        max_depth (int): Maximum depth of trees
        random_state (int): Random state for reproducibility
        model (RandomForestRegressor): The trained model
        feature_generator (FeatureGenerator): Feature engineering pipeline
        feature_importances_ (pd.DataFrame): Feature importance scores
    """
    
    def __init__(self, 
                 n_estimators: int = 100,
                 max_depth: Optional[int] = None,
                 min_samples_split: int = 2,
                 min_samples_leaf: int = 1,
                 random_state: Optional[int] = 42,
                 **kwargs):
        """
        Initialize the Random Forest model.
        
        Parameters:
        -----------
        n_estimators : int, default=100
            Number of trees in the forest
        max_depth : int, optional
            Maximum depth of trees (None for unlimited)
        min_samples_split : int, default=2
            Minimum samples required to split an internal node
        min_samples_leaf : int, default=1
            Minimum samples required at a leaf node
        random_state : int, optional
            Random state for reproducibility
        **kwargs : dict
            Additional parameters for the base class
        """
        super().__init__(**kwargs)
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.random_state = random_state
        
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            random_state=random_state,
            n_jobs=-1  # Use all available cores
        )
        
        self.feature_generator = FeatureGenerator()
        self.feature_importances_ = None
    
    def fit(self, df: pd.DataFrame, 
            date_col: str, 
            target_col: str, 
            validation_data: Optional[pd.DataFrame] = None):
        """
        Fit the Random Forest model to the training data.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Training dataframe
        date_col : str
            Name of the date column
        target_col : str
            Name of the target column
        validation_data : pd.DataFrame, optional
            Validation data (not used for Random Forest, kept for API consistency)
        """
        # Call parent fit method for validation
        super().fit(df, date_col, target_col, validation_data)
        
        # Generate features
        X, y = self.feature_generator.generate_features(df, date_col, target_col)
        
        # Remove rows with NaN values
        valid_mask = X.notna().all(axis=1) & y.notna()
        X_clean = X[valid_mask]
        y_clean = y[valid_mask]
        
        if len(X_clean) == 0:
            raise ValueError("No valid samples found after feature generation")
        
        # Train the model
        self.model.fit(X_clean, y_clean)
        
        # Store feature importances
        self.feature_importances_ = pd.DataFrame({
            'feature': X_clean.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Store clean training data for plotting
        self.X_train = X_clean
        self.y_train = y_clean
        
        self.is_fitted = True
        self.metadata.update({
            'training_completed': pd.Timestamp.now().isoformat(),
            'training_samples': len(X_clean),
            'n_features': len(X_clean.columns)
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
            Not used for Random Forest (kept for API consistency)
            
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
        )[1:]  # Exclude the last_date
        
        future_df = pd.DataFrame({self.date_col: future_dates})
        
        # For prediction, we need to create a combined dataframe for lag features
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
        
        # Calculate prediction intervals using quantile regression approach
        predictions_list = []
        for tree in self.model.estimators_:
            tree_pred = tree.predict(X_future)
            predictions_list.append(tree_pred)
        
        # Convert to array for easier computation
        all_predictions = np.array(predictions_list)
        
        # Calculate quantiles
        yhat_lower = np.percentile(all_predictions, 5, axis=0)
        yhat_upper = np.percentile(all_predictions, 95, axis=0)
        
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
        ax.set_title(f'Top {top_n} Feature Importances - Random Forest')
        
        # Add value labels on bars
        for i, (bar, importance) in enumerate(zip(bars, top_features['importance'])):
            ax.text(bar.get_width() + 0.001, bar.get_y() + bar.get_height()/2, 
                   f'{importance:.3f}', va='center', fontsize=9)
        
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return fig
    
    def get_prediction_intervals(self, confidence_level: float = 0.95) -> pd.DataFrame:
        """
        Get prediction intervals for the latest forecast.
        
        Parameters:
        -----------
        confidence_level : float, default=0.95
            Confidence level for prediction intervals
            
        Returns:
        --------
        pd.DataFrame
            DataFrame with prediction intervals
        """
        if not hasattr(self, 'forecast_df'):
            raise RuntimeError("Make predictions before getting intervals")
        
        alpha = 1 - confidence_level
        lower_quantile = (alpha / 2) * 100
        upper_quantile = (1 - alpha / 2) * 100
        
        return self.forecast_df[[
            self.date_col, 'yhat', 'yhat_lower', 'yhat_upper'
        ]].copy()
    
    def _serialize_model(self) -> Dict[str, Any]:
        """Serialize Random Forest model to JSON-compatible format."""
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before serialization")
            
        # Note: Full sklearn model serialization to JSON is complex
        # This is a simplified version - for production use pickle format
        return {
            'model_params': {
                'n_estimators': self.n_estimators,
                'max_depth': self.max_depth,
                'min_samples_split': self.min_samples_split,
                'min_samples_leaf': self.min_samples_leaf,
                'random_state': self.random_state
            },
            'feature_importances': self.feature_importances_.to_dict('records') if self.feature_importances_ is not None else None,
            'training_samples': self.metadata.get('training_samples'),
            'n_features': self.metadata.get('n_features')
        }
    
    def _deserialize_model(self, model_data: Dict[str, Any]):
        """Deserialize Random Forest model from JSON."""
        # Reconstruct model with saved parameters
        params = model_data['model_params']
        self.model = RandomForestRegressor(**params, n_jobs=-1)
        
        # Restore feature importances
        if model_data['feature_importances']:
            self.feature_importances_ = pd.DataFrame(model_data['feature_importances'])
        
        # Note: This is a simplified deserialization
        # For full model restoration, use pickle format
        warnings.warn("JSON deserialization for Random Forest is limited. "
                     "Use pickle format for complete model restoration.")
        
        self.is_fitted = True
    
    def cross_validate(self, df: pd.DataFrame, 
                      date_col: str, 
                      target_col: str,
                      n_splits: int = 5) -> Dict[str, float]:
        """
        Perform time series cross-validation.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Input dataframe
        date_col : str
            Name of the date column
        target_col : str
            Name of the target column
        n_splits : int, default=5
            Number of CV splits
            
        Returns:
        --------
        dict
            Cross-validation scores
        """
        from ..utils.metrics import calculate_metrics
        
        # Generate features
        X, y = self.feature_generator.generate_features(df, date_col, target_col)
        
        # Remove rows with NaN values
        valid_mask = X.notna().all(axis=1) & y.notna()
        X_clean = X[valid_mask]
        y_clean = y[valid_mask]
        
        # Time series split
        n_samples = len(X_clean)
        test_size = n_samples // (n_splits + 1)
        
        scores = []
        for i in range(n_splits):
            # Split data
            train_end = n_samples - (n_splits - i) * test_size
            test_start = train_end
            test_end = test_start + test_size
            
            X_train_cv = X_clean.iloc[:train_end]
            y_train_cv = y_clean.iloc[:train_end]
            X_test_cv = X_clean.iloc[test_start:test_end]
            y_test_cv = y_clean.iloc[test_start:test_end]
            
            # Train and predict
            model_cv = RandomForestRegressor(**self.model.get_params())
            model_cv.fit(X_train_cv, y_train_cv)
            y_pred_cv = model_cv.predict(X_test_cv)
            
            # Calculate metrics
            fold_metrics = calculate_metrics(y_test_cv, y_pred_cv)
            scores.append(fold_metrics)
        
        # Average scores
        avg_scores = {}
        for metric in scores[0].keys():
            avg_scores[f'cv_{metric}'] = np.mean([score[metric] for score in scores])
            avg_scores[f'cv_{metric}_std'] = np.std([score[metric] for score in scores])
        
        return avg_scores
