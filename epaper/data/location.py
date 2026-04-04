from typing import Optional
from zoneinfo import ZoneInfo

import os


def tz():
    return ZoneInfo("America/Chicago")


_LATLON_FILE = os.path.join("config", "latlon.txt")


def lat_lon() -> Optional[tuple[float, float]]:
    if os.path.exists(_LATLON_FILE):
        with open("config/latlon.txt", "r") as f:
            lat, lon = f.read().strip().split(",")
            return float(lat), float(lon)
    return None


def lat_lon_or_raise() -> tuple[float, float]:
    ret = lat_lon()
    if ret is None:
        raise ValueError(f"Could not get location from config file {_LATLON_FILE}")
    return ret
