from datetime import datetime

from PIL import ImageDraw

from epaper.components.text import TextComponent
from epaper.components.fonts import font
from epaper.data.location import tz


class TimeComponent(TextComponent):
    def __init__(self, font, pos):
        now = datetime.now(tz=tz())
        text = now.strftime("%H:%M")
        super().__init__(text, font, pos)
