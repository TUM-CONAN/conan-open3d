from conans import ConanFile, CMake
import os


class TBBTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def imports(self):
        self.copy("*.dll", "bin", "bin")
        self.copy("*.so*", "bin", "lib")
        self.copy("*.dylib", "bin", "lib")

    def test(self):
        os.chdir("bin")
        if self.settings.os != "Windows":
            self.run("LD_LIBRARY_PATH=./ ./example")
        else:
            self.run(".%sexample" % os.sep)
