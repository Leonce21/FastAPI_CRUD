"""
Vercel Serverless Entry Point
=============================
Properly exports the FastAPI app for Vercel's Python runtime.
Mangum wraps FastAPI for AWS Lambda compatibility.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangum import Mangum
from app.main import app

# Mangum adapter for serverless
handler = Mangum(app, lifespan="off")

# For Vercel, we can also expose app directly
# Vercel's Python runtime will detect it