using PyCall
import Conda

function _start_ipython(name; kwargs...)
    pyimport("replhelper")[name](;
        init_julia = false,
        jl_runtime_path = joinpath(JULIA_HOME, Base.julia_exename()),
        kwargs...)
end

start_ipython(; kwargs...) = _start_ipython(:customized_ipython; kwargs...)

function __init__()
    unshift!(PyVector(pyimport("sys")["path"]), @__DIR__)
    init_repl_if_not()
end
