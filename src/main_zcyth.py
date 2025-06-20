import numpy as np
import zigcython.cython.zcyth as zcyth

def main() -> None:
    print()
    print(80*"=")
    print("CYTHON FILE (should be *.so on Linux):")
    print(zcyth.__file__)
    print(80*"=")
    print()

    v_len: int = 7
    v0 = np.full((v_len,),1.0,dtype=np.float64)
    v1 = np.full((v_len,),1.0,dtype=np.float64)
    v_exp = np.full((v_len,),2.0,dtype=np.float64)

    v_out = zcyth.add_vec(v0,v1)

    print(f"{np.allclose(v_out,v_exp)=}")
    print(f"{v_out=}")
    print()

    print("Getting a struct from Zig:")
    zcyth.print_data()
    print()

    print("Sending a simple struct to Zig:")
    in_data = {"valf": 1.0, "vali": -1, "valu": 1}
    zcyth.set_data(in_data)
    print()

    print("Sending numpy array to zig by deconstruction:")
    mat0 = np.full((3,3),7,dtype=np.float64)
    zcyth.matrix_to_zig(mat0)

    print("Sending numpy array to zig as struct:")
    mat1 = np.full((2,2),4,dtype=np.float64)
    zcyth.matrix_struct_to_zig(mat1)



if __name__ == "__main__":
    main()