module TestConvenience

include("preamble.jl")

@testset "Convenience" begin
    @test_nothrow IPython.envinfo(DevNull)
    @test IPython.pyversion("julia") isa String
    @test IPython.pyversion("IPython") isa String
    @test IPython.pyversion("IPython") ==  IPython._pyversion("IPython")

    println("vvv DRY RUN vvv")
    @test_nothrow IPython.install_dependency("ipython"; dry_run=true)
    @test_nothrow IPython.install_dependency("julia"; dry_run=true)
    println("^^^ DRY RUN ^^^")
end

end  # module
