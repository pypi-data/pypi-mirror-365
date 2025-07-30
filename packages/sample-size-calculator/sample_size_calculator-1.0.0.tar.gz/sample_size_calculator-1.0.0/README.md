# Sample Size Calculator

A comprehensive Python package for calculating sample sizes for various statistical tests including A/B tests, margin analysis, and log-normal distributions.

## Installation

### From PyPI (Public)
```bash
pip install sample-size-calculator
```

### From GitHub Packages (Private)
```bash
# First, create a .netrc file with your GitHub token
echo "machine npm.pkg.github.com login __token__ password pypi-AgEIcHlwaS5vcmcCJDkxMTRhZThjLWY1NmMtNDcxYS1iODczLWQ3OGY4YWE3OWMxZgACKlszLCI2ZjgyNTM2Mi1hNDM4LTQyZTItOTAyMy05NjlkOWMzZmM4OTEiXQAABiCeXzvlesH92aynC9VaDnKJIaRYYy30Fw9QgBJwKBFoPw" > ~/.netrc
chmod 600 ~/.netrc

# Then install the package
pip install sample-size-calculator --index-url https://npm.pkg.github.com/
```

## Quick Start

```python
from sample_size_calculator import calculate_ab_test_sample_size

# Calculate sample size for A/B test
sample_size = calculate_ab_test_sample_size(
    baseline_ctr=0.0375,  # 3.75% baseline CTR
    uplift_pct=5,         # 5% relative uplift
    power=0.8
)
print(f"Required sample size per group: {sample_size}")
```

## Features

- A/B Test Sample Size calculations
- Margin analysis and uplift detection
- Log-normal distribution sample sizes
- Test result analysis with p-values and confidence intervals
- Margin distribution visualization

## Documentation

See the full documentation for detailed API reference and examples.
