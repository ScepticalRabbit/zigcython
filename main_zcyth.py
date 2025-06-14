import numpy as np
import src.zigcython.cython.zcyth as zcyth

def main() -> None:
    print()
    print(80*"=")
    print("CYTHON FILE (should be *.so on Linux):")
    print(zcyth.__file__)
    print(80*"=")
    print()

    v0 = np.full((7,),1.0,dtype=np.float64)
    v1 = np.full((7,),1.0,dtype=np.float64)

    v_out = zcyth.add_vec(v0,v1)

    print(f"{v_out=}")
    print()

if __name__ == "__main__":
    main()