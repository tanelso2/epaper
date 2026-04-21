import logging

from PIL import Image, ImageDraw

from epaper.components.core import (
    Above,
    CenteredOn,
    Position,
    AlignedWith,
    Below,
    LeftOf,
    RightAlignedWith,
)
from epaper.components.date import DateComponent
from epaper.components.fonts import font
from epaper.components.time import TimeComponent
from epaper.components.network import NetworkComponent
from epaper.components.sunlight import SunlightComponent
from epaper.components.weather import (
    TemperatureComponent,
    WindComponent,
    PrecipitationBanner,
    ForecastComponent,
    ConditionsComponent,
)
from epaper.data.weather import get_weather
import epaper.drawing.colors as colors

logger = logging.getLogger(__name__)


class EPaperImage:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.img = Image.new("1", (self.width, self.height), colors.WHITE)
        self.draw = ImageDraw.Draw(self.img)
        self.padding = 25

    def generate(self) -> Image.Image | Exception:
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
            sunlight = SunlightComponent(
                pos=Position(
                    x=self.padding,
                    y=Below(network, padding=15),
                ),
                font_size=28,
            )
        except Exception as _:
            logger.exception("Error initializing components")
            return Exception("Error initializing components")
        components = [
            date,
            time,
            sunlight,
            temp,
            network,
            conditions,
            forecast,
            precipitation,
            wind,
        ]
        for c in components:
            try:
                logger.debug(f"Drawing component: {c}")
                c.draw(self.draw)
            except Exception:
                logger.exception(f"Error drawing component: {c}")
        return self.img
