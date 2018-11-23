cmake_minimum_required(VERSION 3.0.0)

if (NOT CMAKE_VERSION VERSION_LESS "3.1")
    cmake_policy(SET CMP0054 NEW)
endif()

project(Open3D_Conanbuild)

FindPackage(Eigen)
FindPackage(Pybind11)
FindPacakge(GLFW)
FindPackage(GLEW)

add_subdirectory(open3d)