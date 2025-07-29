"""
Simple test script to verify coptic installation and basic functionality.
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def test_basic_import():
    """Test basic imports."""
    try:
        from coptic import CopticForecaster
        from coptic.preprocessing import DataCleaner, FeatureGenerator
        from coptic.utils.metrics import calculate_metrics
        from coptic.utils.plot import plot_forecast
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def create_sample_data():
    """Create sample time series data."""
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    
    # Create synthetic sales data with trend and seasonality
    trend = np.linspace(1000, 2000, len(dates))
    seasonal = 200 * np.sin(2 * np.pi * np.arange(len(dates)) / 365.25)
    weekly = 100 * np.sin(2 * np.pi * np.arange(len(dates)) / 7)
    noise = np.random.normal(0, 50, len(dates))
    
    sales = trend + seasonal + weekly + noise
    
    df = pd.DataFrame({
        'date': dates,
        'sales': sales
    })
    
    return df

def test_data_cleaning():
    """Test data cleaning functionality."""
    try:
        from coptic.preprocessing import DataCleaner
        
        df = create_sample_data()
        
        cleaner = DataCleaner()
        df_clean = cleaner.clean(df, 'date', 'sales')
        
        print(f"✓ Data cleaning successful: {len(df_clean)} rows processed")
        return True, df_clean
    except Exception as e:
        print(f"✗ Data cleaning failed: {e}")
        return False, None

def test_forecasting():
    """Test basic forecasting functionality."""
    try:
        from coptic import CopticForecaster
        
        # Use sample data
        df = create_sample_data()
        
        # Split data
        split_idx = int(len(df) * 0.8)
        train_df = df[:split_idx]
        
        # Test Random Forest model (most reliable)
        forecaster = CopticForecaster(model_type="randomforest", n_estimators=10)
        forecaster.fit(train_df, date_col='date', target_col='sales')
        
        # Generate forecast
        forecast = forecaster.predict(periods=30)
        
        print(f"✓ Forecasting successful: {len(forecast)} predictions generated")
        
        # Test model info (optional features)
        try:
            importance = forecaster.get_feature_importance()
            if importance is not None and len(importance) > 0:
                print(f"  Feature importance available: {len(importance)} features")
        except Exception:
            print("  Feature importance not available for this model")
        
        return True
    except Exception as e:
        print(f"✗ Forecasting failed: {e}")
        return False

def test_metrics():
    """Test metrics calculation."""
    try:
        from coptic.utils.metrics import calculate_metrics
        
        # Generate sample predictions
        y_true = np.random.normal(100, 20, 50)
        y_pred = y_true + np.random.normal(0, 5, 50)  # Add some prediction error
        
        metrics = calculate_metrics(y_true, y_pred)
        
        print(f"✓ Metrics calculation successful")
        print(f"  MAE: {metrics.get('mae', 0):.2f}")
        print(f"  RMSE: {metrics.get('rmse', 0):.2f}")
        print(f"  R²: {metrics.get('r2', 0):.3f}")
        
        return True
    except Exception as e:
        print(f"✗ Metrics calculation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing Coptic Library Installation")
    print("=" * 40)
    
    # Test imports
    if not test_basic_import():
        print("\n❌ Basic imports failed. Please check installation.")
        return False
    
    # Test data cleaning
    data_clean_success, _ = test_data_cleaning()
    
    # Test forecasting
    forecast_success = test_forecasting()
    
    # Test metrics
    metrics_success = test_metrics()
    
    print("\n" + "=" * 40)
    
    if all([data_clean_success, forecast_success, metrics_success]):
        print("🎉 All tests passed! Coptic library is working correctly.")
        print("\nNext steps:")
        print("1. Check out the example notebook: examples/sales_forecast.ipynb")
        print("2. Load your own data and start forecasting!")
        return True
    else:
        print("❌ Some tests failed. Please check your installation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
