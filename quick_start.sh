#!/bin/bash

# Fantasy Football Analytics Tool - Quick Start Script
# This script automatically sets up the virtual environment and installs dependencies

echo "🏈 Fantasy Football Analytics Tool - Quick Start"
echo "================================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher and try again"
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $python_version detected"

# Run the setup script
echo "🔧 Running setup script..."
python3 setup.py

# Activate the virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

echo ""
echo "🎉 Setup complete! Your virtual environment is now active."
echo ""
echo "You can now run:"
echo "  python train_baseline.py          # Train with sample data"
echo "  python train_with_real_data.py    # Train with real NFL data"
echo "  python predict.py                 # Make predictions"
echo "  python -m pytest tests/           # Run tests"
echo ""
echo "To deactivate the virtual environment later, run:"
echo "  deactivate"
