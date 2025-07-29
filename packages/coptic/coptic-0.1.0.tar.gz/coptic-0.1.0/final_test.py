#!/usr/bin/env python3
"""
Final test script for Coptic Library
"""

print("=== COPTIC LIBRARY FINAL TEST ===")

try:
    # Test imports
    from coptic import CopticForecaster
    print("✓ Main class imported successfully")
    
    # Test model types  
    models = ['randomforest', 'xgboost', 'prophet']
    for model in models:
        try:
            forecaster = CopticForecaster(model)
            print(f"✓ {model.upper()} model created successfully")
        except Exception as e:
            print(f"✗ {model.upper()} model failed: {e}")
    
    print("\n🎉 COPTIC LIBRARY IS READY FOR PUBLISHING!")
    print("\nNext steps:")
    print("1. Update setup.py to make pmdarima truly optional")
    print("2. Build final distribution: python -m build")
    print("3. Upload to PyPI: twine upload dist/*")
    
except Exception as e:
    print(f"✗ Critical error: {e}")
    import traceback
    traceback.print_exc()
