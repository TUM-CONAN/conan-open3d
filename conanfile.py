from conans import ConanFile, CMake, tools
import os
from io import StringIO
import shutil


class Open3dConan(ConanFile):
    version = "0.5.0"

    name = "open3d"
    license = "https://github.com/IntelVCL/Open3D/raw/master/LICENSE"
    description = "Open3D: A Modern Library for 3D Data Processing http://www.open3d.org (Forked for use with Ubitrack"
    url = "https://github.com/ulricheck/Open3D"
    settings = "os", "compiler", "build_type", "arch"
    generators = "pkg_config", "cmake"
    short_paths = True

    requires = (
        "eigen/[>=3.3.4]@camposs/stable",
        )

    options = {
        "shared": [True, False],
        "with_visualization": [True, False],
        }

    default_options = (
        "shared=True",
        "with_visualization=False",
        )

    scm = {
        "type": "git",
        "subfolder": "open3d",
        "url": "https://github.com/IntelVCL/Open3D.git",
        "revision": "v%s" % version,
        "submodule": "recursive",
     }

    exports_sources = "CMakeLists.txt",

    def requirements(self):
        if self.options.with_visualization:
            self.requires("glfw/[>=3.2.1]@camposs/stable")
            self.requires("glew/[>=2.1.0]@camposs/stable")
    
    def configure(self):
        if self.options.with_visualization:
            if self.options.shared:
                self.options['glew'].shared = True

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared

        cmake.definitions["BUILD_EIGEN3"] = False
        cmake.definitions["BUILD_PYBIND11"] = False
        cmake.definitions["EIGEN3_FOUND"] = True
        cmake.definitions["BUILD_PYTHON_MODULE"] = False

        # with_visualization currently only causes open3d to use it's bundled 3rd-party libs
        # the src/CMakeLists.txt file would need to be patched to disable the complete module.

        if self.options.with_visualization:
            cmake.definitions["BUILD_GLFW"] = False
            cmake.definitions["BUILD_GLEW"] = False
            cmake.definitions["GLEW_FOUND"] = True
            cmake.definitions["GLFW_FOUND"] = True

        cmake.definitions["BUILD_LIBREALSENSE"] = True

        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        base_dir = os.path.join(self.package_folder, "include", "open3d_conan")
        if os.path.exists(base_dir):
            for name in os.listdir(base_dir):
                shutil.move(os.path.join(base_dir, name), os.path.join(self.package_folder, "include"))

        self.copy(pattern="*", src="bin", dst="./bin")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))



