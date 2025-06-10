from setuptools import  setup, Extension
from Cython.Build import cythonize
from pathlib import Path
import numpy


ext_modules = [
    Extension(
        "zcyth",
        ["zcyth.py",],
        include_dirs=[Path.cwd().as_posix(),
                      numpy.get_include()],
        libraries=["zigarray",], # without the lib and so extension
        library_dirs=[Path.cwd().as_posix(),],
        runtime_library_dirs=[Path.cwd().as_posix(),],
        extra_compile_args=["-ffast-math",
                            "-O3"],


    ),
]


setup(
    ext_modules=cythonize(ext_modules,
                          annotate=True),
)

