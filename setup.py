import os
import subprocess
import sys
import shutil
import platform
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.install import install
from Cython.Build import cythonize
from pathlib import Path
import numpy

PACKAGE_NAME = "zigcython"

#-------------------------------------------------------------------------------
# Platform-specific utilities

def get_platform_info() -> dict[str,str | list[str]]:
    """Get platform-specific file extensions and settings"""
    system = platform.system().lower()

    if system == "windows":
        return {
            "lib_ext": ".dll",
            "lib_prefix": "",
            "rpath_origin": "",  # Windows doesn't use RPATH
            "runtime_lib_dirs": []
        }
    elif system == "darwin":  # macOS
        return {
            "lib_ext": ".dylib",
            "lib_prefix": "lib",
            "rpath_origin": "@loader_path",
            "runtime_lib_dirs": ["@loader_path"]
        }
    else:  # Linux and other Unix-like
        return {
            "lib_ext": ".so",
            "lib_prefix": "lib",
            "rpath_origin": "$ORIGIN",
            "runtime_lib_dirs": ["$ORIGIN"]
        }


PLATFORM_INFO = get_platform_info()

def get_zig_lib_name(name: str) -> str:
    return f"{PLATFORM_INFO['lib_prefix']}{name}{PLATFORM_INFO['lib_ext']}"



#-------------------------------------------------------------------------------
# Custom Multi-Build

class MultiBuildExt(build_ext):

    def run(self):
        print(80*"-")
        print("MultiBuildExt: run")
        print(80*"-")

        output_dir = Path(self.build_temp)
        if not output_dir.is_dir():
            output_dir.mkdir(exist_ok=True,parents=True)

        if str(Path(self.build_lib).resolve()) not in self.library_dirs:
            self.library_dirs.append(str(Path(self.build_lib).resolve()))

        # TODO: need to remove this
        # Add the build location to the runtime path
        if str(Path(self.build_lib).resolve()) not in self.rpath:
             self.rpath.append(str(Path(self.build_lib).resolve()))

        for ee in self.extensions:
            ee.library_dirs.append(str(output_dir))

            print(f"\nConfigured extension: {ee.name}")
            print(f"  include_dirs: {ee.include_dirs}")
            print(f"  library_dirs: {ee.library_dirs}")
            print(f"  libraries: {ee.libraries}")
            print()

        super().run()


    def build_extension(self, ext):
        # TODO check that there is only one source file for zig
        print(80*"-")
        print("MultiBuildExt: build_extension")
        print(f"{ext.name}")
        print(80*"-")
        source_file = Path(ext.sources[0])

        output_filepath = self.get_ext_fullpath(ext.name)
        output_dir = os.path.dirname(output_filepath)
        os.makedirs(output_dir, exist_ok=True)

        print(80*"B")
        print(f"{self.build_lib=}")
        print(f"{self.build_temp=}")
        print(f"{self.libraries=}")
        print(f"{self.library_dirs=}")
        print(80*"B")
        print()

        if source_file.suffix == ".zig":
            print(f"{ext.name}: building with root file - {source_file}")

            zig_python_output = self.get_ext_fullpath(ext.name)
            zig_lib_name = get_zig_lib_name(ext.name)
            zig_lib_output = str(Path(self.build_lib) / zig_lib_name)

            print(f"{ext.name}: output zig library to:\n    {zig_lib_output}")
            print(f"{ext.name}: output python library to:\n    {zig_python_output}")
            print()

            zig_build = [
                "build-lib",
                "-dynamic",
                "-O",
                "ReleaseFast",
                "-lc",
                f"-femit-bin={zig_python_output}",
                *[f"-I{d}" for d in self.include_dirs],
                str(source_file),
            ]

            try:
                # Calls the ziglang pypi package:
                # https://pypi.org/project/ziglang/
                subprocess.check_call([sys.executable, "-m", "ziglang"] + zig_build)
                print(f"{ext.name}: Zig build successful")

                # Copy python extension name to linkable library name
                shutil.copy2(zig_python_output,zig_lib_output)
                print(f"{ext.name}: Copied python extension to:\n    {Path(zig_lib_output)}")

                # Copy linked zig dynamic library to the run time locations
                # NOTE: this is automatically done for the python extension lib
                # runtime_lib_path = Path(self.build_lib) / zig_lib_name
                # shutil.copy2(zig_lib_output, runtime_lib_path)
                # print(f"{ext.name}: Copied library to:\n    {runtime_lib_path}")

                # TODO: On Windows, we might also need to copy to the same directory as the Python extension
                if platform.system().lower() == "windows":
                    python_ext_dir = Path(output_filepath).parent
                    windows_lib_path = python_ext_dir / zig_lib_name
                    shutil.copy2(zig_lib_output, windows_lib_path)
                    print(f"{ext.name}: Copied library to {windows_lib_path} (Windows)")

            except subprocess.CalledProcessError as e:
                print(f"{ext.name}: Zig build failed: {e}")
                raise

        elif (source_file.suffix == ".c"
            or source_file.suffix == ".pyx"
            or source_file.suffix == ".py"):

            print(f"{ext.name}: found C/Cython extension using default build process")
            super().build_extension(ext)

            print(80*"L")
            print()
            for ll in ext.libraries:
                link_lib_name = get_zig_lib_name(ll)
                link_lib_output = str(Path(self.build_lib) / link_lib_name)

                print(f"{link_lib_output=}")

            print(80*"L")
            print()

        else:
            print(f"{ext.name}: extension not recognised using default build process.")
            super().build_extension(ext)

        print(f"{ext.name}: build complete \n")


