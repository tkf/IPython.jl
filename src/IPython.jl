module IPython

using PyCall

function start_ipython()
    pyimport("replhelper")[:customized_ipython]()
end

function __init__()
    unshift!(PyVector(pyimport("sys")["path"]), @__DIR__)
end

end # module
