from typing import Optional
import warnings

from pydantic import BaseModel, ConfigDict, Field
from pydantic.types import deprecated
import requests

from epaper.data.location import lat_lon_or_raise


class LatLon(BaseModel):
    lon: float
    lat: float


class WeatherConditionCode(BaseModel):
    id: int
    main: str
    description: str
    icon: str


class WeatherDescription(BaseModel):
    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    humidity: float
    pressure: float
    sea_level: float
    grnd_level: float


class WindDescription(BaseModel):
    speed: float
    deg: float
    gust: Optional[float] = None


class CloudsDescription(BaseModel):
    # Cloudiness in percentage
    all: float


class PrecipitationDescription(BaseModel):
    one_hour: float = Field(alias="1h")


class RainDescription(PrecipitationDescription):
    pass


class SnowDescription(PrecipitationDescription):
    pass


class WeatherSysParams(BaseModel):
    country: str
    sunrise: float
    sunset: float

    model_config = ConfigDict(extra="allow")


class CurrentWeather(BaseModel):
    coord: LatLon
    weather: list[WeatherConditionCode]
    main: WeatherDescription
    visibility: float
    wind: WindDescription
    rain: Optional[RainDescription] = None
    snow: Optional[SnowDescription] = None
    sys: WeatherSysParams
    # Time of data calcuation, unix timestamp
    dt: float
    # Shift in seconds from UTC
    timezone: float

    @property
    def conditions(self):
        match self.weather:
            case []:
                raise ValueError("Weather data did not contain any conditions")
            case _:
                return self.weather[0]

    model_config = ConfigDict(extra="allow")


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
def get_current_weather(api_key: Optional[str] = None) -> CurrentWeather:
    url = "https://api.openweathermap.org/data/2.5/weather"
    data = _make_openweather_api_call(url, api_key)
    return CurrentWeather.model_validate(data)


@deprecated("Please use get_current_weather instead")
def get_weather(api_key: Optional[str] = None) -> CurrentWeather:
    """Get the current weather"""
    return get_current_weather(api_key=api_key)


def get_5_day_forecast(api_key: Optional[str] = None):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    return _make_openweather_api_call(url, api_key)
