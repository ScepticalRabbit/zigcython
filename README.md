# zigcython
A minimal working example linking Python to Zig through Cython to send numpy arrays to Zig. The example described below details how to send 1D numpy arrays but the code files include additional examples of sending ndarrays as structs back and forth between Python and Zig.

## Running the Example
First create a python virtual environment in the repo directory and activate it:
```shell
python -m venv .venv
source ./.venv/bin/activate
```

Install numpy, cython and ziglang:
```shell
pip install numpy cython ziglang
```

Build the Zig dynamic library and then the Cython files linking the Zig dynamic library (see setup.py):
```shell
python setup.py build_ext --inplace -f
```

You can also install the `zigcython` to your venv using pip:
```shell
pip install -e .
```

Now run the `main_cyth.py` in the src directory which calls the Zig library through Cython:
```shell
python src/main_zcyth.py
```

## How it works: Zig to Numpy

### Zig
First we need to build the interface for our Zig library so that it is C compatible. This means using the key word `export` and following compiler errors to make everything C compatible. For arrays we need to use C style arrays in our functions headers using the `[*c]` syntax. If we make sure we have the length passed to our functions then we can easily create Zig slices to help us out. Here is our basic C style function in zigarray.zig to add two 1D arrays of the same size. Our next job is to get Cython to use this function.

```zig
pub export fn addVec(v0: [*c]const f64 , v1: [*c]const f64, v_out: [*c]f64, len: usize) void {

    const s0 = v0[0..len];
    const s1 = v1[0..len];
    const s_out = v_out[0..len];


    for (0..s_out.len) |ii| {
        s_out[ii] = s0[ii] + s1[ii];
    }
}
```

### Cython
This is where we need to write a bunch of boilerplate to make this work. First we need to write a C header file (.h) and then copy over any definitions we want to a Cython .pxd file. Part of this should be able to be automated with the `-femit-h` Zig compiler flag but unfortunately this is not working with the 0.14 compiler available on pypi (for interest there is a label 'emit-h' tracking github issues related to this [here](https://github.com/ziglang/zig/issues?q=state%3Aopen%20label%3A%22emit-h%22)). Our header file 'zigarray.h' looks like this:

```C
#ifndef ZIGARR_H
#define ZIGARR_H

#include <stddef.h>

void addVec(const double* v0, const double* v1, double* v_out, size_t len);

#endif
```

And our cython 'zigarray.pxd' file looks like this where we basically copy/paste the function header:

```python
cdef extern from "zigarray.h":
    void addVec(const double* v0, const double* v1, double* v_out, size_t len)

```

We now need to write a Cython wrapper around our Zig library to help us by allocating numpy arrays and giving us pointers to them. Here I am going to use the new pure Python style Cython syntax. Our 'zcyth.py' cython wrapper looks like this:

```python
import cython
from cython.cimports import zigarray
import numpy as np

@cython.boundscheck(False) # Turn off array bounds checking
@cython.wraparound(False)  # Turn off negative indexing
@cython.cdivision(True)    # Turn off divide by zero check
def add_vec(v0: cython.double[::1],
            v1: cython.double[::1]) -> np.ndarray:

    v_len: cython.size_t = v0.shape[0]

    v_out_np = np.full((v_len,),0.0,dtype=np.float64)
    v_out: cython.double[::1] = v_out_np


    zigarray.addVec(cython.address(v0[0]),
                    cython.address(v1[0]),
                    cython.address(v_out[0]),
                    v_len)

    return v_out_np
```

A few things to note about this Cython wrapper. First we need to make sure our arrays are row major in C style. Using the Cython memory view syntax of [::1] means Cython will yell at us if get this wrong. The other thing is to make sure the data types of our numpy arrays and Cython memory view are consistent with our C interface. So make sure you set the numpy array `dtype` to match. If you have trouble with numpy arrays not being row major then this can be fixed in python using `array = np.ascontinguousarray(array)`. Finally, we send pointers to the first element in our Cython memory views using the `cython.address(array[0])`.

### Python: Build
All the magic happens in the setup.py file. Here we use the `ziglang` package from pypi to compile our zig code as part of the python build process. Essentially our `build_ext` function looks for a source file with an extension of `.zig` and then invokes the zig compiler on it. If it finds anything else it just invokes the normal python build process.

There is also a bunch of path logic to make sure that the build and runtime directories for the library are correct so that linking works at build and runtime. The key step here was to find any libraries that cross reference each other (e.g. our Cython library which needs our Zig library) then copy the linked library to be in the same directory as the extension that needs it. We also need to make sure the runtime path was set correctly to look in the same directory as the library origin for linked libraries. I have tested this with a normal venv and editable install in a venv and everything seems to work.

### Python: Calling our Library
Calling our library is the easy part. We just import the library create a couple of numpy arrays and pass them to the function:

```python
import numpy as np
import src.zigcython.cython.zcyth as zcyth

v0 = np.full((7,),1.0,dtype=np.float64)
v1 = np.full((7,),1.0,dtype=np.float64)

v_out = zcyth.add_vec(v0,v1)

print(f"{v_out=}")

```




