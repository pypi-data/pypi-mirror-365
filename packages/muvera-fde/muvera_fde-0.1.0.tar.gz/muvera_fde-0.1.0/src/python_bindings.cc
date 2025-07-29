// Copyright 2024 Yasyf Mohamedali
//
// Python bindings for Google's Fixed Dimensional Encoding
// Based on: https://github.com/google/graph-mining/tree/main/sketching/point_cloud

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

#include "fixed_dimensional_encoding.h"
#include "absl/status/statusor.h"

namespace py = pybind11;

namespace graph_mining {

// Convert numpy array to flat vector of floats
std::vector<float> numpy_to_flat_vector(py::array_t<float, py::array::c_style | py::array::forcecast> arr) {
    py::buffer_info buf = arr.request();

    if (buf.ndim != 2) {
        throw std::runtime_error("Input should be a 2D array");
    }

    auto data = static_cast<float*>(buf.ptr);
    size_t total_size = buf.shape[0] * buf.shape[1];

    // Copy data to flat vector (required by Google's API which expects std::vector<float>)
    std::vector<float> result(data, data + total_size);
    return result;
}

// Convert vector of floats to numpy array
py::array_t<float> vector_to_numpy(const std::vector<float>& vec) {
    // Create numpy array that owns the data
    auto result = py::array_t<float>(vec.size());
    py::buffer_info buf = result.request();
    std::memcpy(buf.ptr, vec.data(), vec.size() * sizeof(float));
    return result;
}

// Helper to handle StatusOr and convert errors to Python exceptions
template<typename T>
T check_status(const absl::StatusOr<T>& status_or) {
    if (!status_or.ok()) {
        throw std::runtime_error(std::string(status_or.status().message()));
    }
    return status_or.value();
}

// Python-friendly wrapper for encoding functions
// Note: We can release the GIL after copying the input data
py::array_t<float> py_generate_encoding(
    py::array_t<float, py::array::c_style | py::array::forcecast> points,
    const FixedDimensionalEncodingConfig& config) {

    // Copy input while GIL is held
    auto flat_points = numpy_to_flat_vector(points);

    // Release GIL for the computation
    std::vector<float> encoding;
    {
        py::gil_scoped_release release;
        encoding = check_status(GenerateFixedDimensionalEncoding(flat_points, config));
    }

    // Re-acquire GIL to create numpy array
    return vector_to_numpy(encoding);
}

py::array_t<float> py_generate_query_encoding(
    py::array_t<float, py::array::c_style | py::array::forcecast> points,
    const FixedDimensionalEncodingConfig& config) {

    auto flat_points = numpy_to_flat_vector(points);

    std::vector<float> encoding;
    {
        py::gil_scoped_release release;
        encoding = check_status(GenerateQueryFixedDimensionalEncoding(flat_points, config));
    }

    return vector_to_numpy(encoding);
}

py::array_t<float> py_generate_document_encoding(
    py::array_t<float, py::array::c_style | py::array::forcecast> points,
    const FixedDimensionalEncodingConfig& config) {

    auto flat_points = numpy_to_flat_vector(points);

    std::vector<float> encoding;
    {
        py::gil_scoped_release release;
        encoding = check_status(GenerateDocumentFixedDimensionalEncoding(flat_points, config));
    }

    return vector_to_numpy(encoding);
}

PYBIND11_MODULE(_core, m) {
    m.doc() = "Python bindings for fixed dimensional encoding of point clouds";

    // Bind enums
    py::enum_<FixedDimensionalEncodingConfig::EncodingType>(m, "EncodingType")
        .value("DEFAULT_SUM", FixedDimensionalEncodingConfig::DEFAULT_SUM)
        .value("AVERAGE", FixedDimensionalEncodingConfig::AVERAGE)
        .export_values();

    py::enum_<FixedDimensionalEncodingConfig::ProjectionType>(m, "ProjectionType")
        .value("DEFAULT_IDENTITY", FixedDimensionalEncodingConfig::DEFAULT_IDENTITY)
        .value("AMS_SKETCH", FixedDimensionalEncodingConfig::AMS_SKETCH)
        .export_values();

    // Bind config struct
    py::class_<FixedDimensionalEncodingConfig>(m, "Config")
        .def(py::init<>())
        .def_property("dimension",
            &FixedDimensionalEncodingConfig::dimension,
            &FixedDimensionalEncodingConfig::set_dimension)
        .def_property("num_repetitions",
            &FixedDimensionalEncodingConfig::num_repetitions,
            &FixedDimensionalEncodingConfig::set_num_repetitions)
        .def_property("num_simhash_projections",
            &FixedDimensionalEncodingConfig::num_simhash_projections,
            &FixedDimensionalEncodingConfig::set_num_simhash_projections)
        .def_property("seed",
            &FixedDimensionalEncodingConfig::seed,
            &FixedDimensionalEncodingConfig::set_seed)
        .def_property("encoding_type",
            &FixedDimensionalEncodingConfig::encoding_type,
            &FixedDimensionalEncodingConfig::set_encoding_type)
        .def_property("projection_dimension",
            &FixedDimensionalEncodingConfig::projection_dimension,
            &FixedDimensionalEncodingConfig::set_projection_dimension)
        .def_property("projection_type",
            &FixedDimensionalEncodingConfig::projection_type,
            &FixedDimensionalEncodingConfig::set_projection_type)
        .def_property("fill_empty_partitions",
            &FixedDimensionalEncodingConfig::fill_empty_partitions,
            &FixedDimensionalEncodingConfig::set_fill_empty_partitions)
        .def_property("final_projection_dimension",
            &FixedDimensionalEncodingConfig::final_projection_dimension,
            &FixedDimensionalEncodingConfig::set_final_projection_dimension);

    // Bind encoding functions
    // Note: We handle GIL release manually inside the functions
    m.def("generate_encoding", &py_generate_encoding,
          "Generate fixed dimensional encoding for a point cloud",
          py::arg("points"), py::arg("config"));

    m.def("generate_query_encoding", &py_generate_query_encoding,
          "Generate query encoding (sum aggregation)",
          py::arg("points"), py::arg("config"));

    m.def("generate_document_encoding", &py_generate_document_encoding,
          "Generate document encoding (average aggregation)",
          py::arg("points"), py::arg("config"));
}

}  // namespace graph_mining
