import logging
from typing import override

from epaper.components.core import (
    Component,
    Position,
    AlignedWith,
    Below,
    Above,
    LeftOf,
    CenteredOn,
    RightAlignedWith,
)
from epaper.drawing.components import ImagePlanner
from epaper.components.fonts import font
from epaper.components.date import DateComponent
from epaper.components.network import NetworkComponent
from epaper.components.sunlight import SunlightComponent
from epaper.components.time import TimeComponent
from epaper.components.weather import (
    TemperatureComponent,
    ConditionsComponent,
    ForecastComponent,
    PrecipitationBanner,
    WindComponent,
    WindDirectionArrowComponent,
)
from epaper.data.weather import get_weather

logger = logging.getLogger(__name__)


class EPaperImagePlanner(ImagePlanner):
    def __init__(
        self,
        width: int,
        height: int,
        padding: int = 30,
        draw_outlines: bool = False,
    ):
        self.padding = padding
        super().__init__(width=width, height=height, draw_outlines=draw_outlines)

    @override
    def create_components(self) -> dict[str, Component]:
        try:
            logger.debug("Initializing components")
            date = DateComponent(
                font(size=52), pos=Position(x=self.padding, y=self.padding)
            )
            time = TimeComponent(
                font(size=90),
                pos=Position(x=AlignedWith(date), y=Below(date, padding=20)),
            )
            network = NetworkComponent(
                pos=Position(x=self.padding, y=Below(time, padding=30)), font_size=20
            )
            weather_data = get_weather()
            temp = TemperatureComponent(
                pos=Position(
                    x=RightAlignedWith(self.width - self.padding), y=self.padding
                ),
                weather=weather_data,
                value_size=40,
            )
            conditions = ConditionsComponent(
                pos=Position(
                    x=RightAlignedWith(self.width - self.padding),
                    y=Below(temp, padding=25),
                ),
                weather=weather_data,
                padding=15,
            )
            forecast = ForecastComponent(
                pos=Position(x=self.padding, y=self.height - 100),
                count=5,
                day_padding=10,
            )
            precipitation = PrecipitationBanner(
                pos=Position(x=self.padding, y=Above(forecast, padding=15)),
                weather=weather_data,
            )
            wind = WindComponent(
                pos=Position(
                    x=RightAlignedWith(conditions), y=Below(conditions, padding=15)
                ),
                weather=weather_data,
            )
            wind_deg = weather_data.get("wind", {}).get("deg")
            wind_arrow = WindDirectionArrowComponent(
                pos=Position(x=LeftOf(wind, padding=12), y=CenteredOn(wind)),
                wind_deg=wind_deg,
                arrow_length=55.0,
                arm_length=15.0,
                label_padding=5.0,
            )
            sunlight = SunlightComponent(
                pos=Position(
                    x=self.padding,
                    y=Below(network, padding=15),
                ),
                font_size=28,
            )
        except Exception as e:
            logger.error("Error initializing components")
            raise e

        components = {
            "date": date,
            "time": time,
            "sunlight": sunlight,
            "temp": temp,
            "network": network,
            "conditions": conditions,
            "forecast": forecast,
            "precipitation": precipitation,
            "wind": wind,
            "wind_arrow": wind_arrow,
        }
        return components
