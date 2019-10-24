using Test

macro test_nothrow(ex)
    quote
        @test begin
            $(esc(ex))
            true
        end
    end
end

using IPython
using IPython: @compatattr, _setproperty!
using Compat
