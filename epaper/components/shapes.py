from functools import cached_property
import logging
import math
from typing import override


from PIL import ImageDraw

from epaper.components.core import BoundingBox, Component, Position
from epaper.drawing.arrow import draw_arrow

logger = logging.getLogger(__name__)


class CircleComponent(Component):
    def __init__(
        self,
        pos: Position,
        radius: float = 10.0,
        line_width: int = 1,
        padding: int = 5,
    ):
        self.radius = radius
        self.line_width = line_width
        self.padding = padding
        super().__init__(pos)

    @property
    def center(self) -> tuple[int, int]:
        x_pos, y_pos = self.position
        logger.debug(
            f"In circle, {x_pos=}, {y_pos=} and {self.radius=} and {self.padding=}"
        )
        new_x = int(x_pos + self.radius + self.padding)
        new_y = int(y_pos + self.radius + self.padding)
        logger.debug(f"Center of circle is {(new_x, new_y)}")
        return (new_x, new_y)

    @property
    def size(self) -> int:
        return int(2 * (self.radius + self.padding))

    @override
    def draw(self, draw: ImageDraw.ImageDraw):
        draw.circle(self.center, radius=self.radius, width=self.line_width)

    @cached_property
    @override
    def content_bbox(self) -> BoundingBox:
        return BoundingBox(
            top=0,
            left=0,
            bottom=self.size,
            right=self.size,
        )


class RotatingArrowComponent(Component):
    def __init__(
        self,
        pos: Position,
        arrow_deg: float,
        arrow_length: float = 40.0,
        arm_length: float = 5.0,
        line_width: int = 5,
        arrow_line_width: int = 2,
    ):
        self.arrow_deg = arrow_deg
        self.arrow_length = arrow_length
        self.arm_length = arm_length
        self.line_width = line_width
        self.arrow_line_width = arrow_line_width
        super().__init__(pos)

    @property
    def radius(self) -> float:
        return self.arrow_length / 2.0

    @property
    def center(self):
        x, y = self.position
        r = self.radius
        center_x = int(x + r)
        center_y = int(y + r)
        logger.debug(f"Center of arrow is {(center_x, center_y)}")
        return (center_x, center_y)

    @cached_property
    @override
    def content_bbox(self) -> BoundingBox:
        return BoundingBox(
            left=0,
            top=0,
            right=math.ceil(self.arrow_length),
            bottom=math.ceil(self.arrow_length),
        )

    @override
    def draw(self, draw: ImageDraw.ImageDraw):
        draw_arrow(
            draw,
            center=self.center,
            direction_degs=self.arrow_deg,
            r=self.radius,
            arm_length=self.arm_length,
            line_width=self.line_width,
        )
