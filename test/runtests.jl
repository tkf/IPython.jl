# module TestIPython

using IPython
import PyCall
@static if VERSION < v"0.7.0-DEV.2005"
    using Base.Test
else
    using Test
end

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

# end  # module
