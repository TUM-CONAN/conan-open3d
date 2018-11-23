from conans import ConanFile, CMake, tools
import os
from io import StringIO


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
        "pybind11/[>=2.2.1]@camposs/stable",
        "glew/[>=2.1.0]@camposs/stable",
        )

    options = {
        "shared": [True, False],
        "python": "ANY",
        }

    default_options = (
        "shared=True",
        "python=python3",
        )

    scm = {
        "type": "git",
        "subfolder": "open3d",
        "url": "https://github.com/IntelVCL/Open3D.git",
        "revision": "v%s" % version,
     }


    exports_sources = "CMakeLists.txt"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared

        cmake.definitions["BUILD_EIGEN3"] = False
        cmake.definitions["BUILD_PYBIND11"] = False
        cmake.definitions["BUILD_GLFW"] = False
        cmake.definitions["BUILD_GLEW"] = False

        cmake.definitions["BUILD_LIBREALSENSE"] = True

        cmake.definitions["BUILD_PYTHON_MODULE"] = True

        # cmake.definitions["OPENGL_EXTENSION_WRAPPER"] = self.options.opengl_extension_wrapper 

        self.output.info("python executable: %s (%s)" % (self.python_exec.replace("\\", "/"), self.python_version))
        cmake.definitions['PYBIND11_PYTHON_VERSION'] = self.python_version
        if self.settings.os == "Macos":
            cmake.definitions['CMAKE_FIND_FRAMEWORK'] = "LAST"

        cmake.configure()
        cmake.build()
        # cmake.install()

    def package(self):
        src_folder = os.path.join(self.source_folder, "src")
        for name in ["Core", "IO", "Visualization"]:
            self.copy("*.h", src=os.path.join(src_folder, name), dst="include/%s" % name, keep_path=True)
        self.copy("*", src=os.path.join(self.build_folder, "bin"), dst="bin", keep_path=False)
        self.copy("*.a", src=os.path.join(self.build_folder, "lib"), dst="lib", keep_path=False)
        self.copy("*.dylib", src=os.path.join(self.build_folder, "lib"), dst="lib", keep_path=False)
        self.copy("*.so.*", src=os.path.join(self.build_folder, "lib"), dst="lib", keep_path=False)
        self.copy("*.lib", src=os.path.join(self.build_folder, "lib"), dst="lib", keep_path=False)
        self.copy("py3d.*", src=os.path.join(self.build_folder, "lib"), dst="lib/python", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))

    @property
    def python_exec(self):
        try:
            pyexec = str(self.options.python)
            output = StringIO()
            self.run('{0} -c "import sys; print(sys.executable)"'.format(pyexec), output=output)
            return '"'+output.getvalue().strip().replace("\\","/")+'"'
        except:
            return ""
    
    _python_version = ""
    @property
    def python_version(self):
        cmd = "from sys import *; print('%d.%d' % (version_info[0],version_info[1]))"
        self._python_version = self._python_version or self.run_python_command(cmd)
        return self._python_version
      
    def run_python_command(self, cmd):
        pyexec = self.python_exec
        if pyexec:
            output = StringIO()
            self.run('{0} -c "{1}"'.format(pyexec, cmd), output=output)
            return output.getvalue().strip()
        else:
            return ""

