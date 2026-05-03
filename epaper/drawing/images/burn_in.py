import logging
from typing import override

from epaper.components.core import Component, Position
from epaper.components.shapes import CircleComponent
from epaper.drawing.components import ImagePlanner

logger = logging.getLogger(__name__)


class BurnInImagePlanner(ImagePlanner):
    _count: int
    _radius: int

    def __init__(self, width: int, height: int, draw_outlines: bool = False):
        self._count = 0
        self._radius = 100
        super().__init__(width, height, draw_outlines)

    def location(self) -> tuple[int, int]:
        y = self.height // 2
        x = (self._count * 20) % self.width
        return (x, y)

    @override
    def create_components(self) -> dict[str, Component]:
        self._count += 1
        pos = Position.centered_on(self.location())
        circle = CircleComponent(pos=pos, radius=self._radius, line_width=5)
        return {
            "circle": circle,
        }
