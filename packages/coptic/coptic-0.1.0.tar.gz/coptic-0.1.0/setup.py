"""
Coptic - Advanced Time Series Forecasting Library
================================================

A comprehensive Python library for time series forecasting with multiple 
algorithms including Random Forest, XGBoost, Prophet, and ARIMA.

Features:
- Multiple forecasting algorithms (Random Forest, XGBoost, Prophet, ARIMA)
- Automatic feature engineering
- Built-in data cleaning and preprocessing
- Comprehensive evaluation metrics
- Visualization tools
- Easy-to-use unified API

Quick Start:
    >>> from coptic import CopticForecaster
    >>> forecaster = CopticForecaster(model_type="randomforest")
    >>> forecaster.fit(df, date_col="date", target_col="sales")
    >>> forecast = forecaster.predict(periods=30)
    >>> forecaster.plot()

GitHub: https://github.com/yourusername/coptic
Documentation: https://coptic.readthedocs.io
"""

from setuptools import setup, find_packages
import pathlib

# Read README
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="coptic",
    version="0.1.0",
    author="Coptic Team",
    author_email="contact@coptic-forecasting.com",
    description="Advanced time series forecasting library with multiple algorithms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/coptic",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/coptic/issues",
        "Source": "https://github.com/yourusername/coptic",
        "Documentation": "https://coptic.readthedocs.io",
    },
    packages=find_packages(exclude=["tests*", "docs*", "examples*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.2.0",
        "scikit-learn>=0.24.0",
        "matplotlib>=3.3.0",
        "xgboost>=1.3.0",
        "prophet>=1.0.0",
        "statsmodels>=0.12.0",
    ],
    extras_require={
        "arima": ["pmdarima>=1.8.0"],
        "all": ["pmdarima>=1.8.0"],
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "sphinx>=4.0",
            "mypy>=0.900",
            "jupyter>=1.0",
            "notebook>=6.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=0.5.0",
            "sphinxcontrib-napoleon>=0.7",
        ],
        "examples": [
            "jupyter>=1.0",
            "seaborn>=0.11.0",
            "plotly>=5.0",
        ],
        "all": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "sphinx>=4.0",
            "mypy>=0.900",
            "jupyter>=1.0",
            "notebook>=6.0",
            "sphinx-rtd-theme>=0.5.0",
            "sphinxcontrib-napoleon>=0.7",
            "seaborn>=0.11.0",
            "plotly>=5.0",
        ]
    },
    include_package_data=True,
    keywords=[
        "time-series", "forecasting", "machine-learning", 
        "prophet", "arima", "xgboost", "random-forest",
        "data-science", "analytics", "prediction"
    ],
    entry_points={
        "console_scripts": [
            # Could add CLI tools here in the future
        ],
    },
    zip_safe=False,
)
