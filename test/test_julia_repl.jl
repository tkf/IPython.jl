module TestJuliaREPL

include("preamble.jl")
using IPython: init_repl, init_repl_if_not
using Base.Terminals: TextTerminal


@testset "init_repl_if_not" begin
    repl = init_repl_if_not(; _init_repl=identity)
    if isinteractive()
        @test repl === Base.active_repl
    else
        @test repl === nothing
    end
end


struct DummyTerminal <: TextTerminal
end

function dummy_repl()
    repl = Base.REPL.LineEditREPL(DummyTerminal())
    repl.interface = Base.REPL.setup_interface(repl)
    return repl
end

function dummy_initialized_repl()
    repl = dummy_repl()
    init_repl(repl)
    return repl
end

@testset "init_repl" begin
    repl = dummy_initialized_repl()
    keymap_dict = repl.interface.modes[1].keymap_dict
    @test haskey(keymap_dict, '.')
end

end  # module
