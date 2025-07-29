#!/usr/bin/env python3
"""
Streamlit app launcher for ML Sniff GUI.

Run this script to start the Streamlit web interface:
    python streamlit_app.py
    or
    streamlit run streamlit_app.py
"""

import streamlit as st
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the GUI
from ml_sniff.gui import main

if __name__ == "__main__":
    main() 