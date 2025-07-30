"""
Sample Size Calculator Package

A comprehensive package for calculating sample sizes for various statistical tests
including A/B tests, margin analysis, and log-normal distributions.
"""

from .calculator import (
    calculate_ab_test_sample_size,
    calculate_metal_margin_uplift,
    lognormal_sample_size,
    calculate_margin_sample_size,
    plot_margin_distribution,
    analyze_test_results
)

__version__ = "1.0.0"
__author__ = "Tayo Ososanya"
__email__ = "ososanyatayo@gmail.com"

__all__ = [
    "calculate_ab_test_sample_size",
    "calculate_metal_margin_uplift", 
    "lognormal_sample_size",
    "calculate_margin_sample_size",
    "plot_margin_distribution",
    "analyze_test_results"
]