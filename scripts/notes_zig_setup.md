# Zig Setup

# TODO: Zig Builder
- Need to make sure the Zig .so goes to the correct place for install and inplace
- Need to make sure the Zig .so ends up following the cython .so anywhere it ends up.
- Do we need to keep the built zig python extension? If so, does it need to follow the lib.so?
- Implement `extra_compiler_args` and `extra_link_args`.
- Implement the `language` flag for extensions as well as defaulting to deal with extensions based on file extension

## Build Order

- Overried run, before super().run() add directories for