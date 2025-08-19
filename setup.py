#!/usr/bin/env python3
"""
Setup script for Fantasy Football Analytics Tool.
Automatically creates virtual environment and installs dependencies.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")


def create_virtual_environment():
    """Create a virtual environment."""
    venv_path = Path(".venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return venv_path
    
    print("🔧 Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        print("✅ Virtual environment created successfully")
        return venv_path
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating virtual environment: {e}")
        sys.exit(1)


def get_venv_python():
    """Get the path to the virtual environment Python executable."""
    return Path(".venv/bin/python")


def get_venv_pip():
    """Get the path to the virtual environment pip executable."""
    return Path(".venv/bin/pip")


def install_dependencies():
    """Install dependencies from requirements.txt."""
    pip_path = get_venv_pip()
    
    if not pip_path.exists():
        print(f"❌ Error: pip not found at {pip_path}")
        sys.exit(1)
    
    print("📦 Installing dependencies...")
    try:
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        sys.exit(1)


def create_activation_script():
    """Create activation script for Unix/Linux/macOS."""
    # Unix activation script
    with open("activate_env.sh", "w") as f:
        f.write("#!/bin/bash\n")
        f.write("echo 'Activating virtual environment...'\n")
        f.write("source .venv/bin/activate\n")
        f.write("echo 'Virtual environment activated!'\n")
        f.write("echo 'You can now run: python train_baseline.py'\n")
    
    # Make the script executable
    os.chmod("activate_env.sh", 0o755)
    print("✅ Created activate_env.sh")


def main():
    """Main setup function."""
    print("🏈 Setting up Fantasy Football Analytics Tool")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Create virtual environment
    venv_path = create_virtual_environment()
    
    # Install dependencies
    install_dependencies()
    
    # Create activation scripts
    create_activation_script()
    
    print("\n" + "=" * 50)
    print("🎉 Setup complete!")
    print("=" * 50)
    
    print("\nTo activate the virtual environment:")
    print("  source activate_env.sh")
    print("  OR")
    print("  source .venv/bin/activate")
    
    print("\nAfter activation, you can run:")
    print("  python scripts/train_baseline.py          # Train with sample data")
    print("  python scripts/train_with_real_data.py    # Train with real NFL data")
    print("  python scripts/predict.py                 # Make predictions")
    print("  python scripts/interactive_predictor.py   # Interactive predictions")
    print("  python -m pytest tests/                   # Run tests")


if __name__ == "__main__":
    main()
