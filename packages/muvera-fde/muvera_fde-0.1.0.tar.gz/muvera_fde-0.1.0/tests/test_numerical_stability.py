"""Numerical stability tests for point cloud sketching."""

import numpy as np

from muvera_fde import (
    EncodingType,
    FixedDimensionalEncoder,
    FixedDimensionalEncodingConfig,
    ProjectionType,
)


class TestNumericalStability:
    """Test numerical stability and precision."""

    def test_deterministic_encoding(self):
        """Test that encoding is deterministic with fixed seed."""
        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_simhash_projections=8,
            seed=42,
        )
        encoder = FixedDimensionalEncoder(config)

        points = np.random.randn(100, 3).astype(np.float32)

        # Encode multiple times
        encodings = []
        for _ in range(5):
            enc = encoder.encode(points)
            encodings.append(enc)

        # All should be identical
        for i in range(1, len(encodings)):
            np.testing.assert_array_equal(encodings[0], encodings[i])

    def test_seed_sensitivity(self):
        """Test that different seeds produce different encodings."""
        points = np.random.randn(100, 3).astype(np.float32)

        encodings = []
        for seed in range(5):
            config = FixedDimensionalEncodingConfig(
                dimension=3,
                num_simhash_projections=8,
                seed=seed,
            )
            encoder = FixedDimensionalEncoder(config)
            enc = encoder.encode(points)
            encodings.append(enc)

        # All should be different
        for i in range(len(encodings)):
            for j in range(i + 1, len(encodings)):
                assert not np.array_equal(encodings[i], encodings[j])

    def test_numerical_precision_float32(self):
        """Test numerical precision with float32."""
        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_simhash_projections=8,
        )
        encoder = FixedDimensionalEncoder(config)

        # Points with specific precision
        points = np.array(
            [
                [1.234567890123456789, 2.345678901234567890, 3.456789012345678901],
                [0.000001, 0.000002, 0.000003],
                [1000000.0, 2000000.0, 3000000.0],
            ],
            dtype=np.float32,
        )

        encoding = encoder.encode(points)

        # Check that encoding is finite and reasonable
        assert np.all(np.isfinite(encoding))
        assert encoding.dtype == np.float32

    def test_zero_handling(self):
        """Test handling of zero values."""
        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_simhash_projections=8,
        )
        encoder = FixedDimensionalEncoder(config)

        # All zeros
        zeros = np.zeros((10, 3), dtype=np.float32)
        zero_encoding = encoder.encode(zeros)

        # Mix of zeros and non-zeros
        mixed = np.array(
            [
                [0, 0, 0],
                [1, 0, 0],
                [0, 1, 0],
                [0, 0, 1],
                [1, 1, 1],
            ],
            dtype=np.float32,
        )
        mixed_encoding = encoder.encode(mixed)

        # Both should produce valid encodings
        assert np.all(np.isfinite(zero_encoding))
        assert np.all(np.isfinite(mixed_encoding))

        # Encodings should be different
        assert not np.array_equal(zero_encoding, mixed_encoding)

    def test_scale_invariance(self):
        """Test behavior under scaling."""
        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_simhash_projections=8,
            encoding_type=EncodingType.AVERAGE,  # Average should be less sensitive
        )
        encoder = FixedDimensionalEncoder(config)

        # Base points
        points = np.random.randn(100, 3).astype(np.float32)

        # Scaled versions
        scales = [0.1, 1.0, 10.0, 100.0]
        encodings = []

        for scale in scales:
            scaled_points = points * scale
            enc = encoder.encode(scaled_points)
            # Normalize for comparison
            enc_norm = enc / (np.linalg.norm(enc) + 1e-8)
            encodings.append(enc_norm)

        # Check that normalized encodings are similar
        for i in range(len(encodings)):
            for j in range(i + 1, len(encodings)):
                similarity = np.dot(encodings[i], encodings[j])
                print(
                    f"Scale {scales[i]} vs {scales[j]}: similarity = {similarity:.4f}"
                )
                # Should maintain some similarity
                assert similarity > 0.5

    def test_translation_effect(self):
        """Test effect of translation on encoding."""
        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_simhash_projections=8,
        )
        encoder = FixedDimensionalEncoder(config)

        # Base points centered at origin
        points = np.random.randn(100, 3).astype(np.float32)
        base_encoding = encoder.encode(points)

        # Translate to different locations
        translations = [
            [0, 0, 0],
            [10, 0, 0],
            [0, 10, 0],
            [0, 0, 10],
            [10, 10, 10],
            [100, 100, 100],
        ]

        for trans in translations:
            translated = points + np.array(trans)
            enc = encoder.encode(translated)

            # Compute relative change
            diff = np.linalg.norm(enc - base_encoding) / np.linalg.norm(base_encoding)
            print(f"Translation {trans}: relative change = {diff:.4f}")

    def test_rotation_effect(self):
        """Test effect of rotation on encoding."""
        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_simhash_projections=8,
            seed=42,
        )
        encoder = FixedDimensionalEncoder(config)

        # Create rotation matrix (45 degrees around z-axis)
        theta = np.pi / 4
        rotation = np.array(
            [
                [np.cos(theta), -np.sin(theta), 0],
                [np.sin(theta), np.cos(theta), 0],
                [0, 0, 1],
            ]
        )

        # Base points
        points = np.random.randn(100, 3).astype(np.float32)
        base_encoding = encoder.encode(points)

        # Rotated points
        rotated_points = (rotation @ points.T).T.astype(np.float32)
        rotated_encoding = encoder.encode(rotated_points)

        # Compare encodings
        similarity = np.dot(base_encoding, rotated_encoding) / (
            np.linalg.norm(base_encoding) * np.linalg.norm(rotated_encoding)
        )
        print(f"\nRotation similarity: {similarity:.4f}")

        # Should be somewhat similar but not identical
        assert 0.3 < similarity < 0.95

    def test_numerical_overflow_protection(self):
        """Test protection against numerical overflow."""
        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_simhash_projections=8,
        )
        encoder = FixedDimensionalEncoder(config)

        # Very large values (but not infinity)
        large_points = np.array(
            [
                [1e10, 1e10, 1e10],
                [-1e10, -1e10, -1e10],
                [1e10, -1e10, 1e10],
            ],
            dtype=np.float32,
        )

        encoding = encoder.encode(large_points)

        # Should handle large values without overflow
        assert np.all(np.isfinite(encoding))
        assert not np.any(np.isinf(encoding))
        assert not np.any(np.isnan(encoding))

    def test_numerical_underflow_protection(self):
        """Test protection against numerical underflow."""
        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_simhash_projections=8,
        )
        encoder = FixedDimensionalEncoder(config)

        # Very small values
        small_points = np.array(
            [
                [1e-20, 1e-20, 1e-20],
                [-1e-20, -1e-20, -1e-20],
                [1e-20, -1e-20, 1e-20],
            ],
            dtype=np.float32,
        )

        encoding = encoder.encode(small_points)

        # Should handle small values
        assert np.all(np.isfinite(encoding))

    def test_conditioning_number(self):
        """Test numerical conditioning of the encoding."""
        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_simhash_projections=8,
        )
        encoder = FixedDimensionalEncoder(config)

        # Well-conditioned points
        good_points = np.random.randn(100, 3).astype(np.float32)

        # Poorly conditioned points (nearly collinear)
        t = np.linspace(0, 1, 100)
        poor_points = np.column_stack([t, t * 1e-6, t * 1e-12]).astype(np.float32)

        good_encoding = encoder.encode(good_points)
        poor_encoding = encoder.encode(poor_points)

        # Both should produce valid encodings
        assert np.all(np.isfinite(good_encoding))
        assert np.all(np.isfinite(poor_encoding))

        print(
            f"\nWell-conditioned encoding range: [{good_encoding.min():.2e}, {good_encoding.max():.2e}]"
        )
        print(
            f"Poorly-conditioned encoding range: [{poor_encoding.min():.2e}, {poor_encoding.max():.2e}]"
        )

    def test_accumulation_errors(self):
        """Test for accumulation errors in sum encoding."""
        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_simhash_projections=4,  # Fewer partitions for more accumulation
            encoding_type=EncodingType.DEFAULT_SUM,
        )
        encoder = FixedDimensionalEncoder(config)

        # Many points in same region to cause accumulation
        n_points = 10000
        points = np.random.randn(n_points, 3).astype(np.float32) * 0.1  # Small spread

        encoding = encoder.encode(points)

        # Check for reasonable values despite accumulation
        assert np.all(np.isfinite(encoding))
        assert np.abs(encoding).max() < 1e10  # No extreme values

    def test_cancellation_errors(self):
        """Test for cancellation errors."""
        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_simhash_projections=8,
        )
        encoder = FixedDimensionalEncoder(config)

        # Points that might cause cancellation
        points = np.array(
            [
                [1.0, 1.0, 1.0],
                [-1.0, -1.0, -1.0],
                [1.0000001, 1.0000001, 1.0000001],
                [-0.9999999, -0.9999999, -0.9999999],
            ],
            dtype=np.float32,
        )

        encoding = encoder.encode(points)

        # Should handle near-cancellation
        assert np.all(np.isfinite(encoding))
        assert not np.all(encoding == 0)  # Shouldn't completely cancel

    def test_projection_numerical_stability(self):
        """Test numerical stability of projection operations."""
        config = FixedDimensionalEncodingConfig(
            dimension=100,
            projection_dimension=10,
            projection_type=ProjectionType.AMS_SKETCH,
            num_simhash_projections=8,
        )
        encoder = FixedDimensionalEncoder(config)

        # High-dimensional points with varying scales
        points = np.random.randn(50, 100).astype(np.float32)
        points[:, :50] *= 100  # First half has large scale
        points[:, 50:] *= 0.01  # Second half has small scale

        encoding = encoder.encode(points)

        # Projection should maintain numerical stability
        assert np.all(np.isfinite(encoding))
        assert encoding.std() > 0  # Should have variation

    def test_gray_code_boundaries(self):
        """Test behavior at Gray code boundaries."""
        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_simhash_projections=8,
            seed=42,
        )
        encoder = FixedDimensionalEncoder(config)

        # Points designed to be near partition boundaries
        # Create points along a line that crosses partitions
        t = np.linspace(-10, 10, 1000)
        points = np.column_stack([t, t * 0.5, t * 0.25]).astype(np.float32)

        encoding = encoder.encode(points)

        # Should handle boundary crossings smoothly
        assert np.all(np.isfinite(encoding))
        assert not np.any(np.diff(encoding) > 1e10)  # No huge jumps
