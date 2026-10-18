#!/bin/bash

# Quick setup script for online search

echo "================================================"
echo "IMAGE DRIVE - ONLINE SEARCH QUICK SETUP"
echo "================================================"
echo ""

# Check if requests is installed
if python3 -c "import requests" 2>/dev/null; then
    echo "✓ requests library is installed"
else
    echo "✗ requests library not found"
    echo "Installing requests..."
    pip install requests
fi

echo ""
echo "================================================"
echo "API KEY CONFIGURATION"
echo "================================================"
echo ""

# Check current configuration
if [ -n "$UNSPLASH_ACCESS_KEY" ]; then
    echo "✓ UNSPLASH_ACCESS_KEY is set"
else
    echo "✗ UNSPLASH_ACCESS_KEY not configured"
    echo ""
    echo "To get your Unsplash API key:"
    echo "1. Visit: https://unsplash.com/developers"
    echo "2. Register and create an application"
    echo "3. Copy your Access Key"
    echo ""
    read -p "Paste your Unsplash Access Key (or press Enter to skip): " key
    if [ -n "$key" ]; then
        export UNSPLASH_ACCESS_KEY="$key"
        echo "✓ Unsplash API key configured for this session"
        echo ""
        echo "To make it permanent, add this to your ~/.zshrc or ~/.bashrc:"
        echo "export UNSPLASH_ACCESS_KEY=\"$key\""
    fi
fi

if [ -n "$PEXELS_API_KEY" ]; then
    echo "✓ PEXELS_API_KEY is set"
fi

if [ -n "$PIXABAY_API_KEY" ]; then
    echo "✓ PIXABAY_API_KEY is set"
fi

echo ""
echo "================================================"
echo "READY TO START"
echo "================================================"
echo ""

if [ -n "$UNSPLASH_ACCESS_KEY" ] || [ -n "$PEXELS_API_KEY" ] || [ -n "$PIXABAY_API_KEY" ]; then
    echo "✓ At least one API provider is configured"
    echo ""
    echo "Starting Image Drive..."
    echo "Access at: http://localhost:5000"
    echo ""
    echo "In the Gallery page:"
    echo "  1. Select 'Online' or 'Both (Hybrid)' in the dropdown"
    echo "  2. Enter a search term (e.g., 'sunset', 'dog', 'mountain')"
    echo "  3. Click 'Search'"
    echo ""
    python app.py
else
    echo "⚠  No API keys configured!"
    echo ""
    echo "You can still use the app, but online search won't work."
    echo "Please read ONLINE_SEARCH_SETUP.md for configuration instructions."
    echo ""
    read -p "Start anyway? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python app.py
    fi
fi
