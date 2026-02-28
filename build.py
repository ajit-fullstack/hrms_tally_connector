#!/usr/bin/env python3
"""
Build script for Accounting Connector
"""

import PyInstaller.__main__
import os
import sys

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building Accounting Connector executable...")
    
    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # PyInstaller arguments
    args = [
        'main.py',                      # Main script
        '--name=AccountingConnectorEnhanced',  # Name of executable
        '--onefile',                    # Create single executable
        '--windowed',                   # No console window
        '--clean',                      # Clean PyInstaller cache
        '--noconfirm',                  # Replace output without confirmation
        '--add-data=models.py:.',       # Include model files
        '--add-data=controllers.py:.',
        '--add-data=views.py:.',
        '--add-data=data_manager.py:.',
        '--add-data=mock_data.py:.',
        '--hidden-import=PySide6.QtCore',
        '--hidden-import=PySide6.QtGui',
        '--hidden-import=PySide6.QtWidgets',
        '--icon=icon.ico',              # Optional icon
    ]
    
    try:
        PyInstaller.__main__.run(args)
        print("Build completed successfully!")
        print(f"Executable created in: {current_dir}/dist/")
    except Exception as e:
        print(f"Build failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    build_executable()