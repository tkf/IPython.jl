using PyCall
using Conda
using IPython

if PyCall.conda
    Conda.add("ipython")
    IPython.install_dependency("julia"; force=true)
end
