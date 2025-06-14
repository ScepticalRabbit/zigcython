# Notes: Setup.py

# TODO: Zig Builder
- Need to make sure the Zig .so goes to the correct place
- Need to make sure the Zig .so ends up following the cython .so anywhere it ends up.
- Do we need to keep the built zig python extension? If so, does it need to follow the lib.so?
- Implement `extra_compiler_args` and `extra_link_args`.
- Implement the `language` flag for extensions as well as defaulting to deal with extensions based on file extension


# General Notes
- Inheritance is used when overriding the `build_ext` class. This means you can go to the standard build process at any point using `super()` e.g. `super().run()` or `super().build_extension(ext)`.

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

- `self.build_lib`: where compiled/shared libraries go, this is where `setuptools` expectcs to find compiled extensions. Typically: `build/lib.{platform-arch-python_version}`.

- `self.inplace`: compiler flag indicatin whether compiled extensions should be copied into the source package directory - useful for dev mode.

- `self.plat_name`: The platform name in the form `{platform-arch}` e.g. `'linuz-x86_64'` or `'win-amd64'`.

- `self.plat_specifier`: A string combining the platform and python version e.g. `'linux-x86_64-3.11'` used for constructing `build_lib` and `build_temp` paths.

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




