module IPython

using Compat
using Compat: @warn, @info
include("julia_api.jl")
include("core.jl")
include("convenience.jl")
include("julia_repl.jl")

end # module
