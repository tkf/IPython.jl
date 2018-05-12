# Let PyCall.jl use Python interpreter from Conda.jl
# See: https://github.com/JuliaPy/PyCall.jl
ENV["PYTHON"] = ""

info("Pkg.clone(pwd())")
Pkg.clone(pwd())

info("Pkg.build(IPython)")
Pkg.build("IPython")

using IPython
IPython.install_dependency("ipython"; force=true)
IPython.install_dependency("julia"; force=true)
IPython.install_dependency("pytest"; force=true)

info("show_versions.jl")
include("show_versions.jl")
