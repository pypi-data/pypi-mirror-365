#!/usr/bin/env python3
"""
Simple launcher for ML Sniff GUI.

This script provides a user-friendly way to launch the Streamlit GUI.
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit GUI."""
    
    print("🕵️‍♂️ ML Sniff - Advanced ML Problem Detection")
    print("=" * 50)
    print("Starting Streamlit web interface...")
    print("The GUI will open in your browser at http://localhost:8501")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.headless", "false"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting GUI: {e}")
        print("Make sure you have installed all dependencies:")
        print("pip install -r requirements.txt")

if __name__ == "__main__":
    main() 