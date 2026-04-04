from epaper.utils.wind import cardinal_direction


def test_cardinal_direction():
    test_cases = [
        (0.0, "N"),
        (25.0, "NE"),
        (100, "E"),
        (360.0, "N"),
        (359.09, "N"),
        (180.0, "S"),
    ]
    for input, expected in test_cases:
        actual = cardinal_direction(input)
        assert (
            actual == expected
        ), f"Expected {input} => {expected}, got {actual} instead"
