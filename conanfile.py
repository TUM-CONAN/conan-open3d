from conans import ConanFile, CMake, tools
import os
from io import StringIO
import shutil


class Open3dConan(ConanFile):
    version = "0.4.0"

    name = "open3d"
    license = "https://github.com/IntelVCL/Open3D/raw/master/LICENSE"
    description = "Open3D: A Modern Library for 3D Data Processing http://www.open3d.org (Forked for use with Ubitrack"
    url = "https://github.com/ulricheck/Open3D"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    short_paths = True

    requires = (
        "eigen/[>=3.3.4]@camposs/stable",
        "glfw/[>=3.2.1]@camposs/stable",
        "glew/[>=2.1.0]@camposs/stable",
        )

    options = {
        "shared": [True, False],
        }

    default_options = (
        "shared=True",
        )

    scm = {
        "type": "git",
        "subfolder": "open3d",
        "url": "https://github.com/IntelVCL/Open3D.git",
        "revision": "v%s" % version,
     }


    exports_sources = "CMakeLists.txt",

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared

        cmake.definitions["BUILD_EIGEN3"] = False
        cmake.definitions["BUILD_PYBIND11"] = False
        cmake.definitions["BUILD_GLFW"] = False
        cmake.definitions["BUILD_GLEW"] = False

        cmake.definitions["EIGEN3_FOUND"] = True
        cmake.definitions["GLEW_FOUND"] = True
        cmake.definitions["GLFW_FOUND"] = True

        cmake.definitions["BUILD_LIBREALSENSE"] = True

        cmake.definitions["BUILD_PYTHON_MODULE"] = False

        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        base_dir = os.path.join(self.package_folder, "include", "open3d_conan")
        for name in os.listdir(base_dir):
            shutil.move(os.path.join(base_dir, name), os.path.join(self.package_folder, "include"))

        self.copy(pattern="*", src=os.path.join("open3d","bin"), dst="./bin")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))



