in_CI = lowercase(get(ENV, "CI", "false")) == "true"

if in_CI
    # Let PyCall.jl use Python interpreter from Conda.jl
    # See: https://github.com/JuliaPy/PyCall.jl
    ENV["PYTHON"] = ""
    Pkg.build("PyCall")
end

using PyCall

packages = ["ipython"]
if in_CI
    push!(packages, "pytest")
    if get(ENV, "CONDA_JL_VERSION", "") == "2"
        # For IPython.testing.globalipapp
        push!(packages, "mock")
    end
end
PyCall.conda_add(packages)

if VERSION >= v"0.7.0-"
    @info "PyCall/deps/build.log:"
    print(read(
        joinpath(dirname(dirname(pathof(IPython.PyCall))), "deps", "build.log"),
        String))
end
