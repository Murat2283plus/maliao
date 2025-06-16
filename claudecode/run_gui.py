#!/usr/bin/env python3
"""
GUI launcher for Matrix Mario Game
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gui.matrix_display import run_gui

if __name__ == '__main__':
    run_gui()