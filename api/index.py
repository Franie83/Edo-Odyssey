import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from run import app

# Vercel expects a callable named 'app'
# This is the entry point for Vercel serverless deployment