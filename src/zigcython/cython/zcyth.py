from typing import Any
import cython
from cython.cimports import zigarray
import numpy as np


# Sending two numpy arrays to Zig and getting one back
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


# Getting a struct from Zig as a dict
def print_data() -> None:
    data = zigarray.dataInit()
    print(f"{data=}")


def init_data() -> dict[str,Any]:
    return zigarray.dataInit()


def set_data(in_data: dict[str,Any]) -> None:
    data: zigarray.Data = zigarray.Data(0.0,0,0)
    # OR
    #data: zigarray.Data = zigarray.initData()

    data.valf = in_data.get("valf",0.0)
    data.vali = in_data.get("vali",0)
    data.valu = in_data.get("valu",0)

    zigarray.dataSet(data)


def matrix_to_zig(in_mat: np.ndarray) -> None:

    shape_np = np.array(in_mat.shape,dtype=np.uintp)
    shape: cython.size_t[::1] = shape_np
    ndims: cython.size_t = in_mat.ndim
    size: cython.size_t = in_mat.size
    elems: cython.double[::1] = in_mat.flatten()

    zigarray.matrixToZig(
        cython.address(elems[0]),
        cython.address(shape[0]),
        size,
        ndims,
    )

def matrix_struct_to_zig(in_mat: np.ndarray) -> None:

    shape_np = np.array(in_mat.shape,dtype=np.uintp)
    shape: cython.size_t[::1] = shape_np
    ndims: cython.size_t = in_mat.ndim
    size: cython.size_t = in_mat.size
    elems: cython.double[::1] = in_mat.flatten()

    mat_struct: zigarray.MatrixF64 = zigarray.MatrixF64(
        cython.address(elems[0]),
        cython.address(shape[0]),
        size,
        ndims,
    )

    zigarray.matStructToZig(mat_struct)









