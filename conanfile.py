from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.scm import Git
from conan.tools.files import load, update_conandata, copy, replace_in_file, collect_libs, patch
import os


class Open3dConan(ConanFile):
    upstream_version = "0.18.0"
    package_revision = ""
    version = "{0}{1}".format(upstream_version, package_revision)

    name = "open3d"
    license = "https://github.com/IntelVCL/Open3D/raw/master/LICENSE"
    description = "Open3D: A Modern Library for 3D Data Processing http://www.open3d.org"
    url = "https://github.com/TUM-CONAN/conan-open3d"

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "with_visualization": [True, False],
        }
    default_options = {
        "shared": True,
        "with_visualization": False,
    }

    exports = [
        #"patches/fix_eigen_transform_error.patch",
        "patches/fix_windows_build_download_mkl.patch",
        ]

    def requirements(self):
        self.requires("eigen/3.4.0")
        # self.requires("glfw/3.3.8")
        self.requires("fmt/9.1.0")
        # self.requires("assimp/5.2.2")
        # self.requires("libjpeg/9e")
        # self.requires("jsoncpp/1.9.5")

        if self.options.with_visualization:
            self.requires("glew/2.2.0")

    def configure(self):
        if self.options.with_visualization and self.options.shared:
            self.dependencies['glew'].options.shared = True
            self.dependencies['glfw'].options.shared = True

    def export(self):
        update_conandata(self, {"sources": {
            "commit": "v{}".format(self.version),
            "url": "https://github.com/IntelVCL/Open3D.git"
        }})

    def source(self):
        git = Git(self)
        sources = self.conan_data["sources"]
        git.clone(url=sources["url"], target=self.source_folder, args=["--recursive", ])
        git.checkout(commit=sources["commit"])

        # fix-eigen patch was made for older version, but the problem still seems to be in the sources
        # @todo need to create new patch !!!
        # patch(self, self.source_folder, os.path.join(self.recipe_folder, "patches", "fix_eigen_transform_error.patch"))
        patch(self, self.source_folder, os.path.join(self.recipe_folder, "patches", "fix_windows_build_download_mkl.patch"))


    def generate(self):
        tc = CMakeToolchain(self)

        def add_cmake_option(option, value):
            var_name = "{}".format(option).upper()
            value_str = "{}".format(value)
            var_value = "ON" if value_str == 'True' else "OFF" if value_str == 'False' else value_str
            tc.variables[var_name] = var_value

        for option, value in self.options.items():
            add_cmake_option(option, value)


        # XXX we might want to enable cuda and gui modules at some point
        tc.cache_variables["BUILD_CUDA_MODULE"] = False
        tc.cache_variables["BUILD_GUI"] = False
        tc.cache_variables["BUILD_PYTHON_MODULE"] = False
        tc.cache_variables["BUILD_EXAMPLES"] = False

        # Linking issue: https://github.com/intel-isl/Open3D/issues/2286
        tc.cache_variables["GLIBCXX_USE_CXX11_ABI"] = True

        tc.cache_variables["USE_SYSTEM_EIGEN3"] = True
        tc.cache_variables["USE_SYSTEM_GLEW"] = True
        tc.cache_variables["USE_SYSTEM_FMT"] = True

        if self.options.shared:
            tc.cache_variables['BUILD_SHARED_LIBS'] = True

            # tc.cache_variables["USE_SYSTEM_GLFW"] = True
            # tc.cache_variables["USE_SYSTEM_ASSIMP"] = True
            # tc.cache_variables["USE_SYSTEM_JPEG"] = True
            # tc.cache_variables["USE_SYSTEM_JSONCPP"] = True

        # # with_visualization currently only causes open3d to use it's bundled 3rd-party libs
        # the src/CMakeLists.txt file would need to be patched to disable the complete module.

        if self.options.with_visualization:
            tc.cache_variables["BUILD_GUI"] = True

        tc.cache_variables["BUILD_LIBREALSENSE"] = False

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def layout(self):
        cmake_layout(self, src_folder="source_folder")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
