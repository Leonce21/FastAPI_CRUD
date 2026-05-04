"""
Vercel Serverless Entry Point
=============================
Imports the actual FastAPI application with all routes configured.
DO NOT create a new FastAPI() here — import from app.main
"""

import sys
import os

# Add project root to Python path so 'app' package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the ACTUAL app with all CRUD routes from app/main.py
from app.main import app

# Vercel's @vercel/python builder detects this 'app' object
# This app already has all routes: /api/v1/items/,.