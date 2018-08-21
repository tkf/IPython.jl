using Pkg

# Let PyCall.jl use Python interpreter from Conda.jl
# See: https://github.com/JuliaPy/PyCall.jl
ENV["PYTHON"] = ""

@info "Pkg.clone(pwd())"
Pkg.clone(pwd())

@info "Pkg.build(IPython)"
Pkg.build("IPython")

using IPython
IPython.install_dependency("pytest"; force=true)
IPython.install_dependency("ipython"; force=true)
if get(ENV, "CONDA_JL_VERSION", "") != "2"
    # Use regular IPython when 7.0 is out.
    IPython.install_dependency("ipython-dev"; force=true)
end

@info "show_versions.jl"
include("show_versions.jl")
