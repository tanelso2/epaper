from datetime import datetime, timedelta
from typing import Literal

from epaper.components.core import (
    CompositeComponent,
    MatchAlignedWith,
    Below,
    Position,
)
from epaper.components.text import TextComponent
from epaper.components.fonts import font
from epaper.data.location import tz
from epaper.data.sunlight import hours_of_sunlight, next_sun_event, get_sunlight
from epaper.utils.time_formatting import hours_minutes_str


class SunlightComponent(CompositeComponent):
    def __init__(
        self,
        pos: Position,
        font_size=24,
        padding=10,
    ):
        self.padding = padding
        self.font = font(size=font_size)
        event_type, event_time = next_sun_event()
        now = datetime.now(tz())
        time_till = event_time - now
        hours_till = time_till.total_seconds() / 3600
        event_str = f"{event_type} in {hours_minutes_str(hours_till)}"
        if event_time.date() > now.date():
            # Next event is tomorrow, show tomorrow's sunlight hours
            sunlight_hours = hours_of_sunlight(now + timedelta(days=1))
            sunlight_str = f"{hours_minutes_str(sunlight_hours)} sunlight tomorrow"
        else:
            sunlight_hours = hours_of_sunlight()
            sunlight_str = f"{hours_minutes_str(sunlight_hours)} sunlight today"
        next_event_component = TextComponent(event_str, font=self.font, pos=pos)
        sunlight_component = TextComponent(
            sunlight_str,
            font=self.font,
            pos=Position(
                x=MatchAlignedWith(next_event_component),
                y=Below(next_event_component, padding=self.padding),
            ),
        )
        children = [next_event_component, sunlight_component]
        super().__init__(children, pos=pos)
