"""System check script to verify all dependencies and configurations"""

import sys
import os

def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} (Requires 3.8+)")
        return False

def check_dependencies():
    """Check if required Python packages are installed"""
    print("\nChecking Python dependencies...")
    dependencies = {
        'flask': 'Flask',
        'flask_sqlalchemy': 'Flask-SQLAlchemy',
        'torch': 'PyTorch',
        'clip': 'CLIP',
        'PIL': 'Pillow',
        'pytesseract': 'pytesseract',
        'numpy': 'NumPy',
        'sklearn': 'scikit-learn'
    }

    all_ok = True
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"✓ {name} (installed)")
        except ImportError:
            print(f"✗ {name} (not installed)")
            all_ok = False

    return all_ok

def check_tesseract():
    """Check if Tesseract OCR is installed"""
    print("\nChecking Tesseract OCR...")
    try:
        import pytesseract
        from PIL import Image
        pytesseract.get_tesseract_version()
        print(f"✓ Tesseract OCR (installed)")
        return True
    except Exception as e:
        print(f"✗ Tesseract OCR (not found or not in PATH)")
        print(f"  Error: {str(e)}")
        return False

def check_directories():
    """Check if required directories exist"""
    print("\nChecking directories...")
    directories = ['templates', 'static', 'static/css', 'static/js']
    all_ok = True

    for directory in directories:
        if os.path.exists(directory):
            print(f"✓ {directory}/ (exists)")
        else:
            print(f"✗ {directory}/ (missing)")
            all_ok = False

    return all_ok

def check_files():
    """Check if required files exist"""
    print("\nChecking required files...")
    files = [
        'app.py',
        'config.py',
        'utils.py',
        'init_database.py',
        'requirements.txt',
        'templates/base.html',
        'templates/login.html',
        'templates/gallery.html',
        'static/css/style.css',
        'static/js/main.js'
    ]

    all_ok = True
    for file in files:
        if os.path.exists(file):
            print(f"✓ {file} (exists)")
        else:
            print(f"✗ {file} (missing)")
            all_ok = False

    return all_ok

def main():
    print("="*60)
    print("Image Drive - System Check")
    print("="*60)

    results = []

    results.append(("Python Version", check_python_version()))
    results.append(("Dependencies", check_dependencies()))
    results.append(("Tesseract OCR", check_tesseract()))
    results.append(("Directories", check_directories()))
    results.append(("Required Files", check_files()))

    print("\n" + "="*60)
    print("Summary")
    print("="*60)

    all_passed = True
    for name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {name}: {status}")
        if not result:
            all_passed = False

    print("="*60)

    if all_passed:
        print("\n✓ All checks passed! System is ready.")
        print("\nYou can now:")
        print("  1. Initialize database: python init_database.py")
        print("  2. Run application: python app.py")
        print("  3. Or use the startup script: ./run.sh (Unix) or run.bat (Windows)")
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        print("\nTo install missing dependencies:")
        print("  pip install -r requirements.txt")
        print("\nTo install Tesseract OCR:")
        print("  macOS: brew install tesseract")
        print("  Ubuntu: sudo apt-get install tesseract-ocr")
        print("  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")

    print("="*60)
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
