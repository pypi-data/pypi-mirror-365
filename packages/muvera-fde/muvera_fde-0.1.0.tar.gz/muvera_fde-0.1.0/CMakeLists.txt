cmake_minimum_required(VERSION 3.15)
project(muvera_fde LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Find Python and pybind11
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 CONFIG REQUIRED)

# Download and setup dependencies
include(FetchContent)

# Eigen
FetchContent_Declare(
    eigen
    GIT_REPOSITORY https://gitlab.com/libeigen/eigen.git
    GIT_TAG 3.4.0
    GIT_SHALLOW TRUE
    GIT_PROGRESS TRUE
)
set(EIGEN_BUILD_DOC OFF)
set(EIGEN_BUILD_PKGCONFIG OFF)
set(BUILD_TESTING OFF)

# Abseil
FetchContent_Declare(
    absl
    GIT_REPOSITORY https://github.com/abseil/abseil-cpp.git
    GIT_TAG 20240116.2  # LTS release
    GIT_SHALLOW TRUE
    GIT_PROGRESS TRUE
)
set(ABSL_PROPAGATE_CXX_STD ON)
set(ABSL_BUILD_TESTING OFF)

FetchContent_MakeAvailable(eigen absl)

# Create the extension module
pybind11_add_module(_core MODULE
    src/fixed_dimensional_encoding.cc
    src/python_bindings.cc
)

# Set properties
target_compile_features(_core PRIVATE cxx_std_17)
target_link_libraries(_core PRIVATE 
    Eigen3::Eigen
    absl::status
    absl::statusor
    absl::strings
    absl::log
    absl::check
    absl::span
)

# Install the extension module
install(TARGETS _core COMPONENT python DESTINATION muvera_fde)