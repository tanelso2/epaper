from datetime import datetime
from functools import cached_property
import logging
import math
from typing import override, List, Optional

from PIL import ImageDraw

from epaper.components.core import (
    AlignedWith,
    Below,
    BottomAlignedWith,
    BoundingBox,
    CenteredOn,
    Component,
    CompositeComponent,
    LabeledValueComponent,
    LeftOf,
    MatchAlignedWith,
    Position,
    RightAlignedWith,
    RightOf,
    TextComponent,
)
from epaper.components.fonts import font
from epaper.components.shapes import CircleComponent, RotatingArrowComponent
from epaper.data.location import tz
from epaper.data.weather import (
    CurrentWeather,
    get_current_weather,
    get_5_day_forecast,
)
from epaper.drawing.arrow import draw_arrow
from epaper.utils.angles import add_degrees, invert_degrees, invert_y, project_from
from epaper.utils.wind import cardinal_direction
import epaper.utils.wind_direction_constants as dirs

logger = logging.getLogger(__name__)


def temp(x):
    return f"{x} °F"


def ts(t):
    dt = datetime.fromtimestamp(t, tz=tz())
    return dt.strftime("%H:%M")


class TemperatureComponent(CompositeComponent):
    weather: CurrentWeather
    curr_temp: float
    feels_like: float

    def __init__(
        self,
        pos: Position,
        label_size: int = 24,
        value_size: int = 32,
        padding: int = 30,
        weather=None,
    ):
        self.label_font = font(size=label_size)
        self.value_font = font(size=value_size)
        self.padding = padding
        self.pos = pos
        self.weather = weather or get_current_weather()
        main = self.weather.main
        self.curr_temp = main.temp
        self.feels_like = main.feels_like
        children = self.make_children()
        super().__init__(children, pos=pos)

    def make_children(self) -> list[Component]:
        components = {
            "Temp": temp(self.curr_temp),
            "Feels Like": temp(self.feels_like),
        }
        children = []
        prev = None
        for label, v in components.items():
            if prev is None:
                val_pos = self.pos
            else:
                val_pos = Position(
                    x=RightAlignedWith(prev), y=Below(prev, padding=self.padding)
                )

            val_component = TextComponent(text=v, font=self.value_font, pos=val_pos)
            label_str = f"{label}:"
            label_component = TextComponent(
                text=label_str,
                font=self.label_font,
                pos=Position(
                    x=LeftOf(val_component, padding=4),
                    y=BottomAlignedWith(val_component),
                ),
            )
            children.append(val_component)
            children.append(label_component)
            prev = val_component
        return children


class WeatherComponent(CompositeComponent):
    weather: CurrentWeather

    def __init__(
        self,
        pos: Position,
        label_font=None,
        val_font=None,
        padding=30,
        weather: Optional[CurrentWeather] = None,
    ):
        self.label_font = label_font or font(size=24)
        self.val_font = val_font or font(size=32)
        self.padding = padding
        self.pos = pos
        self.weather = weather or get_current_weather()
        children = self.make_children()
        super().__init__(children, pos=pos)

    def make_children(self) -> list[Component]:
        main = self.weather.main
        curr_temp = main.temp
        humidity = main.humidity
        pressure = main.pressure
        feels_like = main.feels_like
        sys = self.weather.sys
        sunrise = sys.sunrise
        sunset = sys.sunset
        conditions = self.weather.conditions
        cond_desc = conditions.description

        components = {
            "Current": cond_desc,
            "Temp": temp(curr_temp),
            "Feels Like": temp(feels_like),
            "Humidity": f"{humidity}%",
            "Pressure": f"{pressure} hPa",
            "Sunrise": ts(sunrise),
            "Sunset": ts(sunset),
        }

        children = []
        prev = None
        for label, v in components.items():
            if prev is None:
                val_pos = self.pos
            else:
                val_pos = Position(
                    x=RightAlignedWith(prev), y=Below(prev, padding=self.padding)
                )

            val_component = TextComponent(text=v, font=self.val_font, pos=val_pos)
            label_str = f"{label}:"
            label_component = TextComponent(
                text=label_str,
                font=self.label_font,
                pos=Position(
                    x=LeftOf(val_component, padding=4),
                    y=BottomAlignedWith(val_component),
                ),
            )
            children.append(val_component)
            children.append(label_component)
            prev = val_component
        return children


class PrecipitationBanner(TextComponent):
    def __init__(self, pos: Position, weather=None):
        self.weather = weather or get_current_weather()
        msgs = []
        if self.weather.rain is not None:
            rain = self.weather.rain.one_hour
            msgs.append(f"Rain in last hour: {rain} mm")
        if self.weather.snow is not None:
            snow = self.weather.snow.one_hour
            msgs.append(f"Snow in last hour: {snow} mm")
        self.msgs = msgs
        text = "\n".join(msgs)
        super().__init__(text=text, font=font(size=30), pos=pos)

    @override
    def draw(self, draw):
        if not self.msgs:
            return
        super().draw(draw)


class ForecastSummary(CompositeComponent):
    def __init__(self, pos: Position, forecast, font_size=20, padding=1):
        curr_font = font(size=font_size)
        dt = datetime.fromtimestamp(forecast["dt"], tz=tz())
        time_str = dt.strftime("%H:%M")
        cond = forecast["weather"][0]["description"]
        temp_str = temp(forecast["main"]["temp"])
        time_component = TextComponent(text=time_str, font=curr_font, pos=pos)
        temp_component = TextComponent(
            text=temp_str,
            font=curr_font,
            pos=Position(
                x=AlignedWith(time_component), y=Below(time_component, padding=padding)
            ),
        )
        cond_component = TextComponent(
            text=cond,
            font=curr_font,
            pos=Position(
                x=AlignedWith(time_component), y=Below(temp_component, padding=padding)
            ),
        )
        children = [time_component, temp_component, cond_component]
        super().__init__(children, pos=pos)


