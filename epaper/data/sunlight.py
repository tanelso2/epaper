from datetime import datetime, date, timedelta
from typing import Optional

from astral import LocationInfo
from astral.sun import sun

from epaper.data.location import tz, lat_lon


def location() -> LocationInfo:
    latlon = lat_lon()
    match latlon:
        case None:
            return LocationInfo(
                name="Chicago",
                region="USA",
                timezone=tz(),
                latitude=41.8781,
                longitude=-87.6298,
            )
        case (lat, lon):
            return LocationInfo(
                name="Custom Location",
                region="",
                timezone=tz(),
                latitude=lat,
                longitude=lon,
            )


def get_sunlight(dt: Optional[datetime] = None):
    loc = location()
    d: Optional[date] = dt.date() if dt else None
    s = sun(loc.observer, tzinfo=loc.timezone, date=d)
    return s


def hours_of_sunlight(dt: Optional[datetime] = None) -> float:
    s = get_sunlight(dt)
    sunrise = s["sunrise"]
    sunset = s["sunset"]
    return (sunset - sunrise).total_seconds() / 3600


def next_sun_event(dt: Optional[datetime] = None) -> tuple[str, datetime]:
    s = get_sunlight(dt)
    now = dt or datetime.now(tz())
    sunrise = s["sunrise"]
    sunset = s["sunset"]
    if sunrise > now:
        return "Sunrise", sunrise
    elif sunset > now:
        return "Sunset", sunset
    else:
        tomorrow = now + timedelta(days=1)
        s_tomorrow = get_sunlight(tomorrow)
        return "Sunrise", s_tomorrow["sunrise"]


def next_sunrise(dt: Optional[datetime] = None) -> datetime:
    s = get_sunlight(dt)
    now = dt or datetime.now(tz())
    if s["sunrise"] > now:
        return s["sunrise"]
    else:
        tomorrow = now + timedelta(days=1)
        s_tomorrow = get_sunlight(tomorrow)
        return s_tomorrow["sunrise"]
