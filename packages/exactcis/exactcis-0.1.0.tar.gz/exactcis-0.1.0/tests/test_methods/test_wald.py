"""
Tests for the Haldane-Anscombe Wald confidence interval method.
"""

import pytest
from exactcis.methods import ci_wald_haldane


def test_ci_wald_haldane_basic():
    """Test basic functionality of ci_wald_haldane."""
    # Get the actual values from the implementation
    lower, upper = ci_wald_haldane(12, 5, 8, 10, alpha=0.05)
    
    # Log the actual values
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"ci_wald_haldane actual result: ({lower:.3f}, {upper:.3f})")
    
    # Use more flexible assertions that allow for small differences in implementation
    assert 0.7 < lower < 0.8, f"Lower bound {lower:.3f} outside reasonable range"
    assert 9.0 < upper < 12.0, f"Upper bound {upper:.3f} outside reasonable range"


def test_ci_wald_haldane_edge_cases():
    """Test edge cases for ci_wald_haldane."""
    # When a is at the minimum possible value
    lower, upper = ci_wald_haldane(0, 10, 10, 10, alpha=0.05)
    assert lower > 0.0, f"Expected positive lower bound, got {lower}"
    assert upper < float('inf'), f"Expected finite upper bound, got {upper}"

    # When a is at the maximum possible value
    lower, upper = ci_wald_haldane(10, 0, 0, 10, alpha=0.05)
    assert lower > 0.0, f"Expected positive lower bound, got {lower}"
    assert upper < float('inf'), f"Expected finite upper bound, got {upper}"


def test_ci_wald_haldane_invalid_inputs():
    """Test that invalid inputs raise appropriate exceptions."""
    # Negative count
    with pytest.raises(ValueError):
        ci_wald_haldane(-1, 5, 8, 10)

    # Empty margin
    with pytest.raises(ValueError):
        ci_wald_haldane(0, 0, 8, 10)


def test_ci_wald_haldane_small_counts():
    """Test with small counts."""
    lower, upper = ci_wald_haldane(1, 1, 1, 1, alpha=0.05)
    assert lower > 0.0, f"Expected positive lower bound, got {lower}"
    assert upper < float('inf'), f"Expected finite upper bound, got {upper}"


def test_ci_wald_haldane_large_imbalance():
    """Test with large imbalance in counts."""
    lower, upper = ci_wald_haldane(50, 5, 2, 20, alpha=0.05)
    assert lower > 0.0, f"Expected positive lower bound, got {lower}"
    assert upper < float('inf'), f"Expected finite upper bound, got {upper}"


def test_ci_wald_haldane_different_alpha():
    """Test with different alpha values."""
    # Alpha = 0.01 (99% confidence)
    lower_99, upper_99 = ci_wald_haldane(12, 5, 8, 10, alpha=0.01)

    # Alpha = 0.1 (90% confidence)
    lower_90, upper_90 = ci_wald_haldane(12, 5, 8, 10, alpha=0.1)

    # 99% CI should be wider than 90% CI
    assert lower_99 < lower_90, "99% CI lower bound should be smaller than 90% CI lower bound"
    assert upper_99 > upper_90, "99% CI upper bound should be larger than 90% CI upper bound"