class ForecastComponent(CompositeComponent):
    def __init__(self, pos: Position, forecast_data=None, count=5, day_padding=5):
        self.forecast_data = forecast_data or get_5_day_forecast()
        forecasts = self.forecast_data.get("list", [])
        children = []
        prev = None
        for i in range(0, min(count * 2, len(forecasts)), 2):
            forecast = forecasts[i]
            if prev is None:
                curr_pos = pos
            else:
                curr_pos = Position(
                    x=RightOf(prev, padding=day_padding), y=AlignedWith(prev)
                )
            curr_component = ForecastSummary(pos=curr_pos, forecast=forecast)
            children.append(curr_component)
            prev = curr_component
        super().__init__(children, pos=pos)


class ConditionsComponent(CompositeComponent):
    weather: CurrentWeather

    def __init__(
        self,
        pos: Position,
        weather,
        value_size=32,
        label_size=24,
        padding=10,
        label_padding=6,
    ):
        self.padding = padding
        self.label_padding = label_padding
        self.label_font = font(size=label_size)
        self.value_font = font(size=value_size)
        self.weather = weather or get_current_weather()
        main = self.weather.main
        humidity = main.humidity
        pressure = main.pressure
        conditions = self.weather.conditions
        cond_desc = conditions.description
        desc_comp = TextComponent(cond_desc, font=self.value_font, pos=pos)
        components = {"Humidity": f"{humidity}%", "Pressure": f"{pressure} hPa"}

        children = [desc_comp]

        prev = desc_comp
        for label, value in components.items():
            val_component = TextComponent(
                value,
                font=self.value_font,
                pos=Position(
                    x=RightAlignedWith(prev), y=Below(prev, padding=self.padding)
                ),
            )
            label_pos = Position(
                x=LeftOf(val_component, padding=self.label_padding),
                y=CenteredOn(val_component),
            )
            label_component = TextComponent(label, font=self.label_font, pos=label_pos)
            children.extend([val_component, label_component])
            prev = val_component

        super().__init__(children, pos=pos)


class WindComponent(CompositeComponent):
    def __init__(
        self,
        pos: Position,
        weather,
        value_size=32,
        label_size=24,
        padding=10,
        label_padding=6,
    ):
        self.padding = padding
        self.label_padding = label_padding
        self.label_font = font(size=label_size)
        self.value_font = font(size=value_size)
        self.weather = weather or get_current_weather()
        self.wind = self.weather.wind
        wind_speed = self.wind.speed
        wind_deg = self.wind.deg
        wind_str = f"{wind_speed:.2f} mph {cardinal_direction(wind_deg)}"
        comp = LabeledValueComponent(
            value=wind_str,
            label="Wind",
            value_font=self.value_font,
            label_font=self.label_font,
            value_pos=pos,
            label_pos="left",
            padding=padding,
        )
        children: List[Component] = [comp]
        if gust_speed := self.wind.gust:
            gust_str = f"Up to {gust_speed:.2f} mph"
            gust_comp = TextComponent(
                text=gust_str,
                font=self.label_font,
                pos=Position(x=MatchAlignedWith(comp), y=Below(comp, padding=10)),
            )
            children.append(gust_comp)
        super().__init__(children, pos=pos)


# Change this based on the configuration of your display.
# Mine is facing East
DISPLAY_UP_DIRECTION = dirs.E


class WindDirectionArrowComponent(CompositeComponent):
    def __init__(
        self,
        pos: Position,
        wind_deg: float,
        arrow_length: float = 40.0,
        arm_length: float = 5.0,
        padding: int = 5,
        line_width: int = 5,
        label_padding: float = 3.5,
        label_size: int = 12,
    ):
        radius = arrow_length / 2.0
        circle = CircleComponent(pos=pos, radius=radius, padding=padding)
        center = circle.center
        arrow = RotatingArrowComponent(
            pos=Position.centered_on(circle),
            arrow_deg=self._arrow_degs_from_wind(wind_deg),
            arrow_length=arrow_length,
            arm_length=arm_length,
            line_width=line_width,
        )
        children = [arrow, circle]

        label_font = font(size=label_size)
        north = self.north_deg
        degs = [add_degrees(north, 90.0 * i) for i in range(4)]
        deg_names = ["N", "W", "S", "E"]
        for deg, label in zip(degs, deg_names):
            logger.debug(f"{circle.center=}")
            x, y = project_from(
                center, length=(circle.size / 2.0) + label_padding, deg=invert_y(deg)
            )
            label_pos = (int(x), int(y))
            comp = TextComponent(
                label, font=label_font, pos=Position.centered_on(label_pos)
            )
            children.append(comp)

        super().__init__(children, pos)

    def _arrow_degs_from_wind(self, wind_deg: float) -> float:
        """
        Calculate the way the arrow should face based on the direction of the wind
        """
        # Flip the y direction since wind degrees rotate clockwise instead of anti-clockwise
        r1 = invert_y(wind_deg)
        # Rotate by 90 degrees to point North up
        r2 = add_degrees(r1, 90.0)
        # Rotate an additional amount so the arrow is correctly oriented with the display
        r3 = add_degrees(r2, DISPLAY_UP_DIRECTION)
        # Flip the arrow backwards since the tail of the arrow should be where the wind is coming from
        r4 = invert_degrees(r3)
        return r4

    @property
    def north_deg(self):
        return add_degrees(90.0, DISPLAY_UP_DIRECTION)
