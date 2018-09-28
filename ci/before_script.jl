@static if VERSION >= v"0.7.0-"
    using Pkg
else
    macro info(x)
        :(info($(esc(x))))
    end
end

# Let PyCall.jl use Python interpreter from Conda.jl
# See: https://github.com/JuliaPy/PyCall.jl
ENV["PYTHON"] = ""

@info "Pkg.clone(pwd())"
Pkg.clone(pwd())

@info "Pkg.build(IPython)"
Pkg.build("IPython")

using IPython

if VERSION >= v"0.7.0-"
    @info "PyCall/deps/build.log:"
    print(read(
        joinpath(dirname(dirname(pathof(IPython.PyCall))), "deps", "build.log"),
        String))
end

IPython.install_dependency("pytest"; force=true)
IPython.install_dependency("ipython"; force=true)
if get(ENV, "CONDA_JL_VERSION", "") == "2"
    # For IPython.testing.globalipapp
    IPython.install_dependency("mock"; force=true)
end

@info "show_versions.jl"
include("show_versions.jl")

@info "Pkg.build(IPython) since conda might have re-installed different Python"
Pkg.build("IPython")

if VERSION >= v"0.7.0-"
    @info "PyCall/deps/build.log:"
    print(read(
        joinpath(dirname(dirname(pathof(IPython.PyCall))), "deps", "build.log"),
        String))
end
