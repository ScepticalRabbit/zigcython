# zigcython
A minimal working example linking Python to Zig through Cython to send numpy arrays to Zig. For now it can deal with 1D numpy arrays


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

Build the Zig dynamic library and then theCcython files linking the Zig dynamic library (see setup.py):
```shell
python setup.py build_ext --inplace -f
```

Now run the `main_cyth.py` which calls the Zig library through cython:
```shell
python main_zcyth.py
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

A few things to note about this Cython wrapper. First we need to make sure our arrays are row major in C style. Using the Cython memory view syntax of [::1] means Cython will yell at us if get this wrong. The other thing it to make sure the data types of our numpy arrays and Cython memory view are consistent with our C interface. So make sure you set the numpy array `dtype` to match. If you have trouble with numpy arrays not being row major then this can be fixed in python using `array = np.ascontinguousarray(array)`. Finally, we send pointers to the first element in our Cython memory views using the `cython.address(array[0])`.

### Python
All the magic happens in the setup.py file. TODO


