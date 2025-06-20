cdef extern from "zigarray.h":
    ctypedef struct Data:
        double valf
        int vali
        size_t valu

    Data dataInit()
    void dataSet(Data in_data)

    void addVec(const double* v0, const double* v1, double* v_out, size_t len)

    ctypedef struct MatrixF64:
        double* elems
        size_t* dims
        size_t numel
        size_t ndim

    void matrixToZig(double* elems, size_t* dims, size_t numel, size_t ndim);
    void matStructToZig(MatrixF64 mat);


