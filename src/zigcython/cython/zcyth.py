import cython
from cython.cimports import zigarray
import numpy as np


@cython.boundscheck(False) # Turn off array bounds checking
@cython.wraparound(False)  # Turn off negative indexing
@cython.cdivision(True)    # Turn off divide by zero check
def add_vec(v0: cython.double[::1],
            v1: cython.double[::1]) -> np.ndarray:

    v_len:cython.size_t = v0.shape[0]

    v_out_np = np.full((v_len,),0.0,dtype=np.float64)
    v_out: cython.double[::1] = v_out_np

    zigarray.addVec(cython.address(v0[0]),
                       cython.address(v1[0]),
                       cython.address(v_out[0]),
                       v_len)

    return v_out_np


