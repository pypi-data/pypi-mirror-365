"""Type stubs for the _core extension module."""

from enum import IntEnum

import numpy as np
import numpy.typing as npt

class EncodingType(IntEnum):
    """Encoding type enumeration."""

    DEFAULT_SUM = 0
    AVERAGE = 1

class ProjectionType(IntEnum):
    """Projection type enumeration."""

    DEFAULT_IDENTITY = 0
    AMS_SKETCH = 1

class Config:
    """Configuration for fixed dimensional encoding."""

    dimension: int
    num_repetitions: int
    num_simhash_projections: int
    seed: int
    encoding_type: EncodingType
    projection_dimension: int
    projection_type: ProjectionType
    fill_empty_partitions: bool
    final_projection_dimension: int

    def __init__(self) -> None: ...

def generate_encoding(
    points: npt.NDArray[np.float32], config: Config
) -> npt.NDArray[np.float32]:
    """Generate fixed dimensional encoding for a point cloud.

    Args:
        points: A 2D numpy array of shape (n_points, dimension) with float32 dtype.
        config: Configuration object for the encoding.

    Returns:
        A 1D numpy array containing the fixed-dimensional encoding.
    """
    ...

def generate_query_encoding(
    points: npt.NDArray[np.float32], config: Config
) -> npt.NDArray[np.float32]:
    """Generate query encoding (sum aggregation).

    Args:
        points: A 2D numpy array of shape (n_points, dimension) with float32 dtype.
        config: Configuration object for the encoding.

    Returns:
        A 1D numpy array containing the query encoding.
    """
    ...

def generate_document_encoding(
    points: npt.NDArray[np.float32], config: Config
) -> npt.NDArray[np.float32]:
    """Generate document encoding (average aggregation).

    Args:
        points: A 2D numpy array of shape (n_points, dimension) with float32 dtype.
        config: Configuration object for the encoding.

    Returns:
        A 1D numpy array containing the document encoding.
    """
    ...
