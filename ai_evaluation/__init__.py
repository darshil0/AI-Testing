"""
AI-Testing: A professional evaluation framework for AI models.

This package provides tools for benchmarking AI models, running 
automated evaluations, and visualizing results through a dashboard.
"""

__version__ = "2.1.0"

from .run_evaluation import main as run_evaluation
from .dashboard import main as run_dashboard
from .models import BaseModel

# Explicitly define the public API for the package
__all__ = [
    "run_evaluation",
    "run_dashboard",
    "BaseModel",
    "__version__",
]
