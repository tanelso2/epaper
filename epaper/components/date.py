from datetime import datetime

from epaper.components.core import TextComponent
from epaper.components.fonts import font
from epaper.data.location import tz


class DateComponent(TextComponent):
    def __init__(self, font, pos):
        now = datetime.now(tz=tz())
        text = now.strftime("%Y-%m-%d")
        super().__init__(text, font, pos)
