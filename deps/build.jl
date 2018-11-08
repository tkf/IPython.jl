if VERSION >= v"0.7.0-"
    # Adding Pkg in test/REQUIRE would be an error in 0.6.  Using
    # Project.toml still has some gotchas.  So:
    Pkg = Base.require(Base.PkgId(Base.UUID(0x44cfe95a1eb252eab672e2afdf69b78f), "Pkg"))
end

in_CI = lowercase(get(ENV, "CI", "false")) == "true"

if in_CI
    # Let PyCall.jl use Python interpreter from Conda.jl
    # See: https://github.com/JuliaPy/PyCall.jl
    ENV["PYTHON"] = ""
    Pkg.build("PyCall")
end

using PyCall

if get(ENV, "CONDA_JL_VERSION", "") == "3"
    PyCall.conda_add(["python=3.6"])
    PyCall.conda_add(["python=3.7"])
end

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
        joinpath(dirname(dirname(pathof(PyCall))), "deps", "build.log"),
        String))
end
