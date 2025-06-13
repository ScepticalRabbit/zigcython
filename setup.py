import os
import subprocess
import sys
from setuptools import  setup, Extension
from setuptools.command.build_ext import build_ext
from Cython.Build import cythonize
from pathlib import Path
import numpy


#-------------------------------------------------------------------------------
# Custom Multi-Build

class MultiBuildExt(build_ext):

    def run(self):
        super().run()

    def build_extension(self, ext):
        # TODO check that there is only one source file for zig
        print(80*"=")
        print(f"{ext.name}: multi-build extension")
        print(80*"=")
        source_file = Path(ext.sources[0])

        if not os.path.exists(self.build_lib):
            os.makedirs(self.build_lib)

        output_filepath = self.get_ext_fullpath(ext.name)
        output_dir = os.path.dirname(output_filepath)
        os.makedirs(output_dir, exist_ok=True)

        # print(f"{source_file=}")
        # print(f"{self.build_lib=}")
        # print(f"{output_filepath=}")
        # print(f"{output_dir=}")
        # print()

        if source_file.suffix == ".zig":
            print(f"{ext.name}: building with root file - {source_file}")

            zig_build = [
                "build-lib",
                "-dynamic",
                "-O",
                "ReleaseFast",
                "-lc",
                f"-femit-bin={self.get_ext_fullpath(ext.name)}",
                *[f"-I{d}" for d in self.include_dirs],
                source_file.name,
            ]

            # for zz in zig_build:
            #     print(f"{zz}")
            # print()

            # Calls the ziglang pypi package:
            # https://pypi.org/project/ziglang/
            subprocess.call([sys.executable, "-m", "ziglang"] + zig_build)

        elif (source_file.suffix == ".c"
            or source_file.suffix == ".pyx"
            or source_file.suffix == ".py"):

            print(f"{ext.name}: found C/Cython extension using default build process")
            super().build_extension(ext)

        else:
            print(f"{ext.name}: extension not recognised using default build process.")
            super().build_extension(ext)

        print(f"{ext.name}: build complete \n")


#-------------------------------------------------------------------------------
# Extensions

# zig extension
ext_zig = Extension(
    "zigarray",
    sources=["./zigarray.zig",]
)

# cython extension linking zig
ext_cython = Extension(
        "zcyth",
        sources=["zcyth.py",],
        include_dirs=[Path.cwd().as_posix(),
                      numpy.get_include()],
        libraries=["zigarray",], # without the lib and so extension
        library_dirs=[Path.cwd().as_posix(),],
        runtime_library_dirs=[Path.cwd().as_posix(),],
        extra_compile_args=["-ffast-math",
                            "-O3"],
    )

ext_modules = [ext_zig] + cythonize(ext_cython,annotate=True)


#-------------------------------------------------------------------------------
# Setup

setup(
    ext_modules=ext_modules,
    cmdclass={"build_ext": MultiBuildExt},
    zip_safe=False,
)

