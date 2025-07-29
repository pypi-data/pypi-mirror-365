# Coptic Library - Publishing Guide

This guide walks you through the complete process of building and publishing the Coptic forecasting library to PyPI.

## Prerequisites

1. **Python Environment**: Python 3.7 or higher
2. **PyPI Account**: Register at [pypi.org](https://pypi.org)
3. **PyPI API Token**: Generate from your PyPI account settings
4. **Required Tools**: Install build and upload tools

## Step 1: Install Build Tools

```bash
pip install --upgrade pip
pip install build twine
```

## Step 2: Prepare Your Environment

### Set up PyPI credentials

Create `~/.pypirc` file (Windows: `%USERPROFILE%\.pypirc`):

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

## Step 3: Test the Library Locally

Before publishing, ensure everything works:

```bash
# Navigate to the project directory
cd c:\PROJECTS\coptic

# Install in development mode
pip install -e .

# Run the test script
python test_installation.py

# Test with sample data
python -c "
from coptic import CopticForecaster
import pandas as pd
import numpy as np

# Create sample data
dates = pd.date_range('2023-01-01', periods=100, freq='D')
sales = 1000 + np.cumsum(np.random.randn(100) * 10)
df = pd.DataFrame({'date': dates, 'sales': sales})

# Test forecasting
forecaster = CopticForecaster('randomforest')
forecaster.fit(df, 'date', 'sales')
forecast = forecaster.predict(30)
print('✓ Library works correctly!')
print(f'Generated {len(forecast)} forecasts')
"
```

## Step 4: Build the Distribution

```bash
# Clean previous builds
rmdir /s build dist coptic.egg-info 2>nul

# Build source and wheel distributions
python -m build

# Verify build outputs
dir dist
```

You should see:
- `coptic-0.1.0.tar.gz` (source distribution)
- `coptic-0.1.0-py3-none-any.whl` (wheel distribution)

## Step 5: Test Upload to TestPyPI (Recommended)

```bash
# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ coptic

# Test the installed package
python -c "import coptic; print('Test installation successful!')"
```

## Step 6: Upload to PyPI

If TestPyPI works correctly:

```bash
# Upload to main PyPI
twine upload dist/*
```

## Step 7: Verify Publication

```bash
# Install from PyPI
pip uninstall coptic -y
pip install coptic

# Test installation
python -c "
from coptic import CopticForecaster
print(f'Coptic version: {coptic.__version__}')
print('✓ Successfully installed from PyPI!')
"
```

## Step 8: Create GitHub Release

1. **Tag the Release**:
```bash
git tag v0.1.0
git push origin v0.1.0
```

2. **Create Release on GitHub**:
   - Go to your repository on GitHub
   - Click "Releases" → "Create a new release"
   - Select the tag `v0.1.0`
   - Add release notes
   - Upload the distribution files from `dist/`

## Step 9: Update Documentation

Update the README.md with:
- Installation instructions
- PyPI badge
- Version information

## Troubleshooting

### Common Issues

1. **Import Errors**: Check all `__init__.py` files are present
2. **Missing Dependencies**: Verify `setup.py` and `requirements.txt`
3. **Version Conflicts**: Use virtual environment for testing
4. **Upload Errors**: Check PyPI token permissions

### Build Issues

```bash
# Clear Python cache
python -c "import py_compile; py_compile.compile('coptic/__init__.py')"

# Check package structure
python -c "
import setuptools
print(setuptools.find_packages())
"

# Validate setup.py
python setup.py check --metadata --strict
```

### Testing Commands

```bash
# Test specific model
python -c "
from coptic import CopticForecaster
import pandas as pd
import numpy as np

df = pd.DataFrame({
    'date': pd.date_range('2023-01-01', periods=50),
    'sales': np.random.randn(50).cumsum() + 100
})

# Test RandomForest
rf = CopticForecaster('randomforest', n_estimators=10)
rf.fit(df, 'date', 'sales')
forecast = rf.predict(10)
print('RandomForest: ✓')

# Test XGBoost
try:
    xgb = CopticForecaster('xgboost', n_estimators=10)
    xgb.fit(df, 'date', 'sales')
    forecast = xgb.predict(10)
    print('XGBoost: ✓')
except Exception as e:
    print(f'XGBoost: ✗ ({e})')

# Test Prophet
try:
    prophet = CopticForecaster('prophet')
    prophet.fit(df, 'date', 'sales')
    forecast = prophet.predict(10)
    print('Prophet: ✓')
except Exception as e:
    print(f'Prophet: ✗ ({e})')
"
```

## Version Management

For future releases:

1. **Update Version**: Modify version in `setup.py` and `pyproject.toml`
2. **Update Changelog**: Document changes
3. **Test Thoroughly**: Run all tests
4. **Build and Upload**: Follow steps 4-6
5. **Tag Release**: Create new git tag

## Example Release Script

```bash
# release.bat
@echo off
echo Building Coptic Library Release...

echo Step 1: Cleaning previous builds...
rmdir /s /q build dist coptic.egg-info 2>nul

echo Step 2: Building distributions...
python -m build

echo Step 3: Checking distributions...
twine check dist/*

echo Step 4: Testing upload (TestPyPI)...
twine upload --repository testpypi dist/*

echo Step 5: Ready for main PyPI upload
echo Run: twine upload dist/*

pause
```

## Post-Publication Checklist

- [ ] Verify package appears on PyPI
- [ ] Test installation: `pip install coptic`
- [ ] Update repository README badges
- [ ] Announce release
- [ ] Update documentation
- [ ] Plan next version features

## Support and Maintenance

- Monitor PyPI download statistics
- Address user issues promptly
- Maintain compatibility with dependencies
- Regular security updates
- Documentation improvements

---

🎉 **Congratulations!** Your Coptic library is now published and available to the Python community!
