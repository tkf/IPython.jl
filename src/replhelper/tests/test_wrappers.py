def test_array_mutability(Main):
    Main.xs = [1, 2, 3]
    Main.xs[0] = 100
    xs = Main.eval("identity.(xs)")
    assert all(xs == [100, 2, 3])


def test_peal(Main):
    xs = Main.map(Main.identity, range(3))
    assert all(xs == [0, 1, 2])


def test_wrapped_dict(Main):
    dct = Main.eval("dict = Dict()", force_jlwrap=True)
    dct["key"] = "value"
    assert Main.dict == {"key": "value"}
