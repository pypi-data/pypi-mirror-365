"""Basic usage examples for point cloud sketching."""

import numpy as np
import matplotlib.pyplot as plt
from muvera_fde import (
    FixedDimensionalEncodingConfig,
    FixedDimensionalEncoder,
    EncodingType,
    ProjectionType,
)


def generate_point_cloud(n_points: int, dimension: int = 3) -> np.ndarray:
    """Generate a random point cloud."""
    return np.random.randn(n_points, dimension).astype(np.float32)


def example_basic_encoding():
    """Basic encoding example."""
    print("=== Basic Encoding Example ===")
    
    # Create configuration
    config = FixedDimensionalEncodingConfig(
        dimension=3,
        num_simhash_projections=8,
        num_repetitions=2,
        seed=42,
    )
    
    # Initialize encoder
    encoder = FixedDimensionalEncoder(config)
    
    # Generate point cloud
    points = generate_point_cloud(100, 3)
    print(f"Input shape: {points.shape}")
    
    # Encode
    encoding = encoder.encode(points)
    print(f"Encoding shape: {encoding.shape}")
    print(f"Output dimension: {encoder.output_dimension}")
    print(f"Encoding stats: min={encoding.min():.3f}, max={encoding.max():.3f}, mean={encoding.mean():.3f}")
    print()


def example_query_vs_document():
    """Compare query and document encodings."""
    print("=== Query vs Document Encoding ===")
    
    points = generate_point_cloud(50, 3)
    
    # Query encoding (sum aggregation)
    query_config = FixedDimensionalEncodingConfig(
        dimension=3,
        encoding_type=EncodingType.DEFAULT_SUM,
        num_simhash_projections=4,
    )
    query_encoder = FixedDimensionalEncoder(query_config)
    query_encoding = query_encoder.encode_query(points)
    
    # Document encoding (average aggregation)
    doc_config = FixedDimensionalEncodingConfig(
        dimension=3,
        encoding_type=EncodingType.AVERAGE,
        num_simhash_projections=4,
    )
    doc_encoder = FixedDimensionalEncoder(doc_config)
    doc_encoding = doc_encoder.encode_document(points)
    
    print(f"Query encoding stats: mean={query_encoding.mean():.3f}, std={query_encoding.std():.3f}")
    print(f"Document encoding stats: mean={doc_encoding.mean():.3f}, std={doc_encoding.std():.3f}")
    
    # Plot comparison
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    ax1.hist(query_encoding, bins=30, alpha=0.7, label='Query')
    ax1.set_title('Query Encoding Distribution')
    ax1.set_xlabel('Value')
    ax1.set_ylabel('Count')
    
    ax2.hist(doc_encoding, bins=30, alpha=0.7, label='Document', color='orange')
    ax2.set_title('Document Encoding Distribution')
    ax2.set_xlabel('Value')
    ax2.set_ylabel('Count')
    
    plt.tight_layout()
    plt.savefig('encoding_comparison.png')
    print("Saved encoding comparison plot to encoding_comparison.png")
    print()


def example_similarity_search():
    """Demonstrate similarity search with encodings."""
    print("=== Similarity Search Example ===")
    
    config = FixedDimensionalEncodingConfig(
        dimension=3,
        num_simhash_projections=8,
        num_repetitions=4,
        seed=42,
    )
    encoder = FixedDimensionalEncoder(config)
    
    # Create database of point clouds
    n_clouds = 100
    database_encodings = []
    
    for i in range(n_clouds):
        # Generate point clouds with varying sizes
        n_points = np.random.randint(20, 200)
        points = generate_point_cloud(n_points, 3)
        encoding = encoder.encode_document(points)
        database_encodings.append(encoding)
    
    database_encodings = np.array(database_encodings)
    print(f"Database shape: {database_encodings.shape}")
    
    # Create query point cloud
    query_points = generate_point_cloud(50, 3)
    query_encoding = encoder.encode_query(query_points)
    
    # Compute similarities (cosine similarity)
    query_norm = query_encoding / (np.linalg.norm(query_encoding) + 1e-8)
    database_norms = database_encodings / (np.linalg.norm(database_encodings, axis=1, keepdims=True) + 1e-8)
    similarities = database_norms @ query_norm
    
    # Find top-k most similar
    k = 5
    top_k_indices = np.argsort(similarities)[-k:][::-1]
    
    print(f"Top {k} most similar point clouds:")
    for i, idx in enumerate(top_k_indices):
        print(f"  {i+1}. Cloud {idx}: similarity = {similarities[idx]:.4f}")
    print()


def example_dimensionality_reduction():
    """Example with dimensionality reduction."""
    print("=== Dimensionality Reduction Example ===")
    
    # High-dimensional input
    config = FixedDimensionalEncodingConfig(
        dimension=128,
        projection_dimension=32,  # Reduce to 32D before encoding
        projection_type=ProjectionType.AMS_SKETCH,
        num_simhash_projections=6,
        final_projection_dimension=256,  # Final output dimension
        seed=42,
    )
    encoder = FixedDimensionalEncoder(config)
    
    # Generate high-dimensional point cloud
    points = generate_point_cloud(200, 128)
    print(f"Input shape: {points.shape}")
    
    encoding = encoder.encode(points)
    print(f"Final encoding shape: {encoding.shape}")
    
    # Compare sizes
    input_size = points.size * 4  # float32
    encoding_size = encoding.size * 4
    compression_ratio = input_size / encoding_size
    
    print(f"Input size: {input_size / 1024:.2f} KB")
    print(f"Encoding size: {encoding_size / 1024:.2f} KB")
    print(f"Compression ratio: {compression_ratio:.2f}x")
    print()


def example_batch_processing():
    """Example of batch processing multiple point clouds."""
    print("=== Batch Processing Example ===")
    
    config = FixedDimensionalEncodingConfig(
        dimension=3,
        num_simhash_projections=8,
        encoding_type=EncodingType.AVERAGE,
    )
    encoder = FixedDimensionalEncoder(config)
    
    # Process multiple point clouds
    n_clouds = 1000
    encodings = []
    
    import time
    start_time = time.time()
    
    for i in range(n_clouds):
        n_points = np.random.randint(10, 100)
        points = generate_point_cloud(n_points, 3)
        encoding = encoder.encode(points)
        encodings.append(encoding)
    
    elapsed_time = time.time() - start_time
    encodings = np.array(encodings)
    
    print(f"Processed {n_clouds} point clouds in {elapsed_time:.2f} seconds")
    print(f"Average time per cloud: {elapsed_time / n_clouds * 1000:.2f} ms")
    print(f"Encodings shape: {encodings.shape}")
    
    # Analyze encoding diversity
    pairwise_distances = np.sqrt(((encodings[:, None] - encodings[None, :])**2).sum(axis=2))
    avg_distance = pairwise_distances[np.triu_indices(n_clouds, k=1)].mean()
    print(f"Average pairwise distance: {avg_distance:.3f}")
    print()


if __name__ == "__main__":
    # Create examples directory
    import os
    os.makedirs("examples", exist_ok=True)
    
    # Run all examples
    example_basic_encoding()
    example_query_vs_document()
    example_similarity_search()
    example_dimensionality_reduction()
    example_batch_processing()