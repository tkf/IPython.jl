# Launch IPython in Julia

[![Build Status][travis-img]][travis-url]
[![Coverage Status][coveralls-img]][coveralls-url]
[![codecov.io][codecov-img]][codecov-url]


![Example REPL session](example.png)


## Usage

Run `using IPython` and then type `.` in empty `julia>` prompt or run
`IPython.start_ipython()`.  Exiting IPython as usual (e.g., `Ctrl-D`)
bring you back to Julia REPL.  Re-entering IPython keeps the previous
state.  In IPython, two variables are pre-defined: `Main` for
accessing top-level namespace of the Julia REPL and `julia` for
accessing an instance of `julia.Julia` object.

**Note:**
First launch of IPython may be slow.


## Requirements

### Julia

* PyCall

### Python

* pyjulia
* IPython


[travis-img]: https://travis-ci.org/tkf/IPython.jl.svg?branch=master
[travis-url]: https://travis-ci.org/tkf/IPython.jl
[coveralls-img]: https://coveralls.io/repos/tkf/IPython.jl/badge.svg?branch=master&service=github
[coveralls-url]: https://coveralls.io/github/tkf/IPython.jl?branch=master
[codecov-img]: http://codecov.io/github/tkf/IPython.jl/coverage.svg?branch=master
[codecov-url]: http://codecov.io/github/tkf/IPython.jl?branch=master
