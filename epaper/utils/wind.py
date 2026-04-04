from enum import Enum

import epaper.utils.wind_direction_constants as WD


def cardinal_direction(degrees: float) -> str:
    if not (0.0 <= degrees <= 360.0):
        raise ValueError(f"Degrees should be between 0.0 and 360.0. Input: {degrees}")
    if WD.NNE <= degrees < WD.ENE:
        return "NE"
    elif WD.ENE <= degrees < WD.ESE:
        return "E"
    elif WD.ESE <= degrees < WD.SSE:
        return "SE"
    elif WD.SSE <= degrees < WD.SSW:
        return "S"
    elif WD.SSW <= degrees < WD.WSW:
        return "SW"
    elif WD.WSW <= degrees < WD.WNW:
        return "W"
    elif WD.WNW <= degrees < WD.NNW:
        return "NW"
    else:
        return "N"
