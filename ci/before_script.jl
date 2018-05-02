# Let PyCall.jl use Python interpreter from Conda.jl
# See: https://github.com/JuliaPy/PyCall.jl
ENV["PYTHON"] = ""

info("Pkg.clone(pwd())")
Pkg.clone(pwd())

info("Pkg.build(IPython)")
Pkg.build("IPython")

info("Conda.add(ipython)")
using Conda
Conda.add("ipython")

using PyCall
install_pyjulia = `$(PyCall.pyprogramname) -m pip install julia`
info(install_pyjulia)
run(install_pyjulia)

info("show_versions.jl")
include("show_versions.jl")
