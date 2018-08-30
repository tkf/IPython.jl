# Launch IPython in Julia

[![Build Status][travis-img]][travis-url]
[![Coverage Status][coveralls-img]][coveralls-url]
[![codecov.io][codecov-img]][codecov-url]


![Example REPL session](example.png)


## Usage

Run `using IPython` and then type `.` in empty `julia>` prompt or run
`IPython.start_ipython()`.  If you are using IPython 7.0 or above, you
can switch back to Julia REPl by `backspace` or `ctrl-h` key (like
other REPL modes).  For older versions of IPython, exiting IPython as
usual (e.g., `ctrl-d`) brings you back to the Julia REPL.  Re-entering
IPython keeps the previous state.  Use pre-defined `Main` object to
access Julia namespace from IPython.

**Note:**
First launch of IPython may be slow.


## Requirements

### Julia

* PyCall

### Python

* IPython (7.0 or above is recommended)


[travis-img]: https://travis-ci.org/tkf/IPython.jl.svg?branch=master
[travis-url]: https://travis-ci.org/tkf/IPython.jl
[coveralls-img]: https://coveralls.io/repos/tkf/IPython.jl/badge.svg?branch=master&service=github
[coveralls-url]: https://coveralls.io/github/tkf/IPython.jl?branch=master
[codecov-img]: http://codecov.io/github/tkf/IPython.jl/coverage.svg?branch=master
[codecov-url]: http://codecov.io/github/tkf/IPython.jl?branch=master
