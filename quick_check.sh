#!/bin/bash

# Quick check script for Image Drive

echo "================================"
echo "IMAGE DRIVE - QUICK CHECK"
echo "================================"
echo ""

# Check if venv exists
if [ -d "venv" ]; then
    echo "✓ Virtual environment found"

    # Activate venv and run diagnose.py
    source venv/bin/activate

    echo "Running diagnostic script..."
    echo ""
    python diagnose.py

else
    echo "✗ Virtual environment not found"
    echo ""
    echo "Please run: ./run.sh"
    echo "This will create the virtual environment and install dependencies."
fi
