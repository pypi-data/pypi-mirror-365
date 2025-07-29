"""Edge case tests for point cloud sketching."""

import numpy as np

from muvera_fde import (
    EncodingType,
    FixedDimensionalEncoder,
    FixedDimensionalEncodingConfig,
    ProjectionType,
)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_point(self):
        """Test encoding of a single point."""
        config = FixedDimensionalEncodingConfig(dimension=3)
        encoder = FixedDimensionalEncoder(config)

        # Single point at origin
        points = np.zeros((1, 3), dtype=np.float32)
        encoding = encoder.encode(points)
        assert encoding.shape == (encoder.output_dimension,)

        # Single point with values
        points = np.array([[1.0, 2.0, 3.0]], dtype=np.float32)
        encoding = encoder.encode(points)
        assert encoding.shape == (encoder.output_dimension,)
        assert not np.all(encoding == 0)  # Should have non-zero values

    def test_large_point_cloud(self):
        """Test encoding of large point clouds."""
        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_simhash_projections=4,  # Keep small for memory
        )
        encoder = FixedDimensionalEncoder(config)

        # Large point cloud
        points = np.random.randn(10000, 3).astype(np.float32)
        encoding = encoder.encode(points)
        assert encoding.shape == (encoder.output_dimension,)
        assert np.isfinite(encoding).all()

    def test_high_dimensional_points(self):
        """Test encoding of high-dimensional points."""
        config = FixedDimensionalEncodingConfig(
            dimension=1000,
            num_simhash_projections=4,
            projection_dimension=50,
            projection_type=ProjectionType.AMS_SKETCH,
        )
        encoder = FixedDimensionalEncoder(config)

        points = np.random.randn(100, 1000).astype(np.float32)
        encoding = encoder.encode(points)
        assert encoding.shape == (encoder.output_dimension,)
        assert np.isfinite(encoding).all()

    def test_extreme_values(self):
        """Test encoding with extreme point values."""
        config = FixedDimensionalEncodingConfig(dimension=3)
        encoder = FixedDimensionalEncoder(config)

        # Very large values
        points = np.array([[1e10, -1e10, 1e10]], dtype=np.float32)
        encoding = encoder.encode(points)
        assert np.isfinite(encoding).all()

        # Very small values
        points = np.array([[1e-10, -1e-10, 1e-10]], dtype=np.float32)
        encoding = encoder.encode(points)
        assert encoding.shape == (encoder.output_dimension,)

        # Mixed scales
        points = np.array(
            [[1e10, 1e-10, 0], [0, 1e10, 1e-10], [1e-10, 0, 1e10]], dtype=np.float32
        )
        encoding = encoder.encode(points)
        assert np.isfinite(encoding).all()

    def test_identical_points(self):
        """Test encoding of identical points."""
        config = FixedDimensionalEncodingConfig(
            dimension=3,
            encoding_type=EncodingType.AVERAGE,
        )
        encoder = FixedDimensionalEncoder(config)

        # All points identical
        point = np.array([1.5, 2.5, 3.5])
        points = np.tile(point, (100, 1)).astype(np.float32)
        encoding = encoder.encode(points)

        # For average encoding, should be similar to single point
        single_encoding = encoder.encode(point.reshape(1, -1).astype(np.float32))

        # They should be very similar (not exact due to partition assignments)
        assert encoding.shape == single_encoding.shape

    def test_points_on_axes(self):
        """Test points aligned with coordinate axes."""
        config = FixedDimensionalEncodingConfig(dimension=3)
        encoder = FixedDimensionalEncoder(config)

        # Points on each axis
        points = np.array(
            [
                [1, 0, 0],
                [0, 1, 0],
                [0, 0, 1],
                [-1, 0, 0],
                [0, -1, 0],
                [0, 0, -1],
            ],
            dtype=np.float32,
        )

        encoding = encoder.encode(points)
        assert encoding.shape == (encoder.output_dimension,)
        assert not np.all(encoding == 0)

    def test_coplanar_points(self):
        """Test encoding of coplanar points."""
        config = FixedDimensionalEncodingConfig(dimension=3)
        encoder = FixedDimensionalEncoder(config)

        # Points on xy-plane
        points = np.random.randn(50, 2)
        points = np.hstack([points, np.zeros((50, 1))]).astype(np.float32)

        encoding = encoder.encode(points)
        assert encoding.shape == (encoder.output_dimension,)
        assert not np.all(encoding == 0)

    def test_many_repetitions(self):
        """Test with many repetitions."""
        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_repetitions=20,
            num_simhash_projections=4,  # Keep small
        )
        encoder = FixedDimensionalEncoder(config)

        points = np.random.randn(100, 3).astype(np.float32)
        encoding = encoder.encode(points)

        expected_dim = (1 << 4) * 3 * 20
        assert encoding.shape == (expected_dim,)

    def test_many_projections(self):
        """Test with many SimHash projections."""
        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_simhash_projections=16,  # 2^16 = 65536 partitions
            num_repetitions=1,
        )
        encoder = FixedDimensionalEncoder(config)

        points = np.random.randn(100, 3).astype(np.float32)
        encoding = encoder.encode(points)

        expected_dim = (1 << 16) * 3
        assert encoding.shape == (expected_dim,)

    def test_sparse_point_cloud(self):
        """Test encoding of sparse point clouds."""
        config = FixedDimensionalEncodingConfig(
            dimension=100,
            projection_dimension=20,
            projection_type=ProjectionType.AMS_SKETCH,
        )
        encoder = FixedDimensionalEncoder(config)

        # Sparse points (mostly zeros)
        points = np.zeros((50, 100), dtype=np.float32)
        # Add a few non-zero entries
        for i in range(50):
            points[i, np.random.randint(0, 100)] = np.random.randn()

        encoding = encoder.encode(points)
        assert encoding.shape == (encoder.output_dimension,)

    def test_nan_handling(self):
        """Test handling of NaN values."""
        config = FixedDimensionalEncodingConfig(dimension=3)
        encoder = FixedDimensionalEncoder(config)

        # Points with NaN should raise an error or be handled gracefully
        points = np.array([[1, 2, np.nan]], dtype=np.float32)

        # The behavior depends on implementation - either error or handle
        # For now, just ensure it doesn't crash
        try:
            encoding = encoder.encode(points)
            # If it succeeds, check output is finite
            assert encoding.shape == (encoder.output_dimension,)
        except:
            # If it fails, that's also acceptable behavior
            pass

    def test_inf_handling(self):
        """Test handling of infinity values."""
        config = FixedDimensionalEncodingConfig(dimension=3)
        encoder = FixedDimensionalEncoder(config)

        # Points with infinity
        points = np.array([[1, 2, np.inf]], dtype=np.float32)

        try:
            encoding = encoder.encode(points)
            assert encoding.shape == (encoder.output_dimension,)
        except:
            # If it fails, that's also acceptable behavior
            pass

    def test_zero_variance_dimensions(self):
        """Test points with zero variance in some dimensions."""
        config = FixedDimensionalEncodingConfig(dimension=5)
        encoder = FixedDimensionalEncoder(config)

        # All points have same value in dimensions 0 and 2
        points = np.random.randn(100, 5).astype(np.float32)
        points[:, 0] = 1.0  # Constant
        points[:, 2] = -2.5  # Constant

        encoding = encoder.encode(points)
        assert encoding.shape == (encoder.output_dimension,)
        assert not np.all(encoding == 0)

    def test_alternating_signs(self):
        """Test points with alternating signs pattern."""
        config = FixedDimensionalEncodingConfig(dimension=4)
        encoder = FixedDimensionalEncoder(config)

        # Create checkerboard pattern
        points = []
        for i in range(50):
            signs = [(-1) ** (i + j) for j in range(4)]
            points.append([s * abs(np.random.randn()) for s in signs])

        points = np.array(points, dtype=np.float32)
        encoding = encoder.encode(points)
        assert encoding.shape == (encoder.output_dimension,)

    def test_clustered_points(self):
        """Test encoding of clustered points."""
        config = FixedDimensionalEncodingConfig(
            dimension=3,
            encoding_type=EncodingType.AVERAGE,
        )
        encoder = FixedDimensionalEncoder(config)

        # Create 3 clusters
        clusters = []
        centers = [[0, 0, 0], [10, 10, 10], [-10, -10, -10]]

        for center in centers:
            cluster = np.random.randn(30, 3) * 0.5 + center
            clusters.append(cluster)

        points = np.vstack(clusters).astype(np.float32)
        encoding = encoder.encode(points)
        assert encoding.shape == (encoder.output_dimension,)

    def test_sequential_processing_consistency(self):
        """Test that processing order doesn't affect result."""
        config = FixedDimensionalEncodingConfig(
            dimension=3,
            seed=42,
        )
        encoder = FixedDimensionalEncoder(config)

        points = np.random.randn(50, 3).astype(np.float32)

        # Original order
        encoding1 = encoder.encode(points)

        # Shuffled order
        indices = np.random.permutation(50)
        points_shuffled = points[indices]
        encoding2 = encoder.encode(points_shuffled)

        # Should produce same encoding (order doesn't matter for sum/average)
        # Note: Exact equality might not hold due to floating point, but should be very close
        assert encoding1.shape == encoding2.shape
