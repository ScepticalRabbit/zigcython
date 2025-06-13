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

        output_dir = Path(self.build_temp)
        if not output_dir.is_dir():
            output_dir.mkdir(exist_ok=True,parents=True)


        if str(Path(self.build_lib).resolve()) not in self.library_dirs:
            self.library_dirs.append(str(Path(self.build_lib).resolve()))

        if str(Path(self.build_lib).resolve()) not in self.rpath:
             self.rpath.append(str(Path(self.build_lib).resolve()))

        for ee in self.extensions:
            ee.include_dirs.append(str(output_dir))
            ee.library_dirs.append(str(output_dir))

            print(f"\nConfigured extension: {ee.name}")
            print(f"  include_dirs: {ee.include_dirs}")
            print(f"  library_dirs: {ee.library_dirs}")
            print(f"  libraries: {ee.libraries}")
            print()


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

        print(f"{source_file=}")
        print(f"{self.build_lib=}")
        print(f"{output_filepath=}")
        print(f"{output_dir=}")
        print()

        if source_file.suffix == ".zig":
            print(f"{ext.name}: building with root file - {source_file}")

            zig_ext = Path(output_filepath).suffix
            zig_name = f"lib{ext.name}{zig_ext}"
            print(f"{zig_name=}\n")
            zig_output = str(Path(output_filepath)
                             .with_name(zig_name)
                             .resolve())

            print(f"{ext.name}: output library to - {zig_output}")
            print()


            zig_build = [
                "build-lib",
                "-dynamic",
                "-O",
                "ReleaseFast",
                "-lc",
                f"-femit-bin={zig_output}",
                *[f"-I{d}" for d in self.include_dirs],
                str(source_file),
            ]

            # for zz in zig_build:
            #     print(f"{zz}")
            # print()

            try:
                # Calls the ziglang pypi package:
                # https://pypi.org/project/ziglang/
                subprocess.check_call([sys.executable, "-m", "ziglang"] + zig_build)
                print(f"{ext.name}: Zig build successful")  # Add this line
            except subprocess.CalledProcessError as e:
                print(f"{ext.name}: Zig build failed: {e}")
                raise  # Re-raise the exception to stop the build

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

H_DIRS = [numpy.get_include(),
          str(Path.cwd()/"src"/"zig"),]

# LIB_DIRS = [#str(Path.cwd()),
#             str(Path.cwd()/"src"),
#             str(Path.cwd()/"src"/"zig"),
#             str(Path.cwd()/"src"/"cython"),]

# zig extension
ext_zig = Extension(
    "zigarray",
    sources=["src/zigcython/zig/zigarray.zig",]
)

# cython extension linking zig
ext_cython = Extension(
        "zigcython.cython.zcyth",
        sources=["src/zigcython/cython/zcyth.py",],
        include_dirs=H_DIRS,
        libraries=[ext_zig.name,], # without the lib and so extension
        library_dirs=[],
        runtime_library_dirs=[],
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

