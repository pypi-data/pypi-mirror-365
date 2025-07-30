"""
Sample Size Calculator Module

This module provides functions for calculating sample sizes for various statistical tests
including A/B tests, margin analysis, and log-normal distributions.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import scipy.stats as stats
from statsmodels.stats.power import tt_ind_solve_power
from typing import Dict, Tuple, Optional


def calculate_ab_test_sample_size(
    baseline_ctr: float, 
    uplift_pct: float, 
    alpha: float = 0.05, 
    power: float = 0.8
) -> int:
    """
    Calculates the required sample size per group for an A/B test.

    Parameters:
    - baseline_ctr: float, baseline CTR as a decimal (e.g. 0.02 for 2%)
    - uplift_pct: float, desired relative uplift (e.g. 10 for 10%)
    - alpha: float, significance level (default 0.05)
    - power: float, statistical power (default 0.8)

    Returns:
    - Sample size per group (int)
    """
    # Input validation
    if baseline_ctr <= 0:
        raise ValueError("baseline_ctr must be greater than 0")
    if alpha <= 0 or alpha >= 1:
        raise ValueError("alpha must be between 0 and 1")
    if power <= 0 or power >= 1:
        raise ValueError("power must be between 0 and 1")
    
    # Convert uplift percent to absolute CTR change
    p1 = baseline_ctr
    p2 = p1 * (1 + uplift_pct / 100)
    delta = abs(p2 - p1)

    # Pooled probability i.e pooled variance is the average of the two proportions
    p_bar = (p1 + p2) / 2

    # Z-scores
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)

    # Sample size formula
    numerator = 2 * (z_alpha + z_beta) ** 2 * p_bar * (1 - p_bar)
    denominator = delta ** 2

    n_per_group = int(numerator / denominator) + 1
    return n_per_group


def calculate_metal_margin_uplift(
    current_metal_margin: float,
    target_increase_pct: float,
    std_dev: float,
    transactions_per_week: int,
    confidence_level: float = 0.95,
    power: float = 0.8
) -> Dict:
    """
    Calculates required sample size to detect a target metal_margin increase.
    
    Args:
        current_metal_margin: Average metal_margin per week (e.g., 150)
        target_increase_pct: Desired % increase (e.g., 5 for 5%)
        std_dev: Standard deviation of metal_margin
        transactions_per_week: Total weekly transactions (control + test)
        confidence_level: Statistical confidence (default: 0.95)
        power: Statistical power (default: 0.8)
    
    Returns:
        Dictionary with sample size, duration, and business metrics
    """
    # Convert inputs
    target_metal_margin = current_metal_margin * (1 + target_increase_pct / 100)
    mean_diff = target_metal_margin - current_metal_margin
    effect_size = mean_diff / std_dev  # Correct Cohen's d

    # Sample size per group
    sample_size = tt_ind_solve_power(
        effect_size=effect_size,
        alpha=1 - confidence_level,
        power=power,
        ratio=1.0,
        alternative='two-sided'
    )

    # Calculate test duration in weeks
    weeks_needed = np.ceil((sample_size * 2) / transactions_per_week)

    return {
        'current_metal_margin': current_metal_margin,
        'target_increase': round(target_metal_margin, 2),
        'sample_per_group': int(np.ceil(sample_size)),
        'weeks_needed': int(weeks_needed),
        'confidence_level': confidence_level,
        'power': power,
        'minimum_detectable_effect': round(effect_size, 4)
    }


def lognormal_sample_size(
    current_mean: float,
    target_increase_pct: float,
    std_log: float,
    confidence_level: float = 0.95,
    power: float = 0.8
) -> int:
    """
    Sample size per group for detecting a % increase in log-normal mean using z-test.

    Args:
        current_mean: Baseline mean on original scale
        target_increase_pct: Desired increase (e.g. 5 for 5%)
        std_log: Standard deviation of log-transformed values
        confidence_level: e.g., 0.95
        power: e.g., 0.8

    Returns:
        Required sample size per group
    """
    z_alpha = stats.norm.ppf(1 - (1 - confidence_level) / 2)
    z_beta = stats.norm.ppf(power)

    # Effect size on log scale
    delta_log = np.log(1 + target_increase_pct / 100)

    # Sample size formula
    n = 2 * ((z_alpha + z_beta) * std_log / delta_log) ** 2
    return int(np.ceil(n))


def calculate_margin_sample_size(
    current_margin: float,
    margin_increase: float,
    std_dev: float,
    alpha: float = 0.05,
    power: float = 0.8
) -> int:
    """
    Calculates required sample size per group to detect a specified increase in margin.

    Args:
        current_margin: Current average margin (e.g., £200)
        margin_increase: Desired absolute increase in margin (e.g., £50)
        std_dev: Standard deviation of margin
        alpha: Significance level (default 0.05)
        power: Statistical power (default 0.8)

    Returns:
        Required sample size per group (int)
    """
    effect_size = margin_increase / std_dev
    sample_size = tt_ind_solve_power(
        effect_size=effect_size,
        alpha=alpha,
        power=power,
        ratio=1.0
    )
    return int(np.ceil(sample_size))


def plot_margin_distribution(
    mean: float, 
    std_dev: float, 
    num_samples: int = 1000,
    show_plot: bool = True
) -> Optional[Figure]:
    """
    Plots a normal distribution of margins with given mean and standard deviation.

    Args:
        mean: Mean of the distribution
        std_dev: Standard deviation of the distribution
        num_samples: Number of samples to generate for the plot
        show_plot: Whether to display the plot (default True)

    Returns:
        matplotlib Figure object if show_plot=False, None otherwise
    """
    samples = np.random.normal(loc=mean, scale=std_dev, size=num_samples)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(samples, bins=30, density=True, alpha=0.6, color='g')
    
    # Plot the normal distribution curve
    xmin, xmax = ax.get_xlim()
    x = np.linspace(xmin, xmax, 100)
    p = stats.norm.pdf(x, mean, std_dev)
    ax.plot(x, p, 'k', linewidth=2)
    
    ax.set_title('Margin Distribution')
    ax.set_xlabel('Margin (£)')
    ax.set_ylabel('Density')
    ax.grid(True)
    
    if show_plot:
        plt.show()
        return None
    else:
        return fig


def analyze_test_results(
    n: int,
    mean1: float,
    mean2: float,
    alpha: float = 0.05
) -> Dict:
    """
    Analyzes A/B test results using p-value, confidence interval, and z-score.
    
    Args:
        n: Sample size per group
        mean1: Control group mean/proportion
        mean2: Treatment group mean/proportion  
        alpha: Significance level (default 0.05)
    
    Returns:
        Dictionary with test results and statistical significance
    """
    # For proportions (if means are between 0 and 1)
    if 0 <= mean1 <= 1 and 0 <= mean2 <= 1:
        p1, p2 = mean1, mean2
    else:
        # For continuous variables, convert to proportions for demonstration
        p1, p2 = mean1, mean2
    
    # Pooled proportion and standard error
    p_pool = (p1 + p2) / 2
    se = np.sqrt(p1 * (1 - p1) / n + p2 * (1 - p2) / n)
    
    # Difference in means
    diff = p2 - p1
    
    # Z-score
    z = diff / se
    
    # Two-tailed p-value
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))
    
    # Confidence interval for the difference
    z_critical = stats.norm.ppf(1 - alpha / 2)
    ci_low = diff - z_critical * se
    ci_high = diff + z_critical * se
    
    # Decision rules
    is_significant_p = p_value < alpha
    is_significant_ci = ci_low > 0 or ci_high < 0
    is_significant_z = abs(z) > z_critical
    
    return {
        'sample_size_per_group': n,
        'group1_mean': p1,
        'group2_mean': p2,
        'difference': diff,
        'standard_error': se,
        'z_score': z,
        'p_value': p_value,
        'confidence_interval': [ci_low, ci_high],
        'is_significant_p_value': is_significant_p,
        'is_significant_ci': is_significant_ci,
        'is_significant_z_score': is_significant_z,
        'overall_significant': all([is_significant_p, is_significant_ci, is_significant_z])
    }