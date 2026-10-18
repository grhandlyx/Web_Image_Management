#!/bin/bash

# Installation script for Image Drive dependencies

echo "========================================="
echo "IMAGE DRIVE - DEPENDENCY INSTALLER"
echo "========================================="
echo ""

# Check if running in virtualenv
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠  Warning: Not running in a virtual environment"
    echo "It's recommended to use a virtual environment."
    echo ""
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 1: Install Python dependencies
echo "Step 1/2: Installing Python dependencies..."
echo "-------------------------------------------"
pip install --upgrade pip
pip install Flask Flask-SQLAlchemy Werkzeug Pillow numpy scikit-learn pytesseract

# Step 2: Install PyTorch (CPU version for compatibility)
echo ""
echo "Step 2/2: Installing PyTorch..."
echo "-------------------------------------------"
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Step 3: Install CLIP
echo ""
echo "Step 3/3: Installing CLIP model..."
echo "-------------------------------------------"
pip install ftfy regex tqdm
pip install git+https://github.com/openai/CLIP.git

# Step 4: Check Tesseract OCR
echo ""
echo "========================================="
echo "CHECKING TESSERACT OCR"
echo "========================================="

if command -v tesseract &> /dev/null; then
    TESSERACT_VERSION=$(tesseract --version 2>&1 | head -n 1)
    echo "✓ Tesseract is installed: $TESSERACT_VERSION"
else
    echo "✗ Tesseract OCR is NOT installed"
    echo ""
    echo "To install Tesseract:"
    echo "  macOS:   brew install tesseract"
    echo "  Ubuntu:  sudo apt-get install tesseract-ocr"
    echo "  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
    echo ""
    echo "⚠  OCR features will not work without Tesseract!"
fi

echo ""
echo "========================================="
echo "INSTALLATION SUMMARY"
echo "========================================="
echo "✓ Python dependencies installed"
echo "✓ PyTorch installed"
echo "✓ CLIP model installed"

if command -v tesseract &> /dev/null; then
    echo "✓ Tesseract OCR available"
else
    echo "⚠  Tesseract OCR needs to be installed separately"
fi

echo ""
echo "Installation complete!"
echo ""
echo "Next steps:"
echo "1. If Tesseract is not installed, install it using the commands above"
echo "2. Run: python app.py"
echo "3. Open: http://localhost:5000"
echo ""
