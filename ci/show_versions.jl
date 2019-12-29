if VERSION >= v"0.7.0-"
    using Pkg
    Pkg.status()
else
    for line in split(strip(readstring("REQUIRE")), '\n')[2:end]
        name = split(line)[1]
        println(name, "\t", Pkg.installed(name))
    end
end
