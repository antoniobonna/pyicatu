"""
pyicatu package.

A Python package for financial data analysis and metrics.
"""

__version__ = "0.1.0"

# Import key components for easier access
from .financial_metrics import FinancialMetrics
from .settings.config import DatabaseConfig

__all__ = [
    "FinancialMetrics",
    "DatabaseConfig",
]
