cdef extern from "zigarray.h":
    ctypedef struct Data:
        double valf
        int vali
        size_t valu

    void addVec(const double* v0, const double* v1, double* v_out, size_t len)



