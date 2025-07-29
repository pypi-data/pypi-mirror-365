"""Tests for the fixed dimensional encoder."""

import numpy as np
import pytest

from muvera_fde import (
    EncodingType,
    FixedDimensionalEncoder,
    FixedDimensionalEncodingConfig,
    ProjectionType,
)


class TestFixedDimensionalEncoder:
    """Test cases for FixedDimensionalEncoder."""

    def test_basic_encoding(self):
        """Test basic encoding functionality."""
        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_simhash_projections=4,
            num_repetitions=1,
        )
        encoder = FixedDimensionalEncoder(config)

        # Create simple point cloud
        points = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float32)

        encoding = encoder.encode(points)
        assert encoding.shape == (encoder.output_dimension,)
        assert encoding.dtype == np.float32

    def test_empty_point_cloud(self):
        """Test encoding of empty point cloud."""
        config = FixedDimensionalEncodingConfig(dimension=3)
        encoder = FixedDimensionalEncoder(config)

        points = np.zeros((0, 3), dtype=np.float32)
        encoding = encoder.encode(points)

        assert encoding.shape == (encoder.output_dimension,)
        assert np.all(encoding == 0)

    def test_query_vs_document_encoding(self):
        """Test difference between query and document encoding."""
        points = np.random.randn(50, 3).astype(np.float32)

        # Query encoder
        query_config = FixedDimensionalEncodingConfig(
            dimension=3,
            encoding_type=EncodingType.DEFAULT_SUM,
        )
        query_encoder = FixedDimensionalEncoder(query_config)

        # Document encoder
        doc_config = FixedDimensionalEncodingConfig(
            dimension=3,
            encoding_type=EncodingType.AVERAGE,
        )
        doc_encoder = FixedDimensionalEncoder(doc_config)

        query_encoding = query_encoder.encode(points)
        doc_encoding = doc_encoder.encode(points)

        # Should have same shape but different values
        assert query_encoding.shape == doc_encoding.shape
        assert not np.allclose(query_encoding, doc_encoding)

    def test_reproducibility(self):
        """Test that encoding is reproducible with same seed."""
        config = FixedDimensionalEncodingConfig(
            dimension=3,
            seed=42,
        )
        encoder = FixedDimensionalEncoder(config)

        points = np.random.randn(20, 3).astype(np.float32)

        encoding1 = encoder.encode(points)
        encoding2 = encoder.encode(points)

        assert np.allclose(encoding1, encoding2)

    def test_different_seeds(self):
        """Test that different seeds produce different encodings."""
        points = np.random.randn(20, 3).astype(np.float32)

        config1 = FixedDimensionalEncodingConfig(dimension=3, seed=1)
        encoder1 = FixedDimensionalEncoder(config1)

        config2 = FixedDimensionalEncodingConfig(dimension=3, seed=2)
        encoder2 = FixedDimensionalEncoder(config2)

        encoding1 = encoder1.encode(points)
        encoding2 = encoder2.encode(points)

        assert not np.allclose(encoding1, encoding2)

    def test_projection_dimension(self):
        """Test projection dimension feature."""
        config = FixedDimensionalEncodingConfig(
            dimension=10,
            projection_dimension=5,
            projection_type=ProjectionType.AMS_SKETCH,
            num_simhash_projections=3,
        )
        encoder = FixedDimensionalEncoder(config)

        points = np.random.randn(30, 10).astype(np.float32)
        encoding = encoder.encode(points)

        # Output should be based on projection dimension
        expected_dim = (1 << 3) * 5 * 1  # 2^3 partitions * 5 dims * 1 rep
        assert encoding.shape == (expected_dim,)

    def test_final_projection(self):
        """Test final projection dimension."""
        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_simhash_projections=4,
            final_projection_dimension=64,
        )
        encoder = FixedDimensionalEncoder(config)

        points = np.random.randn(20, 3).astype(np.float32)
        encoding = encoder.encode(points)

        assert encoding.shape == (64,)

    def test_multiple_repetitions(self):
        """Test multiple repetitions."""
        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_simhash_projections=2,
            num_repetitions=3,
        )
        encoder = FixedDimensionalEncoder(config)

        points = np.random.randn(15, 3).astype(np.float32)
        encoding = encoder.encode(points)

        expected_dim = (1 << 2) * 3 * 3  # 4 partitions * 3 dims * 3 reps
        assert encoding.shape == (expected_dim,)

    def test_invalid_input_dimension(self):
        """Test error handling for invalid input dimension."""
        config = FixedDimensionalEncodingConfig(dimension=3)
        encoder = FixedDimensionalEncoder(config)

        # Wrong dimension
        points = np.random.randn(10, 5).astype(np.float32)
        with pytest.raises(ValueError, match="dimension"):
            encoder.encode(points)

    def test_invalid_input_shape(self):
        """Test error handling for invalid input shape."""
        config = FixedDimensionalEncodingConfig(dimension=3)
        encoder = FixedDimensionalEncoder(config)

        # 1D array instead of 2D
        points = np.random.randn(10).astype(np.float32)
        with pytest.raises(ValueError, match="2D array"):
            encoder.encode(points)

    def test_dtype_conversion(self):
        """Test automatic dtype conversion."""
        config = FixedDimensionalEncodingConfig(dimension=3)
        encoder = FixedDimensionalEncoder(config)

        # Double precision input
        points = np.random.randn(10, 3).astype(np.float64)
        encoding = encoder.encode(points)

        assert encoding.dtype == np.float32

    def test_output_dimension_property(self):
        """Test output dimension calculation."""
        # Without final projection
        config1 = FixedDimensionalEncodingConfig(
            dimension=3,
            num_simhash_projections=4,
            num_repetitions=2,
        )
        encoder1 = FixedDimensionalEncoder(config1)
        assert encoder1.output_dimension == (1 << 4) * 3 * 2

        # With final projection
        config2 = FixedDimensionalEncodingConfig(
            dimension=3,
            final_projection_dimension=128,
        )
        encoder2 = FixedDimensionalEncoder(config2)
        assert encoder2.output_dimension == 128


class TestConfig:
    """Test cases for configuration validation."""

    def test_invalid_dimension(self):
        """Test validation of dimension parameter."""
        with pytest.raises(ValueError):
            FixedDimensionalEncodingConfig(dimension=0)

        with pytest.raises(ValueError):
            FixedDimensionalEncodingConfig(dimension=-1)

    def test_invalid_repetitions(self):
        """Test validation of num_repetitions parameter."""
        with pytest.raises(ValueError):
            FixedDimensionalEncodingConfig(num_repetitions=0)

    def test_invalid_projections(self):
        """Test validation of num_simhash_projections parameter."""
        # 0 is now valid
        config = FixedDimensionalEncodingConfig(num_simhash_projections=0)
        assert config.num_simhash_projections == 0

        # Only negative values are invalid
        with pytest.raises(ValueError):
            FixedDimensionalEncodingConfig(num_simhash_projections=-1)

    def test_invalid_projection_dimension(self):
        """Test validation of projection_dimension parameter."""
        with pytest.raises(ValueError):
            FixedDimensionalEncodingConfig(projection_dimension=0)

    def test_invalid_final_projection_dimension(self):
        """Test validation of final_projection_dimension parameter."""
        with pytest.raises(ValueError):
            FixedDimensionalEncodingConfig(final_projection_dimension=0)
