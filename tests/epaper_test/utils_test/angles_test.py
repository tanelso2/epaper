from epaper.utils.angles import add_degrees, invert_degrees, invert_y, project_from


def test_add_degrees():
    f = add_degrees
    assert f(10.0, 10.0) == 20.0
    assert f(350.0, 20.0) == 10.0
    assert f(10.0, -20.0) == 350.0


def test_invert_degrees():
    f = invert_degrees
    assert f(0.0) == 180.0
    assert f(90.0) == 270.0
    assert f(10.0) == 190.0
    assert f(190.0) == 10.0


def test_invert_y():
    f = invert_y
    assert f(10.0) == 350.0
    assert f(350.0) == 10.0
    assert f(180.0) == 180.0
    assert f(90.0) == 270.0


def comp_floats(a: float, b: float, tolerance=1e-5) -> bool:
    return abs(b - a) <= tolerance


def comp_float_tuple(p1: tuple[float, float], p2: tuple[float, float]) -> bool:
    x1, y1 = p1
    x2, y2 = p2
    return comp_floats(x1, x2) and comp_floats(y1, y2)


def test_project_from():
    comp = comp_float_tuple
    assert comp((10.0, 0.0), project_from((0.0, 0.0), length=10.0, deg=0.0))
    assert comp((0.0, 10.0), project_from((0.0, 0.0), length=10.0, deg=90.0))
    assert comp((-10.0, 0.0), project_from((0.0, 0.0), length=10.0, deg=180.0))
    assert comp((0.0, -10.0), project_from((0.0, 0.0), length=10.0, deg=270.0))

    assert comp((1.0, 1.0), project_from((0.0, 1.0), length=1.0, deg=0.0))
    assert comp((1.0, 2.0), project_from((0.0, 2.0), length=1.0, deg=0.0))
