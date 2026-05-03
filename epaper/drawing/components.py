from abc import ABC, abstractmethod
import logging
from typing import Optional, Protocol

from PIL import Image, ImageDraw

from epaper.components.core import Component
from epaper.components.debugging import BoundingBoxComponent
import epaper.drawing.colors as colors

logger = logging.getLogger(__name__)


def generate_image(
    width: int,
    height: int,
    components: dict[str, Component],
    image_mode: str = "1",
    background_color=colors.WHITE,
    draw_outlines: bool = False,
) -> Image.Image:
    ret = Image.new(image_mode, (width, height), color=background_color)
    draw = ImageDraw.Draw(ret)
    for name, c in components.items():
        try:
            logger.debug(f"Drawing component: {name}")
            c.draw(draw)
        except Exception:
            logger.exception(f"Error drawing component: {name}")
    if draw_outlines:
        for name, c in components.items():
            b = BoundingBoxComponent(c)
            logger.debug(f"Trying to draw the outline for component: {name}")
            b.draw(draw)
    return ret


class ImagePlanner(ABC):
    width: int
    height: int
    draw_outlines: bool
    _prev_components: dict[str, Component]
    _curr_components: dict[str, Component]
    _curr_image: Optional[Image.Image]

    def __init__(self, width: int, height: int, draw_outlines: bool = False):
        self.width = width
        self.height = height
        self.draw_outlines = draw_outlines
        self._prev_components = {}
        self._curr_components = {}
        self._curr_image = None

    @abstractmethod
    def create_components(self) -> dict[str, Component]:
        raise NotImplementedError("Subclasses must implement create_components")

    def generate(self) -> Image.Image:
        self._prev_components = self._curr_components
        self._curr_components = self.create_components()
        self._curr_image = generate_image(
            width=self.width,
            height=self.height,
            components=self._curr_components,
            draw_outlines=self.draw_outlines,
        )
        return self._curr_image

    @classmethod
    def construct(
        cls, width: int, height: int, *, draw_outlines: bool = False, **_
    ) -> "ImagePlanner":
        """
        Helper method to create a function that matches the ImagePlannerConstructor protocol
        """
        return cls(width=width, height=height, draw_outlines=draw_outlines)


class ImagePlannerConstructor(Protocol):
    def __call__(
        self,
        width: int,
        height: int,
        *,
        draw_outlines: bool = False,
        **kwargs,
    ) -> ImagePlanner: ...
