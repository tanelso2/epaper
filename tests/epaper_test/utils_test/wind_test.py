import pytest

from epaper.utils.wind import cardinal_direction


@pytest.mark.parametrize(
    "input,expected",
    [
        (0.0, "N"),
        (25.0, "NE"),
        (100, "E"),
        (360.0, "N"),
        (359.09, "N"),
        (180.0, "S"),
        (270.0, "W"),
        (325.0, "NW"),
        (210.0, "SW"),
        (150.0, "SE"),
    ],
)
def test_cardinal_direction(input: float, expected: str):
    actual = cardinal_direction(input)
    assert actual == expected, f"Expected {input} => {expected}, got {actual} instead"


@pytest.mark.parametrize(
    "input",
    [
        -1.0,
        375.0,
        -375.0,
    ],
)
def test_cardinal_direction_throws(input: float):
    with pytest.raises(ValueError):
        cardinal_direction(input)
