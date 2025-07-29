"""Tests for configuration classes."""

from dataclasses import fields

import pytest

from muvera_fde import (
    EncodingType,
    FixedDimensionalEncodingConfig,
    ProjectionType,
)


class TestFixedDimensionalEncodingConfig:
    """Test cases for FixedDimensionalEncodingConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = FixedDimensionalEncodingConfig()

        assert config.dimension == 3
        assert config.num_repetitions == 1
        assert config.num_simhash_projections == 8
        assert config.seed == 1
        assert config.encoding_type == EncodingType.DEFAULT_SUM
        assert config.projection_dimension is None
        assert config.projection_type == ProjectionType.DEFAULT_IDENTITY
        assert config.fill_empty_partitions is False
        assert config.final_projection_dimension is None

    def test_custom_values(self):
        """Test configuration with custom values."""
        config = FixedDimensionalEncodingConfig(
            dimension=10,
            num_repetitions=5,
            num_simhash_projections=12,
            seed=42,
            encoding_type=EncodingType.AVERAGE,
            projection_dimension=20,
            projection_type=ProjectionType.AMS_SKETCH,
            fill_empty_partitions=True,
            final_projection_dimension=128,
        )

        assert config.dimension == 10
        assert config.num_repetitions == 5
        assert config.num_simhash_projections == 12
        assert config.seed == 42
        assert config.encoding_type == EncodingType.AVERAGE
        assert config.projection_dimension == 20
        assert config.projection_type == ProjectionType.AMS_SKETCH
        assert config.fill_empty_partitions is True
        assert config.final_projection_dimension == 128

    def test_validation_dimension(self):
        """Test dimension validation."""
        # Valid dimensions
        for dim in [1, 10, 100, 1000]:
            config = FixedDimensionalEncodingConfig(dimension=dim)
            assert config.dimension == dim

        # Invalid dimensions
        for dim in [0, -1, -10]:
            with pytest.raises(ValueError, match="dimension must be positive"):
                FixedDimensionalEncodingConfig(dimension=dim)

    def test_validation_num_repetitions(self):
        """Test num_repetitions validation."""
        # Valid values
        for reps in [1, 5, 10, 100]:
            config = FixedDimensionalEncodingConfig(num_repetitions=reps)
            assert config.num_repetitions == reps

        # Invalid values
        for reps in [0, -1, -5]:
            with pytest.raises(ValueError, match="num_repetitions must be positive"):
                FixedDimensionalEncodingConfig(num_repetitions=reps)

    def test_validation_num_simhash_projections(self):
        """Test num_simhash_projections validation."""
        # Valid values (0 is now allowed)
        for proj in [0, 1, 8, 16, 20]:
            config = FixedDimensionalEncodingConfig(num_simhash_projections=proj)
            assert config.num_simhash_projections == proj

        # Invalid values (only negative)
        for proj in [-1, -10]:
            with pytest.raises(
                ValueError, match="num_simhash_projections must be non-negative"
            ):
                FixedDimensionalEncodingConfig(num_simhash_projections=proj)

    def test_validation_projection_dimension(self):
        """Test projection_dimension validation."""
        # None is valid
        config = FixedDimensionalEncodingConfig(projection_dimension=None)
        assert config.projection_dimension is None

        # Valid positive values
        for dim in [1, 10, 100]:
            config = FixedDimensionalEncodingConfig(projection_dimension=dim)
            assert config.projection_dimension == dim

        # Invalid values
        for dim in [0, -1, -10]:
            with pytest.raises(
                ValueError, match="projection_dimension must be positive"
            ):
                FixedDimensionalEncodingConfig(projection_dimension=dim)

    def test_validation_final_projection_dimension(self):
        """Test final_projection_dimension validation."""
        # None is valid
        config = FixedDimensionalEncodingConfig(final_projection_dimension=None)
        assert config.final_projection_dimension is None

        # Valid positive values
        for dim in [1, 64, 256, 1024]:
            config = FixedDimensionalEncodingConfig(final_projection_dimension=dim)
            assert config.final_projection_dimension == dim

        # Invalid values
        for dim in [0, -1, -100]:
            with pytest.raises(
                ValueError, match="final_projection_dimension must be positive"
            ):
                FixedDimensionalEncodingConfig(final_projection_dimension=dim)

    def test_dataclass_features(self):
        """Test dataclass features work correctly."""
        config1 = FixedDimensionalEncodingConfig(dimension=5, seed=42)
        config2 = FixedDimensionalEncodingConfig(dimension=5, seed=42)
        config3 = FixedDimensionalEncodingConfig(dimension=5, seed=43)

        # Equality
        assert config1 == config2
        assert config1 != config3

        # Field access
        field_names = [f.name for f in fields(config1)]
        assert "dimension" in field_names
        assert "num_repetitions" in field_names
        assert "encoding_type" in field_names

    def test_encoding_type_enum(self):
        """Test EncodingType enum values."""
        assert EncodingType.DEFAULT_SUM == 0
        assert EncodingType.AVERAGE == 1

        # Test enum in config
        config_sum = FixedDimensionalEncodingConfig(
            encoding_type=EncodingType.DEFAULT_SUM
        )
        config_avg = FixedDimensionalEncodingConfig(encoding_type=EncodingType.AVERAGE)

        assert config_sum.encoding_type == EncodingType.DEFAULT_SUM
        assert config_avg.encoding_type == EncodingType.AVERAGE

    def test_projection_type_enum(self):
        """Test ProjectionType enum values."""
        assert ProjectionType.DEFAULT_IDENTITY == 0
        assert ProjectionType.AMS_SKETCH == 1

        # Test enum in config
        config_identity = FixedDimensionalEncodingConfig(
            projection_type=ProjectionType.DEFAULT_IDENTITY
        )
        config_ams = FixedDimensionalEncodingConfig(
            projection_type=ProjectionType.AMS_SKETCH
        )

        assert config_identity.projection_type == ProjectionType.DEFAULT_IDENTITY
        assert config_ams.projection_type == ProjectionType.AMS_SKETCH

    def test_config_combinations(self):
        """Test various configuration combinations."""
        # Query encoding with projection
        query_config = FixedDimensionalEncodingConfig(
            dimension=100,
            projection_dimension=50,
            projection_type=ProjectionType.AMS_SKETCH,
            encoding_type=EncodingType.DEFAULT_SUM,
            num_simhash_projections=10,
            final_projection_dimension=512,
        )
        assert query_config.dimension == 100
        assert query_config.projection_dimension == 50
        assert query_config.final_projection_dimension == 512

        # Document encoding with repetitions
        doc_config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_repetitions=10,
            encoding_type=EncodingType.AVERAGE,
            fill_empty_partitions=True,
        )
        assert doc_config.num_repetitions == 10
        assert doc_config.fill_empty_partitions is True

    def test_edge_case_values(self):
        """Test edge case values."""
        # Large dimensions
        config = FixedDimensionalEncodingConfig(
            dimension=10000, projection_dimension=5000, final_projection_dimension=8192
        )
        assert config.dimension == 10000

        # Maximum reasonable projections (limited by uint32 in C++)
        config = FixedDimensionalEncodingConfig(
            num_simhash_projections=30  # 2^30 partitions
        )
        assert config.num_simhash_projections == 30

        # Large seed values
        config = FixedDimensionalEncodingConfig(seed=2**31 - 1)
        assert config.seed == 2**31 - 1
