"""High-level Python API for fixed dimensional encoding."""

from typing import cast

import numpy as np

from . import _core
from .config import EncodingType, FixedDimensionalEncodingConfig, ProjectionType


class FixedDimensionalEncoder:
    """Fixed dimensional encoder for point clouds.

    This encoder implements the Fixed Dimensional Encoding (FDE) algorithm
    for encoding variable-sized point clouds into fixed-dimensional vectors.
    It supports both query encoding (sum aggregation) and document encoding
    (average aggregation).

    Example:
        >>> config = FixedDimensionalEncodingConfig(
        ...     dimension=3,
        ...     num_simhash_projections=8,
        ...     encoding_type=EncodingType.DEFAULT_SUM
        ... )
        >>> encoder = FixedDimensionalEncoder(config)
        >>> points = np.random.randn(100, 3).astype(np.float32)
        >>> encoding = encoder.encode(points)
    """

    def __init__(self, config: FixedDimensionalEncodingConfig):
        """Initialize the encoder with a configuration.

        Args:
            config: Configuration for the encoding process.
        """
        self.config = config
        self._core_config = self._create_core_config()

    def _create_core_config(self) -> _core.Config:
        """Convert Python config to C++ config."""
        core_config = _core.Config()
        core_config.dimension = self.config.dimension
        core_config.num_repetitions = self.config.num_repetitions
        core_config.num_simhash_projections = self.config.num_simhash_projections
        core_config.seed = self.config.seed

        # Convert enum types
        if self.config.encoding_type == EncodingType.DEFAULT_SUM:
            core_config.encoding_type = _core.EncodingType.DEFAULT_SUM
        else:
            core_config.encoding_type = _core.EncodingType.AVERAGE

        # Handle optional fields
        if self.config.projection_dimension is not None:
            core_config.projection_dimension = self.config.projection_dimension
        else:
            core_config.projection_dimension = 0  # Google's default

        if self.config.projection_type == ProjectionType.DEFAULT_IDENTITY:
            core_config.projection_type = _core.ProjectionType.DEFAULT_IDENTITY
        else:
            core_config.projection_type = _core.ProjectionType.AMS_SKETCH

        core_config.fill_empty_partitions = self.config.fill_empty_partitions

        if self.config.final_projection_dimension is not None:
            core_config.final_projection_dimension = (
                self.config.final_projection_dimension
            )

        return core_config

    def encode(self, points: np.ndarray) -> np.ndarray:
        """Encode a point cloud into a fixed-dimensional vector.

        Args:
            points: A numpy array of shape (n_points, dimension) containing
                   the point cloud data. Must be float32.

        Returns:
            A 1D numpy array containing the fixed-dimensional encoding.

        Raises:
            ValueError: If the input array has incorrect shape or dtype.
        """
        if not isinstance(points, np.ndarray):
            raise ValueError("points must be a numpy array")

        if points.ndim != 2:
            raise ValueError(f"points must be a 2D array, got shape {points.shape}")

        if points.shape[1] != self.config.dimension:
            raise ValueError(
                f"points dimension {points.shape[1]} doesn't match "
                f"config dimension {self.config.dimension}"
            )

        # Ensure float32 dtype for compatibility
        if points.dtype != np.float32:
            points = points.astype(np.float32)

        # Handle empty point cloud
        if points.shape[0] == 0:
            points = np.zeros((0, self.config.dimension), dtype=np.float32)

        return cast(np.ndarray, _core.generate_encoding(points, self._core_config))

    def encode_query(self, points: np.ndarray) -> np.ndarray:
        """Encode a query point cloud (forces sum aggregation).

        Args:
            points: A numpy array of shape (n_points, dimension) containing
                   the point cloud data. Must be float32.

        Returns:
            A 1D numpy array containing the query encoding.
        """
        if not isinstance(points, np.ndarray):
            raise ValueError("points must be a numpy array")

        if points.ndim != 2:
            raise ValueError(f"points must be a 2D array, got shape {points.shape}")

        if points.shape[1] != self.config.dimension:
            raise ValueError(
                f"points dimension {points.shape[1]} doesn't match "
                f"config dimension {self.config.dimension}"
            )

        # Ensure float32 dtype
        if points.dtype != np.float32:
            points = points.astype(np.float32)

        # Handle empty point cloud
        if points.shape[0] == 0:
            points = np.zeros((0, self.config.dimension), dtype=np.float32)

        return cast(
            np.ndarray, _core.generate_query_encoding(points, self._core_config)
        )

    def encode_document(self, points: np.ndarray) -> np.ndarray:
        """Encode a document point cloud (forces average aggregation).

        Args:
            points: A numpy array of shape (n_points, dimension) containing
                   the point cloud data. Must be float32.

        Returns:
            A 1D numpy array containing the document encoding.
        """
        if not isinstance(points, np.ndarray):
            raise ValueError("points must be a numpy array")

        if points.ndim != 2:
            raise ValueError(f"points must be a 2D array, got shape {points.shape}")

        if points.shape[1] != self.config.dimension:
            raise ValueError(
                f"points dimension {points.shape[1]} doesn't match "
                f"config dimension {self.config.dimension}"
            )

        # Ensure float32 dtype
        if points.dtype != np.float32:
            points = points.astype(np.float32)

        # Handle empty point cloud
        if points.shape[0] == 0:
            points = np.zeros((0, self.config.dimension), dtype=np.float32)

        return cast(
            np.ndarray, _core.generate_document_encoding(points, self._core_config)
        )

    @property
    def output_dimension(self) -> int:
        """Get the output dimension of the encoding.

        Returns:
            The dimension of the encoded vectors.
        """
        if self.config.final_projection_dimension is not None:
            return self.config.final_projection_dimension

        num_partitions = 1 << self.config.num_simhash_projections
        base_dim = self.config.dimension
        if self.config.projection_dimension is not None:
            base_dim = self.config.projection_dimension

        return num_partitions * base_dim * self.config.num_repetitions
