from conans import ConanFile, CMake, tools
import os
from io import StringIO
import shutil


class Open3dConan(ConanFile):
    upstream_version = "0.13.0"
    package_revision = ""
    version = "{0}{1}".format(upstream_version, package_revision)

    name = "open3d"
    license = "https://github.com/IntelVCL/Open3D/raw/master/LICENSE"
    description = "Open3D: A Modern Library for 3D Data Processing http://www.open3d.org"
    url = "https://github.com/ulricheck/Open3D"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_find_package", "cmake"
    short_paths = True

    requires = (
        "eigen/[>=3.3.9]@camposs/stable",
        "glfw/3.3.4",
        #"assimp/5.2.2",

        # "fmt/6.2.1",
        # "glew/[>=2.1.0]@camposs/stable",
        )

    options = {
        "shared": [True, False],
        "with_visualization": [True, False],
        "with_python": [True, False],
        }

    default_options = (
        "shared=True",
        "with_visualization=False",
        "with_python=False",
        )

    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"

    scm = {"revision": "v0.13.0",
           "subfolder": "source_subfolder",
           "submodule": "recursive",
           "type": "git",
           "url": "https://github.com/isl-org/Open3D.git"}

    exports = [
        "patches/fix_eigen_transform_error.patch",
        "update_imgui_1.87.patch"
        ]


    # issue with CMake add_subdirectory https://github.com/intel-isl/Open3D/issues/3116
    # exports_sources = "CMakeLists.txt",

    def requirements(self):
        if self.options.with_python:
            self.requires("python_dev_config/[>=1.0]@camposs/stable")
        if self.options.with_visualization:
            self.requires("glew/2.2.0")
            self.requires("imgui/cci.20220207+1.87.docking")
    #         self.requires("imgui/1.66@camposs/stable")
    
    def configure(self):
        if self.options.with_visualization and self.options.shared:
            self.options['glew'].shared = True


    def _cmake_configure(self):
        cmake = CMake(self)

        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["BUILD_GUI"] = 'OFF'
        cmake.definitions["BUILD_PYTHON_MODULE"] = 'OFF'
        cmake.definitions["BUILD_EXAMPLES"] = 'OFF'

        # Linking issue: https://github.com/intel-isl/Open3D/issues/2286
        cmake.definitions["GLIBCXX_USE_CXX11_ABI"] = True

        cmake.definitions["USE_SYSTEM_EIGEN3"] = 'ON'
        cmake.definitions["USE_SYSTEM_GLFW"] = 'ON'
        cmake.definitions["USE_SYSTEM_GLEW"] = 'ON'
        cmake.definitions["USE_SYSTEM_IMGUI"] = 'ON'
        
        # cmake.definitions["USE_SYSTEM_FMT"] = True

        # # with_visualization currently only causes open3d to use it's bundled 3rd-party libs
        # the src/CMakeLists.txt file would need to be patched to disable the complete module.

        if self.options.with_visualization:
            cmake.definitions["BUILD_GUI"] = 'ON'

        #if self.options.with_python:
        #    cmake.definitions["BUILD_PYTHON_MODULE"] = True
        #   cmake.definitions["PYTHON_EXECUTABLE"] = self.deps_user_info["python_dev_config"].PYTHON
            

        cmake.definitions["BUILD_LIBREALSENSE"] = False

        cmake.configure(source_folder="source_subfolder", build_folder="build_subfolder")
        return cmake

    def build(self):
        open3d_source_dir = os.path.join(self.source_folder, self.source_subfolder)
        tools.patch(open3d_source_dir, "patches/fix_eigen_transform_error.patch")
        tools.patch(open3d_source_dir, "patches/update_imgui_1.87.patch")
        tools.replace_in_file(os.path.join(self.source_subfolder, "CMakeLists.txt"),
            """message(STATUS "Open3D ${OPEN3D_VERSION_FULL}")""",
            """message(STATUS "Open3D ${OPEN3D_VERSION_FULL}")
include(${CMAKE_BINARY_DIR}/../conanbuildinfo.cmake)
conan_basic_setup()

SET(EIGEN3_INCLUDE_DIRS "${CONAN_INCLUDE_DIRS_EIGEN}")
SET(GLEW_INCLUDE_DIRS "${CONAN_INCLUDE_DIRS_GLEW}")
SET(GLEW_LIBRARY_DIRS "${CONAN_LIB_DIRS_GLEW}")
SET(GLEW_LIBRARIES "${CONAN_LIBS_GLEW}")

SET(GLFW_LIBRARY_DIRS "${CONAN_LIB_DIRS_GLFW}")
SET(GLFW_INCLUDE_DIRS "${CONAN_INCLUDE_DIRS_GLFW}")
SET(GLFW_LIBRARIES "${CONAN_LIBS_GLFW}")

MESSAGE(STATUS "Eigen: ${EIGEN3_FOUND} inc: ${EIGEN3_INCLUDE_DIRS}")
MESSAGE(STATUS "GLFW: ${CONAN_LIB_DIRS_GLFW} inc: ${GLFW_INCLUDE_DIRS} lib: ${GLFW_LIBRARIES}")
MESSAGE(STATUS "GLEW: ${GLEW_FOUND} inc: ${GLEW_INCLUDE_DIRS} lib: ${GLEW_LIBRARIES}")""") 



        tools.replace_in_file(os.path.join(self.source_subfolder, "3rdparty", "find_dependencies.cmake"),
            """find_package(ImGui)""",
            """find_package(imgui REQUIRED)
            add_library(ImGui::ImGui ALIAS imgui::imgui)""")
    
