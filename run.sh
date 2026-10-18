#!/bin/bash

# Image Drive startup script for Unix/Linux/macOS

echo "================================"
echo "Image Drive - Startup Script"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "Virtual environment created!"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
if [ ! -f ".requirements_installed" ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
    touch .requirements_installed
    echo "Requirements installed!"
fi

# Check if database is initialized
if [ ! -f "image_drive.db" ]; then
    echo ""
    echo "Database not found. Initializing..."
    python init_database.py
fi

# Start the application
echo ""
echo "Starting Image Drive..."
echo "Access the application at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""
python app.py
