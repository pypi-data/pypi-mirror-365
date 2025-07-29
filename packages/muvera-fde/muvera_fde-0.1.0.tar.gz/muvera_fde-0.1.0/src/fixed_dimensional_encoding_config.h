// Copyright 2024 Yasyf Mohamedali
//
// Adapted from Google's graph-mining project:
// https://github.com/google/graph-mining/tree/main/sketching/point_cloud
//
// This file replaces the protobuf config with a simple struct

#ifndef FIXED_DIMENSIONAL_ENCODING_CONFIG_H_
#define FIXED_DIMENSIONAL_ENCODING_CONFIG_H_

#include <cstdint>

namespace graph_mining {

// Configuration struct replacing the protobuf FixedDimensionalEncodingConfig
struct FixedDimensionalEncodingConfig {
  // Enums matching the protobuf definitions
  enum EncodingType {
    DEFAULT_SUM = 0,
    AVERAGE = 1
  };

  enum ProjectionType {
    DEFAULT_IDENTITY = 0,
    AMS_SKETCH = 1
  };

  // Fields with default values matching the protobuf
  int32_t dimension_ = 0;
  int32_t num_repetitions_ = 1;
  int32_t num_simhash_projections_ = 0;
  int32_t seed_ = 1;
  EncodingType encoding_type_ = DEFAULT_SUM;
  int32_t projection_dimension_ = 0;
  ProjectionType projection_type_ = DEFAULT_IDENTITY;
  bool fill_empty_partitions_ = false;
  int32_t final_projection_dimension_ = 0;
  bool has_final_projection_dimension_ = false;

  // Accessors to match protobuf interface
  int32_t dimension() const { return dimension_; }
  int32_t num_repetitions() const { return num_repetitions_; }
  int32_t num_simhash_projections() const { return num_simhash_projections_; }
  int32_t seed() const { return seed_; }
  EncodingType encoding_type() const { return encoding_type_; }
  int32_t projection_dimension() const { return projection_dimension_; }
  ProjectionType projection_type() const { return projection_type_; }
  bool fill_empty_partitions() const { return fill_empty_partitions_; }
  int32_t final_projection_dimension() const { return final_projection_dimension_; }
  bool has_final_projection_dimension() const { return has_final_projection_dimension_; }

  // Setters for pybind11
  void set_dimension(int32_t v) { dimension_ = v; }
  void set_num_repetitions(int32_t v) { num_repetitions_ = v; }
  void set_num_simhash_projections(int32_t v) { num_simhash_projections_ = v; }
  void set_seed(int32_t v) { seed_ = v; }
  void set_encoding_type(EncodingType v) { encoding_type_ = v; }
  void set_projection_dimension(int32_t v) { projection_dimension_ = v; }
  void set_projection_type(ProjectionType v) { projection_type_ = v; }
  void set_fill_empty_partitions(bool v) { fill_empty_partitions_ = v; }
  void set_final_projection_dimension(int32_t v) {
    final_projection_dimension_ = v;
    has_final_projection_dimension_ = true;
  }
};

}  // namespace graph_mining

#endif  // FIXED_DIMENSIONAL_ENCODING_CONFIG_H_
