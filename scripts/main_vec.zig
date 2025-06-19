const std = @import("std");
const print = std.debug.print;

pub fn main() !void {
    const dyn_lib_path = "src/zigcython/zig/libzigarray.so";
    print("Dynamic lib path: {s}\n",.{dyn_lib_path});

    var dyn_lib = try std.DynLib.open(dyn_lib_path);
    defer dyn_lib.close();

    const addVec = dyn_lib.lookup(
        *const fn ([*c]const f64, [*c]const f64, [*c]f64, usize) callconv(.C) void,
        "addVec",
    ) orelse return error.NoFunction;

    const len: usize = 7;
    const v0 = [_]f64{1.0,} ** 7;
    const v1 = [_]f64{1.0,} ** 7;
    var v_out = [_]f64{0.0,} ** 7;

    const s0 = v0[0..v0.len];
    const s1 = v1[0..v1.len];
    const s_out = v_out[0..v_out.len];

    addVec(s0,s1,s_out,len);

    print("\n[",.{});
    for (s_out) |ii| {
        print("{},",.{ii});
    }
    print("]\n\n",.{});

}