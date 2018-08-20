using PyCall
import Conda

julia_exepath() =
    joinpath(VERSION < v"0.7.0-DEV.3073" ? JULIA_HOME : Base.Sys.BINDIR,
             Base.julia_exename())

function _start_ipython(name; kwargs...)
    pyimport("replhelper")[name](;
        init_julia = false,
        jl_runtime_path = julia_exepath(),
        kwargs...)
end

function start_ipython(; kwargs...)
    Base.eval(Main, :(import PyCall))  # pyjulia needs it
    _start_ipython(:customized_ipython; kwargs...)
end

function __init__()
    pushfirst!(PyVector(pyimport("sys")["path"]), @__DIR__)
    init_repl_if_not()
end
