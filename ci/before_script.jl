# Let PyCall.jl use Python interpreter from Conda.jl
# See: https://github.com/JuliaPy/PyCall.jl
ENV["PYTHON"] = ""

info("Pkg.clone(pwd())")
Pkg.clone(pwd())

info("Pkg.build(IPython)")
Pkg.build("IPython")

using IPython
IPython.install_dependency("ipython")
IPython.install_dependency("julia")
IPython.install_dependency("pytest")

info("show_versions.jl")
include("show_versions.jl")
