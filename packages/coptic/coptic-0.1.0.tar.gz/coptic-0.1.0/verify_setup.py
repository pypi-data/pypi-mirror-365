"""
Coptic Library Setup Verification
================================

This script verifies that the Coptic library is properly set up
and ready for publishing.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a required file exists."""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description}: {filepath} - MISSING")
        return False

def check_python_syntax(filepath):
    """Check if a Python file has valid syntax."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            compile(f.read(), filepath, 'exec')
        print(f"✓ Syntax check: {filepath}")
        return True
    except SyntaxError as e:
        print(f"✗ Syntax error in {filepath}: {e}")
        return False
    except Exception as e:
        print(f"✗ Error checking {filepath}: {e}")
        return False

def check_imports():
    """Check if all required packages can be imported."""
    required_imports = [
        'numpy',
        'pandas', 
        'sklearn',
        'matplotlib',
        'xgboost',
        'prophet',
        'statsmodels'
    ]
    
    optional_imports = [
        'pmdarima'  # Optional for ARIMA models
    ]
    
    print("\nChecking required dependencies:")
    all_good = True
    
    for package in required_imports:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - NOT INSTALLED")
            all_good = False
    
    print("\nOptional dependencies:")
    for package in optional_imports:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"○ {package} - optional (not installed)")
    
    return all_good

def verify_package_structure():
    """Verify the package has the correct structure."""
    print("\nChecking package structure:")
    
    required_files = [
        ('setup.py', 'Setup configuration'),
        ('pyproject.toml', 'Build configuration'),
        ('requirements.txt', 'Dependencies list'),
        ('README.md', 'Documentation'),
        ('LICENSE', 'License file'),
        ('coptic/__init__.py', 'Main package init'),
        ('coptic/core/__init__.py', 'Core package init'),
        ('coptic/core/base_model.py', 'Base model class'),
        ('coptic/core/rf_model.py', 'Random Forest model'),
        ('coptic/core/xgb_model.py', 'XGBoost model'),
        ('coptic/core/prophet_model.py', 'Prophet model'),
        ('coptic/core/arima_model.py', 'ARIMA model'),
        ('coptic/preprocessing/__init__.py', 'Preprocessing package init'),
        ('coptic/preprocessing/features.py', 'Feature engineering'),
        ('coptic/preprocessing/cleaner.py', 'Data cleaning'),
        ('coptic/utils/__init__.py', 'Utils package init'),
        ('coptic/utils/metrics.py', 'Evaluation metrics'),
        ('coptic/utils/plot.py', 'Plotting utilities'),
    ]
    
    all_files_exist = True
    for filepath, description in required_files:
        if not check_file_exists(filepath, description):
            all_files_exist = False
    
    return all_files_exist

def verify_python_syntax():
    """Check syntax of all Python files."""
    print("\nChecking Python syntax:")
    
    python_files = [
        'setup.py',
        'coptic/__init__.py',
        'coptic/core/__init__.py',
        'coptic/core/base_model.py',
        'coptic/core/rf_model.py',
        'coptic/core/xgb_model.py',
        'coptic/core/prophet_model.py',
        'coptic/core/arima_model.py',
        'coptic/preprocessing/__init__.py',
        'coptic/preprocessing/features.py',
        'coptic/preprocessing/cleaner.py',
        'coptic/utils/__init__.py',
        'coptic/utils/metrics.py',
        'coptic/utils/plot.py',
    ]
    
    all_syntax_ok = True
    for filepath in python_files:
        if os.path.exists(filepath):
            if not check_python_syntax(filepath):
                all_syntax_ok = False
        else:
            print(f"✗ File not found: {filepath}")
            all_syntax_ok = False
    
    return all_syntax_ok

def test_build():
    """Test if the package can be built."""
    print("\nTesting package build:")
    
    try:
        result = subprocess.run([
            sys.executable, '-c', 
            'import setuptools; print("setuptools available")'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✓ Build tools are available")
            return True
        else:
            print(f"✗ Build tools check failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Build tools check timed out")
        return False
    except Exception as e:
        print(f"✗ Build tools check error: {e}")
        return False

def test_local_import():
    """Test if the package can be imported locally."""
    print("\nTesting local import:")
    
    try:
        # Add current directory to Python path
        current_dir = os.getcwd()
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Try to import the main package
        import coptic
        print(f"✓ Successfully imported coptic (version: {getattr(coptic, '__version__', 'unknown')})")
        
        # Try to import main class
        from coptic import CopticForecaster
        print("✓ Successfully imported CopticForecaster")
        
        # Quick instantiation test
        forecaster = CopticForecaster('randomforest')
        print("✓ Successfully created CopticForecaster instance")
        
        return True
        
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False

def main():
    """Run all verification checks."""
    print("Coptic Library Setup Verification")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists('setup.py'):
        print("✗ Error: setup.py not found. Please run this script from the project root.")
        return False
    
    print(f"Project directory: {os.getcwd()}")
    
    checks = [
        ("Package Structure", verify_package_structure),
        ("Python Syntax", verify_python_syntax),
        ("Dependencies", check_imports),
        ("Build Tools", test_build),
        ("Local Import", test_local_import),
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        print("-" * len(check_name))
        
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"✗ {check_name} check failed with error: {e}")
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 ALL CHECKS PASSED! Your library is ready for publishing.")
        print("\nNext steps:")
        print("1. Run 'python -m build' to build distributions")
        print("2. Run 'twine check dist/*' to validate")
        print("3. Run 'twine upload --repository testpypi dist/*' to test upload")
        print("4. Run 'twine upload dist/*' to publish to PyPI")
    else:
        print("❌ Some checks failed. Please fix the issues before publishing.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
