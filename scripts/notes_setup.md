# Notes: Setup.py

# TODO: Zig Builder
- Need to make sure the Zig .so goes to the correct place
- Need to make sure the Zig .so ends up following the cython .so anywhere it ends up.
- Do we need to keep the built zig python extension? If so, does it need to follow the lib.so?
- Implement `extra_compiler_args` and `extra_link_args`.
- Implement the `language` flag for extensions as well as defaulting to deal with extensions based on file extension


# IMPORTANT General Notes
- Inheritance is used when overriding the `build_ext` class. This means you can go to the standard build process at any point using `super()` e.g. `super().run()` or `super().build_extension(ext)`.
- When calling `build_ext --inplace`: In the `run()` function using `self.get_ext_fullpath(ext.name)` will return the **INSTALL/SRC** directory
- When calling `build_ext --inplace`: In the `build_extension()` function using `self.get_ext_fullpath(ext.name)` will return the **BUILD** directory.
- When calling `pip install .`: both point at the **BUILD** directory.

# Custom `build_ext` class
There are several key methods to possibly override:

## `finalize_options(self)`
Called after processing command line arguments, here we can define custom options for build_ext subclass. e.g. self.my_custom_flag = True.

## `run(self)`
Main body of the command where all extensions are looped through and `build_extension(self,ext)` is called on each one. If `--inplace` is used then it copies the extensions to the correct place (after ).

## `build_extension(self,ext)`
This is the most common to override and it actually calls the compiler for each extension.

## How `build_ext` works
This is a rough outline of how `build_ext` works:
```python
def run(self):
    for ee in self.extensions:
        self.build_extension(ee)
```

## `build_ext`: Class Variables & Directories
These are relevant variables for the `build_ext` class itself:

- `self.build_temp`: where intermediate build files go e.g. object files like .o.

- `self.build_lib`: where compiled/shared libraries go, this is where `setuptools` expects to find compiled extensions. Typically: `build/lib.{platform-arch-python_version}`.

- `self.inplace`: compiler flag indicatin whether compiled extensions should be copied into the source package directory - useful for dev mode.

- `self.plat_name`: The platform name in the form `{platform-arch}` e.g. `'linuz-x86_64'` or `'win-amd64'`.

- `self.include_dirs`: A list of directories to search for header files. Corresponds to the `-I` compiler flag.

- `self.library_dirs`: A list of directories to search for libraries. Corresponds to the `-L` compiler flag.

- `self.libraries`: A list of libraries to link against. Corresponds to the `-l` compiler flag e.g. `-lzigarray` for `libzigarray.s0`.

- `self.rpath`: A list of runtime library search paths for shared libraries. Corresponds to the `-rpath` compiler option.

- `self.extensions`: **IMPORTANT** - This is the list of extensions passed to the `setup()` function.


These are variables for the `Extension` class:

- `ext.name`: `str` - fully qualified python module name of the extension. This determines the import path and the expected filename of the compiled extension.

- `ext.sources`: `list[str]` - A list of source files (e.g. .c, .cpp, .zig) that make up the extension.

- `ext.include_dirs`: `list[str]` - A list of directories to search for header files during compilation. Implements the `-I` compiler.

- `ext.library_dirs`: `list[str]` - A list of directories to search for libraries during linking. Implements the `-L` compiler flag.

- `ext.libraries`: `list[str]` - A list of library names to link against (without the `lib` and the `.so`, `.dll` etc.).

- `ext.rpath`, `ext.runtime_library_dirs`: `list[str]` - A list of directories to search for shared libraries at runtime.

- `ext.extra_compile_args`: `list[str]` - A list of strings specifying additional compiler arguments.

- `ext.extra_link_args`: `list[str]` - A list of strings specifying additiona linking arguments.

- `ext.depends`: `list[str]` - list of files the extension depends on. Useful for headers or other files that are not source files.

- `ext.language`: `str` - The programming language of the extension, selects the correct compiler and linker. Default behaviour is that this is inferred from source extensions.

- `ext.headers`: list[str] optional - list of header files to copy.

# Custom `install` class
There are several key methods to possibly override:

## `finalize_options(self)`
Called after processing command line arguments, here we can define custom options for build_ext subclass. e.g. self.my_custom_flag = True.

## `run(self)`
Runs the whole install process calling sub-commands in this order:
- `run('build')`
- `run('install_lib')`
- `run('install_headers')`
- `run('install_scripts')`
- `run('install_data')`

Override this to add pre or post installation steps i.e. running commands before and after `super().run()`.

## `install`: Class Variables & Directories
These are the member variables for the `install` class:

- `self.distribution`: `str` - Provides access to package meta-data

- `self.install_base`: `str` - the base directory where everything will be installed.

- `self.install_platlib`: `str` - the directory for platform specific python modules, this is where .so, .pyd and .dylib go.

- `self.install_purelib`: `str` - the directory for pure python modules, might be the same as platlib above.

- `self.install_headers`: `str` - the directory for C/C++ header files.

- `self.install_scripts`: `str` - the directory for the python scripts.

- `self.install_data`: `str` - the directory for arbitrary data files.

- `self.install_lib`: `str` - normally set to platlib or purelib above depending on the package.

- `self.prefix`: `str` - the installation prefix e.g. `/usr/local` on unix or `C:\PythonXY` on windows.

- `self.exec_prefix`: `str` - usually the same as prefix above

- `self.home`: `str` - the home directory for user-specific installations

- `self.user`: `bool = True` - True if installing to the user's sit-packages directory. This is the modern way to install non-globally.

- `self.root`: `str` - The root directory under which to install



