import math


def add_degrees(a: float, b: float) -> float:
    return (a + b) % 360


def invert_degrees(a: float) -> float:
    return add_degrees(a, 180)


def invert_y(a: float) -> float:
    """Flips an angle about the x axis"""
    return (-a) % 360


def project_from(
    center: tuple[float, float], length: float, deg: float
) -> tuple[float, float]:
    x, y = center
    rads = math.radians(deg)
    new_x = x + (length * math.cos(rads))
    new_y = y + (length * math.sin(rads))
    return (new_x, new_y)
