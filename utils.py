from types import ModuleType

try:
    from importlib import reload
except ImportError:
    try:
        from imp import reload
    except ImportError:
        pass  # Python 2?


class Singleton(object):

    @classmethod
    def instance(cls, *args, **kwargs):
        try:
            return cls.__initialized
        except AttributeError:
            pass
        cls.__initialized = self = cls(*args, **kwargs)
        return self

    @classmethod
    def initialized(cls, default=None):
        try:
            return cls.__initialized
        except AttributeError:
            return default


def itermodules(root, visited=None):
    visited = set() if visited is None else visited
    visited.add(root)
    for mod in vars(root).values():
        if isinstance(mod, ModuleType) and mod not in visited:
            yield mod
            for sub in itermodules(mod, visited):
                yield sub


def discover_singletons(modules, found=None):
    found = set() if found is None else found
    for mod in modules:
        for cls in vars(mod).values():
            if (isinstance(cls, type) and
                    issubclass(cls, Singleton) and
                    cls is not Singleton and
                    cls not in found):
                found.add(cls)
                yield cls


def reloadall(root, prioritized):
    modules = list(prioritized)
    modules.extend(itermodules(root, visited=set(modules)))
    found = list(discover_singletons(modules))

    for mod in modules:
        reload(mod)
    reload(root)

    for old in found:
        assert old.__module__.startswith(root.__name__ + ".")
        tail = old.__module__[len(root.__name__) + 1:]
        new = eval(tail + "." + old.__name__, vars(root))
        initialized = old.initialized()
        if old is not None:
            new._Singleton__initialized = initialized
