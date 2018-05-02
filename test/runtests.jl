# module TestIPython

include("preamble.jl")

import PyCall
@show PyCall.pyprogramname
@show PyCall.pyversion
@show PyCall.libpython
@show PyCall.conda

ipy_opts = @time IPython._start_ipython(:ipython_options)
ipy_main = ipy_opts["user_ns"]["Main"]

@testset "Main" begin
    ipy_main[:x] = 17061
    @test x == 17061
end

include("test_julia_repl.jl")

# end  # module