#        tools.replace_in_file(os.path.join(self.source_subfolder, "3rdparty", "find_dependencies.cmake"),
#            """find_package(glfw3)""",
#            """find_package(glfw3 REQUIRED)
#    add_library(glfw STATIC IMPORTED)
#    set_target_properties(glfw PROPERTIES
#    IMPORTED_LOCATION "${GLFW_LIBRARY_DIRS}/${CMAKE_STATIC_LIBRARY_PREFIX}glfw3${CMAKE_STATIC_LIBRARY_SUFFIX}"
#    INTERFACE_INCLUDE_DIRECTORIES "${GLFW_INCLUDE_DIRS}"
#    INTERFACE_LINK_LIBRARIES "${GLFW_LIBRARIES}")""")

#         tools.replace_in_file(os.path.join(self.source_subfolder, "3rdparty", "libpng","CMakeLists.txt"),
#             """set(PNG_LIBRARIES ${PNG_LIBRARIES} PARENT_SCOPE)""",
#             """set(PNG_LIBRARIES ${PNG_LIBRARIES} PARENT_SCOPE)
# add_custom_command(TARGET ${PNG_LIBRARY} POST_BUILD
#     COMMAND "${CMAKE_COMMAND}" -E copy_if_different
#         "${CMAKE_BINARY_DIR}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}png${CMAKE_STATIC_LIBRARY_SUFFIX}"
#         "${CMAKE_BINARY_DIR}/lib/Release/${CMAKE_STATIC_LIBRARY_PREFIX}png${CMAKE_STATIC_LIBRARY_SUFFIX}")""")

#         tools.replace_in_file(os.path.join(self.source_subfolder, "3rdparty", "zlib","CMakeLists.txt"),
#             """set(ZLIB_LIBRARY ${ZLIB_LIBRARY} PARENT_SCOPE)""",
#             """set(ZLIB_LIBRARY ${ZLIB_LIBRARY} PARENT_SCOPE)
# add_custom_command(TARGET ${ZLIB_LIBRARY} POST_BUILD
#     COMMAND "${CMAKE_COMMAND}" -E copy_if_different
#         "${CMAKE_BINARY_DIR}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}zlib${CMAKE_STATIC_LIBRARY_SUFFIX}"
#         "${CMAKE_BINARY_DIR}/lib/Release/${CMAKE_STATIC_LIBRARY_PREFIX}zlib${CMAKE_STATIC_LIBRARY_SUFFIX}")""")

        tools.replace_in_file(os.path.join(self.source_subfolder, "3rdparty", "glew","CMakeLists.txt"),
            """set(GLEW_LIBRARIES ${GLEW_LIBRARIES} PARENT_SCOPE)""",
            """set(GLEW_LIBRARIES ${GLEW_LIBRARIES} PARENT_SCOPE)
add_custom_command(TARGET ${GLEW_LIBRARY} POST_BUILD
    COMMAND "${CMAKE_COMMAND}" -E copy_if_different
        "${CMAKE_BINARY_DIR}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}glew${CMAKE_STATIC_LIBRARY_SUFFIX}"
        "${CMAKE_BINARY_DIR}/lib/Release/${CMAKE_STATIC_LIBRARY_PREFIX}glew${CMAKE_STATIC_LIBRARY_SUFFIX}")""")

        tools.replace_in_file(os.path.join(self.source_subfolder, "cpp", "apps","CMakeLists.txt"),
            """APP(Open3DViewer Open3D Open3DViewer ${CMAKE_PROJECT_NAME})""",
            """#APP(Open3DViewer Open3D Open3DViewer ${CMAKE_PROJECT_NAME})""")

        if self.options.with_python and not tools.os_info.is_windows:
            tools.replace_in_file(os.path.join(self.source_subfolder, "3rdparty", "CMake","FindPythonExecutable.cmake"),
                """find_program(PYTHON_IN_PATH "python")""",
                """find_program(PYTHON_IN_PATH "python3")""")


        cmake = self._cmake_configure()
        cmake.build()
        if self.options.with_python:
            cmake.build(target="python-package")

    def package(self):
        cmake = self._cmake_configure()
        cmake.install()
        # only unix match so far ..
        self.copy(pattern="pybind.*.so", src=os.path.join(self.build_subfolder, "lib"), dst="./lib")
        if self.options.with_python:
            with tools.chdir(os.path.join(self.build_folder, self.build_subfolder, "lib", "python_package")):
                self.run('%s setup.py install --prefix="%s"' % (self.deps_user_info["python_dev_config"].PYTHON, self.package_folder), run_environment=True)


    def package_info(self):
        libs = tools.collect_libs(self)
        self.cpp_info.libs = libs
        # self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
