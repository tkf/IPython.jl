function envinfo(io::IO = STDOUT; verbosity::Int = 1)
    if verbosity > 0
        versioninfo(io, verbosity > 1)
        println(io)
    end
    for ex in [:(PyCall.pyprogramname),
               :(PyCall.pyversion),
               :(PyCall.libpython),
               :(PyCall.conda),
               :(pyversion("IPython")),
               :(pyversion("julia")),
               ]
        Base.show_unquoted(io, ex)
        println(io, " = ", eval(ex))
    end
    nothing
end

function pkg_resources_version(name)
    pkg_resources = try
        pyimport("pkg_resources")
    catch err
        if ! (err isa PyCall.PyError)
            rethrow()
        end
        return
    end
    return pkg_resources[:get_distribution](name)[:version]
end

function _pyversion(name)
    package = try
        pyimport(name)
    catch err
        if ! (err isa PyCall.PyError)
            rethrow()
        end
        return
    end
    try
        return package[:__version__]
    catch err
        if ! (err isa KeyError)
            rethrow()
        end
    end
end

function pyversion(name)
    version = pkg_resources_version(name)
    if version !== nothing
        return version
    end
    return _pyversion(name)
end


function yes_or_no(prompt = string("Type \"yes\" and press enter if ",
                                   "you want to run this command.");
                   input = STDIN,
                   output = STDOUT)
    print(output, prompt, " [yes/no]: ")
    answer = readline(input)
    if answer == "yes"
        return true
    elseif answer == "no"
        return false
    end
    warn("Please enter \"yes\" or  \"no\".  Got: $answer")
    return false
end


conda_packages = ("ipython", "pytest")
NOT_INSTALLABLE = (false, "", Void)

function condajl_installation(package)
    if PyCall.conda && package in conda_packages
        message = """
        Installing $package via Conda.jl
        Execute?:
            Conda.add($package)
        """
        install = () -> Conda.add(package)
        return (true, message, install)
    end
    return NOT_INSTALLABLE
end

function conda_installation(package)
    conda = joinpath(dirname(PyCall.pyprogramname), "conda")
    if isfile(conda) && package in conda_packages
        prefix = dirname(dirname(PyCall.pyprogramname))
        command = `$conda install --prefix $prefix $package`
        message = """
        Installing $package with $conda
        Execute?:
            $command
        """
        install = () -> run(command)
        return (true, message, install)
    end
    return NOT_INSTALLABLE
end

function pip_installation(package)
    if package in (conda_packages..., "julia")
        command = `$(PyCall.pyprogramname) -m pip install $package`
        message = """
        Installing $package for $(PyCall.pyprogramname)
        Execute?:
            $command
        """
        install = () -> run(command)
        return (true, message, install)
    end
    return NOT_INSTALLABLE
end

function install_dependency(package; force=false, dry_run=false)
    for check_installer in [condajl_installation,
                            conda_installation,
                            pip_installation]
        found, message, install =  check_installer(package)
        if found
            info(message)
            if !dry_run && (force || yes_or_no())
                install()
            end
            return
        end
    end
    warn("Installing $package not supported.")
end


function test_replhelper()
    command = `$(PyCall.pyprogramname) -m pytest`
    info(command)
    cd(@__DIR__) do
        run(command)
    end
end
