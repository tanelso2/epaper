import pytest

from epaper.utils.time_formatting import hours_minutes_str


@pytest.mark.parametrize(
    "input,expected",
    [
        (1.25, "1h 15m"),
        (0.75, "0h 45m"),
        (1.0, "1h 0m"),
        (0.5, "0h 30m"),
    ],
)
def test_hours_minutes_str(input: float, expected: str):
    assert hours_minutes_str(input) == expected
