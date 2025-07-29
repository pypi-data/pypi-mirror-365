import pytest
import numpy as np

import synthatdelays as satd


def test_ERD_Normal():
    # Create a random number generator with a fixed seed for reproducibility
    rng = np.random.default_rng(42)

    # Test with invalid airport parameters
    assert satd.ERD_Normal(0, 1, 1.0, 0.0, [[1], [1], 0.0, 1.0], rng) == 0.0
    assert satd.ERD_Normal(1, 0, 1.0, 0.0, [[1], [1], 0.0, 1.0], rng) == 0.0

    # Test with valid parameters
    delay = satd.ERD_Normal(1, 1, 1.0, 0.0, [[1], [1], 0.0, 1.0], rng)
    assert isinstance(delay, float)

    # Test with -1 in airport lists (all airports)
    delay = satd.ERD_Normal(0, 1, 1.0, 0.0, [[-1], [1], 0.0, 1.0], rng)
    assert isinstance(delay, float)

    delay = satd.ERD_Normal(1, 0, 1.0, 0.0, [[1], [-1], 0.0, 1.0], rng)
    assert isinstance(delay, float)

    # Test proportionality to flight time
    # Create new RNGs with the same seed for each test to ensure reproducibility
    rng1 = np.random.default_rng(42)
    delay1 = satd.ERD_Normal(1, 1, 1.0, 0.0, [[1], [1], 0.5, 0.1], rng1)

    rng2 = np.random.default_rng(42)
    delay2 = satd.ERD_Normal(1, 1, 2.0, 0.0, [[1], [1], 0.5, 0.1], rng2)

    assert abs(delay2 - 2 * delay1) < 1e-10  # Should be exactly proportional


def test_ERD_Disruptions():
    # Create a random number generator with a fixed seed for reproducibility
    rng = np.random.default_rng(42)

    # Test with invalid airport parameters
    assert satd.ERD_Disruptions(0, 1, 1.0, 0.0, [[1], [1], 0.5, 1.0], rng) == 0.0
    assert satd.ERD_Disruptions(1, 0, 1.0, 0.0, [[1], [1], 0.5, 1.0], rng) == 0.0

    # Test with valid parameters but zero probability
    delay = satd.ERD_Disruptions(1, 1, 1.0, 0.0, [[1], [1], 0.0, 1.0], rng)
    assert delay == 0.0

    # Test with valid parameters and 100% probability
    delay = satd.ERD_Disruptions(1, 1, 1.0, 0.0, [[1], [1], 1.0, 1.0], rng)
    assert delay > 0.0

    # Test with -1 in airport lists (all airports)
    delay = satd.ERD_Disruptions(0, 1, 1.0, 0.0, [[-1], [1], 0.5, 1.0], rng)
    assert isinstance(delay, float)

    delay = satd.ERD_Disruptions(1, 0, 1.0, 0.0, [[1], [-1], 0.5, 1.0], rng)
    assert isinstance(delay, float)

    # Test that flight time doesn't affect the delay (unlike ERD_Normal)
    # Create new RNGs with the same seed for each test to ensure reproducibility
    rng1 = np.random.default_rng(42)
    delay1 = satd.ERD_Disruptions(1, 1, 1.0, 0.0, [[1], [1], 1.0, 2.0], rng1)

    rng2 = np.random.default_rng(42)
    delay2 = satd.ERD_Disruptions(1, 1, 2.0, 0.0, [[1], [1], 1.0, 2.0], rng2)

    assert delay1 == delay2  # Should be the same regardless of flight time
