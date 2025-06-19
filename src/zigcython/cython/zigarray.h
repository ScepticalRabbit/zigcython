#ifndef ZIGARR_H
#define ZIGARR_H

#include <stddef.h>
#include <stdint.h>

typedef struct data {
    double valf;
    int32_t vali;
    size_t valu;
} data_t;

void addVec(const double* v0, const double* v1, double* v_out, size_t len);

#endif