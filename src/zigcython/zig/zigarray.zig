const std = @import("std");
const print = std.debug.print;

//------------------------------------------------------------------------------
// Example for adding two 1D numpy arrays sending them back and forth to Zig
pub export fn addVec(v0: [*c]const f64, v1: [*c]const f64, v_out: [*c]f64, len: usize) void {
    const s0 = v0[0..len];
    const s1 = v1[0..len];
    const s_out = v_out[0..len];

    for (0..s_out.len) |ii| {
        s_out[ii] = s0[ii] + s1[ii];
    }
}

//------------------------------------------------------------------------------
// Example sending a simple struct back and forth from Python to Zig
pub const Data = extern struct {
    valf: f64,
    vali: i32,
    valu: usize,
};

pub export fn dataInit() Data {
    const data: Data = .{
        .valf = 0.0,
        .vali = 0,
        .valu = 0,
    };
    return data;
}

pub export fn dataSet(in_data: Data) void {
    print("\ndataSet\n", .{});
    print("data.valf={}\n", .{in_data.valf});
    print("data.vali={}\n", .{in_data.vali});
    print("data.valu={}\n", .{in_data.valu});
    print("\n", .{});
}


//------------------------------------------------------------------------------
// Example of sending a more complex struct Python->Zig->Python
pub const MatrixF64 = extern struct {
    elems: [*c]f64,
    dims: [*c]usize,
    numel: usize,
    ndim: usize,
};

pub export fn matrixToZig(in_elems: [*c]f64, in_dims: [*c] usize, in_numel: usize, in_ndim: usize) void {
    const matrix: MatrixF64 = .{
        .elems = in_elems,
        .dims = in_dims,
        .numel = in_numel,
        .ndim =  in_ndim,
    };

    printMatrix(matrix);
}

pub export fn matStructToZig(mat: MatrixF64) void {
    printMatrix(mat);
}

fn printMatrix(mat: MatrixF64) void {
    print("\nZig: Matrix\n",.{});

    print("numel={}\n",.{mat.numel});
    print("ndims={}\n",.{mat.ndim});

    const s_dims = mat.dims[0..mat.ndim];
    print("dims=[",.{});
    for (s_dims) |dd|{
        print("{},",.{dd});
    }
    print("]\n",.{});

    const s_elems = mat.elems[0..mat.numel];
    print("elems=[",.{});
    for (s_elems) |ee| {
         print("{},",.{ee});
    }
    print("]\n\n",.{});

}





