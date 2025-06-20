#ifndef ZIGARR_H
#define ZIGARR_H

#include <stddef.h>
#include <stdint.h>

//------------------------------------------------------------------------------
void addVec(const double* v0, const double* v1, double* v_out, size_t len);

//------------------------------------------------------------------------------
typedef struct Data {
    double valf;
    int32_t vali;
    size_t valu;
} Data;

Data dataInit();
void dataSet(Data in_data);

//------------------------------------------------------------------------------
typedef struct MatrixF64 {
    double* elems;
    size_t* dims;
    size_t numel;
    size_t ndim;
} MatrixF64;

void matrixToZig(double* elems, size_t* dims, size_t numel, size_t ndim);
void matStructToZig(MatrixF64 mat);

#endif