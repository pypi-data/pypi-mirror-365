@echo off
REM Coptic Library Release Script
REM This script automates the building and publishing process

echo ====================================
echo    Coptic Library Release Script
echo ====================================
echo.

REM Check if we're in the right directory
if not exist "setup.py" (
    echo Error: setup.py not found. Please run this script from the project root.
    pause
    exit /b 1
)

REM Step 1: Clean previous builds
echo Step 1: Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "coptic.egg-info" rmdir /s /q coptic.egg-info
echo ✓ Cleaned build directories

REM Step 2: Install/upgrade build tools
echo.
echo Step 2: Installing build tools...
pip install --upgrade pip build twine
echo ✓ Build tools updated

REM Step 3: Build distributions
echo.
echo Step 3: Building distributions...
python -m build
if %errorlevel% neq 0 (
    echo ✗ Build failed!
    pause
    exit /b 1
)
echo ✓ Distributions built successfully

REM Step 4: Check distributions
echo.
echo Step 4: Checking distributions...
twine check dist/*
if %errorlevel% neq 0 (
    echo ✗ Distribution check failed!
    pause
    exit /b 1
)
echo ✓ Distributions are valid

REM Step 5: List built files
echo.
echo Step 5: Built files:
dir dist /b
echo.

REM Step 6: Test installation locally
echo Step 6: Testing local installation...
pip install -e . --quiet
python -c "import coptic; print('✓ Local installation test passed')"
if %errorlevel% neq 0 (
    echo ✗ Local installation test failed!
    pause
    exit /b 1
)

REM Step 7: Run basic functionality test
echo.
echo Step 7: Running functionality test...
python -c "
import sys
try:
    from coptic import CopticForecaster
    import pandas as pd
    import numpy as np
    
    # Quick test
    df = pd.DataFrame({
        'date': pd.date_range('2023-01-01', periods=30),
        'sales': np.random.randn(30).cumsum() + 100
    })
    
    forecaster = CopticForecaster('randomforest', n_estimators=5)
    forecaster.fit(df, 'date', 'sales')
    forecast = forecaster.predict(5)
    
    print(f'✓ Functionality test passed - Generated {len(forecast)} forecasts')
except Exception as e:
    print(f'✗ Functionality test failed: {e}')
    sys.exit(1)
"
if %errorlevel% neq 0 (
    echo ✗ Functionality test failed!
    pause
    exit /b 1
)

echo.
echo ====================================
echo    BUILD COMPLETED SUCCESSFULLY!
echo ====================================
echo.
echo Next steps:
echo 1. Test upload to TestPyPI:
echo    twine upload --repository testpypi dist/*
echo.
echo 2. If successful, upload to PyPI:
echo    twine upload dist/*
echo.
echo 3. Test installation from PyPI:
echo    pip install coptic
echo.

REM Ask user what to do next
echo.
set /p choice="Do you want to upload to TestPyPI now? (y/n): "
if /i "%choice%"=="y" (
    echo.
    echo Uploading to TestPyPI...
    twine upload --repository testpypi dist/*
    if %errorlevel% neq 0 (
        echo ✗ TestPyPI upload failed!
        pause
        exit /b 1
    )
    echo ✓ Successfully uploaded to TestPyPI
    echo.
    echo Test installation with:
    echo pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ coptic
    echo.
    
    set /p choice2="Upload to main PyPI? (y/n): "
    if /i "%choice2%"=="y" (
        echo.
        echo Uploading to PyPI...
        twine upload dist/*
        if %errorlevel% neq 0 (
            echo ✗ PyPI upload failed!
            pause
            exit /b 1
        )
        echo.
        echo ====================================
        echo    🎉 SUCCESSFULLY PUBLISHED! 🎉
        echo ====================================
        echo.
        echo Your library is now available at:
        echo https://pypi.org/project/coptic/
        echo.
        echo Install with: pip install coptic
    )
)

echo.
pause
