"""
Graphy - A Python package for plotting machine learning training metrics.

This package provides utilities for visualizing training metrics from machine learning models,
with automatic detection of validation data and clean, publication-ready plots.
"""

from .plotting import plot_metrics

__version__ = "0.1.0"
__all__ = ["plot_metrics"]
