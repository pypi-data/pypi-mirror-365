# CMakeLists.txt

cmake_minimum_required(VERSION 3.15)
project(bytoken LANGUAGES CXX)

find_package(pybind11 REQUIRED)

# Define the C++ extension module with an "internal" name
pybind11_add_module(_bytoken_core
    bytoken/bytoken_binding.cpp
    bytoken/bytoken.cpp
)

# Add include directory for bytoken.h
target_include_directories(_bytoken_core PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/bytoken")

install(TARGETS _bytoken_core DESTINATION bytoken)