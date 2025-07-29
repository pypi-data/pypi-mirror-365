"""Configuration dataclasses for fixed dimensional encoding."""

from dataclasses import dataclass, field
from enum import IntEnum


class EncodingType(IntEnum):
    """Type of encoding to use."""

    DEFAULT_SUM = 0  # For query encoding
    AVERAGE = 1  # For document encoding


class ProjectionType(IntEnum):
    """Type of projection to use."""

    DEFAULT_IDENTITY = 0
    AMS_SKETCH = 1


@dataclass
class FixedDimensionalEncodingConfig:
    """Configuration for fixed dimensional encoding.

    Attributes:
        dimension: Dimension of the input points.
        num_repetitions: Number of repetitions for the encoding.
        num_simhash_projections: Number of SimHash projections to use.
        seed: Random seed for reproducibility.
        encoding_type: Type of encoding (sum for query, average for document).
        projection_dimension: Dimension to project points to before encoding.
        projection_type: Type of projection to use.
        fill_empty_partitions: Whether to fill empty partitions with zeros.
        final_projection_dimension: Optional final dimension to project to.
    """

    dimension: int = field(default=3)
    num_repetitions: int = field(default=1)
    num_simhash_projections: int = field(default=8)
    seed: int = field(default=1)
    encoding_type: EncodingType = field(default=EncodingType.DEFAULT_SUM)
    projection_dimension: int | None = field(default=None)
    projection_type: ProjectionType = field(default=ProjectionType.DEFAULT_IDENTITY)
    fill_empty_partitions: bool = field(default=False)
    final_projection_dimension: int | None = field(default=None)

    def __post_init__(self):
        """Validate configuration parameters."""
        if self.dimension <= 0:
            raise ValueError("dimension must be positive")
        if self.num_repetitions <= 0:
            raise ValueError("num_repetitions must be positive")
        if self.num_simhash_projections < 0:
            raise ValueError("num_simhash_projections must be non-negative")
        if self.projection_dimension is not None and self.projection_dimension <= 0:
            raise ValueError("projection_dimension must be positive")
        if (
            self.final_projection_dimension is not None
            and self.final_projection_dimension <= 0
        ):
            raise ValueError("final_projection_dimension must be positive")
