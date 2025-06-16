#!/usr/bin/env python3
"""
Console launcher for Matrix Mario Game
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main_app import main

if __name__ == '__main__':
    main()