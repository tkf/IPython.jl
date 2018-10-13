# module TestIPython

if lowercase(get(ENV, "CI", "false")) == "true"
    include("install_dependencies.jl")
end

include("preamble.jl")

IPython.envinfo()

ipy_opts = @time IPython._start_ipython(:ipython_options)
ipy_main = ipy_opts["user_ns"]["Main"]

@testset "Main" begin
    ipy_main[:x] = 17061
    @test x == 17061
end

include("test_julia_repl.jl")
include("test_convenience.jl")

IPython.test_ipython_jl(inprocess=true)

# end  # module
