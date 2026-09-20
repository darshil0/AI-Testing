"""
AI-Testing: A professional evaluation framework for AI models.

This package provides tools for benchmarking AI models, running
automated evaluations, and visualizing results through a dashboard.
"""

__version__ = "2.1.8"


def run_evaluation():
    """Wrapper function to invoke evaluation suite CLI."""
    from .run_evaluation import main

    return main()


def run_dashboard():
    """Lazily import and run the Streamlit dashboard."""
    from .dashboard import main

    return main()


def __getattr__(name: str):
    if name == "BaseModel":
        from .models import BaseModel

        return BaseModel
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# Explicitly define the public API for the package
__all__ = [
    "run_evaluation",
    "run_dashboard",
    "BaseModel",
    "__version__",
]
