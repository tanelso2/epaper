from functools import cached_property
from typing import override

from PIL import ImageDraw

from epaper.components.core import Component, BoundingBox, Position
import epaper.drawing.colors as colors


class BoundingBoxComponent(Component):
    def __init__(self, other: Component, line_thickness: int = 1):
        x, y = other.position
        self.x = x
        self.y = y
        super().__init__(pos=Position(x, y))
        bbox = other.content_bbox
        if not bbox.is_normalized():
            self._inner = bbox.normalize()
        else:
            self._inner = bbox
        self._src_component = other
        self.line_thickness = line_thickness

    @cached_property
    @override
    def content_bbox(self) -> BoundingBox:
        return self._inner

    @override
    def draw(self, draw: ImageDraw.ImageDraw) -> None:
        box = self.bbox
        draw.rectangle(
            box.corners, width=self.line_thickness, fill=None, outline=colors.BLACK
        )
