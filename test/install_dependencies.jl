using Compat: @info
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
