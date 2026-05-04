"""
Vercel Serverless Entry Point
=============================
Imports the actual FastAPI application with all routes configured.
"""

import sys
import os

# Add project root to Python path so 'app' package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the actual app with all CRUD routes
from app.main import app

# Vercel's @vercel/python builder will detect this 'app' object
# No Mangum needed — Vercel handles ASGI apps natively