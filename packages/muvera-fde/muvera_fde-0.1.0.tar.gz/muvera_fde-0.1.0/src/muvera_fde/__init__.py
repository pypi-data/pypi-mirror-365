"""Point cloud sketching using Google's Fixed Dimensional Encoding (FDE).

This module provides Python bindings for the FDE algorithm from Google's
graph-mining project, as described in the MUVERA paper:
https://research.google/blog/muvera-making-multi-vector-retrieval-as-fast-as-single-vector-search/

Original implementation:
https://github.com/google/graph-mining/tree/main/sketching/point_cloud
"""

__version__ = "0.1.0"

from .config import EncodingType, FixedDimensionalEncodingConfig, ProjectionType
from .encoder import FixedDimensionalEncoder

__all__ = [
    "FixedDimensionalEncodingConfig",
    "EncodingType",
    "ProjectionType",
    "FixedDimensionalEncoder",
]
