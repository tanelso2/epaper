from datetime import datetime
import logging
from typing import override, List

from epaper.components.core import (
    AlignedWith,
    Below,
    BottomAlignedWith,
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
from epaper.data.location import tz
from epaper.data.weather import get_weather, get_5_day_forecast
from epaper.utils.wind import cardinal_direction

logger = logging.getLogger(__name__)


def temp(x):
    return f"{x} °F"


def ts(t):
    dt = datetime.fromtimestamp(t, tz=tz())
    return dt.strftime("%H:%M")


class TemperatureComponent(CompositeComponent):
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
        self.weather = weather or get_weather()
        main = self.weather.get("main", {})
        self.curr_temp = main.get("temp")
        self.feels_like = main.get("feels_like")
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
    def __init__(
        self, pos: Position, label_font=None, val_font=None, padding=30, weather=None
    ):
        self.label_font = label_font or font(size=24)
        self.val_font = val_font or font(size=32)
        self.padding = padding
        self.pos = pos
        self.weather = weather or get_weather()
        children = self.make_children()
        super().__init__(children, pos=pos)

    def make_children(self) -> list[Component]:
        main = self.weather.get("main", {})
        curr_temp = main.get("temp")
        max_temp = main.get("temp_max")
        min_temp = main.get("temp_min")
        humidity = main.get("humidity")
        pressure = main.get("pressure")
        feels_like = main.get("feels_like")
        sys = self.weather.get("sys", {})
        sunrise = sys.get("sunrise")
        sunset = sys.get("sunset")
        conditions = self.weather.get("weather", [])[0]
        cond_name = conditions.get("main")
        cond_desc = conditions.get("description")
        cond_icon = conditions.get("icon")

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
        self.weather = weather or get_weather()
        msgs = []
        if "rain" in self.weather:
            rain = self.weather["rain"].get("1h")
            msgs.append(f"Rain in last hour: {rain} mm")
        if "snow" in self.weather:
            snow = self.weather["snow"].get("1h")
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
        self.weather = weather or get_weather()
        main = self.weather.get("main", {})
        humidity = main.get("humidity")
        pressure = main.get("pressure")
        conditions = self.weather.get("weather", [])
        if len(conditions) < 1:
            raise ValueError("Could not get conditions from weather data")
        cond_desc = conditions[0].get("description")
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
        self.weather = weather or get_weather()
        wind = self.weather.get("wind")
        if not wind:
            raise ValueError("Could not get wind from weather")
        wind = wind
        wind_speed = wind["speed"]
        wind_deg = wind["deg"]
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
        if "gust" in wind:
            gust_speed = wind["gust"]
            gust_str = f"Up to {gust_speed:.2f} mph"
            gust_comp = TextComponent(
                text=gust_str,
                font=self.label_font,
                pos=Position(x=MatchAlignedWith(comp), y=Below(comp, padding=10)),
            )
            children.append(gust_comp)
        super().__init__(children, pos=pos)
