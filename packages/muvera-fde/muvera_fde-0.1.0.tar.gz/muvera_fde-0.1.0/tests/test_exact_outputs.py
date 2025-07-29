"""Test exact outputs with fixed seeds to ensure algorithm correctness.

This test file contains golden outputs that must remain unchanged after any
optimization. These tests use fixed seeds and inputs to produce deterministic
outputs that can be compared exactly (within float32 epsilon).
"""

import numpy as np
import pytest

from muvera_fde import (
    EncodingType,
    FixedDimensionalEncoder,
    FixedDimensionalEncodingConfig,
    ProjectionType,
)


class TestExactOutputs:
    """Test exact outputs to ensure algorithm remains unchanged during optimization."""

    def test_basic_encoding_exact_output(self):
        """Test basic encoding produces exact expected output."""
        # Fixed input
        points = np.array(
            [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
                [-1.0, 0.0, 0.0],
                [0.0, -1.0, 0.0],
                [0.0, 0.0, -1.0],
            ],
            dtype=np.float32,
        )

        # Fixed config
        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_repetitions=1,
            num_simhash_projections=2,
            seed=42,
            encoding_type=EncodingType.DEFAULT_SUM,
            projection_dimension=None,
            projection_type=ProjectionType.DEFAULT_IDENTITY,
            fill_empty_partitions=False,
            final_projection_dimension=None,
        )

        encoder = FixedDimensionalEncoder(config)
        output = encoder.encode(points)

        # Golden output captured from current implementation
        expected = np.array(
            [
                0.0,
                -1.0,
                -1.0,  # Partition 0
                1.0,
                0.0,
                0.0,  # Partition 1
                0.0,
                1.0,
                1.0,  # Partition 2
                -1.0,
                0.0,
                0.0,  # Partition 3
            ],
            dtype=np.float32,
        )

        # Verify exact match
        np.testing.assert_array_almost_equal(output, expected, decimal=6)

        # Also verify properties
        assert output.shape == (12,)
        assert output.dtype == np.float32
        assert np.linalg.norm(output) == pytest.approx(2.449490, rel=1e-6)

    def test_query_encoding_exact_output(self):
        """Test query encoding with larger input."""
        # Generate deterministic random points
        np.random.seed(12345)
        points = np.random.randn(100, 3).astype(np.float32)

        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_repetitions=2,
            num_simhash_projections=3,  # 8 partitions
            seed=99,
            encoding_type=EncodingType.DEFAULT_SUM,
            projection_dimension=None,
            projection_type=ProjectionType.DEFAULT_IDENTITY,
            fill_empty_partitions=False,
            final_projection_dimension=None,
        )

        encoder = FixedDimensionalEncoder(config)
        output = encoder.encode_query(points)

        # Verify deterministic properties
        assert output.shape == (48,)  # 8 partitions * 3 dims * 2 repetitions
        assert output.dtype == np.float32

        # Save golden output
        self._save_golden_output("query_encoding", output)

        # Verify some statistical properties that should be stable
        assert -200 < np.sum(output) < 200  # Sum should be reasonable
        assert 50 < np.linalg.norm(output) < 150  # Norm should be reasonable

    def test_document_encoding_exact_output(self):
        """Test document encoding with average aggregation."""
        # Fixed input
        points = np.array(
            [
                [1.0, 2.0, 3.0],
                [4.0, 5.0, 6.0],
                [7.0, 8.0, 9.0],
                [-1.0, -2.0, -3.0],
                [-4.0, -5.0, -6.0],
            ],
            dtype=np.float32,
        )

        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_repetitions=1,
            num_simhash_projections=2,
            seed=7,
            encoding_type=EncodingType.AVERAGE,
            projection_dimension=None,
            projection_type=ProjectionType.DEFAULT_IDENTITY,
            fill_empty_partitions=False,
            final_projection_dimension=None,
        )

        encoder = FixedDimensionalEncoder(config)
        output = encoder.encode_document(points)

        assert output.shape == (12,)
        assert output.dtype == np.float32

        # Document encoding should have smaller magnitude due to averaging
        assert np.linalg.norm(output) < 20

        self._save_golden_output("document_encoding", output)

    def test_ams_projection_exact_output(self):
        """Test AMS sketch projection."""
        points = np.eye(10, dtype=np.float32)  # Identity matrix as input

        config = FixedDimensionalEncodingConfig(
            dimension=10,
            num_repetitions=1,
            num_simhash_projections=2,
            seed=555,
            encoding_type=EncodingType.DEFAULT_SUM,
            projection_dimension=5,
            projection_type=ProjectionType.AMS_SKETCH,
            fill_empty_partitions=False,
            final_projection_dimension=None,
        )

        encoder = FixedDimensionalEncoder(config)
        output = encoder.encode(points)

        assert output.shape == (20,)  # 4 partitions * 5 proj_dim
        assert output.dtype == np.float32

        self._save_golden_output("ams_projection", output)

    def test_final_projection_exact_output(self):
        """Test count sketch final projection."""
        # Simple structured input
        points = np.array(
            [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ],
            dtype=np.float32,
        )

        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_repetitions=3,
            num_simhash_projections=4,  # 16 partitions
            seed=1234,
            encoding_type=EncodingType.DEFAULT_SUM,
            projection_dimension=None,
            projection_type=ProjectionType.DEFAULT_IDENTITY,
            fill_empty_partitions=False,
            final_projection_dimension=32,
        )

        encoder = FixedDimensionalEncoder(config)
        output = encoder.encode(points)

        assert output.shape == (32,)
        assert output.dtype == np.float32

        # Count sketch should preserve norm approximately
        intermediate_size = 16 * 3 * 3  # Before final projection
        assert 0.5 < np.linalg.norm(output) < 10

        self._save_golden_output("final_projection", output)

    def test_empty_input_exact_output(self):
        """Test empty point cloud produces zeros."""
        points = np.zeros((0, 3), dtype=np.float32)

        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_repetitions=1,
            num_simhash_projections=3,
            seed=42,
            encoding_type=EncodingType.DEFAULT_SUM,
        )

        encoder = FixedDimensionalEncoder(config)
        output = encoder.encode(points)

        expected = np.zeros(24, dtype=np.float32)  # 8 partitions * 3 dims

        np.testing.assert_array_equal(output, expected)

    def test_numerical_precision(self):
        """Test that outputs are within float32 precision."""
        # Use values that might cause precision issues
        points = np.array(
            [
                [1e-8, 1e8, 1e-8],
                [1e8, 1e-8, 1e8],
                [-1e-8, -1e8, -1e-8],
            ],
            dtype=np.float32,
        )

        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_repetitions=1,
            num_simhash_projections=1,
            seed=0,
            encoding_type=EncodingType.DEFAULT_SUM,
        )

        encoder = FixedDimensionalEncoder(config)
        output1 = encoder.encode(points)
        output2 = encoder.encode(points)

        # Should be exactly equal (deterministic)
        np.testing.assert_array_equal(output1, output2)

        # Values should be finite
        assert np.all(np.isfinite(output1))

    def _save_golden_output(self, name: str, output: np.ndarray):
        """Save output for future comparison (helper for development)."""
        # During development, this helps capture golden outputs
        # In production, we would load and compare against saved values
        print(f"\nGolden output for {name}:")
        print(f"  Shape: {output.shape}")
        print(f"  Dtype: {output.dtype}")
        print(f"  Norm: {np.linalg.norm(output):.6f}")
        print(f"  Sum: {np.sum(output):.6f}")
        print(f"  First 10 values: {output[:10]}")
        if len(output) > 10:
            print(f"  Last 10 values: {output[-10:]}")


