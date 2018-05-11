module IPython

using Base: LineEdit
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

conda_packages = ("ipython", "pytest")

function prefer_condajl(package)
    PyCall.conda && package in conda_packages
end

function prefer_pip(package)
    package in (conda_packages..., "julia")
end

function install_dependency(package; dry_run=false)
    if prefer_condajl(package)
        info("Installing $package via Conda.jl")
        info("Conda.add($package)")
        if ! dry_run
            Conda.add(package)
        end
    elseif prefer_pip(package)
        info("Installing $package for $(PyCall.pyprogramname)")
        pip_install = `$(PyCall.pyprogramname) -m pip install $package`
        info(pip_install)
        if ! dry_run
            run(pip_install)
        end
    else
        warn("Installing $package not supported.")
    end
end


function test_replhelper()
    command = `$(PyCall.pyprogramname) -m pytest`
    info(command)
    cd(@__DIR__) do
        run(command)
    end
end


# Register keybind '.' in Julia REPL:

function init_repl_if_not(; _init_repl=init_repl)
    active_repl = try
        Base.active_repl
    catch err
        err isa UndefVarError || rethrow()
        return
    end

    if isinteractive() && typeof(active_repl) != Base.REPL.BasicREPL
        _init_repl(active_repl)
    end
end
# See: https://github.com/JuliaInterop/RCall.jl/blob/master/src/setup.jl

function init_repl(repl)
    start = function(s, _...)
        if isempty(s) || position(LineEdit.buffer(s)) == 0
            # Force current_module() inside IPython to be Main:
            eval(Main, :($start_ipython()))
            println()
            LineEdit.edit_clear(s)
        else
            LineEdit.edit_insert(s, '.')
        end
    end
    ipy_prompt_keymap = Dict{Any,Any}('.' => start)

    main_mode = repl.interface.modes[1]
    main_mode.keymap_dict = LineEdit.keymap_merge(main_mode.keymap_dict,
                                                  ipy_prompt_keymap)
end
# See: https://github.com/JuliaInterop/RCall.jl/blob/master/src/RPrompt.jl

end # module
