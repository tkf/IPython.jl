using PyCall
import Conda

julia_exepath() =
    joinpath(VERSION < v"0.7.0-DEV.3073" ? JULIA_HOME : Base.Sys.BINDIR,
             Base.julia_exename())

function _start_ipython(name; kwargs...)
    pyimport("ipython_jl")[name](;
        eval_str = JuliaAPI.eval_str,
        api = JuliaAPI,
        kwargs...)
end

function start_ipython(; kwargs...)
    _start_ipython(:customized_ipython; kwargs...)
end

function __init__()
    pushfirst!(PyVector(pyimport("sys")["path"]), @__DIR__)
    afterreplinit(init_repl)
end
