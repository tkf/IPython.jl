using REPL
using REPL: LineEdit

# Register keybind '.' in Julia REPL:

function init_repl_if_not(; _init_repl=init_repl)
    active_repl = try
        Base.active_repl
    catch err
        err isa UndefVarError || rethrow()
        return
    end

    if isinteractive() && typeof(active_repl) != REPL.BasicREPL
        _init_repl(active_repl)
    end
end
# See: https://github.com/JuliaInterop/RCall.jl/blob/master/src/setup.jl

function init_repl(repl)
    start = function(s, _...)
        if isempty(s) || position(LineEdit.buffer(s)) == 0
            # Force current_module() inside IPython to be Main:
            Base.eval(Main, :($start_ipython()))
            println()
            LineEdit.refresh_line(s)
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
