from conans import ConanFile, CMake, tools
import os
from io import StringIO
import shutil


class Open3dConan(ConanFile):
    upstream_version = "0.16.1"
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

        "fmt/9.1.0",
        # "glew/[>=2.1.0]@camposs/stable",
        )

    options = {
        "shared": [True, False],
        "with_visualization": [True, False],
        "with_python": [True, False],
        }

    default_options = {
        "shared":True,
        "with_visualization":False,
        "with_python":False,
        }

    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"

    scm = {"revision": "v%s" % version,
           "subfolder": "source_subfolder",
           "submodule": "recursive",
           "type": "git",
           "url": "https://github.com/isl-org/Open3D.git"}

    exports = [
        "patches/fmtlib_9.10_fix.patch"
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
        
        cmake.definitions["USE_SYSTEM_FMT"] = True

        # # with_visualization currently only causes open3d to use it's bundled 3rd-party libs
        # the src/CMakeLists.txt file would need to be patched to disable the complete module.
        cmake.definitions["USE_SYSTEM_GLFW"] = 'ON'
        if self.options.with_visualization:
            cmake.definitions["BUILD_GUI"] = 'ON'        
            cmake.definitions["USE_SYSTEM_GLEW"] = 'ON'
            cmake.definitions["USE_SYSTEM_IMGUI"] = 'ON'

        #if self.options.with_python:
        #    cmake.definitions["BUILD_PYTHON_MODULE"] = True
        #   cmake.definitions["PYTHON_EXECUTABLE"] = self.deps_user_info["python_dev_config"].PYTHON
            

        cmake.definitions["BUILD_LIBREALSENSE"] = False

        cmake.configure(source_folder="source_subfolder", build_folder="build_subfolder")
        return cmake

    def build(self):
        open3d_source_dir = os.path.join(self.source_folder, self.source_subfolder)
        tools.patch(open3d_source_dir, "patches/fmtlib_9.10_fix.patch")        
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
