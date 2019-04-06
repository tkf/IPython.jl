using Base.Meta: isexpr
using PyCall
import Conda

const _getproperty = try
    pyimport("sys").executable
    getproperty
catch
    getindex
end
if _getproperty === getindex
    _setproperty!(value, name, x) = setindex!(value, x, name)
else
    const _setproperty! = setproperty!
end

compatattr_imp(x) = x
compatattr_imp(ex::Expr) =
    if ex.head == :. && length(ex.args) == 2 && !isexpr(ex.args[2], :tuple)
        :($_getproperty($(compatattr_imp.(ex.args)...)))
    else
        Expr(ex.head, compatattr_imp.(ex.args)...)
    end

macro compatattr(ex)
    esc(compatattr_imp(ex))
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
    pushfirst!(PyVector(@compatattr pyimport("sys")."path"), @__DIR__)
    afterreplinit(init_repl)
end
