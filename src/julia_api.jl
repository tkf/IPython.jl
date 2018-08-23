module JuliaAPI

function eval_str(m::Module, code::String)
    Base.eval(m, Meta.parse(strip(code)))
end

eval_str(code::String) = eval_str(Main, code)

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

end  # module
