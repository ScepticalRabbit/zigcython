import sys, subprocess

zig_build = [
    "build-lib",
    "-dynamic",
    "zigarray.zig"
]

subprocess.call([sys.executable, "-m", "ziglang"] + zig_build)