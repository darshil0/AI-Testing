"""
ai_evaluation package

Tools for evaluating AI models against structured test cases,
collecting results, and viewing them in a dashboard.
"""

from .run_evaluation import main as run_evaluation
from .dashboard import main as run_dashboard
from .models import BaseModel

__all__ = [
    "run_evaluation",
    "run_dashboard",
    "BaseModel",
]
