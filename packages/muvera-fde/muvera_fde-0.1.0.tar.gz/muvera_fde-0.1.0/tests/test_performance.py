"""Performance benchmarks for point cloud sketching."""

import time

import numpy as np
import pytest

from muvera_fde import (
    EncodingType,
    FixedDimensionalEncoder,
    FixedDimensionalEncodingConfig,
    ProjectionType,
)


class TestPerformance:
    """Performance benchmarks and tests."""

    def test_encoding_speed_small(self):
        """Benchmark encoding speed for small point clouds."""
        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_simhash_projections=8,
        )
        encoder = FixedDimensionalEncoder(config)

        # Small point cloud
        points = np.random.randn(100, 3).astype(np.float32)

        # Warmup
        _ = encoder.encode(points)

        # Time multiple runs
        n_runs = 100
        start_time = time.time()
        for _ in range(n_runs):
            _ = encoder.encode(points)
        elapsed = time.time() - start_time

        avg_time = elapsed / n_runs * 1000  # ms
        print(f"\nSmall cloud (100 points): {avg_time:.2f} ms per encoding")

        # Should be fast for small clouds
        assert avg_time < 10  # Less than 10ms

    def test_encoding_speed_medium(self):
        """Benchmark encoding speed for medium point clouds."""
        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_simhash_projections=8,
        )
        encoder = FixedDimensionalEncoder(config)

        # Medium point cloud
        points = np.random.randn(1000, 3).astype(np.float32)

        # Warmup
        _ = encoder.encode(points)

        # Time multiple runs
        n_runs = 50
        start_time = time.time()
        for _ in range(n_runs):
            _ = encoder.encode(points)
        elapsed = time.time() - start_time

        avg_time = elapsed / n_runs * 1000  # ms
        print(f"Medium cloud (1000 points): {avg_time:.2f} ms per encoding")

        # Should still be reasonably fast
        assert avg_time < 50  # Less than 50ms

    def test_encoding_speed_large(self):
        """Benchmark encoding speed for large point clouds."""
        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_simhash_projections=8,
        )
        encoder = FixedDimensionalEncoder(config)

        # Large point cloud
        points = np.random.randn(10000, 3).astype(np.float32)

        # Warmup
        _ = encoder.encode(points)

        # Time multiple runs
        n_runs = 10
        start_time = time.time()
        for _ in range(n_runs):
            _ = encoder.encode(points)
        elapsed = time.time() - start_time

        avg_time = elapsed / n_runs * 1000  # ms
        print(f"Large cloud (10000 points): {avg_time:.2f} ms per encoding")

        # Should complete in reasonable time
        assert avg_time < 500  # Less than 500ms

    def test_scaling_with_points(self):
        """Test how encoding time scales with number of points."""
        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_simhash_projections=8,
        )
        encoder = FixedDimensionalEncoder(config)

        sizes = [100, 500, 1000, 2000, 5000]
        times = []

        for size in sizes:
            points = np.random.randn(size, 3).astype(np.float32)

            # Time single run after warmup
            _ = encoder.encode(points)

            start_time = time.time()
            _ = encoder.encode(points)
            elapsed = time.time() - start_time

            times.append(elapsed * 1000)  # ms

        print("\nScaling with number of points:")
        for size, t in zip(sizes, times, strict=False):
            print(f"  {size} points: {t:.2f} ms")

        # Check that it scales roughly linearly
        # Time should increase but not explode
        assert times[-1] < times[0] * 100  # Not more than 100x slower

    def test_scaling_with_dimensions(self):
        """Test how encoding time scales with point dimensions."""
        sizes = [3, 10, 50, 100, 200]
        times = []

        n_points = 1000

        for dim in sizes:
            config = FixedDimensionalEncodingConfig(
                dimension=dim,
                num_simhash_projections=8,
            )
            encoder = FixedDimensionalEncoder(config)

            points = np.random.randn(n_points, dim).astype(np.float32)

            # Warmup
            _ = encoder.encode(points)

            start_time = time.time()
            _ = encoder.encode(points)
            elapsed = time.time() - start_time

            times.append(elapsed * 1000)  # ms

        print("\nScaling with dimensions:")
        for dim, t in zip(sizes, times, strict=False):
            print(f"  {dim}D: {t:.2f} ms")

        # Should scale reasonably with dimension
        assert times[-1] < times[0] * 200  # Not more than 200x slower

    def test_scaling_with_projections(self):
        """Test how encoding time scales with number of projections."""
        projections = [4, 6, 8, 10, 12]
        times = []

        n_points = 1000

        for n_proj in projections:
            config = FixedDimensionalEncodingConfig(
                dimension=3,
                num_simhash_projections=n_proj,
            )
            encoder = FixedDimensionalEncoder(config)

            points = np.random.randn(n_points, 3).astype(np.float32)

            # Warmup
            _ = encoder.encode(points)

            start_time = time.time()
            _ = encoder.encode(points)
            elapsed = time.time() - start_time

            times.append(elapsed * 1000)  # ms

        print("\nScaling with projections:")
        for n_proj, t in zip(projections, times, strict=False):
            print(f"  {n_proj} projections ({1 << n_proj} partitions): {t:.2f} ms")

        # Should scale exponentially with projections (due to partitions)
        # But still be reasonable for practical values
        assert all(t < 1000 for t in times)  # All under 1 second

    def test_projection_overhead(self):
        """Test overhead of dimension projection."""
        n_points = 1000
        high_dim = 100
        low_dim = 20

        # Without projection
        config1 = FixedDimensionalEncodingConfig(
            dimension=low_dim,
            num_simhash_projections=8,
        )
        encoder1 = FixedDimensionalEncoder(config1)
        points1 = np.random.randn(n_points, low_dim).astype(np.float32)

        # With projection
        config2 = FixedDimensionalEncodingConfig(
            dimension=high_dim,
            projection_dimension=low_dim,
            projection_type=ProjectionType.AMS_SKETCH,
            num_simhash_projections=8,
        )
        encoder2 = FixedDimensionalEncoder(config2)
        points2 = np.random.randn(n_points, high_dim).astype(np.float32)

        # Warmup
        _ = encoder1.encode(points1)
        _ = encoder2.encode(points2)

        # Time without projection
        start_time = time.time()
        _ = encoder1.encode(points1)
        time_without = time.time() - start_time

        # Time with projection
        start_time = time.time()
        _ = encoder2.encode(points2)
        time_with = time.time() - start_time

        overhead = (time_with - time_without) / time_without * 100
        print(f"\nProjection overhead: {overhead:.1f}%")
        print(f"  Without projection: {time_without * 1000:.2f} ms")
        print(f"  With projection: {time_with * 1000:.2f} ms")

        # Projection should add some overhead but not be prohibitive
        assert overhead < 500  # Less than 5x overhead

    def test_repetition_overhead(self):
        """Test overhead of multiple repetitions."""
        n_points = 1000

        configs_and_names = [
            (
                FixedDimensionalEncodingConfig(
                    dimension=3,
                    num_simhash_projections=8,
                    num_repetitions=1,
                ),
                "1 repetition",
            ),
            (
                FixedDimensionalEncodingConfig(
                    dimension=3,
                    num_simhash_projections=8,
                    num_repetitions=5,
                ),
                "5 repetitions",
            ),
            (
                FixedDimensionalEncodingConfig(
                    dimension=3,
                    num_simhash_projections=8,
                    num_repetitions=10,
                ),
                "10 repetitions",
            ),
        ]

        points = np.random.randn(n_points, 3).astype(np.float32)

        print("\nRepetition overhead:")
        base_time = None

        for config, name in configs_and_names:
            encoder = FixedDimensionalEncoder(config)

            # Warmup
            _ = encoder.encode(points)

            # Time
            start_time = time.time()
            _ = encoder.encode(points)
            elapsed = time.time() - start_time

            if base_time is None:
                base_time = elapsed

            print(f"  {name}: {elapsed * 1000:.2f} ms ({elapsed / base_time:.1f}x)")

        # Should scale roughly linearly with repetitions
        assert elapsed < base_time * 15  # Not more than 15x for 10 reps

    def test_memory_efficiency(self):
        """Test memory efficiency of encoding."""
        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_simhash_projections=8,
        )
        encoder = FixedDimensionalEncoder(config)

        # Large point cloud
        n_points = 10000
        points = np.random.randn(n_points, 3).astype(np.float32)

        # Input size
        input_bytes = points.nbytes

        # Encode
        encoding = encoder.encode(points)
        output_bytes = encoding.nbytes

        compression_ratio = input_bytes / output_bytes

        print("\nMemory efficiency:")
        print(f"  Input size: {input_bytes / 1024:.1f} KB")
        print(f"  Output size: {output_bytes / 1024:.1f} KB")
        print(f"  Compression ratio: {compression_ratio:.2f}x")

        # Output should be fixed size regardless of input
        assert output_bytes == encoder.output_dimension * 4  # float32

    def test_batch_vs_individual(self):
        """Compare batch encoding vs individual encoding."""
        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_simhash_projections=8,
            encoding_type=EncodingType.AVERAGE,
        )
        encoder = FixedDimensionalEncoder(config)

        # Generate point clouds
        n_clouds = 100
        clouds = []
        for _ in range(n_clouds):
            size = np.random.randint(50, 150)
            cloud = np.random.randn(size, 3).astype(np.float32)
            clouds.append(cloud)

        # Time individual encoding
        start_time = time.time()
        individual_encodings = []
        for cloud in clouds:
            enc = encoder.encode(cloud)
            individual_encodings.append(enc)
        individual_time = time.time() - start_time

        print("\nBatch vs Individual:")
        print(f"  Individual encoding: {individual_time * 1000:.1f} ms total")
        print(f"  Average per cloud: {individual_time / n_clouds * 1000:.2f} ms")

        # Currently we process individually, but this shows the pattern
        assert len(individual_encodings) == n_clouds

    @pytest.mark.parametrize("dtype", [np.float32, np.float64])
    def test_dtype_conversion_overhead(self, dtype):
        """Test overhead of dtype conversion."""
        config = FixedDimensionalEncodingConfig(
            dimension=3,
            num_simhash_projections=8,
        )
        encoder = FixedDimensionalEncoder(config)

        points = np.random.randn(1000, 3).astype(dtype)

        # Warmup
        _ = encoder.encode(points)

        # Time encoding
        start_time = time.time()
        _ = encoder.encode(points)
        elapsed = time.time() - start_time

        print(f"\nEncoding {dtype.__name__}: {elapsed * 1000:.2f} ms")

        # Should handle both dtypes efficiently
        assert elapsed < 0.1  # Less than 100ms