#-------------------------------------------------------------------------------
# Custom Install Command

class MultiBuildInst(install):

    def run(self):
        print(80*"-")
        print("MultiBuildInst: run")
        print(80*"-")


        print(80*"Z")
        print("Running custom install...")
        print(80*"Z")
        print()
        print(f"{self.install_lib=}")
        print(f"{self.install_platlib=}")
        print(f"{self.install_libbase=}")
        print(f"{self.install_path_file=}")
        print(f"{self.path_file=}")
        print(f"{self.extra_dirs=}")
        print(f"{self.extra_path=}")
        print()

        install_path = Path(self.install_lib) / PACKAGE_NAME
        if not install_path.is_dir():
            install_path.mkdir(exist_ok=True,parents=True)

        for ee in self.distribution.ext_modules:
            print(f"ext module name: {ee.name}")

            if Path(ee.sources[0]).suffix == ".zig":

                zig_lib_name = f"{PLATFORM_INFO['lib_prefix']}{ee.name}{PLATFORM_INFO['lib_ext']}"
                zig_lib_build = str(Path(self.build_lib) / zig_lib_name)
                zig_lib_run = str(Path(self.install_lib) / PACKAGE_NAME / zig_lib_name)
                print(f"{zig_lib_build=}")
                print(f"{zig_lib_run=}")
                print()

                shutil.copy2(zig_lib_build,zig_lib_run)

        print()

        print("Running standard install...")
        super().run()

        #raise Exception("Stop install!")

#-------------------------------------------------------------------------------
# Extensions

H_DIRS = [numpy.get_include(),
          str(Path.cwd()/"src"),
          str(Path.cwd()/"src"/"cython"),
          str(Path.cwd()/"src"/"zig"),]

# zig extension
ext_zig = Extension(
    "zigarray",
    sources=["src/zigcython/zig/zigarray.zig",],
)

# cython extension linking zig
ext_cython = Extension(
        "zigcython.cython.zcyth",
        sources=["src/zigcython/cython/zcyth.py",],
        include_dirs=H_DIRS,
        libraries=[ext_zig.name,],  # without the lib and so extension - e.g. libzigarray.so - zig
        library_dirs=[],            # populated by run() above
        runtime_library_dirs=PLATFORM_INFO["runtime_lib_dirs"],
        headers = ["src/zigcython/cython/zigarray.h",],
        extra_compile_args=["-ffast-math",
                            "-O3"],
    )

ext_modules = [ext_zig] + cythonize(ext_cython,annotate=True)


#-------------------------------------------------------------------------------
# Setup

setup(
    name="zigcython",
    ext_modules=ext_modules,
    cmdclass={"build_ext": MultiBuildExt,},
              #"install": MultiBuildInst},
    zip_safe=False,
    package_data={
        "zigcython": [f"*{PLATFORM_INFO['lib_ext']}"],
        "zigcython.cython": [f"*{PLATFORM_INFO['lib_ext']}"],
        "zigcython.zig": [f"*{PLATFORM_INFO['lib_ext']}"],
        "": [f"*{PLATFORM_INFO['lib_ext']}"],
    },
    include_package_data=True,
)

