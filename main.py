"""Root-level entry point for Railway/Railpack auto-detection.

Railpack looks for main.py or app.py in the root directory.
This file re-exports the FastAPI app from the backend package.
"""
import sys
import os

# Add the backend directory to the Python path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.main import app  # noqa: E402

# This is what uvicorn/Railpack will find: main:app