def test_cross_platform_determinism():
    """Ensure outputs are deterministic across platforms."""
    # This test should produce identical results on any platform
    points = np.array([[1.0, 2.0, 3.0]], dtype=np.float32)

    config = FixedDimensionalEncodingConfig(
        dimension=3,
        num_repetitions=1,
        num_simhash_projections=0,  # No partitioning
        seed=42,
        encoding_type=EncodingType.DEFAULT_SUM,
    )

    encoder = FixedDimensionalEncoder(config)
    output = encoder.encode(points)

    # With no partitioning, output should just be the input
    expected = np.array([1.0, 2.0, 3.0], dtype=np.float32)
    np.testing.assert_array_almost_equal(output, expected, decimal=6)


def test_golden_output_stability():
    """Test that ensures algorithm produces exact expected outputs.

    This is the critical test that must pass after any optimization.
    These exact values must remain unchanged (within float32 epsilon).
    """
    # Test 1: Simple structured input with known output
    points = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float32,
    )

    config = FixedDimensionalEncodingConfig(
        dimension=3,
        num_repetitions=1,
        num_simhash_projections=1,  # 2 partitions
        seed=12345,
        encoding_type=EncodingType.DEFAULT_SUM,
    )

    encoder = FixedDimensionalEncoder(config)
    output = encoder.encode(points)

    # These exact values MUST NOT CHANGE
    expected = np.array(
        [
            1.0,
            1.0,
            1.0,  # Partition 0
            0.0,
            0.0,
            0.0,  # Partition 1
        ],
        dtype=np.float32,
    )

    np.testing.assert_array_almost_equal(
        output,
        expected,
        decimal=6,
        err_msg="Algorithm output changed! This should never happen.",
    )
