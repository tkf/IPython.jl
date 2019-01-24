using PyCall
import Conda

const _getproperty = try
    pyimport("sys").executable
    getproperty
catch
    getindex
end

julia_exepath() =
    joinpath(VERSION < v"0.7.0-DEV.3073" ? JULIA_HOME : Base.Sys.BINDIR,
             Base.julia_exename())

function _start_ipython(name; kwargs...)
    _getproperty(pyimport("ipython_jl"), name)(;
        eval_str = JuliaAPI.eval_str,
        api = JuliaAPI,
        kwargs...)
end

function start_ipython(; kwargs...)
    _start_ipython(:customized_ipython; kwargs...)
end

function __init__()
    pushfirst!(PyVector(_getproperty(pyimport("sys"), "path")), @__DIR__)
    afterreplinit(init_repl)
end
