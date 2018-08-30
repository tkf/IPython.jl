#!/usr/bin/env julia

"""
CLI to run pytest within Julia process.

All arguments are passed to pytest.

Examples:

    cd HERE
    ./pytest.jl
    ./pytest.jl -x --pdb
    ./pytest.jl replhelper/tests/test_ipyext.py
"""

using IPython
code = IPython.test_replhelper(
    `$ARGS`;
    inprocess = true,
    revise = false,
    check = false,
)
exit(code)
