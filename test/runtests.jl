# module TestIPython

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

if VERSION < v"0.7.0-"
    IPython.test_replhelper(`--ignore replhelper/core`; inprocess=true)
else
    IPython.test_replhelper(inprocess=true)
end

# end  # module
