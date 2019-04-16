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

_start_ipython(name::Symbol) = _start_ipython(getipythonjl(name))
# helper function that is used only in tests

_start_ipython(f::PyObject) =
    pycall(
        f, Nothing,
        JuliaAPI.eval_str,
        JuliaAPI,
    )

start_ipython() = _start_ipython(_customized_ipython)

getipythonjl(name) = _getproperty(pyimport("ipython_jl"), name)

const _customized_ipython = PyNULL()

function __init__()
    pushfirst!(PyVector(@compatattr pyimport("sys")."path"), @__DIR__)
    copy!(_customized_ipython, getipythonjl(:customized_ipython))
    afterreplinit(init_repl)
end
