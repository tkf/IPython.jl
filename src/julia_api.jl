module JuliaAPI

@static if VERSION >= v"0.7-"
    import REPL
end
using PyCall: pyjlwrap_new

function eval_str(m::Module, code::String;
                  # auto_jlwrap = true,
                  force_jlwrap = false)
    result = Base.eval(m, Meta.parse(strip(code)))
    if force_jlwrap
        return pyjlwrap_new(result)
    # elseif auto_jlwrap
    #     return _wrap(result)
    end
    return result
end

eval_str(code::String; kwargs...) = eval_str(Main, code; kwargs...)

# Not sure if I need it:
#=
_wrap(result::Union{
    # Types to be wrapped:
    Symbol,
}) = pyjlwrap_new(result)

_wrap(result) = result
=#


set_var(name::String, value) = set_var(Symbol(name), value)

function set_var(name::Symbol, value)
    Base.eval(Main, :($name = $value))
    nothing
end

@static if VERSION < v"0.7-"
    getproperty_str(obj, name) = getfield(obj, Symbol(name))
else
    getproperty_str(obj, name) = getproperty(obj, Symbol(name))
end

@static if VERSION < v"0.7-"
    dir(m::Module; all=true, imported=false) = names(m, all, imported)
    dir(::T; _...) where T = fieldnames(T)
else
    dir(m::Module; kwargs...) = names(m; all=true, kwargs...)
    dir(m; all=true) = propertynames(m, private=!all)
end

struct _jlwrap_type end  # a type that would be wrapped as jlwrap by PyCall

get_jlwrap_prototype() = _jlwrap_type()

@static if VERSION < v"0.7-"
    completions(_a...; __k...) = String[]
else
    function completions(string, pos, context_module = Main)
        ret, _, should_complete =
            REPL.completions(string, pos, context_module)
        if should_complete
            return map(REPL.completion_text, ret)
        else
            return String[]
        end
    end
end

end  # module
