"""Pytest configuration and fixtures."""

import numpy as np
import pytest


@pytest.fixture
def sample_points_3d():
    """Generate sample 3D points."""
    return np.random.randn(100, 3).astype(np.float32)


@pytest.fixture
def sample_points_high_dim():
    """Generate sample high-dimensional points."""
    return np.random.randn(50, 100).astype(np.float32)


@pytest.fixture
def sample_config():
    """Generate sample configuration."""
    from muvera_fde import FixedDimensionalEncodingConfig

    return FixedDimensionalEncodingConfig(
        dimension=3,
        num_simhash_projections=8,
        seed=42,
    )


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
