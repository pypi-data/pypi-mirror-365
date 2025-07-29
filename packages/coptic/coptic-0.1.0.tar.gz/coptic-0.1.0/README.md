# Coptic - Advanced Time Series Forecasting Library

[![PyPI version](https://badge.fury.io/py/coptic.svg)](https://badge.fury.io/py/coptic)
[![Python versions](https://img.shields.io/pypi/pyversions/coptic.svg)](https://pypi.org/project/coptic/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://github.com/yourusername/coptic/workflows/CI/badge.svg)](https://github.com/yourusername/coptic/actions)

A comprehensive Python library for time series forecasting with multiple algorithms including Random Forest, XGBoost, Prophet, and ARIMA. Coptic provides a unified interface for different forecasting models with automatic feature engineering, data preprocessing, and comprehensive evaluation metrics.

## 🚀 Features

- **Multiple Algorithms**: Random Forest, XGBoost, Prophet, and ARIMA models
- **Unified API**: Single interface for all forecasting models
- **Automatic Feature Engineering**: Time-based features, lags, rolling statistics
- **Data Preprocessing**: Built-in data cleaning and outlier detection
- **Comprehensive Metrics**: MAE, RMSE, MAPE, SMAPE, MASE, and more
- **Visualization Tools**: Forecast plots, residual analysis, feature importance
- **Easy Model Comparison**: Compare multiple models effortlessly
- **Model Persistence**: Save and load trained models

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install coptic
```

### From Source

```bash
git clone https://github.com/yourusername/coptic.git
cd coptic
pip install -e .
```

### Dependencies

Coptic requires Python 3.7+ and the following packages:
- numpy >= 1.20.0
- pandas >= 1.2.0
- scikit-learn >= 0.24.0
- matplotlib >= 3.3.0
- xgboost >= 1.3.0
- prophet >= 1.0.0
- pmdarima >= 1.8.0
- statsmodels >= 0.12.0

## 🎯 Quick Start

### Basic Usage

```python
import pandas as pd
from coptic import CopticForecaster

# Load your time series data
df = pd.read_csv('your_data.csv')
# Ensure your data has date and target columns

# Create forecaster
forecaster = CopticForecaster(model_type="randomforest")

# Fit the model
forecaster.fit(df, date_col="date", target_col="sales")

# Generate forecasts
forecast = forecaster.predict(periods=30)

# Plot results
forecaster.plot()

# Evaluate performance (if you have test data)
test_metrics = forecaster.evaluate(test_df)
print(test_metrics)
```

### Advanced Usage

```python
from coptic import CopticForecaster
from coptic.preprocessing import DataCleaner

# Clean your data first
cleaner = DataCleaner(remove_outliers=True, outlier_method='iqr')
clean_df = cleaner.clean(df, date_col="date", target_col="sales")

# Create forecaster with custom parameters
forecaster = CopticForecaster(
    model_type="xgboost",
    n_estimators=200,
    learning_rate=0.1,
    max_depth=6
)

# Fit with validation data for early stopping
forecaster.fit(
    clean_df, 
    date_col="date", 
    target_col="sales",
    validation_data=val_df
)

# Generate forecasts with confidence intervals
forecast = forecaster.predict(periods=60, freq="D")

# Plot feature importance (for tree-based models)
forecaster.plot_feature_importance()

# Save the model
forecaster.save("my_forecaster.pkl")

# Load the model later
loaded_forecaster = CopticForecaster.load("my_forecaster.pkl")
```

## 🔧 Supported Models

### 1. Random Forest
```python
forecaster = CopticForecaster(
    model_type="randomforest",
    n_estimators=100,
    max_depth=None,
    random_state=42
)
```

### 2. XGBoost
```python
forecaster = CopticForecaster(
    model_type="xgboost",
    n_estimators=100,
    learning_rate=0.1,
    max_depth=6,
    early_stopping_rounds=10
)
```

### 3. Prophet
```python
forecaster = CopticForecaster(
    model_type="prophet",
    seasonality_mode='additive',
    yearly_seasonality=True,
    weekly_seasonality=True
)
```

### 4. ARIMA
```python
forecaster = CopticForecaster(
    model_type="arima",
    seasonal=True,
    m=12,  # seasonal period
    max_p=3,
    max_q=3
)
```

## 📊 Data Preprocessing

### Data Cleaning
```python
from coptic.preprocessing import DataCleaner

cleaner = DataCleaner(
    remove_outliers=True,
    outlier_method='iqr',  # 'iqr', 'zscore', 'isolation_forest'
    fill_method='interpolate'  # 'interpolate', 'forward_fill', 'mean'
)

clean_df = cleaner.clean(df, date_col="date", target_col="sales")

# Get data quality report
quality_report = cleaner.get_data_quality_report(df, "date", "sales")
```

### Feature Engineering
```python
from coptic.preprocessing import FeatureGenerator

feature_gen = FeatureGenerator(
    add_lags=True,
    add_seasonality=True,
    add_statistics=True,
    lag_periods=[1, 7, 30],
    rolling_windows=[7, 30, 90]
)

X, y = feature_gen.generate_features(df, "date", "sales")
```

## 📈 Evaluation and Visualization

### Comprehensive Metrics
```python
# Get detailed metrics
metrics = forecaster.evaluate(test_df)
print(f"MAE: {metrics['mae']:.2f}")
print(f"RMSE: {metrics['rmse']:.2f}")
print(f"MAPE: {metrics['mape']:.2f}%")
print(f"R²: {metrics['r2']:.3f}")

# Get forecast accuracy summary
from coptic.utils.metrics import forecast_accuracy_summary
summary = forecast_accuracy_summary(metrics)
print(summary)
```

### Visualization
```python
# Basic forecast plot
forecaster.plot()

# Plot with custom settings
forecaster.plot(plot_components=True, figsize=(15, 8))

# Residual analysis
from coptic.utils.plot import plot_residuals
plot_residuals(y_true, y_pred, dates=test_dates)

# Compare multiple models
from coptic.utils.plot import plot_multiple_forecasts
forecasts_dict = {
    'Random Forest': rf_forecast,
    'XGBoost': xgb_forecast,
    'Prophet': prophet_forecast
}
plot_multiple_forecasts(train_df, forecasts_dict)
```

## 🔍 Model Comparison

```python
models = {
    'RandomForest': CopticForecaster(model_type="randomforest"),
    'XGBoost': CopticForecaster(model_type="xgboost"),
    'Prophet': CopticForecaster(model_type="prophet"),
    'ARIMA': CopticForecaster(model_type="arima")
}

results = {}
for name, model in models.items():
    model.fit(train_df, date_col="date", target_col="sales")
    forecast = model.predict(periods=30)
    metrics = model.evaluate(test_df)
    results[name] = metrics

# Compare results
comparison_df = pd.DataFrame(results).T
print(comparison_df[['mae', 'rmse', 'mape', 'r2']])
```

## 📚 Examples

Check out our [example notebooks](examples/) for detailed tutorials:

- [Getting Started with Coptic](examples/01_getting_started.ipynb)
- [Sales Forecasting Example](examples/02_sales_forecasting.ipynb)
- [Model Comparison Tutorial](examples/03_model_comparison.ipynb)
- [Advanced Feature Engineering](examples/04_feature_engineering.ipynb)
- [Custom Seasonality with Prophet](examples/05_prophet_seasonality.ipynb)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/yourusername/coptic.git
cd coptic
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black coptic/
flake8 coptic/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [coptic.readthedocs.io](https://coptic.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/yourusername/coptic/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/coptic/discussions)

## 🎉 Acknowledgments

- Built on top of excellent libraries: scikit-learn, XGBoost, Prophet, pmdarima
- Inspired by the forecasting community and real-world use cases
- Thanks to all contributors and users

## 🚀 What's Next?

- [ ] Deep learning models (LSTM, Transformer)
- [ ] Automated hyperparameter optimization
- [ ] Ensemble methods
- [ ] More preprocessing options
- [ ] Streaming forecasts
- [ ] Cloud deployment tools

---

**Made with ❤️ by the Coptic Team**
