# zigcython
A minimal working example linking python to zig through cython to send numpy arrays to zig.


## Running the Example
First create a python virtual environment in the repo directory and activate it:
```shell
python -m venv .venv
source ./.venv/bin/activate
```

Install numpy and cython:
```shell
pip install numpy cython
```

Build the Zig dynamic library:
```shell
zig build-lib -dynamic zigarray.zig
```

Build the cython files and link the Zig dynamic library (see setup.py):
```shell
python setup.py build_ext --inplace -f
```

Now run the `main_cyth.py` which calls the Zig library through cython:
```shell
python main_zcyth.py
```

<!-- ## How it works
### Zig
The

### Cython

### Python -->

