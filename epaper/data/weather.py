import requests
from typing import Optional

from epaper.data.location import lat_lon_or_raise


def get_openweather_api_key(filename="openweatherapikey.txt") -> str:
    with open(filename, "r") as f:
        return f.read().strip()


def _make_openweather_api_call(
    url: str,
    api_key: Optional[str] = None,
    extra_params: Optional[dict] = None,
):
    if api_key is None:
        api_key = get_openweather_api_key()
    lat, lon = lat_lon_or_raise()
    params = {"appid": api_key, "lat": lat, "lon": lon, "units": "imperial"}
    if extra_params:
        params.update(extra_params)
    resp = requests.get(
        url,
        params=params,
        headers={"Content-Type": "application/json"},
        timeout=3,
    )
    resp.raise_for_status()
    return resp.json()


# API docs:
# https://openweathermap.org/current?collection=current_forecast
def get_current_weather(api_key: Optional[str] = None):
    url = "https://api.openweathermap.org/data/2.5/weather"
    return _make_openweather_api_call(url, api_key)


def get_weather(api_key: Optional[str] = None):
    """Get the current weather"""
    return get_current_weather(api_key)


def get_5_day_forecast(api_key: Optional[str] = None):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    return _make_openweather_api_call(url, api_key)
